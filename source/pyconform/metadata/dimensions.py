"""
Dimension Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from memberobjects import MemberObject
from numpy import integer


class Dimension(MemberObject):
    """
    Metadata describing a NetCDF dimension
    """

    def __init__(self, name, **kwds):
        super(Dimension, self).__init__(name, **kwds)
        self.__size = None
        self.__is_unlimited = False

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, size):
        if size is None:
            self.__size = None
        elif isinstance(size, (int, integer)) and size > 0:
            self.__size = size
        else:
            msg = 'Dimension {!r} must have positive integer size'
            raise TypeError(msg.format(self.name))

    @property
    def is_unlimited(self):
        return self.__is_unlimited

    @is_unlimited.setter
    def is_unlimited(self, unlimited):
        self.__is_unlimited = bool(unlimited)

    @classmethod
    def from_netcdf4(cls, ncdim, **kwds):
        obj = cls(ncdim.name, **kwds)
        obj.size = len(ncdim)
        obj.is_unlimited = ncdim.isunlimited()
        return obj

    def __eq__(self, other):
        if not isinstance(other, Dimension):
            return False
        elif self.size != other.size:
            return False
        elif self.is_unlimited != other.is_unlimited:
            return False
        else:
            return True

    def __ne__(self, other):
        return not (self == other)
