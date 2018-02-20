"""
Unit Tests for Specification Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.specification import Specification
from collections import OrderedDict


class DatasetTests(unittest.TestCase):

    def setUp(self):
        self.spec = Specification()

    def test_create(self):
        self.assertIsInstance(self.spec, Specification)

    def test_default_dimensions_is_empty_set(self):
        self.assertEqual(self.spec.dimensions, {})

    def test_setting_dimensions_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.spec.dimensions = 3

    def test_default_variables_is_empty_set(self):
        self.assertEqual(self.spec.variables, {})

    def test_setting_variables_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.spec.variables = 3

    def test_default_files_is_empty_set(self):
        self.assertEqual(self.spec.files, {})

    def test_setting_files_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.spec.files = 3

    def test_new_dimension(self):
        d = self.spec.new_dimension('x')
        self.assertIn(d, self.spec)
        self.assertEqual(self.spec.dimensions, {'x': d})

    def test_new_dimension_sets_dimension_dataset(self):
        d = self.spec.new_dimension('x')
        self.assertIs(d.specification, self.spec)

    def test_two_new_dimensions_with_same_name_raises_value_error(self):
        self.spec.new_dimension('x')
        with self.assertRaises(ValueError):
            self.spec.new_dimension('x')

    def test_new_variable(self):
        v = self.spec.new_variable('v')
        self.assertIn(v, self.spec)
        self.assertEqual(self.spec.variables, {'v': v})

    def test_new_variable_sets_variable_dataset(self):
        v = self.spec.new_variable('v')
        self.assertIs(v.specification, self.spec)

    def test_two_new_variables_with_same_name_raises_value_error(self):
        self.spec.new_variable('v')
        with self.assertRaises(ValueError):
            self.spec.new_variable('v')

    def test_new_file(self):
        f = self.spec.new_file('test.nc')
        self.assertIn(f, self.spec)
        self.assertEqual(self.spec.files, {'test.nc': f})

    def test_new_file_sets_file_dataset(self):
        f = self.spec.new_file('test.nc')
        self.assertIs(f.specification, self.spec)

    def test_two_new_files_with_same_name_raises_value_error(self):
        self.spec.new_file('test.nc')
        with self.assertRaises(ValueError):
            self.spec.new_file('test.nc')

    def test_get_dimension(self):
        x1 = self.spec.new_dimension('x')
        x2 = self.spec.dimensions['x']
        self.assertIs(x1, x2)

    def test_get_dimension_not_found_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.spec.dimensions['x']

    def test_get_variable(self):
        v1 = self.spec.new_variable('v')
        v2 = self.spec.variables['v']
        self.assertIs(v1, v2)

    def test_get_variable_not_found_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.spec.variables['v']

    def test_get_file(self):
        f1 = self.spec.new_file('test.nc')
        f2 = self.spec.files['test.nc']
        self.assertIs(f1, f2)

    def test_get_file_not_found_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.spec.files['test.nc']

    def test_default_coordinates_is_empty_set(self):
        self.assertEqual(self.spec.coordinates, {})

    def test_setting_coordinates_by_matching_dimensions_and_variable_names(self):
        self.spec.new_dimension('x')
        x = self.spec.new_variable('x')
        x.dimensions = ('x',)
        self.assertEqual(self.spec.coordinates, {'x': x})

    def test_setting_coordinates_with_coordinates_attribute(self):
        self.spec.new_dimension('i')
        self.spec.new_dimension('j')
        x = self.spec.new_variable('x')
        x.dimensions = ('i', 'j')
        y = self.spec.new_variable('y')
        y.dimensions = ('i', 'j')
        v = self.spec.new_variable('v')
        v.dimensions = ('i', 'j')
        v.auxcoords = ('x', 'y')
        self.assertEqual(self.spec.coordinates, {'x': x, 'y': y})

    def test_setting_coordinates_with_axis_attribute(self):
        self.spec.new_dimension('i')
        x = self.spec.new_variable('x')
        x.axis = 'X'
        self.assertEqual(self.spec.coordinates, {'x': x})

    def test_from_standardization_with_non_dict_raises_type_error(self):
        with self.assertRaises(TypeError):
            Specification.from_standardization('x')

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
        spec = Specification.from_standardization(std)
        self.assertIsInstance(spec, Specification)
        self.assertItemsEqual(spec.dimensions, ('x', 'y', 't'))
        self.assertItemsEqual(spec.variables, ('x', 'y', 't', 'v', 'u'))
        self.assertItemsEqual(spec.files, ('u_1.nc',))
        v = spec.variables['v']
        self.assertEqual(v.definition, 'f(V)')
        self.assertEqual(v.datatype, 'float')
        self.assertEqual(v.units, 'kg')
        u = spec.variables['u']
        self.assertEqual(u.definition, 'U')
        self.assertEqual(u.attributes, OrderedDict())
        f = spec.files['u_1.nc']
        self.assertEqual(f.deflate, 5)
        self.assertEqual(f.shuffle, 'on')
        self.assertEqual(f.attributes, {'var': 'u'})
        self.assertItemsEqual(f.dimensions, ('x', 'y', 't'))
        self.assertItemsEqual(f.variables, ('x', 'y', 't', 'u', 'v'))
        self.assertItemsEqual(f.coordinates, ('x', 'y', 't'))


if __name__ == '__main__':
    unittest.main()
