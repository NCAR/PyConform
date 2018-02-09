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
        super(File, self).__init__(name, dataset=kwds.pop('dataset', None))
        self.__attributes = OrderedDict()
        self.__dimensions = OrderedDict()
        self.__variables = OrderedDict()
        self.format = kwds.pop('format', 'NETCDF4_CLASSIC')
        self.deflate = kwds.pop('deflate', 1)
        self.shuffle = kwds.pop('shuffle', 'off')
        self.attributes.update(kwds.pop('attributes', {}))
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

    def add_dimensions(self, *dnames):
        not_found = [d for d in dnames if d not in self.dataset.dimensions]
        if not_found:
            dstr = ', '.join(repr(d) for d in not_found)
            msg = 'Unknown dimensions {} cannot be added to file {!r}'
            raise KeyError(msg.format(dstr, self.name))
        for d in dnames:
            self.__dimensions[d] = self.dataset.dimensions[d]

    def add_variables(self, *vnames):
        not_found = [v for v in vnames if v not in self.dataset.variables]
        if not_found:
            vstr = ', '.join(repr(d) for d in not_found)
            msg = 'Unknown variable {!r} cannot be added to file {!r}'
            raise KeyError(msg.format(vstr, self.name))
        for v in vnames:
            self.__variables[v] = self.dataset.variables[v]
            self.__variables[v]._add_to_file(self.name)

    @property
    def coordinates(self):
        return Frozen(OrderedDict((c, self.variables[c]) for c in self.variables
                                  if c in self.dataset.coordinates))
