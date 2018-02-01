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

    def test_create(self):
        f = self.ds.new_file('test.nc')
        self.assertIsInstance(f, File)

    def test_default_attributes_is_empty_dict(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.attributes, {})

    def test_setting_attributes_raises_attribute_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.attributes = 4

    def test_setting_attributes_by_key_value(self):
        f = self.ds.new_file('test.nc')
        f.attributes['a'] = 'b'
        self.assertEqual(f.attributes, {'a': 'b'})

    def test_default_deflate_is_1(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.deflate, 1)

    def test_setting_deflate_to_invalid_value_raises_type_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(TypeError):
            f.deflate = 20

    def test_setting_deflate_to_valid_saves_value(self):
        f = self.ds.new_file('test.nc')
        f.deflate = 3
        self.assertEqual(f.deflate, 3)

    def test_default_shuffle_is_off(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.shuffle, 'off')

    def test_setting_shuffle_to_invalid_value_raises_type_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(TypeError):
            f.shuffle = True

    def test_setting_shuffle_to_on_saves_value(self):
        f = self.ds.new_file('test.nc')
        f.shuffle = 'on'
        self.assertEqual(f.shuffle, 'on')

    def test_default_dimensions_is_empty_dict(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.dimensions, {})

    def test_setting_dimensions_raises_attribute_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.dimensions = 4

    def test_adding_dimension_by_name(self):
        x = self.ds.new_dimension('x')
        y = self.ds.new_dimension('y')
        f = self.ds.new_file('test.nc')
        f.add_dimension('x')
        f.add_dimension('y')
        self.assertItemsEqual(f.dimensions, {'x': x, 'y': y})

    def test_file_get_dimensions_variables(self):
        x = self.ds.new_dimension('x')
        v = self.ds.new_variable('v')
        v.dimensions = ('x',)
        f = self.ds.new_file('test.nc')
        f.add_dimension('x')
        f.add_variable('v')
        self.assertEquals(f.dimensions, {'x': x})
        self.assertEquals(f.variables, {'v': v})

    def test_default_variables_is_empty_dict(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.variables, {})

    def test_setting_variables_raises_attribute_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.variables = 4

    def test_adding_variables_by_name(self):
        u = self.ds.new_variable('u')
        v = self.ds.new_variable('v')
        f = self.ds.new_file('test.nc')
        f.add_variable('u')
        f.add_variable('v')
        self.assertItemsEqual(f.variables, {'u': u, 'v': v})

    def test_setting_variables_not_found_raises_key_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(KeyError):
            f.add_variable('u')

    def test_default_coordinates_is_empty_set(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.coordinates, {})

    def test_coordinates(self):
        self.ds.new_dimension('x')
        x = self.ds.new_variable('x')
        x.dimensions = ('x',)
        self.ds.new_dimension('y')
        y = self.ds.new_variable('y')
        y.dimensions = ('y',)
        f = self.ds.new_file('test.nc')
        f.add_variable('y')
        self.ds.new_variable('v')
        f.add_variable('v')
        self.assertEqual(f.coordinates, {'y': y})


if __name__ == '__main__':
    unittest.main()
