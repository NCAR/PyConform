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

    def test_default_dimensions_is_empty_list(self):
        self.assertEqual(self.ds.dimensions, [])

    def test_setting_dimensions_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.dimensions = 3

    def test_add_wrong_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            Dataset(files=('x', 'y'))

    def test_default_variables_is_empty_tuple(self):
        self.assertEqual(self.ds.variables, [])

    def test_setting_variables_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.variables = 3

    def test_default_files_is_empty_tuple(self):
        self.assertEqual(self.ds.files, [])

    def test_setting_files_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.ds.files = 3

    def test_add_file(self):
        f = File('test.nc')
        ds = Dataset(files=(f,))
        self.assertIn(f, ds)

    def test_add_different_files_with_same_name_raises_value_error(self):
        f1 = File('test.nc')
        f2 = File('test.nc')
        with self.assertRaises(ValueError):
            Dataset(files=(f1, f2))

    def test_add_file_also_adds_variables_and_dimensions(self):
        d = Dimension('x')
        v = Variable('v', dimensions=(d,))
        f = File('test.nc', variables=(v,))
        ds = Dataset(files=(f,))
        self.assertIn(v, ds)
        self.assertIn(d, ds)


if __name__ == '__main__':
    unittest.main()
