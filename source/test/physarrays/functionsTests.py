"""
Unit Tests for PhysArray Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays.newarrays import PhysArray

import pyconform.physarrays.functions as fn
import xarray as xr
import numpy as np
import cf_units as cu
import unittest


class FunctionsTests(unittest.TestCase):

    def test_get_name_of_int_returns_str(self):
        name = fn.get_name(1)
        self.assertEqual(name, '1')

    def test_get_name_of_ndarray_returns_str(self):
        name = fn.get_name(np.array([[1, 2], [3, 4]], dtype='f'))
        self.assertEqual(name, '[[1. 2.] [3. 4.]]')

    def test_get_name_of_xarray_returns_name(self):
        name = fn.get_name(xr.DataArray(2.3, name='x'))
        self.assertEqual(name, 'x')

    def test_get_name_of_physarray_returns_name(self):
        name = fn.get_name(PhysArray(2.3, name='x'))
        self.assertEqual(name, 'x')

    def test_get_data_of_int_returns_self(self):
        data = fn.get_data(1)
        self.assertEqual(data, 1)

    def test_get_data_of_ndarray_returns_self(self):
        idata = np.array([[1, 2], [3, 4]], dtype='f')
        odata = fn.get_data(idata)
        np.testing.assert_array_equal(odata, idata)

    def test_get_data_of_xarray_returns_self(self):
        idata = xr.DataArray(2.3, name='x')
        odata = fn.get_data(idata)
        xr.testing.assert_equal(odata, idata)

    def test_get_data_of_physarray_returns_xarray(self):
        idata = xr.DataArray(2.3, name='x')
        odata = fn.get_data(PhysArray(idata))
        xr.testing.assert_equal(odata, idata)

    def test_get_dtype_of_int_returns_int64(self):
        dtyp = fn.get_dtype(1)
        self.assertEqual(dtyp, np.dtype('int64'))

    def test_get_dtype_of_ndarray_returns_dtype(self):
        data = np.array([[1, 2], [3, 4]], dtype='f')
        dtyp = fn.get_dtype(data)
        np.testing.assert_array_equal(dtyp, np.dtype('f'))

    def test_get_dtype_of_xarray_returns_dtype(self):
        data = xr.DataArray(np.array(2.3, dtype='f'), name='x')
        dtyp = fn.get_dtype(data)
        np.testing.assert_array_equal(dtyp, np.dtype('f'))

    def test_get_dtype_of_physarray_returns_dtype(self):
        data = PhysArray(xr.DataArray(np.array(2.3, dtype='f'), name='x'))
        dtyp = fn.get_dtype(data)
        np.testing.assert_array_equal(dtyp, np.dtype('f'))

    def test_is_char_type_of_int_returns_false(self):
        ischar = fn.is_char_type(1)
        self.assertFalse(ischar)

    def test_is_char_type_of_str_returns_true(self):
        ischar = fn.is_char_type('abc')
        self.assertTrue(ischar)

    def test_is_char_type_of_str_ndarray_returns_true(self):
        data = np.array(['a', 'b', 'c'])
        ischar = fn.is_char_type(data)
        self.assertTrue(ischar)

    def test_is_char_type_of_str_xarray_returns_true(self):
        data = xr.DataArray(np.array(['a', 'b', 'c']), name='x')
        ischar = fn.is_char_type(data)
        self.assertTrue(ischar)

    def test_is_char_type_of_str_physarray_returns_true(self):
        data = PhysArray(xr.DataArray(np.array(['a', 'b', 'c']), name='x'))
        ischar = fn.is_char_type(data)
        self.assertTrue(ischar)

    def test_is_char_type_of_int_physarray_returns_false(self):
        data = PhysArray(xr.DataArray(np.array([1, 2, 3]), name='x'))
        ischar = fn.is_char_type(data)
        self.assertFalse(ischar)

    def test_get_cfunits_of_int_returns_1(self):
        units = fn.get_cfunits(1)
        self.assertEqual(units, 1)

    def test_get_cfunits_of_ndarray_returns_1(self):
        units = fn.get_cfunits(np.array([1, 2, 3]))
        self.assertEqual(units, 1)

    def test_get_cfunits_of_char_type_ndarray_returns_no_unit(self):
        units = fn.get_cfunits(np.array(['a', 'b', 'c']))
        self.assertEqual(units, 'no unit')

    def test_get_cfunits_of_xarray_returns_units_attr(self):
        data = xr.DataArray(2.3, name='x', attrs={'units': 'g'})
        units = fn.get_cfunits(data)
        self.assertEqual(units, 'g')

    def test_get_cfunits_of_physarray_returns_units_attr(self):
        data = PhysArray(2.3, name='x', attrs={'units': 'g'})
        units = fn.get_cfunits(data)
        self.assertEqual(units, 'g')

    def test_get_cfunits_of_physarray_with_reftime_returns_units_attr(self):
        attrs = {'units': 'days since 1974-02-06', 'calendar': 'noleap'}
        data = PhysArray(2.3, name='x', attrs=attrs)
        units = fn.get_cfunits(data)
        xunits = cu.Unit(attrs['units'], calendar=attrs['calendar'])
        self.assertEqual(units, xunits)

    def test_set_cfunits_of_non_xarray_raises_type_error(self):
        with self.assertRaises(TypeError):
            fn.set_cfunits(np.array([1, 2, 3]), 'g')

    def test_set_cfunits_of_xarray_changes_attr(self):
        x1 = xr.DataArray(2.3, name='x', attrs={'units': 'g'})
        fn.set_cfunits(x1, 'kg')
        x2 = xr.DataArray(2.3, name='x', attrs={'units': 'kg'})
        xr.testing.assert_equal(x1, x2)
        self.assertEqual(x1.attrs['units'], x2.attrs['units'])

    def test_set_cfunits_of_physarray_changes_attr(self):
        x1 = PhysArray(2.3, name='x', attrs={'units': 'g'})
        fn.set_cfunits(x1, 'kg')
        x2 = PhysArray(2.3, name='x', attrs={'units': 'kg'})
        xr.testing.assert_equal(x1.data_array, x2.data_array)
        self.assertEqual(x1.attrs['units'], x2.attrs['units'])

    def test_set_cfunits_of_physarray_with_calendar(self):
        attrs1 = {'units': 'days since 1974-02-06', 'calendar': 'noleap'}
        x1 = PhysArray(2.3, name='x', attrs=attrs1)
        to_units = cu.Unit('hours since 2000-01-01')
        fn.set_cfunits(x1, to_units)
        attrs2 = {'units': str(to_units), 'calendar': str(to_units.calendar)}
        x2 = PhysArray(2.3, name='x', attrs=attrs2)
        xr.testing.assert_equal(x1.data_array, x2.data_array)
        self.assertEqual(x1.attrs['units'], x2.attrs['units'])
        self.assertEqual(x1.attrs['calendar'], x2.attrs['calendar'])

    def test_set_cfunits_of_physarray_from_nontime_to_time(self):
        x1 = PhysArray(2.3, name='x', attrs={'units': 'g'})
        to_units = cu.Unit('hours since 2000-01-01')
        fn.set_cfunits(x1, to_units)
        attrs2 = {'units': str(to_units), 'calendar': str(to_units.calendar)}
        x2 = PhysArray(2.3, name='x', attrs=attrs2)
        xr.testing.assert_equal(x1.data_array, x2.data_array)
        self.assertEqual(x1.attrs['units'], x2.attrs['units'])
        self.assertEqual(x1.attrs['calendar'], x2.attrs['calendar'])

    def test_set_cfunits_of_physarray_from_time_to_nontime(self):
        to_units = cu.Unit('hours since 2000-01-01')
        attrs1 = {'units': str(to_units), 'calendar': str(to_units.calendar)}
        x1 = PhysArray(2.3, name='x', attrs=attrs1)
        fn.set_cfunits(x1, cu.Unit('g'))
        x2 = PhysArray(2.3, name='x', attrs={'units': 'g'})
        xr.testing.assert_equal(x1.data_array, x2.data_array)
        self.assertEqual(x1.attrs['units'], x2.attrs['units'])
        self.assertNotIn('calendar', x1.attrs)


if __name__ == "__main__":
    unittest.main()
