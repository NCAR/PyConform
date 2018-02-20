"""
Unit Tests for File Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.specification import File, Specification


class FileTests(unittest.TestCase):

    def setUp(self):
        self.spec = Specification()

    def test_create(self):
        f = self.spec.new_file('test.nc')
        self.assertIsInstance(f, File)

    def test_default_attributes_is_empty_dict(self):
        f = self.spec.new_file('test.nc')
        self.assertEqual(f.attributes, {})

    def test_setting_attributes_raises_attribute_error(self):
        f = self.spec.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.attributes = 4

    def test_setting_attributes_by_key_value(self):
        f = self.spec.new_file('test.nc')
        f.attributes['a'] = 'b'
        self.assertEqual(f.attributes, {'a': 'b'})

    def test_setting_attributes_in_constructor_with_dict(self):
        f = self.spec.new_file('test.nc', attributes={'a': 'b'})
        self.assertEqual(f.attributes, {'a': 'b'})

    def test_default_deflate_is_1(self):
        f = self.spec.new_file('test.nc')
        self.assertEqual(f.deflate, 1)

    def test_setting_deflate_to_invalid_value_raises_type_error(self):
        f = self.spec.new_file('test.nc')
        with self.assertRaises(TypeError):
            f.deflate = 20

    def test_setting_deflate_property_to_valid_saves_value(self):
        f = self.spec.new_file('test.nc')
        f.deflate = 3
        self.assertEqual(f.deflate, 3)

    def test_setting_deflate_in_constructor_to_valid_saves_value(self):
        f = self.spec.new_file('test.nc')
        f.deflate = 3
        self.assertEqual(f.deflate, 3)

    def test_default_shuffle_is_off(self):
        f = self.spec.new_file('test.nc')
        self.assertEqual(f.shuffle, 'off')

    def test_setting_shuffle_to_invalid_value_raises_type_error(self):
        f = self.spec.new_file('test.nc')
        with self.assertRaises(TypeError):
            f.shuffle = True

    def test_setting_shuffle_property_to_on_saves_value(self):
        f = self.spec.new_file('test.nc')
        f.shuffle = 'on'
        self.assertEqual(f.shuffle, 'on')

    def test_setting_shuffle_in_constructor_to_on_saves_value(self):
        f = self.spec.new_file('test.nc', shuffle='on')
        self.assertEqual(f.shuffle, 'on')

    def test_default_dimensions_is_empty_dict(self):
        f = self.spec.new_file('test.nc')
        self.assertEqual(f.dimensions, {})

    def test_setting_dimensions_raises_attribute_error(self):
        f = self.spec.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.dimensions = 4

    def test_adding_dimensions_by_name(self):
        x = self.spec.new_dimension('x')
        y = self.spec.new_dimension('y')
        f = self.spec.new_file('test.nc')
        f.add_dimensions('x', 'y')
        self.assertItemsEqual(f.dimensions, {'x': x, 'y': y})

    def test_file_get_dimensions_variables(self):
        x = self.spec.new_dimension('x')
        v = self.spec.new_variable('v')
        v.dimensions = ('x',)
        f = self.spec.new_file('test.nc')
        f.add_dimensions('x')
        f.add_variables('v')
        self.assertEquals(f.dimensions, {'x': x})
        self.assertEquals(f.variables, {'v': v})

    def test_default_variables_is_empty_dict(self):
        f = self.spec.new_file('test.nc')
        self.assertEqual(f.variables, {})

    def test_setting_variables_raises_attribute_error(self):
        f = self.spec.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.variables = 4

    def test_adding_variables_by_name(self):
        u = self.spec.new_variable('u')
        v = self.spec.new_variable('v')
        f = self.spec.new_file('test.nc')
        f.add_variables('u', 'v')
        self.assertItemsEqual(f.variables, {'u': u, 'v': v})

    def test_setting_variables_not_found_raises_key_error(self):
        f = self.spec.new_file('test.nc')
        with self.assertRaises(KeyError):
            f.add_variables('u')

    def test_default_coordinates_is_empty_set(self):
        f = self.spec.new_file('test.nc')
        self.assertEqual(f.coordinates, {})

    def test_coordinates(self):
        self.spec.new_dimension('x')
        self.spec.new_dimension('y')
        x = self.spec.new_variable('x')
        x.dimensions = ('x',)
        y = self.spec.new_variable('y')
        y.dimensions = ('y',)
        self.spec.new_variable('v')
        f = self.spec.new_file('test.nc')
        f.add_variables('y', 'v')
        self.assertEqual(f.coordinates, {'y': y})


if __name__ == '__main__':
    unittest.main()
