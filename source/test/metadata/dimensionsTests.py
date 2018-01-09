"""
Unit Tests for Dimension Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import Dimension


class DimensionTests(unittest.TestCase):

    def setUp(self):
        self.d = Dimension('x')

    def test_create(self):
        self.assertIsInstance(self.d, Dimension)

    def test_default_size_is_none(self):
        self.assertEqual(self.d.size, None)

    def test_default_is_unlimited_is_false(self):
        self.assertEqual(self.d.is_unlimited, False)


if __name__ == '__main__':
    unittest.main()
