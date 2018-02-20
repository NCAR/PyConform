"""
Unit Tests for Dimension Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.specification import Dimension, Specification


class DimensionTests(unittest.TestCase):

    def setUp(self):
        self.ds = Specification()

    def test_create(self):
        d = self.ds.new_dimension('x')
        self.assertIsInstance(d, Dimension)

    def test_default_size_is_none(self):
        d = self.ds.new_dimension('x')
        self.assertEqual(d.size, None)

    def test_setting_size_property_stores_value(self):
        d = self.ds.new_dimension('x')
        d.size = 5
        self.assertEqual(d.size, 5)

    def test_setting_size_in_constructor_stores_value(self):
        d = self.ds.new_dimension('x', size=5)
        self.assertEqual(d.size, 5)

    def test_setting_size_to_non_int_raises_type_error(self):
        d = self.ds.new_dimension('x')
        with self.assertRaises(TypeError):
            d.size = '4'

    def test_setting_size_to_non_positive_raises_type_error(self):
        x = self.ds.new_dimension('x')
        with self.assertRaises(TypeError):
            x.size = -2

    def test_default_is_unlimited_is_false(self):
        d = self.ds.new_dimension('x')
        self.assertEqual(d.is_unlimited, False)

    def test_setting_is_unlimited_property_to_bool_saves_bool(self):
        d = self.ds.new_dimension('x')
        d.is_unlimited = True
        self.assertTrue(d.is_unlimited)

    def test_setting_is_unlimited_in_constructor_to_bool_saves_bool(self):
        d = self.ds.new_dimension('x', is_unlimited=True)
        self.assertTrue(d.is_unlimited)

    def test_setting_is_unlimited_to_non_bool_saves_bool_value(self):
        d = self.ds.new_dimension('x', is_unlimited=5)
        self.assertTrue(d.is_unlimited)

    def test_equal(self):
        ds1 = Specification()
        ds2 = Specification()
        d1 = ds1.new_dimension('x', size=4)
        d2 = ds2.new_dimension('x', size=4)
        self.assertEqual(d1, d2)

    def test_not_equal(self):
        ds1 = Specification()
        ds2 = Specification()
        d1 = ds1.new_dimension('x', size=3)
        d2 = ds2.new_dimension('y', size=4)
        self.assertIsNot(d1, d2)
        self.assertNotEqual(d1, d2)


if __name__ == '__main__':
    unittest.main()
