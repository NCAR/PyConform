"""
Unit Tests for InputDatasets

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest
import netCDF4 as nc
import numpy as np

from os import remove
from pyconform.metadata import InputDataset


class InputDatasetTests(unittest.TestCase):

    def setUp(self):
        ncf = nc.Dataset('test1.nc', 'w')
        ncf.createDimension('x', 2)
        ncf.createDimension('y', 3)
        ncf.createDimension('t')
        x = ncf.createVariable('x', 'd', ('x',))
        x[:] = np.arange(2, dtype='d')
        y = ncf.createVariable('y', 'd', ('y',))
        y[:] = np.arange(3, dtype='d')
        t = ncf.createVariable('t', 'd', ('t',))
        t[:] = np.arange(4, dtype='d')
        v = ncf.createVariable('v', 'f', ('x', 'y', 't'))
        v[:] = np.ones((2, 3, 4), dtype='f')
        ncf.close()

        ncf = nc.Dataset('test2.nc', 'w')
        ncf.createDimension('x', 2)
        ncf.createDimension('y', 3)
        ncf.createDimension('t')
        x = ncf.createVariable('x', 'd', ('x',))
        x[:] = np.arange(2, dtype='d')
        y = ncf.createVariable('y', 'd', ('y',))
        y[:] = np.arange(3, dtype='d')
        t = ncf.createVariable('t', 'd', ('t',))
        t[:] = np.arange(4, dtype='d')
        u = ncf.createVariable('u', 'f', ('x', 'y', 't'))
        u[:] = np.ones((2, 3, 4), dtype='f')
        ncf.close()

    def tearDown(self):
        remove('test1.nc')
        remove('test2.nc')

    def test_create_empty(self):
        ids = InputDataset()
        self.assertIsInstance(ids, InputDataset)

    def test_create_from_single_file(self):
        ids = InputDataset('test1.nc')
        self.assertIsInstance(ids, InputDataset)
        self.assertIn('v', ids.variables)
        v = ids.get_variable('v')
        self.assertEqual(v.datatype, 'float')
        self.assertIn('x', ids.variables)
        x = ids.get_variable('x')
        self.assertEqual(x.datatype, 'double')
        self.assertIn('x', ids.dimensions)
        xd = ids.get_dimension('x')
        self.assertEqual(xd.size, 2)
        self.assertEqual(xd.is_unlimited, False)
        self.assertIn('y', ids.variables)
        y = ids.get_variable('y')
        self.assertEqual(y.datatype, 'double')
        self.assertIn('y', ids.dimensions)
        yd = ids.get_dimension('y')
        self.assertEqual(yd.size, 3)
        self.assertEqual(yd.is_unlimited, False)
        self.assertIn('t', ids.variables)
        t = ids.get_variable('t')
        self.assertEqual(t.datatype, 'double')
        self.assertIn('t', ids.dimensions)
        td = ids.get_dimension('t')
        self.assertEqual(td.size, 4)
        self.assertEqual(td.is_unlimited, True)
        self.assertIn('test1.nc', ids.files)

    def test_create_from_two_files(self):
        ids = InputDataset('test1.nc', 'test2.nc')
        self.assertIsInstance(ids, InputDataset)
        self.assertIn('v', ids.variables)
        v = ids.get_variable('v')
        self.assertEqual(v.datatype, 'float')
        self.assertIn('u', ids.variables)
        u = ids.get_variable('u')
        self.assertEqual(u.datatype, 'float')
        self.assertIn('x', ids.variables)
        x = ids.get_variable('x')
        self.assertEqual(x.datatype, 'double')
        self.assertIn('x', ids.dimensions)
        xd = ids.get_dimension('x')
        self.assertEqual(xd.size, 2)
        self.assertEqual(xd.is_unlimited, False)
        self.assertIn('y', ids.variables)
        y = ids.get_variable('y')
        self.assertEqual(y.datatype, 'double')
        self.assertIn('y', ids.dimensions)
        yd = ids.get_dimension('y')
        self.assertEqual(yd.size, 3)
        self.assertEqual(yd.is_unlimited, False)
        self.assertIn('t', ids.variables)
        t = ids.get_variable('t')
        self.assertEqual(t.datatype, 'double')
        self.assertIn('t', ids.dimensions)
        td = ids.get_dimension('t')
        self.assertEqual(td.size, 4)
        self.assertEqual(td.is_unlimited, True)
        self.assertIn('test1.nc', ids.files)
        self.assertIn('test2.nc', ids.files)


if __name__ == "__main__":
    unittest.main()
