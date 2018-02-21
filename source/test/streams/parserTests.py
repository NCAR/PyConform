"""
Unit Tests for Definition Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.streams import parser

import unittest


class ParserTests(unittest.TestCase):

    def test_uint_expr(self):
        token = parser.uint_expr.parseString('142')[0]
        self.assertEqual(token, 142)

    def test_int_expr_positive(self):
        token = parser.int_expr.parseString('142')[0]
        self.assertEqual(token, 142)

    def test_int_expr_negative(self):
        token = parser.int_expr.parseString('-142')[0]
        self.assertEqual(token, -142)

    def test_ufloat_expr_with_decimal(self):
        token = parser.ufloat_expr.parseString('1.2')[0]
        self.assertEqual(token, 1.2)

    def test_ufloat_expr_with_decimal_without_trailing_zero(self):
        token = parser.ufloat_expr.parseString('1.')[0]
        self.assertEqual(token, 1.0)

    def test_ufloat_expr_without_decimal_and_positive_exponent(self):
        token = parser.ufloat_expr.parseString('1e+4')[0]
        self.assertEqual(token, 10000.)

    def test_ufloat_expr_without_decimal_and_negative_exponent(self):
        token = parser.ufloat_expr.parseString('1e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_ufloat_expr_with_decimal_and_positive_exponent(self):
        token = parser.ufloat_expr.parseString('1.234e+4')[0]
        self.assertEqual(token, 12340.)

    def test_ufloat_expr_with_decimal_without_trailing_zero_and_negative_exponent(self):
        token = parser.ufloat_expr.parseString('1.e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_float_expr_with_decimal_and_positive_exponent(self):
        token = parser.float_expr.parseString('-1.234e+4')[0]
        self.assertEqual(token, -12340.)

    def test_str_expr_with_single_quotes(self):
        token = parser.str_expr.parseString("'a b c'")[0]
        self.assertEqual(token, 'a b c')

    def test_str_expr_with_double_quotes(self):
        token = parser.str_expr.parseString('"a b c"')[0]
        self.assertEqual(token, 'a b c')

    def test_name_expr_as_solo_underscore(self):
        token = parser.name_expr.parseString('_')[0]
        self.assertEqual(token, '_')

    def test_name_expr_with_underscore_separation(self):
        token = parser.name_expr.parseString('_a_b_c_')[0]
        self.assertEqual(token, '_a_b_c_')

    def test_slice_expr_empty(self):
        token = parser.slice_expr.parseString(':')[0]
        self.assertEqual(token, slice(None))

    def test_slice_expr_start_only(self):
        token = parser.slice_expr.parseString('1:')[0]
        self.assertEqual(token, slice(1, None))

    def test_slice_expr_stop_only(self):
        token = parser.slice_expr.parseString(':-2')[0]
        self.assertEqual(token, slice(None, -2))

    def test_slice_expr_step_only(self):
        token = parser.slice_expr.parseString('::-1')[0]
        self.assertEqual(token, slice(None, None, -1))

    def test_slice_expr_start_stop(self):
        token = parser.slice_expr.parseString('-1 :  3')[0]
        self.assertEqual(token, slice(-1, 3))

    def test_slice_expr_start_stop_step(self):
        token = parser.slice_expr.parseString('-1 :  3 : 8')[0]
        self.assertEqual(token, slice(-1, 3, 8))

    def test_var_expr_no_indices(self):
        token = parser.expr.parseString('x')[0]
        self.assertEqual(token, parser.VarType('x', []))

    def test_var_expr_int_indices(self):
        token = parser.expr.parseString('x[ 1, 2]')[0]
        self.assertEqual(token, parser.VarType('x', [1, 2]))

    def test_func_expr_no_arguments(self):
        token = parser.expr.parseString('f()')[0]
        self.assertEqual(token, parser.FuncType('f', []))

    def test_func_expr_pos_arguments(self):
        token = parser.expr.parseString('f(3,4)')[0]
        self.assertEqual(token, parser.FuncType('f', [3, 4]))

    def test_func_expr_kwd_arguments(self):
        token = parser.expr.parseString('f(a=3,b=4)')[0]
        a = parser.KwdType('a', 3)
        b = parser.KwdType('b', 4)
        fobj = parser.FuncType('f', [a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_pos_and_kwd_arguments(self):
        token = parser.expr.parseString('f(1,2,a=3,b=4)')[0]
        a = parser.KwdType('a', 3)
        b = parser.KwdType('b', 4)
        fobj = parser.FuncType('f', [1, 2, a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_with_variable_argument(self):
        token = parser.expr.parseString('f(1,x[2:4, 6],a=3,b=4)')[0]
        vobj = parser.VarType('x', [slice(2, 4), 6])
        a = parser.KwdType('a', 3)
        b = parser.KwdType('b', 4)
        fobj = parser.FuncType('f', [1, vobj, a, b])
        self.assertEqual(token, fobj)

    def test_func_expr_with_function_argument(self):
        token = parser.expr.parseString('f(1,g(2,3),a=5,b=6.2)')[0]
        g = parser.FuncType('g', [2, 3])
        a = parser.KwdType('a', 5)
        b = parser.KwdType('b', 6.2)
        f = parser.FuncType('f', [1, g, a, b])
        self.assertEqual(token, f)

    def test_func_expr_with_function_keyword_argument(self):
        token = parser.expr.parseString('f(1,"c",a=g(2,3),b=4)')[0]
        g = parser.FuncType('g', [2, 3])
        a = parser.KwdType('a', g)
        b = parser.KwdType('b', 4)
        f = parser.FuncType('f', [1, 'c', a, b])
        self.assertEqual(token, f)

    def test_math_expr_with_multiple_types(self):
        token = parser.expr.parseString('4 + 5 * x[2:4]')[0]
        x = parser.VarType('x', [slice(2, 4)])
        mulop = parser.OpType('*', [5, x])
        addop = parser.OpType('+', [4, mulop])
        self.assertEqual(token, addop)

    def test_math_expr_with_parentheses(self):
        token = parser.expr.parseString('(4 + 5) * x[2:4]')[0]
        x = parser.VarType('x', [slice(2, 4)])
        addop = parser.OpType('+', [4, 5])
        mulop = parser.OpType('*', [addop, x])
        self.assertEqual(token, mulop)

    def test_math_expr_within_function(self):
        string = 'f(4.6 * x[2:4],"f",d="c")'
        token = parser.expr.parseString(string)[0]
        x = parser.VarType('x', [slice(2, 4)])
        mulop = parser.OpType('*', [4.6, x])
        d = parser.KwdType('d', 'c')
        f = parser.FuncType('f', [mulop, 'f', d])
        self.assertEqual(token, f)

    def test_math_expr_within_parenthesis_within_function(self):
        string = 'f( (3.0/4)*x[2:4]*(1 +y), a="f")'
        parser.expr.setDebug(True)
        token = parser.expr.parseString(string)[0]
        y = parser.VarType('y', [])
        add1 = parser.OpType('+', [1, y])
        x = parser.VarType('x', [slice(2, 4)])
        mul1 = parser.OpType('*', [x, add1])
        div1 = parser.OpType('/', [3.0, 4])
        mul2 = parser.OpType('*', [div1, mul1])
        a = parser.KwdType('a', 'f')
        f = parser.FuncType('f', [mul2, a])
        self.assertEqual(token, f)

    def test_math_expr_sum_functions(self):
        token = parser.expr.parseString('f(4,5) + g(2,3)')[0]
        f = parser.FuncType('f', [4, 5])
        g = parser.FuncType('g', [2, 3])
        addop = parser.OpType('+', [f, g])
        self.assertEqual(token, addop)

    def test_math_expr_sum_function_and_variable(self):
        token = parser.expr.parseString('(f(4,(5+6)) + g[2,3])*5')[0]
        addop1 = parser.OpType('+', [5, 6])
        f = parser.FuncType('f', [4, addop1])
        g = parser.VarType('g', [2, 3])
        addop = parser.OpType('+', [f, g])
        mulop = parser.OpType('*', [addop, 5])
        self.assertEqual(token, mulop)

    def test_math_expr_with_comparison(self):
        string = 'integrate( x[where(y > 0)], "i" )'
        token = parser.expr.parseString(string)[0]
        y = parser.VarType('y', [])
        y_gt_0 = parser.OpType('>', [y, 0])
        where_y = parser.FuncType('where', [y_gt_0])
        x = parser.VarType('x', [where_y])
        integrate = parser.FuncType('integrate', [x, 'i'])
        self.assertEqual(token, integrate)

    def test_parse_definition(self):
        definition = 'f(x[4:8:-1] > 4, a=y, c=["g", 3], b={"g": 4.8})'
        result = parser.parse_definition(definition)
        x = parser.VarType('x', [slice(4, 8, -1)])
        x_gt_4 = parser.OpType('>', [x, 4])
        y = parser.VarType('y', [])
        a = parser.KwdType('a', y)
        c = parser.KwdType('c', ["g", 3])
        b = parser.KwdType('b', {'g': 4.8})
        f = parser.FuncType('f', [x_gt_4, a, c, b])
        self.assertEqual(result, f)
        print result


if __name__ == "__main__":
    unittest.main()
