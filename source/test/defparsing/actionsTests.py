"""
Unit Tests for Parse Actions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import ParseResults
from pyconform.defparsing import actions

import unittest


class ActionTests(unittest.TestCase):

    def test_integer_action(self):
        result = actions.integer_action(['1'])
        self.assertEqual(result, 1)

    def test_float_action_on_int(self):
        result = actions.float_action(['1.0'])
        self.assertEqual(result, 1.0)

    def test_float_action_on_exp(self):
        result = actions.float_action(['1e5'])
        self.assertEqual(result, 1e5)

    def test_variable_action_on_solo_symbol(self):
        result = actions.variable_action(['x'])
        self.assertEqual(result.name, 'x')
        self.assertEqual(result.indices, None)

    def test_variable_action_with_1D_slice(self):
        result = actions.variable_action([['x', [slice(1, 5)]]])
        self.assertEqual(result.name, 'x')
        self.assertEqual(result.indices, [slice(1, 5)])

    def test_variable_action_with_2D_slice(self):
        data = [['x', [slice(1, 5), 4]]]
        result = actions.variable_action(data)
        self.assertEqual(result.name, 'x')
        self.assertEqual(result.indices, [slice(1, 5), 4])

    def test_list_action(self):
        data = ParseResults([1, 2, 3, 4])
        result = actions.list_action(data)
        self.assertEqual(result, [1, 2, 3, 4])

    def test_list_action_with_nesting(self):
        data = ParseResults([1, ParseResults([2, 3]), 4])
        result = actions.list_action(data)
        self.assertEqual(result, [1, [2, 3], 4])


if __name__ == "__main__":
    unittest.main()
