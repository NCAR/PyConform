"""
Unit Tests for Definition Parser Recursive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparsing import recursions

import unittest


class Tests(unittest.TestCase):

    def test_var_expr_no_indices(self):
        token = recursions.expr.parseString('x')[0]
        self.assertEqual(token, recursions.VarType('x', []))

    def test_var_expr_int_indices(self):
        token = recursions.expr.parseString('x[ 1, 2]')[0]
        self.assertEqual(token, recursions.VarType('x', [1, 2]))

    def test_func_expr_no_arguments(self):
        token = recursions.expr.parseString('f()')[0]
        self.assertEqual(token, recursions.FuncType('f', []))

    def test_func_expr_pos_arguments(self):
        token = recursions.expr.parseString('f(3,4)')[0]
        self.assertEqual(token, recursions.FuncType('f', [3, 4]))

    def test_func_expr_kwd_arguments(self):
        token = recursions.expr.parseString('f(a=3,b=4)')[0]
        a = recursions.KwdType('a', 3)
        b = recursions.KwdType('b', 4)
        fobj = recursions.FuncType('f', [a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_pos_and_kwd_arguments(self):
        token = recursions.expr.parseString('f(1,2,a=3,b=4)')[0]
        a = recursions.KwdType('a', 3)
        b = recursions.KwdType('b', 4)
        fobj = recursions.FuncType('f', [1, 2, a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_with_variable_argument(self):
        token = recursions.expr.parseString('f(1,x[2:4, 6],a=3,b=4)')[0]
        vobj = recursions.VarType('x', [slice(2, 4), 6])
        a = recursions.KwdType('a', 3)
        b = recursions.KwdType('b', 4)
        fobj = recursions.FuncType('f', [1, vobj, a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_with_function_argument(self):
        token = recursions.expr.parseString('f(1,g(2,3),a=5,b=6.2)')[0]
        g = recursions.FuncType('g', [2, 3])
        a = recursions.KwdType('a', 5)
        b = recursions.KwdType('b', 6.2)
        f = recursions.FuncType('f', [1, g, a, b])
        self.assertEqual(token, f)

    def test_func_expr_with_function_keyword_argument(self):
        token = recursions.expr.parseString('f(1,"c",a=g(2,3),b=4)')[0]
        g = recursions.FuncType('g', [2, 3])
        a = recursions.KwdType('a', g)
        b = recursions.KwdType('b', 4)
        f = recursions.FuncType('f', [1, 'c', a, b])
        self.assertEqual(token, f)

    def test_math_expr_with_multiple_types(self):
        token = recursions.expr.parseString('4 + 5 * x[2:4]')[0]
        x = recursions.VarType('x', [slice(2, 4)])
        mulop = recursions.OpType('*', [5, x])
        addop = recursions.OpType('+', [4, mulop])
        self.assertEqual(token, addop)

    def test_math_expr_with_parentheses(self):
        token = recursions.expr.parseString('(4 + 5) * x[2:4]')[0]
        x = recursions.VarType('x', [slice(2, 4)])
        addop = recursions.OpType('+', [4, 5])
        mulop = recursions.OpType('*', [addop, x])
        self.assertEqual(token, mulop)

    def test_math_expr_within_function(self):
        string = 'f(4.6 * x[2:4],"f",d="c")'
        token = recursions.expr.parseString(string)[0]
        x = recursions.VarType('x', [slice(2, 4)])
        mulop = recursions.OpType('*', [4.6, x])
        d = recursions.KwdType('d', 'c')
        f = recursions.FuncType('f', [mulop, 'f', d])
        self.assertEqual(token, f)

    def test_math_expr_within_parenthesis_within_function(self):
        string = 'f( (3.0/4)*x[2:4]*(1 +y), a="f")'
        recursions.expr.setDebug(True)
        token = recursions.expr.parseString(string)[0]
        y = recursions.VarType('y', [])
        add1 = recursions.OpType('+', [1, y])
        x = recursions.VarType('x', [slice(2, 4)])
        mul1 = recursions.OpType('*', [x, add1])
        div1 = recursions.OpType('/', [3.0, 4])
        mul2 = recursions.OpType('*', [div1, mul1])
        a = recursions.KwdType('a', 'f')
        f = recursions.FuncType('f', [mul2, a])
        self.assertEqual(token, f)

    def test_math_expr_sum_functions(self):
        token = recursions.expr.parseString('f(4,5) + g(2,3)')[0]
        f = recursions.FuncType('f', [4, 5])
        g = recursions.FuncType('g', [2, 3])
        addop = recursions.OpType('+', [f, g])
        self.assertEqual(token, addop)

    def test_math_expr_sum_function_and_variable(self):
        token = recursions.expr.parseString('(f(4,(5+6)) + g[2,3])*5')[0]
        addop1 = recursions.OpType('+', [5, 6])
        f = recursions.FuncType('f', [4, addop1])
        g = recursions.VarType('g', [2, 3])
        addop = recursions.OpType('+', [f, g])
        mulop = recursions.OpType('*', [addop, 5])
        self.assertEqual(token, mulop)

    def test_math_expr_with_comparison(self):
        string = 'integrate( x[where(y > 0)], "i" )'
        token = recursions.expr.parseString(string)[0]
        y = recursions.VarType('y', [])
        y_gt_0 = recursions.OpType('>', [y, 0])
        where_y = recursions.FuncType('where', [y_gt_0])
        x = recursions.VarType('x', [where_y])
        integrate = recursions.FuncType('integrate', [x, 'i'])
        self.assertEqual(token, integrate)


if __name__ == "__main__":
    unittest.main()
