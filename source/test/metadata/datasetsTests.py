"""
Unit Tests for Dataset Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata.datasets import Dataset
from collections import OrderedDict


class DatasetTests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()

    def test_create(self):
        self.assertIsInstance(self.ds, Dataset)

    def test_default_dimensions_is_empty_set(self):
        self.assertEqual(self.ds.dimensions, {})

    def test_setting_dimensions_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.dimensions = 3

    def test_default_variables_is_empty_set(self):
        self.assertEqual(self.ds.variables, {})

    def test_setting_variables_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.variables = 3

    def test_default_files_is_empty_set(self):
        self.assertEqual(self.ds.files, {})

    def test_setting_files_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.files = 3

    def test_new_dimension(self):
        d = self.ds.new_dimension('x')
        self.assertIn(d, self.ds)
        self.assertEqual(self.ds.dimensions, {'x': d})

    def test_new_dimension_sets_dimension_dataset(self):
        d = self.ds.new_dimension('x')
        self.assertIs(d.dataset, self.ds)

    def test_two_new_dimensions_with_same_name_raises_value_error(self):
        self.ds.new_dimension('x')
        with self.assertRaises(ValueError):
            self.ds.new_dimension('x')

    def test_new_variable(self):
        v = self.ds.new_variable('v')
        self.assertIn(v, self.ds)
        self.assertEqual(self.ds.variables, {'v': v})

    def test_new_variable_sets_variable_dataset(self):
        v = self.ds.new_variable('v')
        self.assertIs(v.dataset, self.ds)

    def test_two_new_variables_with_same_name_raises_value_error(self):
        self.ds.new_variable('v')
        with self.assertRaises(ValueError):
            self.ds.new_variable('v')

    def test_new_file(self):
        f = self.ds.new_file('test.nc')
        self.assertIn(f, self.ds)
        self.assertEqual(self.ds.files, {'test.nc': f})

    def test_new_file_sets_file_dataset(self):
        f = self.ds.new_file('test.nc')
        self.assertIs(f.dataset, self.ds)

    def test_two_new_files_with_same_name_raises_value_error(self):
        self.ds.new_file('test.nc')
        with self.assertRaises(ValueError):
            self.ds.new_file('test.nc')

    def test_get_dimension(self):
        x1 = self.ds.new_dimension('x')
        x2 = self.ds.dimensions['x']
        self.assertIs(x1, x2)

    def test_get_dimension_not_found_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.ds.dimensions['x']

    def test_get_variable(self):
        v1 = self.ds.new_variable('v')
        v2 = self.ds.variables['v']
        self.assertIs(v1, v2)

    def test_get_variable_not_found_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.ds.variables['v']

    def test_get_file(self):
        f1 = self.ds.new_file('test.nc')
        f2 = self.ds.files['test.nc']
        self.assertIs(f1, f2)

    def test_get_file_not_found_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.ds.files['test.nc']

    def test_default_coordinates_is_empty_set(self):
        self.assertEqual(self.ds.coordinates, {})

    def test_setting_coordinates_by_matching_dimensions_and_variable_names(self):
        self.ds.new_dimension('x')
        x = self.ds.new_variable('x')
        x.dimensions = ('x',)
        self.assertEqual(self.ds.coordinates, {'x': x})

    def test_setting_coordinates_with_coordinates_attribute(self):
        self.ds.new_dimension('i')
        self.ds.new_dimension('j')
        x = self.ds.new_variable('x')
        x.dimensions = ('i', 'j')
        y = self.ds.new_variable('y')
        y.dimensions = ('i', 'j')
        v = self.ds.new_variable('v')
        v.dimensions = ('i', 'j')
        v.auxcoords = ('x', 'y')
        self.assertEqual(self.ds.coordinates, {'x': x, 'y': y})

    def test_setting_coordinates_with_axis_attribute(self):
        self.ds.new_dimension('i')
        x = self.ds.new_variable('x')
        x.axis = 'X'
        self.assertEqual(self.ds.coordinates, {'x': x})

    def test_from_standardization_with_non_dict_raises_type_error(self):
        with self.assertRaises(TypeError):
            Dataset.from_standardization('x')

    def create_standardization(self):
        std = OrderedDict()
        std['x'] = OrderedDict()
        std['x']['definition'] = 'X'
        std['x']['dimensions'] = ['x']
        std['x']['attributes'] = {'units': 'm'}
        std['y'] = OrderedDict()
        std['y']['definition'] = 'Y'
        std['y']['dimensions'] = ['y']
        std['y']['attributes'] = {'units': 'm'}
        std['t'] = OrderedDict()
        std['t']['definition'] = 'T'
        std['t']['datatype'] = 'double'
        std['t']['dimensions'] = ['t']
        std['t']['attributes'] = {'units': 'days since 1974-02-06'}
        std['v'] = OrderedDict()
        std['v']['definition'] = 'f(V)'
        std['v']['datatype'] = 'float'
        std['v']['dimensions'] = ['x', 'y', 't']
        std['v']['attributes'] = {'units': 'kg'}
        std['u'] = OrderedDict()
        std['u']['definition'] = 'U'
        std['u']['file'] = OrderedDict()
        std['u']['file']['filename'] = 'u_1.nc'
        std['u']['file']['deflate'] = 5
        std['u']['file']['shuffle'] = 'on'
        std['u']['file']['attributes'] = {'var': 'u'}
        return std

    def test_from_standardization(self):
        std = self.create_standardization()
        ods = Dataset.from_standardization(std)
        self.assertIsInstance(ods, Dataset)
        self.assertItemsEqual(ods.dimensions, ('x', 'y', 't'))
        self.assertItemsEqual(ods.variables, ('x', 'y', 't', 'v', 'u'))
        self.assertItemsEqual(ods.files, ('u_1.nc',))
        v = ods.variables['v']
        self.assertEqual(v.definition, 'f(V)')
        self.assertEqual(v.datatype, 'float')
        self.assertEqual(v.units, 'kg')
        u = ods.variables['u']
        self.assertEqual(u.definition, 'U')
        self.assertEqual(u.attributes, OrderedDict())
        f = ods.files['u_1.nc']
        self.assertEqual(f.deflate, 5)
        self.assertEqual(f.shuffle, 'on')
        self.assertEqual(f.attributes, {'var': 'u'})
        self.assertItemsEqual(f.dimensions, ('x', 'y', 't'))
        self.assertItemsEqual(f.variables, ('x', 'y', 't', 'u', 'v'))
        self.assertItemsEqual(f.coordinates, ('x', 'y', 't'))


if __name__ == '__main__':
    unittest.main()
