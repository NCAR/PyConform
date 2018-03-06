"""
PhysArray

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from exceptions import PositiveError
from functions import get_data, get_name
from functions import get_cfunits, set_cfunits, convert
from functions import get_positive, set_positive, flip

import xarray as xr

__COMPUTE_UNITS__ = {'__mul__': lambda x, y: x * y,
                     '__rmul__': lambda x, y: y * x,
                     '__div__': lambda x, y: x / y,
                     '__rdiv__': lambda x, y: y / x,
                     '__truediv__': lambda x, y: x / y,
                     '__rtruediv__': lambda x, y: y / x}


def bin_op_compute_units(func):
    def wrapper(self, other):
        self_units = get_cfunits(self)
        other_units = get_cfunits(other)
        new_units = __COMPUTE_UNITS__[func.__name__](self_units, other_units)
        new_array = func(self, other)
        set_cfunits(new_array, new_units)
        return new_array
    return wrapper


def bin_op_match_units(func):
    def wrapper(self, other):
        new_units = get_cfunits(self)
        new_other = convert(other, new_units)
        new_array = func(self, new_other)
        if 'units' in self.attrs:
            set_cfunits(new_array, new_units)
        return new_array
    return wrapper


def bin_op_match_positive(func):
    def wrapper(self, other):
        self_pos = get_positive(self)
        new_other = flip(other, self_pos)
        new_array = func(self, new_other)
        set_positive(new_array, self_pos)
        return new_array
    return wrapper


class PhysArray(object):
    """
    PhysArray - Wrapper around an xarray.DataArray
    """

    def __init__(self, *args, **kwds):
        units = kwds.pop('units', None)
        calendar = kwds.pop('calendar', None)
        positive = kwds.pop('positive', None)
        self.__data = xr.DataArray(*args, **kwds)
        if units:
            self.units = units
        if calendar:
            self.calendar = calendar
        if positive:
            self.positive = positive

    @property
    def data_array(self):
        return self.__data

    @property
    def name(self):
        return self.__data.name

    @name.setter
    def name(self, name):
        self.__data.name = name

    @property
    def dtype(self):
        return self.__data.dtype

    @property
    def units(self):
        return self.__data.attrs.get('units', None)

    @units.setter
    def units(self, to_units):
        set_cfunits(self.__data, to_units)

    @property
    def calendar(self):
        return self.__data.attrs.get('calendar', None)

    @calendar.setter
    def calendar(self, to_cal):
        if to_cal is None:
            self.__data.attrs.pop('calendar', None)
        else:
            self.__data.attrs['calendar'] = str(to_cal)

    @property
    def positive(self):
        return self.__data.attrs.get('positive', None)

    @positive.setter
    def positive(self, to_pos):
        if to_pos is None:
            self.__data.attrs.pop('positive', None)
        else:
            pstr = str(to_pos).lower()
            if pstr not in ('up', 'down'):
                raise PositiveError('Positive attribute must be up or down')
            self.__data.attrs['positive'] = pstr

    def cfunits(self):
        return get_cfunits(self.__data)

    @property
    def attrs(self):
        return self.__data.attrs

    def __str__(self):
        return str(self.__data).replace('xarray.DataArray', 'PhysArray')

    def __neg__(self):
        name = '(-{})'.format(self.name)
        return PhysArray(-self.__data, name=name, attrs=self.attrs)

    @bin_op_match_positive
    @bin_op_match_units
    def __add__(self, other):
        name = '({}+{})'.format(self.name, get_name(other))
        return PhysArray(self.__data + get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __radd__(self, other):
        name = '({}+{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) + self.__data, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __sub__(self, other):
        name = '({}-{})'.format(self.name, get_name(other))
        return PhysArray(self.__data - get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __rsub__(self, other):
        name = '({}-{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) - self.__data, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __mul__(self, other):
        name = '({}*{})'.format(self.name, get_name(other))
        return PhysArray(self.__data * get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rmul__(self, other):
        name = '({}*{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) * self.__data, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __div__(self, other):
        name = '({}/{})'.format(self.name, get_name(other))
        return PhysArray(self.__data / get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rdiv__(self, other):
        name = '({}/{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) / self.__data, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __truediv__(self, other):
        name = '({}/{})'.format(self.name, get_name(other))
        return PhysArray(self.__data / get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rtruediv__(self, other):
        name = '({}/{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) / self.__data, name=name)
