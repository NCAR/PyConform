"""
Unit Tests for Variable Filters

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.filters.variablefilter import VariableFilter
import unittest


class VariableFiltersTest(unittest.TestCase):

    def test_init(self):
        f = VariableFilter()
        self.assertIsInstance(f, VariableFilter)


if __name__ == '__main__':
    unittest.main()
