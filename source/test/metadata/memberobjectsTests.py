"""
Unit Tests for MemberObjects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata.memberobjects import MemberObject


class MemberObjectTests(unittest.TestCase):

    def test_create(self):
        m = MemberObject('name')
        self.assertIsInstance(m, MemberObject)
        self.assertEqual(m.name, 'name')

    def test_default_dataset_is_none(self):
        m = MemberObject('name')
        self.assertIsNone(m._dataset)

    def test_setting_dataset_to_non_dataset_raises_type_error(self):
        m = MemberObject('name')
        with self.assertRaises(TypeError):
            m._dataset = 4

    def test_setting_dataset_to_dataset_stores_dataset(self):
        m = MemberObject('name')
        from pyconform.metadata.datasets import Dataset
        m._dataset = Dataset()
        self.assertIsInstance(m._dataset, Dataset)


if __name__ == '__main__':
    unittest.main()
