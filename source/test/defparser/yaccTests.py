"""
Unit Tests for Yacc Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparser import yacc

import unittest


def yacc_parse(s):
    return yacc.yacc.parse(s)  # @UndefinedVariable


class YaccTests(unittest.TestCase):

    def test_string_1(self):
        p = yacc_parse("'1 b 4'")
        self.assertEqual(p, '1 b 4')

    def test_string_2(self):
        p = yacc_parse('"1 b 4"')
        self.assertEqual(p, '1 b 4')

    def test_int(self):
        p = yacc_parse('143')
        self.assertEqual(p, 143)

    def test_int_positive(self):
        p = yacc_parse('+143')
        self.assertEqual(p, 143)

    def test_int_negative(self):
        p = yacc_parse('-143')
        self.assertEqual(p, -143)

    def test_float(self):
        p = yacc_parse('12.34')
        self.assertEqual(p, 12.34)

    def test_variable_name_only(self):
        p = yacc_parse('x')
        self.assertEqual(p, yacc.VarType('x', []))

    def test_variable_positive(self):
        p = yacc_parse('+x')
        self.assertEqual(p, yacc.VarType('x', []))

    def test_variable_negative(self):
        p = yacc_parse('-x')
        self.assertEqual(p, yacc.OpType('-', [yacc.VarType('x', [])]))

    def test_variable_integer_index(self):
        p = yacc_parse('x[2]')
        self.assertEqual(p, yacc.VarType('x', [2]))

    def test_variable_negative_integer_index(self):
        p = yacc_parse('x[-2]')
        self.assertEqual(p, yacc.VarType('x', [-2]))

    def test_variable_positive_integer_index(self):
        p = yacc_parse('x[+2]')
        self.assertEqual(p, yacc.VarType('x', [2]))

    def test_variable_integer_indices(self):
        p = yacc_parse('xyz[ 2 , -3 ,4]')
        self.assertEqual(p, yacc.VarType('xyz', [2, -3, 4]))

    def test_variable_slice(self):
        p = yacc_parse('x[2:-3:4]')
        self.assertEqual(p, yacc.VarType('x', [slice(2, -3, 4)]))

    def test_variable_slice_index(self):
        p = yacc_parse('x[2:-3:4, 7]')
        self.assertEqual(p, yacc.VarType('x', [slice(2, -3, 4), 7]))

    def test_variable_slice_none_1(self):
        p = yacc_parse('x[:-3:4]')
        self.assertEqual(p, yacc.VarType('x', [slice(None, -3, 4)]))

    def test_variable_slice_none_2(self):
        p = yacc_parse('x[1::4]')
        self.assertEqual(p, yacc.VarType('x', [slice(1, None, 4)]))

    def test_variable_slice_none_3(self):
        p = yacc_parse('x[1:4]')
        self.assertEqual(p, yacc.VarType('x', [slice(1, 4)]))

    def test_function_no_args(self):
        p = yacc_parse('f()')
        self.assertEqual(p, yacc.FuncType('f', [], {}))

    def test_function_negative(self):
        p = yacc_parse('-f()')
        self.assertEqual(p, yacc.OpType('-', [yacc.FuncType('f', [], {})]))

    def test_function_one_arg(self):
        p = yacc_parse('f(1)')
        self.assertEqual(p, yacc.FuncType('f', [1], {}))

    def test_function_two_arg(self):
        p = yacc_parse('f(1, 2)')
        self.assertEqual(p, yacc.FuncType('f', [1, 2], {}))

    def test_function_one_kwd(self):
        p = yacc_parse('f(x=4)')
        self.assertEqual(p, yacc.FuncType('f', [], {'x': 4}))

    def test_function_one_arg_one_kwd(self):
        p = yacc_parse('f(1, a = 4)')
        self.assertEqual(p, yacc.FuncType('f', [1], {'a': 4}))

    def test_function_two_arg_two_kwd(self):
        p = yacc_parse('f(1, 2, a = 4, b=-8)')
        self.assertEqual(p, yacc.FuncType('f', [1, 2], {'a': 4, 'b': -8}))

    def test_add_numbers(self):
        p = yacc_parse('1 + 3.5')
        self.assertEqual(p, 4.5)

    def test_add_number_and_var(self):
        p = yacc_parse('1 + x')
        self.assertEqual(p, yacc.OpType('+', [1, yacc.VarType('x', [])]))

    def test_add_func_and_var(self):
        p = yacc_parse('f(1,2) + x')
        f = yacc.FuncType('f', [1, 2], {})
        x = yacc.VarType('x', [])
        self.assertEqual(p, yacc.OpType('+', [f, x]))

    def test_sub_numbers(self):
        p = yacc_parse('1 - 3.5')
        self.assertEqual(p, -2.5)

    def test_mul_numbers(self):
        p = yacc_parse('2 * 3.5')
        self.assertEqual(p, 7.0)

    def test_div_numbers(self):
        p = yacc_parse('2 / 3.5')
        self.assertEqual(p, 4 / 7.0)

    def test_pow_numbers(self):
        p = yacc_parse('2 ** 3.5')
        self.assertEqual(p, 2**3.5)

    def test_precidence(self):
        p = yacc_parse('1 + 5.0/2 ** 3 - 2*3/2.0')
        self.assertEqual(p, -2 + 5.0 / 8)


if __name__ == '__main__':
    unittest.main()
