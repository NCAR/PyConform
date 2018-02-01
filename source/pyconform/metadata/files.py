"""
File Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import OrderedDict
from xarray.core.utils import Frozen
from memberobjects import MemberObject


class File(MemberObject):
    """
    Metadata describing a NetCDF file
    """
    _NETCDF3_FORMATS_ = {'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC',
                         'NETCDF3_64BIT_OFFSET', 'NETCDF3_64BIT_DATA',
                         'NETCDF3_64BIT'}

    _NETCDF4_FORMATS_ = {'NETCDF4'}

    def __init__(self, name, **kwds):
        super(File, self).__init__(name, **kwds)
        self.__attributes = OrderedDict()
        self.__format = 'NETCDF4_CLASSIC'
        self.__deflate = 1
        self.__shuffle = 'off'
        self.__variables = OrderedDict()
        self.__dimensions = OrderedDict()
        self.path = name

    @property
    def attributes(self):
        return self.__attributes

    @property
    def format(self):
        return self.__format

    @format.setter
    def format(self, fmt):
        if fmt in File._NETCDF3_FORMATS_ or fmt in File._NETCDF4_FORMATS_:
            self.__format = fmt
        else:
            msg = 'File {!r} format {!r} is not recognized'
            raise TypeError(msg.format(self.name, format))

    def is_netcdf3(self):
        if self.format in File._NETCDF3_FORMATS_:
            return True
        else:
            return False

    @property
    def deflate(self):
        return self.__deflate

    @deflate.setter
    def deflate(self, deflate):
        if deflate in range(10):
            self.__deflate = deflate
        else:
            msg = 'File {!r} deflate level must be an integer from 0 to 9'
            raise TypeError(msg.format(self.name))

    @property
    def shuffle(self):
        return self.__shuffle

    @shuffle.setter
    def shuffle(self, shfl):
        if shfl in ('on', 'off'):
            self.__shuffle = shfl
        else:
            msg = 'File {!r} shuffle must be "on" or "off"'
            raise TypeError(msg.format(self.name))

    @property
    def dimensions(self):
        return Frozen(self.__dimensions)

    @property
    def variables(self):
        return Frozen(self.__variables)

    def add_dimension(self, dname):
        if dname not in self.dataset.dimensions:
            msg = 'Unknown dimension {!r} cannot be added to file {!r}'
            raise KeyError(msg.format(dname, self.name))
        self.__dimensions[dname] = self.dataset.dimensions[dname]

    def add_variable(self, vname):
        if vname not in self.dataset.variables:
            msg = 'Unknown variable {!r} cannot be added to file {!r}'
            raise KeyError(msg.format(vname, self.name))
        self.__variables[vname] = self.dataset.variables[vname]
        self.__variables[vname]._add_to_file(self.name)

    @property
    def coordinates(self):
        return Frozen(OrderedDict((c, self.variables[c]) for c in self.variables
                                  if c in self.dataset.coordinates))
