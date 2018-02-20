"""
Unit Tests for NamedObjects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.specification.namedobjects import NamedObject


class NamedObjectTests(unittest.TestCase):

    def setUp(self):
        self.no = NamedObject('name')

    def test_create(self):
        self.assertIsInstance(self.no, NamedObject)

    def test_name(self):
        self.assertEqual(self.no.name, 'name')


if __name__ == '__main__':
    unittest.main()
