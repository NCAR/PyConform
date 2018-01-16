"""
Unit Tests

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import InputDataset


class Tests(unittest.TestCase):

    def test_create_empty(self):
        ids = InputDataset()
        self.assertIsInstance(ids, InputDataset)

    def test_create_from_single_file(self):
        ids = InputDataset('test1.nc')
        self.assertIsInstance(ids, InputDataset)


if __name__ == "__main__":
    unittest.main()
