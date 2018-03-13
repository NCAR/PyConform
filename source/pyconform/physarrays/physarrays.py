"""
PhysArray Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from exceptions import PositiveError
from decorators import bin_op_compute_units, bin_op_match_positive, bin_op_match_units, uni_op_unitless
from functions import get_data, get_name
from functions import get_cfunits, set_cfunits, convert
from xarray.core.utils import is_scalar

import xarray as xr
import numpy as np


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

    def __repr__(self):
        return repr(self._data).replace('xarray.DataArray', 'PhysArray')

    def __array_ufunc__(self, ufunc, method, *args, **kwds):
        fname = ufunc.__name__
        if 'name' in kwds:
            name = kwds.pop('name')
        else:
            names = [get_name(a) for a in args]
            names += ['{}={}'.format(k, get_name(kwds[k])) for k in kwds]
            name = '{}({})'.format(fname, ', '.join(names))
        if hasattr(self, fname):
            _args = tuple(a for a in args if a is not self)
            result = getattr(self, fname)(*_args, **kwds)
        else:
            _args = tuple(get_data(a) for a in args)
            _kwds = dict((k, get_data(kwds[k])) for k in kwds)
            _kwds['keep_attrs'] = True
            _kwds['dask'] = 'parallelize'
            ufunc_method = getattr(ufunc, method)
            result = PhysArray(xr.apply_ufunc(ufunc_method, *_args, **_kwds))
        result.name = name
        return result

    def __neg__(self):
        name = '(-{})'.format(self.name)
        return self.__array_ufunc__(np.negative, '__call__', self, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __add__(self, other):
        name = '({}+{})'.format(self.name, get_name(other))
        return self.__array_ufunc__(np.add, '__call__', self, other, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __radd__(self, other):
        name = '({}+{})'.format(get_name(other), self.name)
        return self.__array_ufunc__(np.add, '__call__', other, self, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __sub__(self, other):
        name = '({}-{})'.format(self.name, get_name(other))
        return self.__array_ufunc__(np.subtract, '__call__', self, other, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __rsub__(self, other):
        name = '({}-{})'.format(get_name(other), self.name)
        return self.__array_ufunc__(np.subtract, '__call__', other, self, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __mul__(self, other):
        name = '({}*{})'.format(self.name, get_name(other))
        return self.__array_ufunc__(np.multiply, '__call__', self, other, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rmul__(self, other):
        name = '({}*{})'.format(get_name(other), self.name)
        return self.__array_ufunc__(np.multiply, '__call__', other, self, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __div__(self, other):
        name = '({}/{})'.format(self.name, get_name(other))
        return self.__array_ufunc__(np.divide, '__call__', self, other, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rdiv__(self, other):
        name = '({}/{})'.format(get_name(other), self.name)
        return self.__array_ufunc__(np.divide, '__call__', other, self, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __truediv__(self, other):
        name = '({}/{})'.format(self.name, get_name(other))
        return self.__array_ufunc__(np.true_divide, '__call__', self, other, name=name)

    @bin_op_match_positive
    @bin_op_compute_units
    def __rtruediv__(self, other):
        name = '({}/{})'.format(get_name(other), self.name)
        return self.__array_ufunc__(np.true_divide, '__call__', other, self, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __gt__(self, other):
        name = '({}>{})'.format(self.name, get_name(other))
        return self.__array_ufunc__(np.greater, '__call__', self, other, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def __lt__(self, other):
        name = '({}<{})'.format(self.name, get_name(other))
        return self.__array_ufunc__(np.less, '__call__', self, other, name=name)

    @bin_op_match_positive
    @bin_op_match_units
    def minimum(self, other, *args, **kwds):
        return PhysArray(np.minimum(self._data, get_data(other), *args, **kwds))

    @bin_op_match_positive
    @bin_op_match_units
    def maximum(self, other, *args, **kwds):
        return PhysArray(np.maximum(self._data, get_data(other), *args, **kwds))

    def __pow__(self, other):
        other_units = get_cfunits(other)
        if other_units.is_convertible(1) and is_scalar(other):
            new_other = convert(other, 1)
            new_units = pow(get_cfunits(self), new_other)
            new_name = '({}**{})'.format(self.name, get_name(other))
            new_array = self.__array_ufunc__(
                np.power, '__call__', self, new_other, name=new_name)
            set_cfunits(new_array, new_units)
            return new_array
        else:
            msg = "Exponents in 'pow' function must be unitless scalars, not {}"
            raise TypeError(msg.format(type(other)))

    def sqrt(self, *args, **kwds):
        new_units = get_cfunits(self).root(2)
        return PhysArray(np.sqrt(self._data, *args, **kwds), units=new_units)

    def cbrt(self, *args, **kwds):
        new_units = get_cfunits(self).root(3)
        return PhysArray(np.cbrt(self._data, *args, **kwds), units=new_units)

    @uni_op_unitless
    def sin(self, *args, **kwds):
        return PhysArray(np.sin(self._data, *args, **kwds))

    @uni_op_unitless
    def arcsin(self, *args, **kwds):
        return PhysArray(np.arcsin(self._data, *args, **kwds))

    @uni_op_unitless
    def cos(self, *args, **kwds):
        return PhysArray(np.cos(self._data, *args, **kwds))

    @uni_op_unitless
    def arccos(self, *args, **kwds):
        return PhysArray(np.arccos(self._data, *args, **kwds))

    @uni_op_unitless
    def tan(self, *args, **kwds):
        return PhysArray(np.tan(self._data, *args, **kwds))

    @uni_op_unitless
    def arctan(self, *args, **kwds):
        return PhysArray(np.arctan(self._data, *args, **kwds))

    def arctan2(self, other, *args, **kwds):
        new_other = convert(other, get_cfunits(self))
        return PhysArray(np.arctan2(self._data, get_data(new_other), *args, **kwds))

    @uni_op_unitless
    def exp(self, *args, **kwds):
        return PhysArray(np.exp(self._data, *args, **kwds))

    @uni_op_unitless
    def log(self, *args, **kwds):
        return PhysArray(np.log(self._data, *args, **kwds))

    @uni_op_unitless
    def log10(self, *args, **kwds):
        return PhysArray(np.log10(self._data, *args, **kwds))

    @uni_op_unitless
    def sinh(self, *args, **kwds):
        return PhysArray(np.sinh(self._data, *args, **kwds))

    @uni_op_unitless
    def arcsinh(self, *args, **kwds):
        return PhysArray(np.arcsinh(self._data, *args, **kwds))

    @uni_op_unitless
    def cosh(self, *args, **kwds):
        return PhysArray(np.cosh(self._data, *args, **kwds))

    @uni_op_unitless
    def arccosh(self, *args, **kwds):
        return PhysArray(np.arccosh(self._data, *args, **kwds))

    @uni_op_unitless
    def tanh(self, *args, **kwds):
        return PhysArray(np.tanh(self._data, *args, **kwds))

    @uni_op_unitless
    def arctanh(self, *args, **kwds):
        return PhysArray(np.arctanh(self._data, *args, **kwds))
