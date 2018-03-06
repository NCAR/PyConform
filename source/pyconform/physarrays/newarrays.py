"""
PhysArray

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from exceptions import PositiveError
from functions import get_data, get_name
from functions import get_cfunits, set_cfunits, convert
from functions import get_positive, set_positive, flip
from xarray.core.utils import is_scalar

import xarray as xr
import numpy as np
import cf_units as cu

_COMPUTE_UNITS_ = {'__mul__': lambda x, y: x * y,
                   '__rmul__': lambda x, y: y * x,
                   '__div__': lambda x, y: x / y,
                   '__rdiv__': lambda x, y: y / x,
                   '__truediv__': lambda x, y: x / y,
                   '__rtruediv__': lambda x, y: y / x}


def bin_op_compute_units(func):
    def wrapper(self, other):
        self_units = get_cfunits(self)
        other_units = get_cfunits(other)
        new_units = _COMPUTE_UNITS_[func.__name__](self_units, other_units)
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


def uni_op_trig_units(func):
    def wrapper(self):
        old_name = self.name
        new_array = func(convert(self, 1))
        new_array.name = '{}({})'.format(func.__name__, old_name)
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
        self._data = xr.DataArray(*args, **kwds)
        if units:
            self.units = units
        if calendar:
            self.calendar = calendar
        if positive:
            self.positive = positive

    @property
    def data_array(self):
        return self._data

    @property
    def name(self):
        return self._data.name

    @name.setter
    def name(self, name):
        self._data.name = name

    @property
    def dtype(self):
        return self._data.dtype

    @property
    def units(self):
        return self._data.attrs.get('units', None)

    @units.setter
    def units(self, to_units):
        set_cfunits(self._data, to_units)

    @property
    def calendar(self):
        return self._data.attrs.get('calendar', None)

    @calendar.setter
    def calendar(self, to_cal):
        if to_cal is None:
            self._data.attrs.pop('calendar', None)
        else:
            self._data.attrs['calendar'] = str(to_cal)

    @property
    def positive(self):
        return self._data.attrs.get('positive', None)

    @positive.setter
    def positive(self, to_pos):
        if to_pos is None:
            self._data.attrs.pop('positive', None)
        else:
            pstr = str(to_pos).lower()
            if pstr not in ('up', 'down'):
                raise PositiveError('Positive attribute must be up or down')
            self._data.attrs['positive'] = pstr

    def cfunits(self):
        return get_cfunits(self._data)

    @property
    def attrs(self):
        return self._data.attrs

    def __str__(self):
        return str(self._data).replace('xarray.DataArray', 'PhysArray')

    def __neg__(self):
        name = '(-{})'.format(self.name)
        return PhysArray(-self._data, name=name, attrs=self.attrs)

    @bin_op_match_positive
    @bin_op_match_units
    def __add__(self, other):
        name = '({}+{})'.format(self.name, get_name(other))
        return PhysArray(self._data + get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __radd__(self, other):
        name = '({}+{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) + self._data, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __sub__(self, other):
        name = '({}-{})'.format(self.name, get_name(other))
        return PhysArray(self._data - get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __rsub__(self, other):
        name = '({}-{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) - self._data, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __mul__(self, other):
        name = '({}*{})'.format(self.name, get_name(other))
        return PhysArray(self._data * get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rmul__(self, other):
        name = '({}*{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) * self._data, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __div__(self, other):
        name = '({}/{})'.format(self.name, get_name(other))
        return PhysArray(self._data / get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rdiv__(self, other):
        name = '({}/{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) / self._data, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __truediv__(self, other):
        name = '({}/{})'.format(self.name, get_name(other))
        return PhysArray(self._data / get_data(other), name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rtruediv__(self, other):
        name = '({}/{})'.format(get_name(other), self.name)
        return PhysArray(get_data(other) / self._data, name=name)

    def __pow__(self, other):
        other_units = get_cfunits(other)
        if other_units.is_convertible(1) and is_scalar(other):
            new_other = convert(other, 1)
            new_units = pow(get_cfunits(self), new_other)
            new_array = pow(self._data, new_other)
            set_cfunits(new_array, new_units)
            new_array.name = '({}**{})'.format(self.name, get_name(other))
            return PhysArray(new_array)
        else:
            msg = "Exponents in 'pow' function must be unitless scalars, not {}"
            raise TypeError(msg.format(type(other)))

    def sqrt(self):
        new_units = get_cfunits(self).root(2)
        new_array = np.sqrt(self._data)
        set_cfunits(new_array, new_units)
        new_array.name = 'sqrt({})'.format(self.name)
        return PhysArray(new_array)

    @uni_op_trig_units
    def sin(self):
        return PhysArray(np.sin(self._data))

    @uni_op_trig_units
    def cos(self):
        return PhysArray(np.cos(self._data))

    @uni_op_trig_units
    def tan(self):
        return PhysArray(np.tan(self._data))
