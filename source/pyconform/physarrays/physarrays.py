"""
Physical Array Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import functions as fn
import xarray as xr
import operator as op

__OP_SYMBOLS__ = {'__add__': '+', '__radd__': '+', '__iadd__': '+',
                  '__sub__': '-', '__rsub__': '-', '__isub__': '-',
                  '__mul__': '*', '__rmul__': '*', '__imul__': '*',
                  '__div__': '/', '__rdiv__': '/', '__idiv__': '/',
                  '__truediv__': '/', '__rtruediv__': '/', '__itruediv__': '/'}

__SYMBOL_OPS__ = {'+': op.add, '-': op.sub, '*': op.mul, '/': op.div}

__ROP_NAMES__ = {'__radd__', '__rsub__',
                 '__rmul__', '__rdiv__', '__rtruediv__'}


def _bin_op_name(func, self, other):
    nself = fn.get_name(self)
    nother = fn.get_name(other)
    if func.__name__ in __ROP_NAMES__:
        return '({}{}{})'.format(nother, __OP_SYMBOLS__[func.__name__], nself)
    else:
        return '({}{}{})'.format(nself, __OP_SYMBOLS__[func.__name__], nother)


def _bin_op_match_units_decorator(func):
    def wrapper(self, other):
        self_units = fn.get_cfunits(self)
        new_other = fn.convert(other, self_units)
        new_array = func(self, new_other)
        fn.set_cfunits(new_array, self_units)
        new_array.name = _bin_op_name(func, self, new_other)
        return new_array
    return wrapper


def _bin_op_compute_units_decorator(func):
    def wrapper(self, other):
        self_units = fn.get_cfunits(self)
        other_units = fn.get_cfunits(other)
        op = __SYMBOL_OPS__[__OP_SYMBOLS__[func.__name__]]
        new_units = op(self_units, other_units)
        new_array = func(self, other)
        fn.set_cfunits(new_array, new_units)
        new_array.name = _bin_op_name(func, self, other)
        return new_array
    return wrapper


def _bin_op_match_positive_decorator(func):
    def wrapper(self, other):
        self_pos = fn.get_positive(self)
        fn.change_positive(other, self_pos)
        other.name = other.name
        new_array = func(self, other)
        new_array.name = _bin_op_name(func, self, other)
        return new_array
    return wrapper


class PhysArray(xr.DataArray):
    """
    Physical Array subclass of xarray.DataArray
    """

    def __init__(self, *args, **kwds):
        units = kwds.pop('units', None)
        calendar = kwds.pop('calendar', None)
        positive = kwds.pop('positive', None)
        super(PhysArray, self).__init__(*args, **kwds)
        if units:
            self.attrs['units'] = units
        if calendar:
            self.attrs['calendar'] = calendar
        if positive:
            self.attrs['positive'] = positive

    @property
    def cfunits(self):
        return fn.get_cfunits(self)

    @cfunits.setter
    def cfunits(self, to_units):
        fn.set_cfunits(self, to_units)

    @property
    def positive(self):
        return self.attrs.get('positive', None)

    @positive.setter
    def positive(self, p):
        fn.set_positive(self, p)

    @_bin_op_match_units_decorator
    def __add__(self, other):
        return super(PhysArray, self).__add__(other)

    @_bin_op_match_units_decorator
    def __radd__(self, other):
        return super(PhysArray, self).__radd__(other)

    @_bin_op_match_units_decorator
    def __iadd__(self, other):
        return super(PhysArray, self).__iadd__(other)

    @_bin_op_match_units_decorator
    def __sub__(self, other):
        return super(PhysArray, self).__sub__(other)

    @_bin_op_match_units_decorator
    def __rsub__(self, other):
        return super(PhysArray, self).__rsub__(other)

    @_bin_op_match_units_decorator
    def __isub__(self, other):
        return super(PhysArray, self).__isub__(other)

    @_bin_op_compute_units_decorator
    def __mul__(self, other):
        return super(PhysArray, self).__mul__(other)

    @_bin_op_compute_units_decorator
    def __rmul__(self, other):
        return super(PhysArray, self).__rmul__(other)

    @_bin_op_compute_units_decorator
    def __imul__(self, other):
        return super(PhysArray, self).__imul__(other)

    @_bin_op_compute_units_decorator
    def __div__(self, other):
        return super(PhysArray, self).__div__(other)

    @_bin_op_compute_units_decorator
    def __rdiv__(self, other):
        return super(PhysArray, self).__rdiv__(other)

    @_bin_op_compute_units_decorator
    def __idiv__(self, other):
        return super(PhysArray, self).__idiv__(other)

    @_bin_op_compute_units_decorator
    def __truediv__(self, other):
        return super(PhysArray, self).__truediv__(other)

    @_bin_op_compute_units_decorator
    def __rtruediv__(self, other):
        return super(PhysArray, self).__rtruediv__(other)

    @_bin_op_compute_units_decorator
    def __itruediv__(self, other):
        return super(PhysArray, self).__itruediv__(other)
