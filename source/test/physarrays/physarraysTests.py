"""
Unit Tests for PhysArray Class and Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays import PhysArray, UnitsError, get_cfunits, get_name, get_positive

import xarray as xr
import unittest


class PhysArrayTests(unittest.TestCase):

    def assertPhysArraysEqual(self, obj1, obj2):
        self.assertEqual(type(obj1), type(obj2))
        xr.testing.assert_equal(obj1, obj2)
        self.assertEqual(get_name(obj1), get_name(obj2))
        self.assertEqual(get_cfunits(obj1), get_cfunits(obj2))
        self.assertEqual(get_positive(obj1), get_positive(obj2))

    def test_create(self):
        x = PhysArray(1.0, name='x')
        self.assertIsInstance(x, PhysArray)
        self.assertIsInstance(x, xr.DataArray)

    def test_add_float_to_scalar(self):
        x = 3.5
        y = PhysArray(2.0, name='y')
        z = PhysArray(5.5, name="(3.5+y)")
        self.assertPhysArraysEqual(x + y, z)

    def test_add_float_to_scalar_with_unconvertable_units_raises_units_error(self):
        x = 3.5
        y = PhysArray(2.0, name='y', units='m')
        with self.assertRaises(UnitsError):
            x + y

    def test_add_scalar_to_float(self):
        x = PhysArray(2.0, name='x')
        y = 3.5
        z = PhysArray(5.5, name="(x+3.5)")
        self.assertPhysArraysEqual(x + y, z)

    def test_add_scalar_to_scalar_without_units(self):
        x = PhysArray(3.0, name='x')
        y = PhysArray(2.0, name='y')
        z = PhysArray(5.0, name="(x+y)")
        self.assertPhysArraysEqual(x + y, z)

    def test_add_scalar_to_array_without_units(self):
        x = PhysArray(3.0, name='x')
        y = PhysArray([2., 3., 4.], name='y',
                      dims=['i'], coords=[[0, 1, 2]])
        z = PhysArray([5., 6., 7.], name="(x+y)",
                      dims=['i'], coords=[[0, 1, 2]])
        self.assertPhysArraysEqual(x + y, z)

    def test_add_array_to_scalar_without_units(self):
        x = PhysArray([2., 3., 4.], name='x',
                      dims=['i'], coords=[[0, 1, 2]])
        y = PhysArray(3.0, name='y')
        z = PhysArray([5., 6., 7.], name="(x+y)",
                      dims=['i'], coords=[[0, 1, 2]])
        self.assertPhysArraysEqual(x + y, z)

    def test_add_array_to_array_without_units(self):
        x = PhysArray([2., 3., 4.], name='x',
                      dims=['i'], coords=[[0, 1, 2]])
        y = PhysArray([2., 3., 4.], name='y',
                      dims=['j'], coords=[[0, 1, 2]])
        z = PhysArray([[4., 5., 6.],
                       [5., 6., 7.],
                       [6., 7., 8.]],
                      name="(x+y)", dims=['i', 'j'], coords=[[0, 1, 2], [0, 1, 2]])
        self.assertPhysArraysEqual(x + y, z)

    def test_add_scalar_to_scalar_with_units(self):
        x = PhysArray(3.0, name='x', units='m')
        y = PhysArray(2.0, name='y', units='km')
        z = PhysArray(2003.0, name="(x+convert(y, to='m'))", units='m')
        self.assertPhysArraysEqual(x + y, z)

    def test_add_scalar_to_scalar_with_positive_up_inverts_then_adds(self):
        x = PhysArray(3.0, name='x', positive='up')
        y = PhysArray(2.0, name='y', positive='down')
        z = PhysArray(1.0, name="(x+up(y))", positive='up')
        self.assertPhysArraysEqual(x + y, z)

    def test_add_scalar_to_scalar_with_positive_down_inverts_then_adds(self):
        x = PhysArray(3.0, name='x', positive='down')
        y = PhysArray(2.0, name='y', positive='up')
        z = PhysArray(1.0, name="(x+down(y))", positive='down')
        self.assertPhysArraysEqual(x + y, z)

    def test_add_float_to_scalar_with_positive_raises_value_error(self):
        x = 3.0
        y = PhysArray(2.0, name='y', positive='down')
        with self.assertRaises(ValueError):
            x + y

    def test_add_scalar_to_scalar_with_time_referenced_units(self):
        x = PhysArray(3.0, name='x', units='days since 1999-01-01',
                      calendar='noleap')
        y = PhysArray(2.0, name='y', units='days since 2000-01-01',
                      calendar='noleap')
        z = PhysArray(370.0, name="(x+convert(y, to='days since 1999-01-01'))",
                      units='days since 1999-01-01', calendar='noleap')
        self.assertPhysArraysEqual(x + y, z)

    def test_add_scalar_to_scalar_with_time_referenced_units_and_different_calendar_raises_units_error(self):
        x = PhysArray(3.0, name='x', units='days since 1999-01-01',
                      calendar='noleap')
        y = PhysArray(2.0, name='y', units='hours since 2000-01-01',
                      calendar='gregorian')
        with self.assertRaises(UnitsError):
            x + y

    def test_add_scalar_to_array_with_units(self):
        x = PhysArray(3.0, name='x', units='m')
        y = PhysArray([2., 3., 4.], name='y', units='km',
                      dims=['i'], coords=[[0, 1, 2]])
        z = PhysArray([2003., 3003., 4003.], name="(x+convert(y, to='m'))",
                      units='m', dims=['i'], coords=[[0, 1, 2]])
        self.assertPhysArraysEqual(x + y, z)

    def test_add_array_to_scalar_with_units(self):
        x = PhysArray([2., 3., 4.], name='x', units='m',
                      dims=['i'], coords=[[0, 1, 2]])
        y = PhysArray(3.0, name='y', units='km')
        z = PhysArray([3002., 3003., 3004.], name="(x+convert(y, to='m'))",
                      units='m', dims=['i'], coords=[[0, 1, 2]])
        self.assertPhysArraysEqual(x + y, z)

    def test_add_array_to_array_with_units(self):
        x = PhysArray([2., 3., 4.], name='x', units='m',
                      dims=['i'], coords=[[0, 1, 2]])
        y = PhysArray([2., 3., 4.], name='y', units='km',
                      dims=['j'], coords=[[0, 1, 2]])
        z = PhysArray([[2002., 3002., 4002.],
                       [2003., 3003., 4003.],
                       [2004., 3004., 4004.]],
                      name="(x+convert(y, to='m'))", units='m',
                      dims=['i', 'j'], coords=[[0, 1, 2], [0, 1, 2]])
        self.assertPhysArraysEqual(x + y, z)

    def test_sub_scalar_to_scalar_with_units(self):
        x = PhysArray(3.0, name='x', units='m')
        y = PhysArray(2.0, name='y', units='km')
        z = PhysArray(-1997.0, name="(x-convert(y, to='m'))", units='m')
        self.assertPhysArraysEqual(x - y, z)

    def test_sub_scalar_to_scalar_with_positive_up_inverts_then_subtracts(self):
        x = PhysArray(3.0, name='x', positive='up')
        y = PhysArray(2.0, name='y', positive='down')
        z = PhysArray(5.0, name="(x-up(y))", positive='up')
        self.assertPhysArraysEqual(x - y, z)

    def test_sub_scalar_to_scalar_with_time_referenced_units(self):
        x = PhysArray(1.0, name='x', units='days since 2000-01-01')
        y = PhysArray(1.0, name='y', units='hours since 1999-01-01')
        z = PhysArray(366. - 1. / 24.,
                      name="(x-convert(y, to='days since 2000-01-01'))",
                      units='days since 2000-01-01')
        self.assertPhysArraysEqual(x - y, z)

    def test_mul_scalar_to_scalar_with_units(self):
        x = PhysArray(3.0, name='x', units='m')
        y = PhysArray(2.0, name='y', units='km')
        z = PhysArray(6.0, name="(x*y)", units='1000 m^2')
        self.assertPhysArraysEqual(x * y, z)

    def test_mul_scalar_to_scalar_with_positive_up_inverts_then_multiplies(self):
        x = PhysArray(3.0, name='x', positive='up')
        y = PhysArray(2.0, name='y', positive='down')
        z = PhysArray(-6.0, name="(x*up(y))", positive='up')
        self.assertPhysArraysEqual(x * y, z)

    def test_mul_scalar_to_scalar_with_time_referenced_units(self):
        x = PhysArray(1.0, name='x', units='days since 2000-01-01')
        y = PhysArray(1.0, name='y', units='hours since 1999-01-01')
        z = PhysArray(1.0, name="(x*y)", units='24 hours^2')
        self.assertPhysArraysEqual(x * y, z)

    def test_div_scalar_to_scalar_with_units(self):
        x = PhysArray(3.0, name='x', units='m')
        y = PhysArray(2.0, name='y', units='km')
        z = PhysArray(1.5, name="(x/y)", units='0.001')
        self.assertPhysArraysEqual(x / y, z)

    def test_div_scalar_to_scalar_with_positive_up_inverts_then_divides(self):
        x = PhysArray(3.0, name='x', positive='up')
        y = PhysArray(2.0, name='y', positive='down')
        z = PhysArray(-1.5, name="(x/up(y))", positive='up')
        self.assertPhysArraysEqual(x / y, z)

    def test_div_scalar_to_scalar_with_time_referenced_units(self):
        x = PhysArray(1.0, name='x', units='days since 2000-01-01')
        y = PhysArray(1.0, name='y', units='hours since 1999-01-01')
        z = PhysArray(1.0, name="(x/y)", units='24')
        self.assertPhysArraysEqual(x / y, z)

    def test_pow_scalar_to_integer_with_units(self):
        x = PhysArray(3.0, name='x', units='m')
        y = 2
        z = PhysArray(9.0, name="(x**2)", units='m2')
        self.assertPhysArraysEqual(x ** y, z)

    def test_pow_scalar_to_scalar_with_units(self):
        x = PhysArray(3.0, name='x', units='m')
        y = PhysArray(2.0, name='y', units='1')
        z = PhysArray(9.0, name="(x**y)", units='m2')
        self.assertPhysArraysEqual(x ** y, z)

    def test_pow_array_to_scalar_with_units(self):
        x = PhysArray([3.0, 4.0], dims=['x'], coords=[[0, 1]],
                      name='x', units='m')
        y = PhysArray(2.0, name='y', units='1')
        z = PhysArray([9.0, 16.0], dims=['x'], coords=[[0, 1]],
                      name='(x**y)', units='m2')
        self.assertPhysArraysEqual(x ** y, z)

    def test_pow_array_to_scalar_with_unitful_exponent_raises_type_error(self):
        x = PhysArray([3.0, 4.0], dims=['x'], coords=[[0, 1]],
                      name='x', units='m')
        y = PhysArray(2.0, name='y', units='g')
        with self.assertRaises(TypeError):
            x ** y

    def test_pow_array_to_scalar_with_unitless_exponent(self):
        x = PhysArray([3.0, 4.0], dims=['x'], coords=[[0, 1]],
                      name='x', units='m')
        y = PhysArray(20.0, name='y', units='0.1')
        z = PhysArray([9.0, 16.0], dims=['x'], coords=[[0, 1]],
                      name='(x**y)', units='m2')
        self.assertPhysArraysEqual(x ** y, z)

    def test_pow_array_to_array_raises_type_error(self):
        x = PhysArray([3.0, 4.0], dims=['x'], coords=[[0, 1]],
                      name='x', units='m')
        y = PhysArray([1.0, 2.0], dims=['x'], coords=[[0, 1]],
                      name='y', units='1')
        with self.assertRaises(TypeError):
            x ** y


if __name__ == "__main__":
    unittest.main()
