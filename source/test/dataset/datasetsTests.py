"""
Unit Tests for Input Dataset Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.dataset import Dataset
from pyconform.physarray import PhysArray

import unittest
import netCDF4 as nc
import numpy as np
import os


class DatasetTests(unittest.TestCase):

    def setUp(self):
        self.dimensions = {'x': 50, 'y': 40, 't': 30}
        self.variables = ['v', 'u', 'w']
        self.filenames = {v: '{}.nc'.format(v) for v in self.variables}
        self.vardims = ('x', 'y', 't')
        self.cleanUp()
        self.writeTimeSeries()
        self.ds = Dataset(self.filenames.values())

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        for filename in self.filenames.values():
            if os.path.exists(filename):
                os.remove(filename)

    def writeTimeSeries(self):
        for n, v in enumerate(self.variables):
            f = nc.Dataset(self.filenames[v], 'w')
            for d in self.dimensions:
                f.createDimension(d, None if d == 't' else self.dimensions[d])
                f.createVariable(d, 'd', (d,))
                if d == 't':
                    f.variables[d].setncattr('units', 'days since 1974-02-06')
                    f.variables[d].setncattr('calendar', 'noleap')
                else:
                    f.variables[d].setncattr('units', 'g')
            f.createVariable(v, 'f', self.vardims)
            for d in self.dimensions:
                f.variables[d][:] = np.arange(self.dimensions[d], dtype='d')
            vshape = tuple(self.dimensions[d] for d in self.vardims)
            f.variables[v][:] = n * np.ones(vshape, dtype='f')
            f.close()

    def test_create(self):
        self.assertIsInstance(self.ds, Dataset)

    def test_dims(self):
        self.assertEqual(self.ds.dims, self.dimensions)

    def test_contains(self):
        for d in self.dimensions:
            self.assertIn(d, self.ds)
        for v in self.variables:
            self.assertIn(v, self.ds)

    def test_getitem_v_returns_physarray(self):
        for v in self.variables:
            va = self.ds[v]
            self.assertIsInstance(va, PhysArray)
        for d in self.dimensions:
            da = self.ds[d]
            self.assertIsInstance(da, PhysArray)


if __name__ == '__main__':
    unittest.main()
