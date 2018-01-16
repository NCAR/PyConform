"""
New Module

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import netCDF4 as nc

from datasets import Dataset


class InputDataset(Dataset):
    """
    Dataset computed from a list of netcdf files
    """

    def __init__(self, *filenames):
        for filename in filenames:
            ncf = nc.Dataset(filename)
            ncf.close()
