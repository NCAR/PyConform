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
        data = ParseResults([['x']])
        result = actions.variable_action(data)
        self.assertEqual(result.name, 'x')
        self.assertEqual(result.indices, None)

    def test_variable_action_with_1D_slice(self):
        data = ParseResults([['x', slice(1, 5)]])
        result = actions.variable_action(data)
        self.assertEqual(result.name, 'x')
        self.assertEqual(result.indices, [slice(1, 5)])

    def test_variable_action_with_2D_slice(self):
        data = ParseResults([['x', slice(1, 5), 4]])
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

    def test_keyword_action(self):
        data = ParseResults([['a', 4.5]])
        result = actions.keyword_action(data)
        self.assertEqual(result.key, 'a')
        self.assertEqual(result.value, 4.5)

    def test_function_action(self):
        data = ParseResults([['f']])
        result = actions.function_action(data)
        self.assertEqual(result.name, 'f')
        self.assertEqual(result.arguments, tuple())
        self.assertEqual(result.keywords, {})

    def test_function_action_with_arguments(self):
        data = ParseResults([['f', 2.3, 4]])
        result = actions.function_action(data)
        self.assertEqual(result.name, 'f')
        self.assertEqual(result.arguments, (2.3, 4))
        self.assertEqual(result.keywords, {})

    def test_unary_op_action_with_plus_sign(self):
        data = ParseResults([['+', 5]])
        result = actions.unary_op_action(data)
        self.assertEqual(result, 5)

    def test_unary_op_action_with_minus_sign(self):
        data = ParseResults([['-', 5]])
        result = actions.unary_op_action(data)
        exp = actions.UnaryOpType('-', 5)
        self.assertEqual(result, exp)

    def test_binary_op_action(self):
        data = ParseResults([[3, '+', 5]])
        result = actions.binary_op_action(data)
        exp = actions.BinaryOpType('+', 3, 5)
        self.assertEqual(result, exp)


if __name__ == "__main__":
    unittest.main()
