"""
Input Dataset Container Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays import PhysArray

import xarray as xr


class Dataset(object):
    """
    A container for Xarray dataset objects
    """

    def __init__(self, filenames=None):
        ds = xr.open_mfdataset(filenames, autoclose=True, chunks={})
        self.__dataset = ds

    def __contains__(self, name):
        return name in self.__dataset.data_vars or name in self.__dataset.coords

    @property
    def dims(self):
        return self.__dataset.dims

    def __getitem__(self, name):
        if name in self.__dataset.data_vars:
            return PhysArray(self.__dataset.data_vars[name])
        elif name in self.__dataset.coords:
            return PhysArray(self.__dataset.coords[name])
        else:
            raise KeyError('{!r} not found in Dataset'.format(name))
