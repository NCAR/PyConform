"""
InputDataset Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import netCDF4 as nc

from datasets import Dataset
from . import Dimension, Variable, File


class InputDataset(Dataset):
    """
    Dataset computed from a list of netcdf files
    """

    def __init__(self, *filenames):
        super(InputDataset, self).__init__()
        for filename in set(filenames):
            self.__add_netcdf_file(filename)

    def __add_netcdf_file(self, filename):
        ncf = nc.Dataset(filename)
        for name in ncf.dimensions:
            self.__add_netcdf_dimension(ncf.dimensions[name])
        for name in ncf.variables:
            self.__add_netcdf_variable(ncf.variables[name])
        f = File(filename, dimensions=tuple(ncf.dimensions),
                 variables=tuple(ncf.variables))
        ncfatts = {a: ncf.getncattr(a) for a in ncf.ncattrs()}
        f.attributes.update(ncfatts)
        self._add_file(f)
        ncf.close()

    def __add_netcdf_dimension(self, ncd):
        d = Dimension.from_netcdf4(ncd)
        if d.name not in self.dimensions:
            self._add_dimension(d)
        elif self.get_dimension(d.name) != d:
            msg = 'Dimension {!r} is different across files'
            raise ValueError(msg.format(d.name))

    def __add_netcdf_variable(self, ncv):
        v = Variable.from_netcdf4(ncv)
        if v.name not in self.variables:
            self._add_variable(v)
        elif self.get_variable(v.name) != v:
            msg = 'Variable {!r} is different across files'
            raise ValueError(msg.format(v.name))
