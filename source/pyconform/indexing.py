"""
Index Class & Functions

Because Python treats input to the __getitem__ method of a class as special, allowing for syntax
that cannot normally be supplied to any other method or function, the Index class provides a way
of parsing input to the __getitem__ method and returning the parsed value.

The Index class provides 2 ways of returning the __getitem__ parsing: through a static interface
and through an instantiated interface.

In the static inteface, one simply calls Index[index] to return a parsing of the index syntax into
a Python indexing object.  For example:

    >>> Index[1:2:3, 4] == (slice(1,2,3), 4)
    True
    
    >>> Index[1] == 1
    True
    
    >>> Index[1:2:3] == slice(1,2,3)
    True

The instantiated interface is slightly different, requiring an instantiation of an Index object
before any attempts to parse an index.  For example:

    >>> idx = Index()
    
    >>> idx[1]
    <indexing.Index at 0x102c89fd0>

    >>> idx.value
    1

The instantiated interface also allows for smart string conversion from an indexing object.

    >>> str(idx[1:2:3, 4])
    '1:2:3, 4'

In the instantiated case, the last index input into the __getitem__ method (i.e., through the [...]
interface) is stored in the instantiation of the Index object.  This allows you to references the
last input index.  For example:

    >>> idx[1,2,3:4:5]
    
    >>> str(idx)
    '1, 2, 3:4:5'

----------------------------------------------------------------------------------------------------

The 'join' operations in this module are designed to reduce multiple slicing operations, where
consecutive slices are reduced to a single slice:

    A[slice1][slice2] = A[slice12]

Most Python programmers that work with Numpy have been told that slicing an array results in a 
'view' of the array.  Namely, they have been told that slicing the array costs nothing, so multiple
consecutive slices need no reduction.

While this statement is true for in-memory (Numpy) arrays, array-like access to data stored on file
(NetCDF, for example) presents a problem.  The first slice of the file-storaged data results in an
I/O read operation which returns an in-memory (Numpy) array, and the second slice results in a view
of that array.  The I/O operation can be costly, so it is worth our time to invest in a way of
reducing the amount of data read, as well as limiting the possibility of overrunning memory with
a large read.

----------------------------------------------------------------------------------------------------

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from types import EllipsisType
from numpy import index_exp, arange


#===================================================================================================
# index_str
#===================================================================================================
def index_str(index):
    """
    Convert an index expression into a compact string
    """
    if isinstance(index, int):
        return str(index)
    elif isinstance(index, EllipsisType):
        return '...'
    elif isinstance(index, slice):
        strrep = ''
        if index.start is not None:
            strrep += str(index.start)
        strrep += ':'
        if index.stop is not None:
            strrep += str(index.stop)
        if index.step is not None:
            strrep += ':{!s}'.format(index.step)
        return strrep
    elif isinstance(index, tuple):
        return ', '.join(index_str(i) for i in index)
    else:
        raise ValueError('Unsupported index value {!r}'.format(index))


#===================================================================================================
# _index_tuple_
#===================================================================================================
def _index_tuple_(index, shape):
    """
    Generate an index tuple from a given index expression and array shape tuple
    """
    idx = index_exp(index)
    ndims = len(shape)

    # Find the locations of all Ellipsis in the index expression
    elocs = [loc for loc, i in enumerate(idx) if isinstance(i, EllipsisType)]
    if len(elocs) == 0:
        nfill = ndims - len(idx)
        if nfill < 0:
            raise ValueError('Too many indices for array of shape {}'.format(shape))
        return idx + (slice(None),) * nfill
    elif len(elocs) == 1:
        eloc = elocs[0]
        prefix = idx[:eloc]
        suffix = idx[eloc + 1:]
        nfill = ndims - len(prefix) - len(suffix)
        if nfill < 0:
            raise ValueError('Too many indices for array of shape {}'.format(shape))
        return prefix + (slice(None),) * nfill + suffix
    else:
        raise ValueError('Too many ellipsis in index expression {}'.format(idx))


#===================================================================================================
# join
#===================================================================================================
def join(shape0, index1, index2):
    """
    Join two index expressions into a single index expression
    
    Parameters:
        shape0: The shape of the original array
        index1: The first index expression to apply to the array
        index2: The second index expression to apply to the array
    """
    if not isinstance(shape0, tuple):
        raise TypeError('Array shape must be a tuple')
    if len(shape0) == 0:
        raise TypeError('Cannot index scalar array')
    for n in shape0:
        if not isinstance(n, int):
            raise TypeError('Array shape must be a tuple of integers')

    idx1 = _index_tuple_(index1, shape0)
    shape1_ = tuple(None if isinstance(s, int) else len(arange(n)[s]) for s, n in zip(idx1, shape0))
    shape1 = tuple(s for s in shape1_ if s is not None)
    idx2 = _index_tuple_(index2, shape1)
