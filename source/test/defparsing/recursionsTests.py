"""
Unit Tests for Definition Parser Recursive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparsing import recursions as rcr
from pyconform.defparsing import actions as act

import unittest


class Tests(unittest.TestCase):

    def test_lists_empty(self):
        token = rcr.expression.parseString('[]')[0]
        self.assertEqual(token, [])

    def test_lists_of_patterns(self):
        token = rcr.expression.parseString('[1, 2.3, "c", x2]')[0]
        self.assertEqual(token, [1, 2.3, 'c', act.VariableType('x2', None)])

    def test_lists_of_lists(self):
        token = rcr.expression.parseString('[1, 2.3, ["c", x2]]')[0]
        self.assertEqual(token, [1, 2.3, ['c', act.VariableType('x2', None)]])

    def test_function_no_arguments(self):
        token = rcr.expression.parseString('f()')[0]
        self.assertEqual(token, act.FunctionType('f', tuple(), {}))

    def test_function_pos_arguments(self):
        token = rcr.expression.parseString('f(3,4)')[0]
        self.assertEqual(token, act.FunctionType('f', (3, 4), {}))

    def test_function_kwd_arguments(self):
        token = rcr.expression.parseString('f(a=3,b=4)')[0]
        self.assertEqual(token, act.FunctionType(
            'f', tuple(), {'a': 3, 'b': 4}))

    def test_function_pos_and_kwd_arguments(self):
        token = rcr.expression.parseString('f(1,2,a=3,b=4)')[0]
        self.assertEqual(token, act.FunctionType(
            'f', (1, 2), {'a': 3, 'b': 4}))


if __name__ == "__main__":
    unittest.main()
