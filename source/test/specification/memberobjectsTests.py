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
        self.ds = Specification()
        self.m = MemberObject('name', dataset=self.ds)

    def test_create(self):
        self.assertIsInstance(self.m, MemberObject)

    def test_name_is_stored(self):
        self.assertEqual(self.m.name, 'name')

    def test_setting_dataset_to_dataset_stores_dataset(self):
        self.assertIs(self.m.dataset, self.ds)


if __name__ == '__main__':
    unittest.main()
