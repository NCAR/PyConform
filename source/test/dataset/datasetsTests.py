"""
Unit Tests for Input Dataset Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.dataset import Dataset

import unittest


class DatasetTests(unittest.TestCase):

    def test_create(self):
        ds = Dataset()
        self.assertIsInstance(ds, Dataset)
    
    def test_


if __name__ == '__main__':
    unittest.main()
