"""
PhysArray Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from numpy import asarray
from cf_units import Unit


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
