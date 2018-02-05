"""
Functions and decorators for handling units

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import cf_units as cu
import xarray as xr
import numpy as np
import os


def get_dtype(obj):
    return np.asarray(obj).dtype


def is_char_type(obj):
    return get_dtype(obj).char in ('S', 'U')


def get_name(obj):
    if isinstance(obj, xr.DataArray):
        return obj.name
    else:
        return ' '.join(str(obj).replace(os.linesep, ' ').split())


def get_units(obj):
    if is_char_type(obj):
        return cu.Unit('no unit')
    elif isinstance(obj, xr.DataArray):
        return cu.Unit(obj.attrs.get('units', 1))
    else:
        return cu.Unit(1)


def get_positive(obj):
    if isinstance(obj, xr.DataArray):
        return obj.attrs.get('positive', None)
    else:
        return None
