"""
Unit Tests for Dimension Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import Dimension


class DimensionTests(unittest.TestCase):

    def setUp(self):
        self.d = Dimension('x')

    def test_create(self):
        self.assertIsInstance(self.d, Dimension)

    def test_default_size_is_none(self):
        self.assertEqual(self.d.size, None)

    def test_setting_size_property_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.d.size = 5

    def test_set_size_to_int_in_constructor(self):
        d = Dimension('x', size=4)
        self.assertEqual(d.size, 4)

    def test_set_size_to_non_int_raises_type_error(self):
        with self.assertRaises(TypeError):
            Dimension('x', size='4')

    def test_set_size_to_non_positive_raises_value_error(self):
        with self.assertRaises(ValueError):
            Dimension('x', size=-2)

    def test_default_is_unlimited_is_false(self):
        self.assertEqual(self.d.is_unlimited, False)

    def test_setting_is_unlimited_property_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.d.is_unlimited = True

    def test_set_is_unlimited_to_bool_in_constructor(self):
        d = Dimension('x', is_unlimited=True)
        self.assertEqual(d.is_unlimited, True)

    def test_set_is_unlimited_to_non_bool_raises_type_error(self):
        with self.assertRaises(TypeError):
            Dimension('x', is_unlimited='false')


if __name__ == '__main__':
    unittest.main()
