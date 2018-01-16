"""
Unit Tests for Dataset Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import Dataset, Dimension, Variable, File


class DatasetTests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()

    def test_create(self):
        self.assertIsInstance(self.ds, Dataset)

    def test_default_dimensions_is_empty_tuple(self):
        self.assertEqual(self.ds.dimensions, ())

    def test_setting_dimensions_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.dimensions = 3

    def test_add_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.ds.add('x')

    def test_default_variables_is_empty_tuple(self):
        self.assertEqual(self.ds.variables, ())

    def test_setting_variables_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.variables = 3

    def test_default_files_is_empty_tuple(self):
        self.assertEqual(self.ds.files, ())

    def test_setting_files_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.files = 3

    def test_add_dimension(self):
        d = Dimension('x')
        self.ds.add(d)
        self.assertIn(d, self.ds)

    def test_add_different_dimensions_with_same_name_raises_value_error(self):
        d1 = Dimension('x')
        d2 = Dimension('x')
        self.ds.add(d1)
        with self.assertRaises(ValueError):
            self.ds.add(d2)

    def test_add_variable(self):
        v = Variable('v')
        self.ds.add(v)
        self.assertIn(v, self.ds)

    def test_add_different_variables_with_same_name_raises_value_error(self):
        v1 = Variable('v')
        v2 = Variable('v')
        self.ds.add(v1)
        with self.assertRaises(ValueError):
            self.ds.add(v2)

    def test_add_variable_without_dimensions_raises_key_error(self):
        v = Variable('v', dimensions=('x',))
        with self.assertRaises(KeyError):
            self.ds.add(v)

    def test_add_file(self):
        f = File('test.nc')
        self.ds.add(f)
        self.assertIn(f, self.ds)

    def test_add_different_files_with_same_name_raises_value_error(self):
        f1 = File('test.nc')
        f2 = File('test.nc')
        self.ds.add(f1)
        with self.assertRaises(ValueError):
            self.ds.add(f2)

    def test_add_file_without_variables_raises_key_error(self):
        f = File('test.nc', variables=('v',))
        with self.assertRaises(KeyError):
            self.ds.add(f)

    def test_new_dimension(self):
        d = self.ds.new_dimension('x', size=5)
        self.assertIn(d, self.ds)
        self.assertEqual(d.size, 5)

    def test_new_variable(self):
        v = self.ds.new_variable('v', datatype='int64')
        self.assertIn(v, self.ds)
        self.assertEqual(v.datatype, 'int64')

    def test_new_variable_without_dimensions_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.ds.new_variable('v', dimensions=('x',))

    def test_new_file(self):
        f = self.ds.new_file('test.nc', format='NETCDF4')
        self.assertIn(f, self.ds)
        self.assertEqual(f.format, 'NETCDF4')


if __name__ == '__main__':
    unittest.main()
