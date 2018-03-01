"""
Unit Tests for New PhysArrays

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays.newarrays import PhysArray

import xarray as xr
import cf_units as cu
import unittest


class PhysArrayTests(unittest.TestCase):

    def test_create(self):
        a = PhysArray(2.3)
        self.assertIsInstance(a, PhysArray)

    def test_phys_array_from_data_array(self):
        x_da = xr.DataArray(1.2, name='x', attrs={'units': 'g'})
        x_pa = PhysArray(x_da)
        self.assertIsInstance(x_pa, PhysArray)
        self.assertEqual(x_pa.data_array, x_da)
        self.assertEqual(x_pa.units, 'g')
        self.assertEqual(x_pa.calendar, None)
        self.assertEqual(x_pa.positive, None)

    def test_phys_array_from_arguments(self):
        x_pa = PhysArray(1.2, name='x', attrs={'units': 'g'})
        self.assertIsInstance(x_pa, PhysArray)
        self.assertEqual(x_pa.data_array, 1.2)
        self.assertEqual(x_pa.units, 'g')
        self.assertEqual(x_pa.calendar, None)
        self.assertEqual(x_pa.positive, None)

    def test_phys_array_with_units_argument(self):
        x_pa = PhysArray(1.2, name='x', units='g')
        self.assertIsInstance(x_pa, PhysArray)
        self.assertEqual(x_pa.data_array, 1.2)
        self.assertEqual(x_pa.units, 'g')
        self.assertEqual(x_pa.calendar, None)
        self.assertEqual(x_pa.positive, None)

    def test_phys_array_with_calendar_argument(self):
        x_pa = PhysArray(1.2, name='x', units='days since 1974-02-06',
                         calendar='noleap')
        self.assertIsInstance(x_pa, PhysArray)
        self.assertEqual(x_pa.data_array, 1.2)
        self.assertEqual(x_pa.units, 'days since 1974-02-06')
        self.assertEqual(x_pa.calendar, 'noleap')
        self.assertEqual(x_pa.positive, None)

    def test_phys_array_with_positive_argument(self):
        x_pa = PhysArray(1.2, name='x', units='g', positive='Up')
        self.assertIsInstance(x_pa, PhysArray)
        self.assertEqual(x_pa.data_array, 1.2)
        self.assertEqual(x_pa.units, 'g')
        self.assertEqual(x_pa.calendar, None)
        self.assertEqual(x_pa.positive, 'up')

    def test_cfunits_with_time_units(self):
        x_pa = PhysArray(1.2, name='x', units='days since 1974-02-06',
                         calendar='noleap')
        self.assertEqual(x_pa.cfunits(),
                         cu.Unit('days since 1974-02-06', calendar='noleap'))


if __name__ == "__main__":
    unittest.main()
