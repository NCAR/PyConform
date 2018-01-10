"""
Unit Tests for File Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import File, Variable, Dimension


class FileTests(unittest.TestCase):

    def setUp(self):
        self.f = File('test.nc')

    def test_create(self):
        self.assertIsInstance(self.f, File)

    def test_default_attributes_is_empty_dict(self):
        self.assertEqual(self.f.attributes, {})

    def test_setting_attributes_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.attributes = 4

    def test_default_deflate_is_1(self):
        self.assertEqual(self.f.deflate, 1)

    def test_setting_deflate_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.deflate = 4

    def test_setting_deflate_in_constructor(self):
        f = File('test.nc', deflate=3)
        self.assertEqual(f.deflate, 3)

    def test_setting_deflate_to_invalid_raises_type_error(self):
        with self.assertRaises(TypeError):
            File('test.nc', deflate='3')

    def test_default_dimensions_is_empty_tuple(self):
        self.assertEqual(self.f.dimensions, ())

    def test_setting_dimensions_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.dimensions = 4

    def test_default_variables_is_empty_tuple(self):
        self.assertEqual(self.f.variables, ())

    def test_setting_variables_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.variables = 4

    def test_add_dimension(self):
        d = Dimension('x')
        self.f.add(d)
        self.assertIn(d, self.f)

    def test_add_different_dimensions_with_same_names_raises_value_error(self):
        d1 = Dimension('x')
        d2 = Dimension('x')
        self.f.add(d1)
        with self.assertRaises(ValueError):
            self.f.add(d2)

    def test_add_variable(self):
        v = Variable('v')
        self.f.add(v)
        self.assertIn(v, self.f)

    def test_add_different_variables_with_same_names_raises_value_error(self):
        v1 = Variable('v')
        v2 = Variable('v')
        self.f.add(v1)
        with self.assertRaises(ValueError):
            self.f.add(v2)

    def test_add_variable_with_non_variable_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.f.add('v')

    def test_add_variable_adds_dimensions(self):
        d = Dimension('x')
        v = Variable('v', dimensions=(d,))
        self.f.add(v)
        self.assertIn(d, self.f)


if __name__ == '__main__':
    unittest.main()
