"""
Dimension Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from namedobjects import NamedObject


class Dimension(NamedObject):
    """
    Metadata describing a NetCDF dimension
    """

    def __init__(self, name, size=None, is_unlimited=False):
        super(Dimension, self).__init__(name)
        self.__size = self.__validate_size_type(size)
        self.__is_unlimited = self.__validate_is_unlimited_type(is_unlimited)

    def __validate_size_type(self, size):
        if size is None:
            return None
        if not isinstance(size, int):
            msg = 'Dimension {} must have integer size'
            raise TypeError(msg.format(self.name))
        return self.__validate_size_value(size)

    def __validate_size_value(self, size):
        if size < 1:
            msg = 'Dimension {} must have positive size'
            raise ValueError(msg.format(self.name))
        return size

    def __validate_is_unlimited_type(self, is_unlimited):
        if not isinstance(is_unlimited, bool):
            msg = 'Dimension {} must have bool is_unlimited'
            raise TypeError(msg.format(self.name))
        return is_unlimited

    @property
    def size(self):
        return self.__size

    @property
    def is_unlimited(self):
        return self.__is_unlimited

    @classmethod
    def from_netcdf4(cls, ncdim):
        return cls(ncdim.name, size=len(ncdim), is_unlimited=ncdim.isunlimited())
