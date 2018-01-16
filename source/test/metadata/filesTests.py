"""
Unit Tests for File Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import File, Variable, Dimension, Dataset


class FileTests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()
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

    def test_setting_dimensions_in_constructor(self):
        f = File('test.nc', dimensions=('x', 'y'))
        self.assertItemsEqual(f.dimensions, ('x', 'y'))

    def test_default_variables_is_empty_tuple(self):
        self.assertEqual(self.f.variables, ())

    def test_setting_variables_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.variables = 4

    def test_setting_variables_in_constructor(self):
        f = File('test.nc', variables=('u', 'v'))
        self.assertItemsEqual(f.variables, ('u', 'v'))

    def test_setting_variables_with_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            File('test.nc', variables=(1, 2))


if __name__ == '__main__':
    unittest.main()
