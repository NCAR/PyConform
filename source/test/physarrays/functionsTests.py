"""
Unit Tests for PhysArray functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays import PhysArray, UnitsError, PositiveError

import pyconform.physarrays.functions as fn
import pyconform.physarrays.generics as gn
import cf_units as cu
import numpy as np
import xarray as xr
import unittest


class FunctionsTests(unittest.TestCase):

    def assertPhysArraysEqual(self, obj1, obj2):
        self.assertEqual(type(obj1), type(obj2))
        xr.testing.assert_equal(obj1, obj2)
        self.assertEqual(gn.get_name(obj1), gn.get_name(obj2))
        self.assertEqual(gn.get_cfunits(obj1), gn.get_cfunits(obj2))
        self.assertEqual(gn.get_positive(obj1), gn.get_positive(obj2))

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
        self.assertPhysArraysEqual(actual, expctd)

    def test_flip_of_dataarray_from_up_to_down(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'positive': 'up'})
        actual = fn.flip(obj, 'down')
        expctd = xr.DataArray(np.array([-5, -8, -7], dtype='f'), name='down(x)',
                              dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                              attrs={'positive': 'down'})
        self.assertPhysArraysEqual(actual, expctd)

    def test_flip_of_dataarray_from_down_to_up(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'positive': 'down'})
        actual = fn.flip(obj, 'up')
        expctd = xr.DataArray(np.array([-5, -8, -7], dtype='f'), name='up(x)',
                              dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                              attrs={'positive': 'up'})
        self.assertPhysArraysEqual(actual, expctd)

    def test_flip_of_dataarray_from_down_to_none_raises_positive_error(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')],
                           attrs={'positive': 'down'})
        with self.assertRaises(PositiveError):
            fn.flip(obj, None)

    def test_flip_of_dataarray_from_none_to_up_raises_positive_error(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')])
        with self.assertRaises(PositiveError):
            fn.flip(obj, 'up')

    def test_flip_of_dataarray_from_up_to_invalid_raises_positive_error(self):
        obj = xr.DataArray(np.array([5, 8, 7], dtype='f'), name='x',
                           dims=['x'], coords=[np.array([0, 1, 2], dtype='d')])
        with self.assertRaises(PositiveError):
            fn.flip(obj, 'x')


if __name__ == "__main__":
    unittest.main()
