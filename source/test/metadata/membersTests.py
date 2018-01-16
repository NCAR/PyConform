"""
Unit Tests

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata.members import MemberObject
from pyconform.metadata.datasets import Dataset


class Tests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()
        self.m = MemberObject('x', dataset=self.ds)

    def test_create_without_dataset_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            MemberObject('x')

    def test_create(self):
        self.assertIsInstance(self.m, MemberObject)

    def test_dataset_property(self):
        self.assertIs(self.m.dataset, self.ds)


if __name__ == "__main__":
    unittest.main()
