"""
Variable Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from cf_units import Unit
from numpy import ndarray, dtype
from memberobjects import MemberObject


class Variable(MemberObject):
    """
    Metadata describing a NetCDF variable
    """

    _NETCDF3_TYPES_ = ('byte', 'char', 'short', 'int',
                       'float', 'double')

    _NETCDF4_TYPES_ = ('byte', 'ubyte', 'char',
                       'short', 'ushort',
                       'int', 'uint',
                       'int64', 'uint64',
                       'float', 'double', 'real')

    _NUMPY_DTYPES_ = (dtype('b'), dtype('u1'), dtype('S1'),
                      dtype('i2'), dtype('u2'),
                      dtype('i4'), dtype('u4'),
                      dtype('i8'), dtype('u8'),
                      dtype('f4'), dtype('f8'), dtype('f4'))

    @classmethod
    def datatype_from_dtype(cls, dt):
        if not isinstance(dt, dtype) or dt not in Variable._NUMPY_DTYPES_:
            raise TypeError('Unrecognized variable dtype {!r}'.format(dt))
        idt = Variable._NUMPY_DTYPES_.index(dt)
        return Variable._NETCDF4_TYPES_[idt]

    def __init__(self, name, definition=None, datatype=None, dimensions=None, attributes={}, **kwds):
        super(Variable, self).__init__(name, **kwds)
        self.__definition = self.__validate_definition(definition)
        self.__datatype = self.__validate_datatype(datatype)
        self.__dimensions = self.__validate_dimensions(dimensions)
        self.__attributes = self.__validate_attributes(attributes)
        self.__files = None

    def __validate_definition(self, definition):
        if definition is None:
            return None
        if not isinstance(definition, (basestring, ndarray)):
            msg = 'Variable {!r} must have a string or array definition'
            raise TypeError(msg.format(self.name))
        return definition

    def __validate_datatype(self, datatype):
        if datatype is None:
            return None
        if datatype not in Variable._NETCDF4_TYPES_:
            msg = 'Variable {!r} has invalid datatype {!r}'
            raise ValueError(msg.format(self.name, datatype))
        return datatype

    def __validate_dimensions(self, dimensions):
        if dimensions is None:
            return None
        if not (isinstance(dimensions, (list, tuple)) and
                all(isinstance(d, basestring) for d in dimensions)):
            msg = 'Variable {!r} must have a list or tuple of dimension names'
            raise TypeError(msg.format(self.name))
        for dname in dimensions:
            self.dataset.get_dimension(dname)
        return dimensions

    def __validate_attributes(self, attributes):
        if not isinstance(attributes, dict):
            msg = 'Variable {!r} attributes should be a dictionary'
            raise TypeError(msg.format(self.name))
        return attributes

    @classmethod
    def from_netcdf4(cls, ncvar, **kwds):
        dt = cls.datatype_from_dtype(ncvar.dtype)
        ncatts = {a: ncvar.getncattr(a) for a in ncvar.ncattrs()}
        return Variable(ncvar.name, datatype=dt, dimensions=ncvar.dimensions,
                        attributes=ncatts, **kwds)

    @property
    def definition(self):
        return self.__definition

    @property
    def datatype(self):
        return self.__datatype

    @property
    def dtype(self):
        idt = Variable._NETCDF4_TYPES_.index(self.__datatype)
        return Variable._NUMPY_DTYPES_[idt]

    def is_netcdf3_type(self):
        return self.datatype in Variable._NETCDF3_TYPES_

    @property
    def dimensions(self):
        return self.__dimensions

    def get_dimensions(self):
        return {n: self.dataset.get_dimension(n) for n in self.dimensions}

    @property
    def files(self):
        if self.__files is None:
            return None
        return frozenset(self.__files)

    def _add_to_file(self, fname):
        if self.__files is None:
            self.__files = set()
        self.__files.add(fname)

    def get_files(self):
        return {n: self.dataset.get_file(n) for n in self.files}

    @property
    def attributes(self):
        return frozenset(self.__attributes)

    def get_attribute(self, name):
        return self.__attributes[name]

    @property
    def standard_name(self):
        return self.__attributes.get('standard_name', None)

    @property
    def units(self):
        ustr = str(self.__attributes.get('units', '?')
                   ).split('since')[0].strip()
        return None if ustr in ('', '?', 'unknown') else ustr

    @property
    def refdatetime(self):
        lstr = str(self.__attributes.get('units', '?')).split('since')
        rstr = lstr[1].strip() if len(lstr) > 1 else ''
        return None if rstr in ('', '?', 'unknown') else rstr

    @property
    def calendar(self):
        return self.__attributes.get('calendar', None)

    def cfunits(self):
        return Unit(self.__attributes.get('units'), calendar=self.calendar)

    @property
    def positive(self):
        return self.__attributes.get('positive', None)

    @property
    def axis(self):
        return self.__attributes.get('axis', None)

    @property
    def bounds(self):
        return self.__attributes.get('bounds', None)

    @property
    def auxcoords(self):
        return frozenset(self.__attributes.get('coordinates', '').split())

    @property
    def coordinates(self):
        if self.dimensions is None:
            return self.auxcoords
        else:
            coords = {n for n in self.dimensions if n in self.dataset.variables}
            return frozenset(coords.union(self.auxcoords))

    def get_coordinates(self):
        return {n: self.dataset.get_variable(n) for n in self.coordinates}

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False
        elif self.definition != other.definition:
            return False
        elif self.datatype != other.datatype:
            return False
        elif self.dimensions != other.dimensions:
            return False
        elif self.units != other.units:
            return False
        elif self.refdatetime != other.refdatetime:
            return False
        elif self.calendar != other.calendar:
            return False
        elif self.positive != other.positive:
            return False
        elif self.auxcoords != other.auxcoords:
            return False
        elif self.axis != other.axis:
            return False
        else:
            return True

    def __ne__(self, other):
        return not (self == other)
