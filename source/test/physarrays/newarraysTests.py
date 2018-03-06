"""
Unit Tests for New PhysArrays

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays.newarrays import PhysArray

import xarray as xr
import cf_units as cu
import numpy as np
import unittest


class PhysArrayTests(unittest.TestCase):

    def assertPhysArraysEqual(self, obj1, obj2):
        self.assertEqual(type(obj1), type(obj2))
        xr.testing.assert_equal(obj1.data_array, obj2.data_array)
        self.assertEqual(obj1.name, obj2.name)
        self.assertEqual(obj1.cfunits(), obj2.cfunits())
        self.assertEqual(obj1.positive, obj2.positive)

    def test_create(self):
        a = PhysArray(2.3)
        self.assertIsInstance(a, PhysArray)

    def test_phys_array_from_data_array(self):
        x_da = xr.DataArray(1.2, name='x', attrs={'units': 'g'})
        x = PhysArray(x_da)
        self.assertIsInstance(x, PhysArray)
        self.assertEqual(x.data_array, x_da)
        self.assertEqual(x.units, 'g')
        self.assertEqual(x.calendar, None)
        self.assertEqual(x.positive, None)

    def test_phys_array_from_arguments(self):
        x = PhysArray(1.2, name='x', attrs={'units': 'g'})
        self.assertIsInstance(x, PhysArray)
        self.assertEqual(x.data_array, 1.2)
        self.assertEqual(x.units, 'g')
        self.assertEqual(x.calendar, None)
        self.assertEqual(x.positive, None)

    def test_phys_array_with_units_argument(self):
        x = PhysArray(1.2, name='x', units='g')
        self.assertIsInstance(x, PhysArray)
        self.assertEqual(x.data_array, 1.2)
        self.assertEqual(x.units, 'g')
        self.assertEqual(x.calendar, None)
        self.assertEqual(x.positive, None)

    def test_phys_array_with_calendar_argument(self):
        x = PhysArray(1.2, name='x', units='days since 1974-02-06',
                      calendar='noleap')
        self.assertIsInstance(x, PhysArray)
        self.assertEqual(x.data_array, 1.2)
        self.assertEqual(x.units, 'days since 1974-02-06')
        self.assertEqual(x.calendar, 'noleap')
        self.assertEqual(x.positive, None)

    def test_phys_array_with_positive_argument(self):
        x = PhysArray(1.2, name='x', units='g', positive='Up')
        self.assertIsInstance(x, PhysArray)
        self.assertEqual(x.data_array, 1.2)
        self.assertEqual(x.units, 'g')
        self.assertEqual(x.calendar, None)
        self.assertEqual(x.positive, 'up')

    def test_cfunits_with_time_units(self):
        x = PhysArray(1.2, name='x', units='days since 1974-02-06',
                      calendar='noleap')
        xu = cu.Unit('days since 1974-02-06', calendar='noleap')
        self.assertEqual(x.cfunits(), xu)

    def test_name(self):
        x = PhysArray(1.3, name='x')
        self.assertEqual(x.name, 'x')

    def test_set_name(self):
        x = PhysArray(1.3, name='x')
        x.name = 'y'
        self.assertEqual(x.name, 'y')

    def test_dtype(self):
        x = PhysArray(np.array(1.3, dtype='f'), name='x')
        self.assertEqual(x.dtype, np.dtype('f'))

    def test_attrs(self):
        x = PhysArray(2.3, name='x', attrs={'a': 'b'})
        self.assertEqual(x.attrs, {'a': 'b'})

    def test_set_attrs(self):
        x = PhysArray(2.3, name='x', attrs={'a': 'b'})
        x.attrs['c'] = 'd'
        self.assertEqual(x.attrs, {'a': 'b', 'c': 'd'})

    def test_negate_scalar(self):
        x = PhysArray(2.0, name='x')
        y = -x
        z = PhysArray(-2.0, name="(-x)")
        self.assertPhysArraysEqual(y, z)

    def test_add_scalar_to_float(self):
        x = PhysArray(2.0, name='x')
        y = 3.5
        z = PhysArray(5.5, name="(x+3.5)")
        self.assertPhysArraysEqual(x + y, z)

    def test_add_float_to_scalar(self):
        x = 3.5
        y = PhysArray(2.0, name='y')
        z = PhysArray(5.5, name="(3.5+y)")
        self.assertPhysArraysEqual(x + y, z)

    def test_add_scalar_to_scalar(self):
        x = PhysArray(3.5, name='x')
        y = PhysArray(2.0, name='y')
        z = PhysArray(5.5, name="(x+y)")
        self.assertPhysArraysEqual(x + y, z)

    def test_iadd_to_float(self):
        x = PhysArray(3.5, name='x')
        x += 2.0
        z = PhysArray(5.5, name="(x+2.0)")
        self.assertPhysArraysEqual(x, z)

    def test_iadd_to_scalar(self):
        x = PhysArray(3.5, name='x')
        x += PhysArray(2.0, name='y')
        z = PhysArray(5.5, name="(x+y)")
        self.assertPhysArraysEqual(x, z)

    def test_iadd_to_array(self):
        x = PhysArray(3.5, name='x')
        x += PhysArray([1.0, 2.0], name='y')
        z = PhysArray([4.5, 5.5], name="(x+y)")
        self.assertPhysArraysEqual(x, z)

    def test_add_scalars_with_unit_conversion(self):
        x = PhysArray(3.5, name='x', units='kg', attrs={'a': 'b'})
        y = PhysArray(500.0, name='y', units='g')
        z = PhysArray(4.0, name="(x+convert(y, to='kg'))", units='kg')
        self.assertPhysArraysEqual(x + y, z)

    def test_add_scalars_with_positive_flipping(self):
        x = PhysArray(3.5, name='x', positive='up')
        y = PhysArray(0.5, name='y', positive='down')
        z = PhysArray(3.0, name="(x+flip(y, to='up'))", positive='up')
        self.assertPhysArraysEqual(x + y, z)

    def test_sub_scalar_to_scalar(self):
        x = PhysArray(3.5, name='x')
        y = PhysArray(2.0, name='y')
        z = PhysArray(1.5, name="(x-y)")
        self.assertPhysArraysEqual(x - y, z)

    def test_sub_float_to_scalar(self):
        x = 3.5
        y = PhysArray(2.0, name='y')
        z = PhysArray(1.5, name="(3.5-y)")
        self.assertPhysArraysEqual(x - y, z)

    def test_mul_scalar_to_scalar(self):
        x = PhysArray(3.5, name='x', units='m')
        y = PhysArray(2.0, name='y', units='s')
        z = PhysArray(7.0, name="(x*y)", units='m.s')
        self.assertPhysArraysEqual(x * y, z)

    def test_mul_float_to_scalar(self):
        x = 3.5
        y = PhysArray(2.0, name='y', units='s')
        z = PhysArray(7.0, name="(3.5*y)", units='s')
        self.assertPhysArraysEqual(x * y, z)

    def test_div_scalar_to_scalar(self):
        x = PhysArray(3.5, name='x', units='m')
        y = PhysArray(2.0, name='y', units='s')
        z = PhysArray(1.75, name="(x/y)", units='m/s')
        self.assertPhysArraysEqual(x / y, z)

    def test_div_float_to_scalar(self):
        x = 3.5
        y = PhysArray(2.0, name='y', units='s')
        z = PhysArray(1.75, name="(3.5/y)", units='Hz')
        self.assertPhysArraysEqual(x / y, z)

    def test_pow_scalar(self):
        x = PhysArray(2.0, name='x', units='m')
        y = x**3
        z = PhysArray(8.0, name='(x**3)', units='m3')
        self.assertPhysArraysEqual(y, z)

    def test_sqrt_scalar(self):
        x = PhysArray(4.0, name='x', units='m2')
        y = np.sqrt(x)
        z = PhysArray(2.0, name='sqrt(x)', units='m')
        self.assertPhysArraysEqual(y, z)

    def test_hypotnuse_scalar(self):
        x = PhysArray(3.0, name='x', units='m')
        y = PhysArray(4.0, name='y', units='m')
        z = np.sqrt(x**2 + y**2)
        zz = PhysArray(5.0, name='sqrt(((x**2)+(y**2)))', units='m')
        self.assertPhysArraysEqual(z, zz)

    def test_trig_scalar(self):
        x = PhysArray(90.0, name='x', units='degree')
        y = np.sin(x)
        z = PhysArray(1.0, name='sin(x)')
        self.assertPhysArraysEqual(y, z)


if __name__ == "__main__":
    unittest.main()
