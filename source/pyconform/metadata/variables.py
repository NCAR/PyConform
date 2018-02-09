"""
Variable Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from cf_units import Unit
from numpy import asarray, dtype
from collections import OrderedDict
from xarray.core.utils import Frozen
from memberobjects import MemberObject


def is_array_like(obj):
    try:
        arr = asarray(obj)
    except:
        return False
    if arr.ndim == 0:
        return False
    else:
        return True


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

    def __init__(self, name, **kwds):
        super(Variable, self).__init__(name, dataset=kwds.pop('dataset', None))
        self.__attributes = OrderedDict()
        self.__files = OrderedDict()
        self.definition = kwds.pop('definition', None)
        self.datatype = kwds.pop('datatype', None)
        self.dimensions = kwds.pop('dimensions', None)
        self.attributes.update(kwds.pop('attributes', {}))

    @property
    def definition(self):
        return self.__definition

    @definition.setter
    def definition(self, definition):
        if definition is None:
            self.__definition = None
        elif isinstance(definition, basestring):
            self.__definition = definition
        elif is_array_like(definition):
            self.__definition = definition
        else:
            msg = 'Variable {!r} must have a string or array-like definition'
            raise TypeError(msg.format(self.name))

    @property
    def datatype(self):
        return self.__datatype

    @datatype.setter
    def datatype(self, datatype):
        if datatype is None:
            self.__datatype = None
        elif datatype in Variable._NETCDF4_TYPES_:
            self.__datatype = datatype
        else:
            msg = 'Variable {!r} has invalid datatype {!r}'
            raise ValueError(msg.format(self.name, datatype))

    @property
    def dtype(self):
        idt = Variable._NETCDF4_TYPES_.index(self.__datatype)
        return Variable._NUMPY_DTYPES_[idt]

    def is_netcdf3_type(self):
        return self.datatype in Variable._NETCDF3_TYPES_

    @property
    def dimensions(self):
        if self.__dimensions is None:
            return None
        return Frozen(OrderedDict((d, self.dataset.dimensions[d]) for d in self.__dimensions))

    @dimensions.setter
    def dimensions(self, dimensions):
        if dimensions is None:
            self.__dimensions = None
        elif isinstance(dimensions, (list, tuple)):
            not_found = [d for d in dimensions
                         if d not in self.dataset.dimensions]
            if not_found:
                dstr = ', '.join(str(d) for d in not_found)
                msg = 'Variable {!r} references dimensions {} not found in dataset'
                raise KeyError(msg.format(self.name, dstr))
            self.__dimensions = dimensions
        else:
            msg = 'Variable {!r} must have a list or tuple of dimension names'
            raise TypeError(msg.format(self.name))

    @property
    def attributes(self):
        return self.__attributes

    @property
    def files(self):
        return Frozen(self.__files)

    def _add_to_file(self, fname):
        self.__files[fname] = self.dataset.files[fname]

    @property
    def standard_name(self):
        return self.__attributes.get('standard_name', None)

    @standard_name.setter
    def standard_name(self, standard_name):
        self.__attributes['standard_name'] = standard_name

    @property
    def units(self):
        if 'units' not in self.__attributes:
            return None
        else:
            units = self._split_units_attribute()[0].strip()
            return self.__validate_units_value(units)

    def _split_units_attribute(self):
        return [s.strip() for s in str(self.__attributes.get('units', '?')).split('since')]

    @units.setter
    def units(self, units):
        if units is None:
            self.__attributes.pop('units')
        else:
            ulist = self._split_units_attribute()
            ulist[0] = self.__validate_units_value(units)
            self.__attributes['units'] = ' since '.join(ulist)

    def __validate_units_value(self, units):
        if units in ('', '?', 'unknown'):
            return 'unknown'
        else:
            return str(units).strip()

    @property
    def refdatetime(self):
        ulist = self._split_units_attribute()
        if len(ulist) < 2:
            return None
        else:
            return self.__validate_units_value(ulist[1])

    @refdatetime.setter
    def refdatetime(self, refdt):
        if refdt is None:
            if self.units is not None:
                self.__attributes['units'] = self.units
            return
        if self.units is None:
            self.units = 'unknown'
        ulist = [self.units, self.__validate_units_value(refdt)]
        self.__attributes['units'] = ' since '.join(ulist)

    @property
    def calendar(self):
        return self.__attributes.get('calendar', None)

    @calendar.setter
    def calendar(self, calendar):
        Unit('days since 0001-01-01', calendar=calendar)
        self.__attributes['calendar'] = str(calendar).strip()

    def cfunits(self):
        return Unit(self.__attributes.get('units'), calendar=self.calendar)

    @property
    def positive(self):
        return self.__attributes.get('positive', None)

    @positive.setter
    def positive(self, positive):
        pstr = str(positive).strip()
        if pstr not in ['up', 'down']:
            msg = 'Variable {!r} cannot have positive value of {!r}'
            raise ValueError(msg.format(self.name, pstr))
        self.__attributes['positive'] = pstr

    @property
    def axis(self):
        return self.__attributes.get('axis', None)

    @axis.setter
    def axis(self, axis):
        axstr = str(axis).strip().upper()
        if axstr not in ['X', 'Y', 'Z', 'T']:
            msg = 'Variable {!r} cannot have axis value of {!r}'
            raise ValueError(msg.format(self.name, axstr))
        self.__attributes['axis'] = axstr

    @property
    def bounds(self):
        if 'bounds' in self.__attributes:
            bounds = self.__attributes['bounds']
            return self.dataset.variables[bounds]
        else:
            return None

    @bounds.setter
    def bounds(self, bounds):
        if bounds not in self.dataset.variables:
            msg = 'Bounds variable {!r} not found'
            raise KeyError(msg.format(bounds))
        self.__attributes['bounds'] = str(bounds)

    @property
    def auxcoords(self):
        auxcoords = self.__attributes.get('coordinates', '').split()
        return Frozen(OrderedDict((c, self.dataset.variables[c]) for c in auxcoords))

    @auxcoords.setter
    def auxcoords(self, auxcoords):
        if not isinstance(auxcoords, (tuple, list)):
            msg = 'Auxiliary coordinates must be given as a list or tuple'
            raise ValueError(msg)
        not_found = [c for c in auxcoords if c not in self.dataset.variables]
        if not_found:
            cstr = ', '.join(str(c) for c in not_found)
            msg = 'Auxiliary coordinate(s) {} not found in dataset'
            raise KeyError(msg.format(cstr))
        self.__attributes['coordinates'] = ' '.join(str(c) for c in auxcoords)

    @property
    def coordinates(self):
        if self.dimensions is None:
            return self.auxcoords
        else:
            coords = OrderedDict((n, self.dataset.variables[n]) for n in self.dimensions
                                 if n in self.dataset.variables)
            coords.update(self.auxcoords)
            return Frozen(coords)

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
