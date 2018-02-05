"""
Unit Tests for PhysArray functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import pyconform.physarrays.functions as fn
import cf_units as cu
import numpy as np
import xarray as xr
import unittest


class FunctionsTests(unittest.TestCase):

    def test_get_dtype(self):
        obj_values = [(2.0, np.dtype('float64')),
                      ('a', np.dtype('S1')),
                      ([1, 2, 3], np.dtype('int64')),
                      ([1.0, 3.0], np.dtype('float64')),
                      (np.array([1, 2, 3], dtype='f'), np.dtype('f')),
                      (xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                                    dims=['x'], coords=[np.array([0, 1, 2], dtype='d')]),
                       np.dtype('f'))]
        for obj, value in obj_values:
            self.assertEqual(fn.get_dtype(obj), value)

    def test_is_char_type(self):
        self.assertTrue(fn.is_char_type('a'))
        self.assertFalse(fn.is_char_type(1.0))

    def test_get_units(self):
        obj_values = [(2.0, cu.Unit(1)),
                      ('a', cu.Unit('no unit')),
                      (xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                                    dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                                    attrs={'units': 'g'}),
                       cu.Unit('grams'))]
        for obj, value in obj_values:
            self.assertEqual(fn.get_units(obj), value)

    def test_get_name(self):
        obj_values = [(2.0, str(2.0)),
                      ('a', 'a'),
                      (xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                                    dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                                    attrs={'units': 'g'}), 'x'),
                      (np.array([[1, 2], [3, 4]]), '[[1 2] [3 4]]')]
        for obj, value in obj_values:
            self.assertEqual(fn.get_name(obj), value)

    def test_get_positive(self):
        obj_values = [(2.0, None),
                      (xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                                    dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                                    attrs={'units': 'g', 'positive': 'up'}), 'up'),
                      (xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                                    dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                                    attrs={'units': 'g'}), None)]
        for obj, value in obj_values:
            self.assertEqual(fn.get_positive(obj), value)


if __name__ == "__main__":
    unittest.main()
