"""
Unit Tests for IDL Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest
import numpy as np

from pyconform.modules.idl import deriv, spl_init, spl_interp, int_tabulated


class Tests(unittest.TestCase):

    def test_deriv_list_no_y(self):
        x = [1.2345, 2.34567, 3.45678, 4.56789, 5.678901]
        actual = deriv(x)
        expected = [1.11120, 1.11114, 1.11111, 1.11106, 1.11096]
        np.testing.assert_array_almost_equal(actual, expected, 6)

    def test_deriv_list(self):
        x = [2., 5., 7., 3., 4.]
        y = [3., 5., 4., 7., 8.]
        actual = deriv(x, y)
        expected = [1.3666666, -0.033333302, -0.25000000, 1.5833340, 0.41666698]
        np.testing.assert_array_almost_equal(actual, expected, 6)

    def test_deriv_array(self):
        x = np.array([2., 5., 7., 3., 4.])
        y = np.array([3., 5., 4., 7., 8.])
        actual = deriv(x, y)
        expected = np.array([1.3666666, -0.033333302, -0.25000000, 1.5833340, 0.41666698])
        np.testing.assert_array_almost_equal(actual, expected, 6)

    def test_spl_init_array(self):
        x = np.array([2., 5., 7., 3., 4.])
        y = np.array([3., 5., 4., 7., 8.])
        actual = spl_init(x, y)
        expected = np.array([0.0000000, -1.5192308, 4.0961542, -4.4807696, 0.0000000])
        np.testing.assert_array_almost_equal(actual, expected, 6)

    def test_spl_interp_array(self):
        x = np.array([2., 5., 7., 8., 13.])
        y = np.array([3., 5., 4., 7., 8.])
        xi = np.array([3., 6., 7.5, 9.])
        actual = spl_interp(x, y, spl_init(x, y), xi)
        expected = np.array([4.3612623, 3.8121600, 5.3403325, 9.3114195])
        np.testing.assert_array_almost_equal(actual, expected, 6)

    def test_int_tabulated_array(self):
        x = np.array([2., 5., 7., 8., 13.])
        y = np.array([3., 5., 4., 7., 8.])
        actual = int_tabulated(x, y)
        expected = 77.627388
        np.testing.assert_array_almost_equal(actual, expected, 5)


if __name__ == "__main__":
    unittest.main()
