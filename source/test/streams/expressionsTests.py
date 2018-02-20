"""
Unit Tests for Definition Parser Recursive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.streams import expressions

import unittest


class ExpressionTests(unittest.TestCase):

    def test_uint_expr(self):
        token = expressions.uint_expr.parseString('142')[0]
        self.assertEqual(token, 142)

    def test_int_expr_positive(self):
        token = expressions.int_expr.parseString('142')[0]
        self.assertEqual(token, 142)

    def test_int_expr_negative(self):
        token = expressions.int_expr.parseString('-142')[0]
        self.assertEqual(token, -142)

    def test_ufloat_expr_with_decimal(self):
        token = expressions.ufloat_expr.parseString('1.2')[0]
        self.assertEqual(token, 1.2)

    def test_ufloat_expr_with_decimal_without_trailing_zero(self):
        token = expressions.ufloat_expr.parseString('1.')[0]
        self.assertEqual(token, 1.0)

    def test_ufloat_expr_without_decimal_and_positive_exponent(self):
        token = expressions.ufloat_expr.parseString('1e+4')[0]
        self.assertEqual(token, 10000.)

    def test_ufloat_expr_without_decimal_and_negative_exponent(self):
        token = expressions.ufloat_expr.parseString('1e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_ufloat_expr_with_decimal_and_positive_exponent(self):
        token = expressions.ufloat_expr.parseString('1.234e+4')[0]
        self.assertEqual(token, 12340.)

    def test_ufloat_expr_with_decimal_without_trailing_zero_and_negative_exponent(self):
        token = expressions.ufloat_expr.parseString('1.e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_float_expr_with_decimal_and_positive_exponent(self):
        token = expressions.float_expr.parseString('-1.234e+4')[0]
        self.assertEqual(token, -12340.)

    def test_str_expr_with_single_quotes(self):
        token = expressions.str_expr.parseString("'a b c'")[0]
        self.assertEqual(token, 'a b c')

    def test_str_expr_with_double_quotes(self):
        token = expressions.str_expr.parseString('"a b c"')[0]
        self.assertEqual(token, 'a b c')

    def test_name_expr_as_solo_underscore(self):
        token = expressions.name_expr.parseString('_')[0]
        self.assertEqual(token, '_')

    def test_name_expr_with_underscore_separation(self):
        token = expressions.name_expr.parseString('_a_b_c_')[0]
        self.assertEqual(token, '_a_b_c_')

    def test_slice_expr_empty(self):
        token = expressions.slice_expr.parseString(':')[0]
        self.assertEqual(token, slice(None))

    def test_slice_expr_start_only(self):
        token = expressions.slice_expr.parseString('1:')[0]
        self.assertEqual(token, slice(1, None))

    def test_slice_expr_stop_only(self):
        token = expressions.slice_expr.parseString(':-2')[0]
        self.assertEqual(token, slice(None, -2))

    def test_slice_expr_step_only(self):
        token = expressions.slice_expr.parseString('::-1')[0]
        self.assertEqual(token, slice(None, None, -1))

    def test_slice_expr_start_stop(self):
        token = expressions.slice_expr.parseString('-1 :  3')[0]
        self.assertEqual(token, slice(-1, 3))

    def test_slice_expr_start_stop_step(self):
        token = expressions.slice_expr.parseString('-1 :  3 : 8')[0]
        self.assertEqual(token, slice(-1, 3, 8))

    def test_var_expr_no_indices(self):
        token = expressions.expr.parseString('x')[0]
        self.assertEqual(token, expressions.VarType('x', []))

    def test_var_expr_int_indices(self):
        token = expressions.expr.parseString('x[ 1, 2]')[0]
        self.assertEqual(token, expressions.VarType('x', [1, 2]))

    def test_func_expr_no_arguments(self):
        token = expressions.expr.parseString('f()')[0]
        self.assertEqual(token, expressions.FuncType('f', []))

    def test_func_expr_pos_arguments(self):
        token = expressions.expr.parseString('f(3,4)')[0]
        self.assertEqual(token, expressions.FuncType('f', [3, 4]))

    def test_func_expr_kwd_arguments(self):
        token = expressions.expr.parseString('f(a=3,b=4)')[0]
        a = expressions.KwdType('a', 3)
        b = expressions.KwdType('b', 4)
        fobj = expressions.FuncType('f', [a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_pos_and_kwd_arguments(self):
        token = expressions.expr.parseString('f(1,2,a=3,b=4)')[0]
        a = expressions.KwdType('a', 3)
        b = expressions.KwdType('b', 4)
        fobj = expressions.FuncType('f', [1, 2, a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_with_variable_argument(self):
        token = expressions.expr.parseString('f(1,x[2:4, 6],a=3,b=4)')[0]
        vobj = expressions.VarType('x', [slice(2, 4), 6])
        a = expressions.KwdType('a', 3)
        b = expressions.KwdType('b', 4)
        fobj = expressions.FuncType('f', [1, vobj, a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_with_function_argument(self):
        token = expressions.expr.parseString('f(1,g(2,3),a=5,b=6.2)')[0]
        g = expressions.FuncType('g', [2, 3])
        a = expressions.KwdType('a', 5)
        b = expressions.KwdType('b', 6.2)
        f = expressions.FuncType('f', [1, g, a, b])
        self.assertEqual(token, f)

    def test_func_expr_with_function_keyword_argument(self):
        token = expressions.expr.parseString('f(1,"c",a=g(2,3),b=4)')[0]
        g = expressions.FuncType('g', [2, 3])
        a = expressions.KwdType('a', g)
        b = expressions.KwdType('b', 4)
        f = expressions.FuncType('f', [1, 'c', a, b])
        self.assertEqual(token, f)

    def test_math_expr_with_multiple_types(self):
        token = expressions.expr.parseString('4 + 5 * x[2:4]')[0]
        x = expressions.VarType('x', [slice(2, 4)])
        mulop = expressions.OpType('*', [5, x])
        addop = expressions.OpType('+', [4, mulop])
        self.assertEqual(token, addop)

    def test_math_expr_with_parentheses(self):
        token = expressions.expr.parseString('(4 + 5) * x[2:4]')[0]
        x = expressions.VarType('x', [slice(2, 4)])
        addop = expressions.OpType('+', [4, 5])
        mulop = expressions.OpType('*', [addop, x])
        self.assertEqual(token, mulop)

    def test_math_expr_within_function(self):
        string = 'f(4.6 * x[2:4],"f",d="c")'
        token = expressions.expr.parseString(string)[0]
        x = expressions.VarType('x', [slice(2, 4)])
        mulop = expressions.OpType('*', [4.6, x])
        d = expressions.KwdType('d', 'c')
        f = expressions.FuncType('f', [mulop, 'f', d])
        self.assertEqual(token, f)

    def test_math_expr_within_parenthesis_within_function(self):
        string = 'f( (3.0/4)*x[2:4]*(1 +y), a="f")'
        expressions.expr.setDebug(True)
        token = expressions.expr.parseString(string)[0]
        y = expressions.VarType('y', [])
        add1 = expressions.OpType('+', [1, y])
        x = expressions.VarType('x', [slice(2, 4)])
        mul1 = expressions.OpType('*', [x, add1])
        div1 = expressions.OpType('/', [3.0, 4])
        mul2 = expressions.OpType('*', [div1, mul1])
        a = expressions.KwdType('a', 'f')
        f = expressions.FuncType('f', [mul2, a])
        self.assertEqual(token, f)

    def test_math_expr_sum_functions(self):
        token = expressions.expr.parseString('f(4,5) + g(2,3)')[0]
        f = expressions.FuncType('f', [4, 5])
        g = expressions.FuncType('g', [2, 3])
        addop = expressions.OpType('+', [f, g])
        self.assertEqual(token, addop)

    def test_math_expr_sum_function_and_variable(self):
        token = expressions.expr.parseString('(f(4,(5+6)) + g[2,3])*5')[0]
        addop1 = expressions.OpType('+', [5, 6])
        f = expressions.FuncType('f', [4, addop1])
        g = expressions.VarType('g', [2, 3])
        addop = expressions.OpType('+', [f, g])
        mulop = expressions.OpType('*', [addop, 5])
        self.assertEqual(token, mulop)

    def test_math_expr_with_comparison(self):
        string = 'integrate( x[where(y > 0)], "i" )'
        token = expressions.expr.parseString(string)[0]
        y = expressions.VarType('y', [])
        y_gt_0 = expressions.OpType('>', [y, 0])
        where_y = expressions.FuncType('where', [y_gt_0])
        x = expressions.VarType('x', [where_y])
        integrate = expressions.FuncType('integrate', [x, 'i'])
        self.assertEqual(token, integrate)

    def test_parse_definition(self):
        definition = 'f(x[4:8:-1] > 4, a=y, c=["g", 3], b={"g": 4.8})'
        result = expressions.parse_definition(definition)
        x = expressions.VarType('x', [slice(4, 8, -1)])
        x_gt_4 = expressions.OpType('>', [x, 4])
        y = expressions.VarType('y', [])
        a = expressions.KwdType('a', y)
        c = expressions.KwdType('c', ["g", 3])
        b = expressions.KwdType('b', {'g': 4.8})
        f = expressions.FuncType('f', [x_gt_4, a, c, b])
        self.assertEqual(result, f)
        print result


if __name__ == "__main__":
    unittest.main()
