"""
Unit Tests for NamedObjects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata.namedobjects import NamedObject


class NamedObjectTests(unittest.TestCase):

    def setUp(self):
        self.no = NamedObject('name')

    def test_create(self):
        self.assertIsInstance(self.no, NamedObject)

    def test_name(self):
        self.assertEqual(self.no.name, 'name')

    def test_default_namespace_is_none(self):
        self.assertEqual(self.no.namespace, None)

    def test_namespace(self):
        no = NamedObject('name', namespace='a')
        self.assertEqual(no.namespace, 'a')

    def test_objects_with_same_key_are_same(self):
        no = NamedObject('name')
        self.assertIs(self.no, no)


if __name__ == '__main__':
    unittest.main()
