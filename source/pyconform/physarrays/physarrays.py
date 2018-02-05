"""
Physical Array Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import xarray as xr


class PhysArray(xr.DataArray):
    """
    Physical Array subclass of xarray.DataArray
    """

    def __init__(self, *args, **kwds):
        super(PhysArray, self).__init__(*args, **kwds)
