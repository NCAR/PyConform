"""
Unit Tests for PhysArray functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays import PhysArray, UnitsError

import pyconform.physarrays.functions as fn
import cf_units as cu
import numpy as np
import xarray as xr
import unittest


class FunctionsTests(unittest.TestCase):

    def test_convert(self):
        v = PhysArray([[1, 2], [3, 4]], name='v', dims=['x', 'y'],
                      coords=[[0, 1], [1, 2]], units='g')
        v_kg = fn.convert(v, 'kg')
        self.assertIsInstance(v_kg, PhysArray)

    def test_convert_unconvertable_units_raises_units_error(self):
        v = PhysArray([[1, 2], [3, 4]], name='v', dims=['x', 'y'],
                      coords=[[0, 1], [1, 2]], units='g')
        with self.assertRaises(UnitsError):
            fn.convert(v, 'm')

    def test_convert_time_referenced_with_diff_calendar_units_raises_units_error(self):
        v = PhysArray([[1, 2], [3, 4]], name='v', dims=['x', 'y'],
                      coords=[[0, 1], [1, 2]], units='days since 1974-02-06',
                      calendar='noleap')
        to_units = cu.Unit('hours since 2000-01-01', calendar='gregorian')
        with self.assertRaises(UnitsError):
            fn.convert(v, to_units)

    def test_convert_time_referenced_with_same_calendar_units(self):
        v = PhysArray(0.0, name='v', units='days since 1999-01-01',
                      calendar='noleap')
        to_units = cu.Unit('hours since 2000-01-01', calendar='noleap')
        actual = fn.convert(v, to_units)
        expctd = PhysArray(-8760.0, name="convert(v, to='hours since 2000-01-01')",
                           units='hours since 2000-01-01', calendar='noleap')
        np.testing.assert_array_equal(actual, expctd)
        self.assertEqual(actual.name, expctd.name)
        self.assertEqual(actual.cfunits, expctd.cfunits)

    def test_get_dtype_of_float_returns_float64(self):
        self.assertEqual(fn.get_dtype(2.0), np.dtype('float64'))

    def test_get_dtype_of_str_returns_S(self):
        self.assertEqual(fn.get_dtype('a'), np.dtype('S1'))

    def test_get_dtype_of_int_list_returns_int64(self):
        self.assertEqual(fn.get_dtype([1, 2, 3]), np.dtype('int64'))

    def test_get_dtype_of_float_list_returns_float64(self):
        self.assertEqual(fn.get_dtype([1., 2., 3]), np.dtype('float64'))

    def test_get_dtype_of_f_array_returns_float32(self):
        obj = np.array([1, 2, 3], dtype='f')
        self.assertEqual(fn.get_dtype(obj), np.dtype('float32'))

    def test_get_dtype_of_f_dataarray_returns_float32(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')])
        self.assertEqual(fn.get_dtype(obj), np.dtype('float32'))

    def test_string_is_char_type(self):
        self.assertTrue(fn.is_char_type('a'))

    def test_float_is_not_char_type(self):
        self.assertFalse(fn.is_char_type(1.0))

    def test_get_cfunits_of_float_returns_no_unit(self):
        self.assertEqual(fn.get_cfunits(2.0), cu.Unit('no unit'))

    def test_get_cfunits_of_str_returns_no_unit(self):
        self.assertEqual(fn.get_cfunits('a'), cu.Unit('no unit'))

    def test_get_cfunits_of_f_dataarray_returns_units_property(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'units': 'g'})
        self.assertEqual(fn.get_cfunits(obj), cu.Unit('grams'))

    def test_set_cfunits_of_float_to_m_raises_units_error(self):
        with self.assertRaises(UnitsError):
            fn.set_cfunits(2.0, 'm')

    def test_set_cfunits_of_float_to_no_unit_does_nothing(self):
        fn.set_cfunits(2.0, 'no unit')

    def test_set_cfunits_of_dataarray_saves_units(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'units': 'g'})
        fn.set_cfunits(obj, 'm')
        self.assertEqual(fn.get_cfunits(obj), cu.Unit('m'))

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
