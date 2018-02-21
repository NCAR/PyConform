"""
Unit Tests for PhysArray generic functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays import UnitsError

import pyconform.physarrays.generics as gn
import cf_units as cu
import numpy as np
import xarray as xr
import unittest


class FunctionsTests(unittest.TestCase):

    def test_is_equal_dataarray_with_matching_units_and_positive_is_true(self):
        v1 = xr.DataArray(1.4, name='v',
                          attrs={'units': 'g', 'positive': 'up'})
        v2 = xr.DataArray(1.4, name='v',
                          attrs={'units': 'g', 'positive': 'up'})
        self.assertTrue(gn.is_equal(v1, v2))

    def test_is_equal_dataarray_with_mismatched_units_is_false(self):
        v1 = xr.DataArray(1.4, name='v',
                          attrs={'units': 'kg', 'positive': 'up'})
        v2 = xr.DataArray(1.4, name='v',
                          attrs={'units': 'g', 'positive': 'up'})
        self.assertFalse(gn.is_equal(v1, v2))

    def test_is_equal_dataarray_with_mismatched_name_is_false(self):
        v1 = xr.DataArray(1.4, name='u',
                          attrs={'units': 'g', 'positive': 'up'})
        v2 = xr.DataArray(1.4, name='v',
                          attrs={'units': 'g', 'positive': 'up'})
        self.assertFalse(gn.is_equal(v1, v2))

    def test_is_equal_dataarray_with_mismatched_positive_is_false(self):
        v1 = xr.DataArray(1.4, name='v', attrs={'units': 'g'})
        v2 = xr.DataArray(1.4, name='v',
                          attrs={'units': 'g', 'positive': 'up'})
        self.assertFalse(gn.is_equal(v1, v2))

    def test_is_equal_dataarray_with_mismatched_values_is_false(self):
        v1 = xr.DataArray(1.4, name='v', attrs={'units': 'g'})
        v2 = xr.DataArray(1.5, name='v', attrs={'units': 'g'})
        self.assertFalse(gn.is_equal(v1, v2))

    def test_get_dtype_of_float_returns_float64(self):
        self.assertEqual(gn.get_dtype(2.0), np.dtype('float64'))

    def test_get_dtype_of_str_returns_S(self):
        self.assertEqual(gn.get_dtype('a'), np.dtype('S1'))

    def test_get_dtype_of_int_list_returns_int64(self):
        self.assertEqual(gn.get_dtype([1, 2, 3]), np.dtype('int64'))

    def test_get_dtype_of_float_list_returns_float64(self):
        self.assertEqual(gn.get_dtype([1., 2., 3]), np.dtype('float64'))

    def test_get_dtype_of_f_array_returns_float32(self):
        obj = np.array([1, 2, 3], dtype='f')
        self.assertEqual(gn.get_dtype(obj), np.dtype('float32'))

    def test_get_dtype_of_f_dataarray_returns_float32(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')])
        self.assertEqual(gn.get_dtype(obj), np.dtype('float32'))

    def test_string_is_char_type(self):
        self.assertTrue(gn.is_char_type('a'))

    def test_float_is_not_char_type(self):
        self.assertFalse(gn.is_char_type(1.0))

    def test_get_cfunits_of_float_returns_unit_one(self):
        self.assertEqual(gn.get_cfunits(2.0), cu.Unit(1))

    def test_get_cfunits_of_float_ndarray_returns_unit_one(self):
        obj = np.array([1.4])
        self.assertEqual(gn.get_cfunits(obj), cu.Unit(1))

    def test_get_cfunits_of_str_returns_no_unit(self):
        self.assertEqual(gn.get_cfunits('a'), cu.Unit('no unit'))

    def test_get_cfunits_of_f_dataarray_returns_units_property(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'units': 'g'})
        self.assertEqual(gn.get_cfunits(obj), cu.Unit('grams'))

    def test_set_cfunits_of_float_to_m_raises_units_error(self):
        with self.assertRaises(UnitsError):
            gn.set_cfunits(2.0, 'm')

    def test_set_cfunits_of_float_to_no_unit_does_nothing(self):
        gn.set_cfunits(2.0, 'no unit')

    def test_set_cfunits_of_dataarray_saves_units(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'units': 'g'})
        gn.set_cfunits(obj, 'm')
        self.assertEqual(gn.get_cfunits(obj), cu.Unit('m'))

    def test_get_name_of_float_returns_str(self):
        self.assertEqual(gn.get_name(2.0), '2.0')

    def test_get_name_of_str_returns_itself(self):
        self.assertEqual(gn.get_name('a'), 'a')

    def test_get_name_of_dataarray_returns_name(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')])
        self.assertEqual(gn.get_name(obj), 'x')

    def test_get_name_of_ndarray_returns_one_line_str(self):
        obj = np.array([[1, 2], [3, 4]])
        self.assertEqual(gn.get_name(obj), '[[1 2] [3 4]]')

    def test_get_positive_of_float_returns_none(self):
        self.assertIsNone(gn.get_positive(2.0))

    def test_get_positive_of_dataarray_returns_positive(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'units': 'g', 'positive': 'up'})
        self.assertEqual(gn.get_positive(obj), 'up')

    def test_get_positive_of_dataarray_returns_none_if_no_positive(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'units': 'g'})
        self.assertEqual(gn.get_positive(obj), None)

    def test_set_positive_of_float_to_up_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.assertEqual(gn.set_positive(1.0, 'up'))

    def test_set_positive_of_float_to_down_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.assertEqual(gn.set_positive(1.0, 'down'))

    def test_set_positive_of_float_to_none(self):
        gn.set_positive(1.0, None)

    def test_set_positive_of_dataarray_to_up(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'units': 'g'})
        gn.set_positive(obj, 'up')
        self.assertEqual(gn.get_positive(obj), 'up')

    def test_set_positive_of_dataarray_to_invalid_name_raises_value_error(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'units': 'g'})
        with self.assertRaises(ValueError):
            gn.set_positive(obj, 'x')


if __name__ == "__main__":
    unittest.main()
