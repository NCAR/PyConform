"""
Unit Tests for Definition Parser Recursive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparsing import recursions as rcr
from pyconform.defparsing import actions as act

import unittest


class Tests(unittest.TestCase):

    def test_function_no_arguments(self):
        token = rcr.expression.parseString('f()')[0]
        self.assertEqual(token, act.FunctionType('f', tuple(), {}))

    def test_function_pos_arguments(self):
        token = rcr.expression.parseString('f(3,4)')[0]
        self.assertEqual(token, act.FunctionType('f', (3, 4), {}))

    def test_function_kwd_arguments(self):
        token = rcr.expression.parseString('f(a=3,b=4)')[0]
        fobj = act.FunctionType('f', tuple(), {'a': 3, 'b': 4})
        self.assertEqual(token, fobj)

    def test_function_pos_and_kwd_arguments(self):
        token = rcr.expression.parseString('f(1,2,a=3,b=4)')[0]
        fobj = act.FunctionType('f', (1, 2), {'a': 3, 'b': 4})
        self.assertEqual(token, fobj)

    def test_function_with_variable_argument(self):
        token = rcr.expression.parseString('f(1,x[2:4, 6],a=3,b=4)')[0]
        vobj = act.VariableType('x', [slice(2, 4), 6])
        fobj = act.FunctionType('f', (1, vobj), {'a': 3, 'b': 4})
        self.assertEqual(token, fobj)

    def test_function_with_function_argument(self):
        token = rcr.expression.parseString('f(1,g(2,3),a=5,b=6.2)')[0]
        g = act.FunctionType('g', (2, 3), {})
        f = act.FunctionType('f', (1, g), {'a': 5, 'b': 6.2})
        self.assertEqual(token, f)

    def test_function_with_function_keyword_argument(self):
        token = rcr.expression.parseString('f(1,"c",a=g(2,3),b=4)')[0]
        g = act.FunctionType('g', (2, 3), {})
        f = act.FunctionType('f', (1, 'c'), {'a': g, 'b': 4})
        self.assertEqual(token, f)

    def test_mathematics_with_multiple_types(self):
        token = rcr.expression.parseString('4 + 5 * x[2:4]')[0]
        x = act.VariableType('x', [slice(2, 4)])
        mulop = act.BinaryOpType('*', 5, x)
        addop = act.BinaryOpType('+', 4, mulop)
        self.assertEqual(token, addop)

    def test_mathematics_with_parentheses(self):
        token = rcr.expression.parseString('(4 + 5) * x[2:4]')[0]
        x = act.VariableType('x', [slice(2, 4)])
        addop = act.BinaryOpType('+', 4, 5)
        mulop = act.BinaryOpType('*', addop, x)
        self.assertEqual(token, mulop)

    def test_mathematics_with_parentheses_and_functions(self):
        token = rcr.expression.parseString('f((4.5 + +5)*x[2:4],"f",d="c")')[0]
        x = act.VariableType('x', [slice(2, 4)])
        addop = act.BinaryOpType('+', 4.5, 5)
        mulop = act.BinaryOpType('*', addop, x)
        f = act.FunctionType('f', (mulop, 'f'), {'d': 'c'})
        self.assertEqual(token, f)


if __name__ == "__main__":
    unittest.main()
