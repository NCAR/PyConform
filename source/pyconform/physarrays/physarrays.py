"""
Physical Array Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import functions as fn
import xarray as xr
import operator as op
from pyconform.physarrays.functions import get_units

__OP_SYMBOLS__ = {'__add__': '+', '__radd__': '+', '__iadd__': '+',
                  '__sub__': '-', '__rsub__': '-', '__isub__': '-',
                  '__mul__': '*', '__rmul__': '*', '__imul__': '*',
                  '__div__': '/', '__rdiv__': '/', '__idiv__': '/',
                  '__truediv__': '/', '__rtruediv__': '/', '__itruediv__': '/'}

__SYMBOL_OPS__ = {'+': op.add, '-': op.sub, '*': op.mul, '/': op.div}

__ROP_NAMES__ = {'__radd__', '__rsub__',
                 '__rmul__', '__rdiv__', '__rtruediv__'}


def convert(obj, to_units):
    u1 = fn.get_units(obj)
    if u1 != to_units:
        new_obj = xr.apply_ufunc(u1.convert, obj, to_units)
        new_obj.name = "convert({}, to='{!s}')".format(obj.name, to_units)
        return type(obj)(new_obj)
    else:
        return obj


def _bin_op_name(func, self, other):
    nself = fn.get_name(self)
    nother = fn.get_name(other)
    if func.__name__ in __ROP_NAMES__:
        return '({}{}{})'.format(nother, __OP_SYMBOLS__[func.__name__], nself)
    else:
        return '({}{}{})'.format(nself, __OP_SYMBOLS__[func.__name__], nother)


def _bin_op_match_units_decorator(func):
    def wrapper(self, other):
        new_other = convert(other, fn.get_units(self))
        newarr = func(self, new_other)
        if 'units' in self.attrs:
            newarr.attrs['units'] = self.attrs['units']
        newarr.name = _bin_op_name(func, self, new_other)
        return newarr
    return wrapper


def _bin_op_compute_units_decorator(func):
    def wrapper(self, other):
        uself = fn.get_units(self)
        uother = fn.get_units(other)
        op = __SYMBOL_OPS__[__OP_SYMBOLS__[func.__name__]]
        newunits = op(uself, uother)
        newarr = func(self, other)
        newarr.attrs['units'] = str(newunits)
        newarr.name = _bin_op_name(func, self, other)
        return newarr
    return wrapper


class PhysArray(xr.DataArray):
    """
    Physical Array subclass of xarray.DataArray
    """

    def __init__(self, *args, **kwds):
        super(PhysArray, self).__init__(*args, **kwds)

    @property
    def units(self):
        return get_units(self)

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
