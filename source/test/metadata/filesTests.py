"""
Unit Tests for File Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import File


class FileTests(unittest.TestCase):

    def setUp(self):
        self.f = File('test.nc')

    def test_create(self):
        self.assertIsInstance(self.f, File)

    def test_name(self):
        self.assertEqual(self.f.name, 'test.nc')

    def test_default_attributes_is_none(self):
        self.assertEqual(self.f.attributes, {})

    def test_default_deflate_is_1(self):
        self.assertEqual(self.f.deflate, 1)


if __name__ == '__main__':
    unittest.main()
