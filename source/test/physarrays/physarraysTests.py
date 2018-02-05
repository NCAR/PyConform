"""
Unit Tests for PhysArray Class and Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarrays import PhysArray

import xarray as xr
import unittest


class PhysArrayTests(unittest.TestCase):

    def test_create(self):
        x = PhysArray(1.0, name='x')
        self.assertIsInstance(x, PhysArray)
        self.assertIsInstance(x, xr.DataArray)


if __name__ == "__main__":
    unittest.main()
