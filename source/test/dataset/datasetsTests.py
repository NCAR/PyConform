"""
Unit Tests for Input Dataset Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.dataset import Dataset

import unittest
import netCDF4 as nc
import numpy as np


class DatasetTests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()
        self.filename = 'test.nc'
        self.dimensions = {'x': 100, 'y': 150, 't': 50}
        self.variables = ['v1', 'v2', 'v3']
        self.vardims = ('x', 'y', 't')
        self._write_file_()

    def _write_file_(self):
        f = nc.Dataset(self.filename, 'w')
        for d in self.dimensions:
            f.createDimension(d, None if d == 't' else self.dimensions[d])
            f.createVariable(d, 'd', (d,))
            if d == 't':
                f.variables[d].setncattr('units', 'days since 1974-02-06')
                f.variables[d].setncattr('calendar', 'noleap')
            else:
                f.variables[d].setncattr('units', 'g')
        for v in self.variables:
            f.createVariable(v, 'f', self.vardims)
        for d in self.dimensions:
            f.variables[d][:] = np.arange(self.dimensions[d], dtype='d')
        vshape = tuple(self.dimensions[d] for d in self.vardims)
        for v in self.variables:
            f.variables[v][:] = np.ones(vshape, dtype='f')
        f.close()

    def test_create(self):
        self.assertIsInstance(self.ds, Dataset)

    def test_add_file(self):
        self.ds.add_file(self.filename)
        for v in self.variables:
            self.assertIn(v, self.ds)


if __name__ == '__main__':
    unittest.main()
