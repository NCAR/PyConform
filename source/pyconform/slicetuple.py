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
    
    def __init__(self, obj):
        """
        Initializer
        
        Parameters:
            obj (tuple, slice, int): Initializing object, can be a tuple of
                slice or int objects, or a single slice or int object
        """
        if isinstance(obj, (int, slice)):
            self._idx = obj
        elif isinstance(obj, tuple):
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
        if isinstance(self._idx, int):
            return str(self._idx)
        elif isinstance(self._idx, slice):
            return ':'.join('' if s is None else str(s) for s in
                            [self._idx.start, self._idx.stop, self._idx.step])
        elif isinstance(self._idx, tuple):
            return '({0})'.format(','.join(str(SliceTuple(s)) for s in self._idx))
    
    @property
    def index(self):
        """
        Return the object that indexes into an array
        """
        return self._idx        
