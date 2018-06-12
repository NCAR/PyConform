"""
Unit Tests for Variable Adapter

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.adapters.variableadapter import VariableAdapter
import unittest


class VariableAdapterTest(unittest.TestCase):

    def test_init(self):
        f = VariableAdapter()
        self.assertIsInstance(f, VariableAdapter)


if __name__ == '__main__':
    unittest.main()
