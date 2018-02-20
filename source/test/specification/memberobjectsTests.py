"""
Unit Tests for MemberObjects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.specification.memberobjects import MemberObject
from pyconform.specification import Specification


class MemberObjectTests(unittest.TestCase):

    def setUp(self):
        self.spec = Specification()
        self.m = MemberObject('name', specification=self.spec)

    def test_create(self):
        self.assertIsInstance(self.m, MemberObject)

    def test_name_is_stored(self):
        self.assertEqual(self.m.name, 'name')

    def test_setting_specification_to_specification_stores_specification(self):
        self.assertIs(self.m.specification, self.spec)


if __name__ == '__main__':
    unittest.main()
