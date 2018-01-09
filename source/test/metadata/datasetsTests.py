"""
Unit Tests for Dataset Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import Dataset


class DatasetTests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()

    def test_create(self):
        self.assertIsInstance(self.ds, Dataset)

    def test_default_dimensions_is_empty_dict(self):
        self.assertEqual(self.ds.dimensions, {})

    def test_default_variables_is_empty_dict(self):
        self.assertEqual(self.ds.variables, {})

    def test_default_files_is_empty_dict(self):
        self.assertEqual(self.ds.files, {})

    def test_get_dimension(self):
        self.ds.dimensions['x'] = 4
        self.assertEqual(self.ds.get_dimension('x'), 4)

    def test_get_dimension_not_found_raises_key_error(self):
        self.assertRaises(KeyError, self.ds.get_dimension, 'x')

    def test_get_variable(self):
        self.ds.variables['v'] = 9
        self.assertEqual(self.ds.get_variable('v'), 9)

    def test_get_variable_not_found_raises_key_error(self):
        self.assertRaises(KeyError, self.ds.get_variable, 'x')

    def test_get_file(self):
        self.ds.files['test.nc'] = 'abcdefg'
        self.assertEqual(self.ds.get_file('test.nc'), 'abcdefg')

    def test_get_file_not_found_raises_key_error(self):
        self.assertRaises(KeyError, self.ds.get_file, 'x')


if __name__ == '__main__':
    unittest.main()
