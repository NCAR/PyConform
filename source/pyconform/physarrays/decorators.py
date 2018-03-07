"""
PhysArray

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from functions import get_cfunits, set_cfunits, convert
from functions import get_positive, set_positive, flip


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


def uni_op_unitless(func):
    def wrapper(self):
        old_name = self.name
        new_array = func(convert(self, 1))
        new_array.name = '{}({})'.format(func.__name__, old_name)
        return new_array
    return wrapper
