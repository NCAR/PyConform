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

    def test_default_attributes_is_empty_set(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.attributes, frozenset())

    def test_setting_attributes_raises_attribute_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.attributes = 4

    def test_setting_attributes_in_constructor(self):
        f = self.ds.new_file('test.nc', attributes={'a': 'b'})
        self.assertEqual(f.attributes, {'a'})

    def test_get_attribute(self):
        f = self.ds.new_file('test.nc', attributes={'a': 'b'})
        self.assertEqual(f.get_attribute('a'), 'b')

    def test_default_deflate_is_1(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.deflate, 1)

    def test_setting_deflate_raises_attribute_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.deflate = 4

    def test_setting_deflate_in_constructor(self):
        f = self.ds.new_file('test.nc', deflate=3)
        self.assertEqual(f.deflate, 3)

    def test_setting_deflate_to_invalid_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.ds.new_file('test.nc', deflate='3')

    def test_default_shuffle_is_off(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.shuffle, 'off')

    def test_setting_shuffle_raises_attribute_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.shuffle = 'on'

    def test_setting_shuffle_in_constructor(self):
        f = self.ds.new_file('test.nc', shuffle='on')
        self.assertEqual(f.shuffle, 'on')

    def test_setting_shuffle_to_invalid_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.ds.new_file('test.nc', shuffle=True)

    def test_default_dimensions_is_empty_set(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.dimensions, frozenset())

    def test_setting_dimensions_raises_attribute_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.dimensions = 4

    def test_setting_dimensions_in_constructor(self):
        self.ds.new_dimension('x')
        self.ds.new_dimension('y')
        f = self.ds.new_file('test.nc', dimensions=('x', 'y'))
        self.assertItemsEqual(f.dimensions, ('x', 'y'))

    def test_file_get_dimensions_variables(self):
        x = self.ds.new_dimension('x', size=5)
        v = self.ds.new_variable('v', dimensions=('x',))
        f = self.ds.new_file('test.nc', dimensions=('x',), variables=('v',))
        self.assertEquals(f.get_dimensions()['x'], x)
        self.assertEquals(f.get_variables()['v'], v)

    def test_default_variables_is_empty_set(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.variables, frozenset())

    def test_setting_variables_raises_attribute_error(self):
        f = self.ds.new_file('test.nc')
        with self.assertRaises(AttributeError):
            f.variables = 4

    def test_setting_variables_in_constructor(self):
        self.ds.new_variable('u')
        self.ds.new_variable('v')
        f = self.ds.new_file('test.nc', variables=('u', 'v'))
        self.assertItemsEqual(f.variables, ('u', 'v'))

    def test_setting_variables_not_found_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.ds.new_file('test.nc', variables=('u', 'v'))

    def test_setting_variables_with_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.ds.new_file('test.nc', variables=(1, 2))

    def test_default_coordinates_is_empty_set(self):
        f = self.ds.new_file('test.nc')
        self.assertEqual(f.coordinates, frozenset())


if __name__ == '__main__':
    unittest.main()
