"""
PhysArray Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from exceptions import UnitsError, PositiveError
from os import linesep
from numpy import asarray
from cf_units import Unit

import xarray as xr


def get_name(obj):
    if hasattr(obj, 'name'):
        return obj.name
    else:
        return str(obj).replace(linesep, '')


def get_data(obj):
    if hasattr(obj, 'data_array'):
        return obj.data_array
    else:
        return obj


def get_dtype(obj):
    if hasattr(obj, 'dtype'):
        return obj.dtype
    else:
        return asarray(obj).dtype


def is_char_type(obj):
    return get_dtype(obj).char in ('S', 'U')


def get_cfunits(obj):
    if is_char_type(obj):
        return Unit('no unit')
    elif hasattr(obj, 'attrs'):
        ustr = obj.attrs.get('units', Unit(1))
        cstr = obj.attrs.get('calendar', None)
        return Unit(ustr, calendar=cstr)
    else:
        return Unit(1)


def set_cfunits(obj, to_units):
    if hasattr(obj, 'attrs'):
        obj.attrs['units'] = str(to_units)
        if isinstance(to_units, Unit):
            if to_units.calendar is None:
                obj.attrs.pop('calendar', None)
            else:
                obj.attrs['calendar'] = str(to_units.calendar)
    else:
        msg = 'Cannot set units for object of type {}'
        raise TypeError(msg.format(type(obj)))


def convert(obj, to_units):
    from_units = get_cfunits(obj)
    if from_units == to_units:
        return obj
    elif from_units.is_convertible(to_units):
        new_obj = xr.apply_ufunc(from_units.convert, get_data(obj), to_units, keep_attrs=True,
                                 dask='parallelized', output_dtypes=[get_dtype(obj)])
        new_obj = type(obj)(new_obj)
        if hasattr(new_obj, 'name'):
            new_obj.name = "convert({}, to='{!s}')".format(obj.name, to_units)
        if hasattr(new_obj, 'attrs'):
            set_cfunits(new_obj, to_units)
        return new_obj
    else:
        msg = 'Unable to convert units {!s} to {!s}'
        raise UnitsError(msg.format(from_units, to_units))


def get_positive(obj):
    if hasattr(obj, 'attrs'):
        return obj.attrs.get('positive', None)
    else:
        return None


def set_positive(obj, to_pos):
    if to_pos is None:
        if hasattr(obj, 'attrs'):
            obj.attrs.pop('positive', None)
    elif hasattr(obj, 'attrs'):
        str_pos = str(to_pos).strip().lower()
        if str_pos in ('up', 'down'):
            obj.attrs['positive'] = str_pos
        else:
            msg = 'Invalid positive value {}'
            raise PositiveError(msg.format(to_pos))
    else:
        msg = 'Cannot set positive for object of type {}'
        raise TypeError(msg.format(type(obj)))


def flip(obj, to_pos):
    from_pos = get_positive(obj)
    to_pos = None if to_pos is None else str(to_pos).strip().lower()
    if from_pos == to_pos:
        return obj
    elif from_pos is None or to_pos is None:
        msg = "No rule for changing positive from '{}' to '{}'"
        raise PositiveError(msg.format(from_pos, to_pos))
    else:
        new_obj = -obj
        set_positive(new_obj, to_pos)
        if hasattr(new_obj, 'name'):
            new_obj.name = "flip({}, to='{!s}')".format(obj.name, to_pos)
        return new_obj
