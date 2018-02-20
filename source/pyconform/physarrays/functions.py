"""
Generic functions for special DataArray attribute handling

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from exceptions import UnitsError, PositiveError

import cf_units as cu
import xarray as xr
import numpy as np
import os


def convert(obj, to_units):
    from_units = get_cfunits(obj)
    if from_units == to_units:
        return obj
    elif from_units.is_convertible(to_units):
        new_obj = xr.apply_ufunc(from_units.convert, obj, to_units, keep_attrs=True,
                                 dask='parallelized', output_dtypes=[get_dtype(obj)])
        new_obj.name = "convert({}, to='{!s}')".format(obj.name, to_units)
        set_cfunits(new_obj, to_units)
        return type(obj)(new_obj)
    else:
        msg = "Cannot convert units '{!s}' to '{!s}'"
        raise UnitsError(msg.format(from_units, to_units))


def flip(obj, to_pos):
    from_pos = get_positive(obj)
    if from_pos == to_pos:
        return obj
    elif from_pos is None or to_pos is None:
        msg = 'No rule for changing positive direction from {!r} to {!r}'
        raise PositiveError(msg.format(to_pos, from_pos))
    else:
        new_obj = -obj
        new_obj.name = '{!s}({})'.format(to_pos, obj.name)
        set_positive(new_obj, to_pos)
        return type(obj)(new_obj)


def is_char_type(obj):
    return get_dtype(obj).char in ('S', 'U')


def is_equal(obj1, obj2):
    if not type(obj1) == type(obj2):
        return False
    elif not xr.DataArray.equals(obj1, obj2):
        return False
    elif not get_name(obj1) == get_name(obj2):
        return False
    elif not get_cfunits(obj1) == get_cfunits(obj2):
        return False
    elif not get_positive(obj1) == get_positive(obj2):
        return False
    else:
        return True


def get_dtype(obj):
    return np.asarray(obj).dtype


def get_name(obj):
    if isinstance(obj, xr.DataArray):
        return obj.name
    else:
        return ' '.join(str(obj).replace(os.linesep, ' ').split())


def get_cfunits(obj):
    if is_char_type(obj):
        return cu.Unit('no unit')
    elif isinstance(obj, xr.DataArray):
        ustr = obj.attrs.get('units', 1)
        cstr = obj.attrs.get('calendar', None)
        return cu.Unit(ustr, calendar=cstr)
    else:
        return cu.Unit(1)


def set_cfunits(obj, to_units):
    if isinstance(obj, xr.DataArray):
        obj.attrs['units'] = str(to_units)
        if isinstance(to_units, cu.Unit) and to_units.calendar:
            obj.attrs['calendar'] = str(to_units.calendar)
    elif not cu.Unit(to_units).is_no_unit():
        msg = "Cannot set units for object of type '{!s}'"
        raise UnitsError(msg.format(type(obj)))


def get_positive(obj):
    if isinstance(obj, xr.DataArray):
        p = obj.attrs.get('positive', None)
        if p is None:
            return p
        else:
            return str(p).lower()
    else:
        return None


def set_positive(obj, to_value):
    if isinstance(obj, xr.DataArray):
        if to_value is None:
            obj.attrs.pop('positive', None)
        else:
            pstr = str(to_value).lower()
            if pstr not in ('up', 'down'):
                raise PositiveError('Positive attribute must be up or down')
            obj.attrs['positive'] = pstr
    elif to_value is not None:
        msg = "Cannot set positive for object of type '{!s}'"
        raise PositiveError(msg.format(type(obj)))
