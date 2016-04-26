"""
SliceTuple Class

The SliceTuple object represents an object that can act as an array index, as
array slice, or a tuple of array indices or slices.  This provides one compact
object that can index or slice an array.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""


#===============================================================================
# SliceTuple
#===============================================================================
class SliceTuple(object):
    """
    Container class that represents a tuple of array slices
    """
    
    def __init__(self, obj=None):
        """
        Initializer
        
        Parameters:
            obj (tuple, slice, int): Initializing object, can be a tuple of
                slice or int objects, or a single slice or int object.  If None,
                defaults to slice(None)
        """
        if obj is None:
            self._idx = (slice(None),)
        elif isinstance(obj, SliceTuple):
            self._idx = obj._idx.copy()
        elif isinstance(obj, (int, slice)):
            self._idx = (obj,)
        elif isinstance(obj, tuple):
            if len(obj) == 0:
                raise TypeError('Empty tuple cannot be a SliceTuple')
            idx = []
            for i, o in enumerate(obj):
                if isinstance(o, (int, slice)):
                    idx.append(o)
                else:
                    raise TypeError(('Element {0} not an int or slice in tuple '
                                     '{1!r}').format(i, obj))
            self._idx = tuple(idx)
        else:
            raise TypeError(('Object not an int, slice, or tuple '
                             '{0!r}').format(obj))
    
    def __str__(self):
        """
        Compact string representation of SliceTuple
        """
        strreps = []
        for idx in self._idx:
            if isinstance(idx, int):
                strreps.append(str(idx))
            elif isinstance(idx, slice):
                sss = idx.start, idx.stop, idx.step
                strrep = ':'.join('' if s is None else str(s) for s in sss)
                strreps.append(strrep)
        return '({0})'.format(','.join(strreps))

    def __eq__(self, other):
        """
        Check if two SliceTuples are equal
        """
        return self._idx == other._idx

    def __ne__(self, other):
        """
        Check if two SliceTuples are not equal
        """
        return not (self._idx == other._idx)

    @property
    def index(self):
        """
        Return the object that indexes into an array
        """
        return self._idx        
