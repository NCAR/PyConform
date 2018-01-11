"""
Unit Tests for InputDatasets

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from pyconform.metadata import InputDataset


class InputDatasetTest(unittest.TestCase):

    def test_create(self):
        filenames = ('test.nc',)
        ids = InputDataset(filenames)
        self.assertIsInstance(ids, InputDataset)


if __name__ == '__main__':
    unittest.main()
