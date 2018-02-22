"""
Generic functions for special DataArray attribute handling

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from exceptions import UnitsError, PositiveError

import generics as gn
import xarray as xr


def convert(obj, to_units):
    from_units = gn.get_cfunits(obj)
    if from_units == to_units:
        return obj
    elif from_units.is_convertible(to_units):
        new_obj = xr.apply_ufunc(from_units.convert, obj, to_units, keep_attrs=True,
                                 dask='parallelized', output_dtypes=[gn.get_dtype(obj)])
        new_obj.name = "convert({}, to='{!s}')".format(obj.name, to_units)
        gn.set_cfunits(new_obj, to_units)
        return type(obj)(new_obj)
    else:
        msg = "Cannot convert units '{!s}' to '{!s}'"
        raise UnitsError(msg.format(from_units, to_units))


def flip(obj, to_pos):
    from_pos = gn.get_positive(obj)
    if from_pos == to_pos:
        return obj
    elif from_pos is None or to_pos is None:
        msg = 'No rule for changing positive direction from {!r} to {!r}'
        raise PositiveError(msg.format(to_pos, from_pos))
    else:
        new_obj = -obj
        new_obj.name = '{!s}({})'.format(to_pos, obj.name)
        gn.set_positive(new_obj, to_pos)
        return type(obj)(new_obj)
