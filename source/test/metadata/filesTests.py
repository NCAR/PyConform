"""
Unit Tests for File Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import File
from pyconform.metadata.datasets import Dataset


class FileTests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()
        self.f = File('test.nc', dataset=self.ds)

    def test_create(self):
        self.assertIsInstance(self.f, File)

    def test_default_attributes_is_empty_dict(self):
        self.assertEqual(self.f.attributes, {})

    def test_setting_attributes_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.attributes = 4

    def test_setting_attributes_in_constructor(self):
        f = File('test.nc', attributes={'a': 'b'}, dataset=self.ds)
        self.assertEqual(f.attributes, {'a': 'b'})

    def test_default_deflate_is_1(self):
        self.assertEqual(self.f.deflate, 1)

    def test_setting_deflate_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.deflate = 4

    def test_setting_deflate_in_constructor(self):
        f = File('test.nc', deflate=3, dataset=self.ds)
        self.assertEqual(f.deflate, 3)

    def test_setting_deflate_to_invalid_raises_type_error(self):
        with self.assertRaises(TypeError):
            File('test.nc', deflate='3')

    def test_default_shuffle_is_off(self):
        self.assertEqual(self.f.shuffle, 'off')

    def test_setting_shuffle_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.shuffle = 'on'

    def test_setting_shuffle_in_constructor(self):
        f = File('test.nc', shuffle='on', dataset=self.ds)
        self.assertEqual(f.shuffle, 'on')

    def test_setting_shuffle_to_invalid_raises_type_error(self):
        with self.assertRaises(TypeError):
            File('test.nc', shuffle=True)

    def test_default_dimensions_is_empty_set(self):
        self.assertEqual(self.f.dimensions, frozenset())

    def test_setting_dimensions_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.dimensions = 4

    def test_setting_dimensions_in_constructor(self):
        f = File('test.nc', dimensions=('x', 'y'), dataset=self.ds)
        self.assertItemsEqual(f.dimensions, ('x', 'y'))

    def test_default_variables_is_empty_set(self):
        self.assertEqual(self.f.variables, frozenset())

    def test_setting_variables_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.f.variables = 4

    def test_setting_variables_in_constructor(self):
        f = File('test.nc', variables=('u', 'v'), dataset=self.ds)
        self.assertItemsEqual(f.variables, ('u', 'v'))

    def test_setting_variables_with_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            File('test.nc', variables=(1, 2), dataset=self.ds)

    def test_default_coordinates_is_empty_set(self):
        self.assertEqual(self.f.coordinates, frozenset())


if __name__ == '__main__':
    unittest.main()
