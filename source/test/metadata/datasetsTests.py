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
        v1 = Dimension('v')
        v2 = Dimension('v')
        self.ds.add(v1)
        with self.assertRaises(ValueError):
            self.ds.add(v2)

    def test_add_variable_also_adds_dimensions(self):
        d = Dimension('x')
        v = Variable('v', dimensions=(d,))
        self.ds.add(v)
        self.assertIn(d, self.ds)

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

    def test_add_file_also_adds_variables_and_dimensions(self):
        d = Dimension('x')
        v = Variable('v', dimensions=(d,))
        f = File('test.nc', variables=(v,))
        self.ds.add(f)
        self.assertIn(v, self.ds)
        self.assertIn(d, self.ds)


if __name__ == '__main__':
    unittest.main()
