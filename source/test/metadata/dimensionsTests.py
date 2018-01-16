"""
Unit Tests for Dimension Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import Dimension, Dataset


class MockNetCDF4Dimension(object):

    def __init__(self, name, size, isunlimited=False):
        self.name = name
        self.size = size
        self._isunlimited = isunlimited

    def __len__(self):
        return self.size

    def isunlimited(self):
        return self._isunlimited


class DimensionTests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()
        self.d = Dimension('x', dataset=self.ds)

    def test_create(self):
        self.assertIsInstance(self.d, Dimension)

    def test_default_size_is_none(self):
        self.assertEqual(self.d.size, None)

    def test_setting_size_property_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.d.size = 5

    def test_set_size_to_int_in_constructor(self):
        d = Dimension('x', size=4, dataset=self.ds)
        self.assertEqual(d.size, 4)

    def test_set_size_to_non_int_raises_type_error(self):
        with self.assertRaises(TypeError):
            Dimension('x', size='4', dataset=self.ds)

    def test_set_size_to_non_positive_raises_value_error(self):
        with self.assertRaises(ValueError):
            Dimension('x', size=-2, dataset=self.ds)

    def test_default_is_unlimited_is_false(self):
        self.assertEqual(self.d.is_unlimited, False)

    def test_setting_is_unlimited_property_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.d.is_unlimited = True

    def test_set_is_unlimited_to_bool_in_constructor(self):
        d = Dimension('x', is_unlimited=True, dataset=self.ds)
        self.assertEqual(d.is_unlimited, True)

    def test_set_is_unlimited_to_non_bool_raises_type_error(self):
        with self.assertRaises(TypeError):
            Dimension('x', is_unlimited='false', dataset=self.ds)

    def test_from_netcdf4(self):
        ncdim = MockNetCDF4Dimension('x', 4, isunlimited=True)
        dim = Dimension.from_netcdf4(ncdim, dataset=self.ds)
        self.assertEqual(dim.name, 'x')
        self.assertEqual(dim.size, 4)
        self.assertTrue(dim.is_unlimited)

    def test_equal(self):
        d1 = Dimension('x', size=5, is_unlimited=True, dataset=self.ds)
        d2 = Dimension('x', size=5, is_unlimited=True, dataset=self.ds)
        self.assertEqual(d1, d2)

    def test_not_equal(self):
        d1 = Dimension('x', size=5, is_unlimited=True, dataset=self.ds)
        d2 = Dimension('x', size=2, is_unlimited=True, dataset=self.ds)
        self.assertIsNot(d1, d2)
        self.assertNotEqual(d1, d2)


if __name__ == '__main__':
    unittest.main()
