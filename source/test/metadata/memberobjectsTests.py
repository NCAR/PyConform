"""
Unit Tests

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata.memberobjects import MemberObject


class Tests(unittest.TestCase):

    def test_create(self):
        m = MemberObject('x')
        self.assertIsInstance(m, MemberObject)

    def test_dataset_property(self):
        m = MemberObject('x')
        m._dataset = 3
        self.assertEqual(m.dataset, 3)


if __name__ == "__main__":
    unittest.main()
