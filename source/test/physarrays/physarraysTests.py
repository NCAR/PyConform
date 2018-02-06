"""
Unit Tests for PhysArray Class and Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays import PhysArray, convert

import xarray as xr
import numpy as np
import unittest


class PhysArrayTests(unittest.TestCase):

    def test_create(self):
        x = PhysArray(1.0, name='x')
        self.assertIsInstance(x, PhysArray)
        self.assertIsInstance(x, xr.DataArray)

    def test_convert(self):
        v = PhysArray([[1, 2], [3, 4]], name='v', dims=['x', 'y'],
                      coords=[[0, 1], [1, 2]], attrs={'units': 'g'})
        v_kg = convert(v, 'kg')
        self.assertIsInstance(v_kg, PhysArray)

    def test_add_x_y(self):
        xs = [PhysArray(3.0, name='x', attrs={'units': 'km'}),
              PhysArray([3.0, 4.0, 5.0], dims=['i'], coords=[
                        [0, 1, 2]], name='x', attrs={'units': 'km'}),
              PhysArray(3.0, name='x'), 1.0]
        ys = [PhysArray(2.0, name='y', attrs={'units': 'm'}),
              PhysArray([9.0, 7.0, 5.0], dims=['i'], coords=[
                        [0, 1, 2]], name='y', attrs={'units': 'm'}),
              1.0, PhysArray(3.0, name='y')]
        zs = [PhysArray(3.002, name="(x+convert(y, to='km'))", attrs={'units': 'km'}),
              PhysArray([3.009, 4.007, 5.005], name="(x+convert(y, to='km'))",
                        dims=['i'], coords=[[0, 1, 2]], attrs={'units': 'km'}),
              PhysArray(4.0, name='(x+1.0)'),
              PhysArray(4.0, name='(1.0+y)')]
        for x, y, z_expected in zip(xs, ys, zs):
            z_actual = x + y
            np.testing.assert_array_equal(z_actual, z_expected)
            self.assertEqual(z_actual.name, z_expected.name)
            self.assertEqual(z_actual.units, z_expected.units)

    def test_sub_x_y(self):
        xs = [PhysArray(3.0, name='x', attrs={'units': 'km'}),
              PhysArray([3.0, 4.0, 5.0], dims=['i'], coords=[
                        [0, 1, 2]], name='x', attrs={'units': 'km'}),
              PhysArray(3.0, name='x'), 1.0]
        ys = [PhysArray(2.0, name='y', attrs={'units': 'm'}),
              PhysArray([9.0, 7.0, 5.0], dims=['i'], coords=[
                        [0, 1, 2]], name='y', attrs={'units': 'm'}),
              1.0, PhysArray(3.0, name='y')]
        zs = [PhysArray(2.998, name="(x-convert(y, to='km'))", attrs={'units': 'km'}),
              PhysArray([2.991, 3.993, 4.995], name="(x-convert(y, to='km'))",
                        dims=['i'], coords=[[0, 1, 2]], attrs={'units': 'km'}),
              PhysArray(2.0, name='(x-1.0)'),
              PhysArray(-2.0, name='(1.0-y)')]
        for x, y, z_expected in zip(xs, ys, zs):
            z_actual = x - y
            np.testing.assert_array_equal(z_actual, z_expected)
            self.assertEqual(z_actual.name, z_expected.name)
            self.assertEqual(z_actual.units, z_expected.units)

    def test_mul_x_y(self):
        xs = [PhysArray(3.0, name='x', attrs={'units': 'm'}),
              PhysArray([3.0, 4.0, 5.0], dims=['i'], coords=[[0, 1, 2]],
                        name='x', attrs={'units': 'm'}),
              PhysArray(3.0, name='x'), 2.0]
        ys = [PhysArray(2.0, name='y', attrs={'units': 'km'}),
              PhysArray([9.0, 7.0, 5.0], dims=['i'], coords=[[0, 1, 2]],
                        name='y', attrs={'units': 'km'}),
              2.0, PhysArray(3.0, name='y')]
        zs = [PhysArray(6.0, name="(x*y)", attrs={'units': '1000 m^2'}),
              PhysArray([27., 28., 25.], name="(x*y)",
                        dims=['i'], coords=[[0, 1, 2]], attrs={'units': '1000 m^2'}),
              PhysArray(6.0, name='(x*2.0)'),
              PhysArray(6.0, name='(2.0*y)')]
        for x, y, z_expected in zip(xs, ys, zs):
            z_actual = x * y
            np.testing.assert_array_equal(z_actual, z_expected)
            self.assertEqual(z_actual.name, z_expected.name)
            self.assertEqual(z_actual.units, z_expected.units)

    def test_div_x_y(self):
        xs = [PhysArray(3.0, name='x', attrs={'units': 'm'}),
              PhysArray([3.0, 4.0, 5.0], dims=['i'], coords=[[0, 1, 2]],
                        name='x', attrs={'units': 'm'}),
              PhysArray(3.0, name='x'), 2.0]
        ys = [PhysArray(2.0, name='y', attrs={'units': 'cm'}),
              PhysArray([9.0, 7.0, 5.0], dims=['i'], coords=[[0, 1, 2]],
                        name='y', attrs={'units': 'cm'}),
              2.0, PhysArray(3.0, name='y')]
        zs = [PhysArray(1.5, name="(x/y)", attrs={'units': '100'}),
              PhysArray([1. / 3, 4. / 7, 1.], name="(x/y)",
                        dims=['i'], coords=[[0, 1, 2]], attrs={'units': '100'}),
              PhysArray(1.5, name='(x/2.0)'),
              PhysArray(2. / 3, name='(2.0/y)')]
        for x, y, z_expected in zip(xs, ys, zs):
            z_actual = x / y
            np.testing.assert_array_equal(z_actual, z_expected)
            self.assertEqual(z_actual.name, z_expected.name)
            self.assertEqual(z_actual.units, z_expected.units)


if __name__ == "__main__":
    unittest.main()
