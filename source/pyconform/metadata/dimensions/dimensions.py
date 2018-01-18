"""
Dimension Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from ..memberobjects import MemberObject


class Dimension(MemberObject):
    """
    Metadata describing a NetCDF dimension
    """

    def __init__(self, name, size=None, is_unlimited=False, **kwds):
        super(Dimension, self).__init__(name, **kwds)
        self.__size = self.__validate_size_type(size)
        self.__is_unlimited = self.__validate_is_unlimited_type(is_unlimited)

    def __validate_size_type(self, size):
        if size is None:
            return None
        if not isinstance(size, int):
            msg = 'Dimension {!r} must have integer size'
            raise TypeError(msg.format(self.name))
        return self.__validate_size_value(size)

    def __validate_size_value(self, size):
        if size < 1:
            msg = 'Dimension {!r} must have positive size'
            raise ValueError(msg.format(self.name))
        return size

    def __validate_is_unlimited_type(self, is_unlimited):
        if not isinstance(is_unlimited, bool):
            msg = 'Dimension {!r} must have bool is_unlimited'
            raise TypeError(msg.format(self.name))
        return is_unlimited

    @property
    def size(self):
        return self.__size

    @property
    def is_unlimited(self):
        return self.__is_unlimited

    @classmethod
    def from_netcdf4(cls, ncdim, **kwds):
        return cls(ncdim.name, size=len(ncdim), is_unlimited=ncdim.isunlimited(), **kwds)

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
