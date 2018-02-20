"""
Input Dataset Container Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import xarray as xr


class Dataset(object):
    """
    A container for Xarray dataset objects
    """

    def __init__(self, filenames=[]):
        self.__datasets = {}

    def __contains__(self, name):
        for ds in self.__datasets:
            if name in self.__datasets[ds].data_vars:
                return True
        return False

    def add_file(self, filename):
        self.__datasets[filename] = xr.open_dataset(
            filename, autoclose=True, chunks={})
