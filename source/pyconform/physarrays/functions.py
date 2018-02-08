"""
Functions and decorators for handling units

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from exceptions import UnitsError

import cf_units as cu
import xarray as xr
import numpy as np
import os


def convert(obj, to_units):
    from_units = get_cfunits(obj)
    if from_units == to_units:
        return obj
    elif from_units.is_convertible(to_units):
        new_obj = xr.apply_ufunc(from_units.convert, obj, to_units)
        new_obj.name = "convert({}, to='{!s}')".format(obj.name, to_units)
        set_cfunits(new_obj, to_units)
        return type(obj)(new_obj)
    else:
        msg = "Cannot convert units '{!s}' to '{!s}'"
        raise UnitsError(msg.format(from_units, to_units))


def get_dtype(obj):
    return np.asarray(obj).dtype


def is_char_type(obj):
    return get_dtype(obj).char in ('S', 'U')


def get_name(obj):
    if isinstance(obj, xr.DataArray):
        return obj.name
    else:
        return ' '.join(str(obj).replace(os.linesep, ' ').split())


def get_cfunits(obj):
    if is_char_type(obj):
        return cu.Unit('no unit')
    elif isinstance(obj, xr.DataArray):
        ustr = obj.attrs.get('units', 'no unit')
        cstr = obj.attrs.get('calendar', None)
        return cu.Unit(ustr, calendar=cstr)
    else:
        return cu.Unit('no unit')


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
                raise ValueError('Positive attribute must be up or down')
            obj.attrs['positive'] = pstr
    elif to_value is not None:
        msg = "Cannot set positive for object of type '{!s}'"
        raise ValueError(msg.format(type(obj)))


def change_positive(obj, to_value):
    old_pos = get_positive(obj)
    new_pos = None if to_value is None else str(to_value).lower()
    if old_pos == new_pos:
        return
    elif old_pos is None or new_pos is None:
        set_positive(obj, to_value)
    else:
        flip_positive(obj)


def flip_positive(obj):
    pos = get_positive(obj)
    if pos is None:
        return
    elif pos == 'up':
        set_positive(obj, 'down')
    else:
        set_positive(obj, 'up')
    obj *= -1
