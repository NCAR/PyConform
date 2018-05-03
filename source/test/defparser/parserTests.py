"""
Unit Tests for Lex/Yacc-based Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparser.parser import Parser, OpType, VarType, FuncType

import unittest
import numpy as np
from pip._vendor.distlib._backport.tarfile import S_IFREG


class ParserTests(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def test_init(self):
        self.assertIsInstance(self.parser, Parser)

    def test_int(self):
        p = self.parser.parse_definition('143')
        self.assertEqual(p, 143)

    def test_int_positive(self):
        p = self.parser.parse_definition('+143')
        self.assertEqual(p, 143)

    def test_int_negative(self):
        p = self.parser.parse_definition('-143')
        self.assertEqual(p, -143)

    def test_float(self):
        p = self.parser.parse_definition('12.34')
        self.assertEqual(p, 12.34)

    def test_variable_name_only(self):
        p = self.parser.parse_definition('x')
        self.assertEqual(p, VarType('x', []))

    def test_variable_time(self):
        p = self.parser.parse_definition('time')
        self.assertEqual(p, VarType('time', []))

    def test_variable_positive(self):
        p = self.parser.parse_definition('+x')
        self.assertEqual(p, VarType('x', []))

    def test_variable_negative(self):
        p = self.parser.parse_definition('-x')
        self.assertEqual(p, OpType('-', [VarType('x', [])]))

    def test_variable_integer_index(self):
        p = self.parser.parse_definition('x[2]')
        self.assertEqual(p, VarType('x', [2]))

    def test_variable_negative_integer_index(self):
        p = self.parser.parse_definition('x[-2]')
        self.assertEqual(p, VarType('x', [-2]))

    def test_variable_positive_integer_index(self):
        p = self.parser.parse_definition('x[+2]')
        self.assertEqual(p, VarType('x', [2]))

    def test_variable_integer_indices(self):
        p = self.parser.parse_definition('xyz[ 2 , -3 ,4]')
        self.assertEqual(p, VarType('xyz', [2, -3, 4]))

    def test_variable_slice(self):
        p = self.parser.parse_definition('x[2:-3:4]')
        self.assertEqual(p, VarType('x', [slice(2, -3, 4)]))

    def test_variable_slice_index(self):
        p = self.parser.parse_definition('x[2:-3:4, 7]')
        self.assertEqual(p, VarType('x', [slice(2, -3, 4), 7]))

    def test_variable_slice_none_1(self):
        p = self.parser.parse_definition('x[:-3:4]')
        self.assertEqual(p, VarType('x', [slice(None, -3, 4)]))

    def test_variable_slice_none_2(self):
        p = self.parser.parse_definition('x[1::4]')
        self.assertEqual(p, VarType('x', [slice(1, None, 4)]))

    def test_variable_slice_none_3(self):
        p = self.parser.parse_definition('x[1:4]')
        self.assertEqual(p, VarType('x', [slice(1, 4)]))

    def test_function_no_args(self):
        p = self.parser.parse_definition('f()')
        self.assertEqual(p, FuncType('f', [], {}))

    def test_function_negative(self):
        p = self.parser.parse_definition('-f()')
        self.assertEqual(p, OpType('-', [FuncType('f', [], {})]))

    def test_function_one_arg(self):
        p = self.parser.parse_definition('f(1)')
        self.assertEqual(p, FuncType('f', [1], {}))

    def test_function_str1_arg(self):
        p = self.parser.parse_definition('f("1")')
        self.assertEqual(p, FuncType('f', ['1'], {}))

    def test_function_str2_arg(self):
        p = self.parser.parse_definition("f('1')")
        self.assertEqual(p, FuncType('f', ['1'], {}))

    def test_function_two_arg(self):
        p = self.parser.parse_definition('f(1, 2)')
        self.assertEqual(p, FuncType('f', [1, 2], {}))

    def test_function_one_kwd(self):
        p = self.parser.parse_definition('f(x=4)')
        self.assertEqual(p, FuncType('f', [], {'x': 4}))

    def test_function_one_arg_one_kwd(self):
        p = self.parser.parse_definition('f(1, a = 4)')
        self.assertEqual(p, FuncType('f', [1], {'a': 4}))

    def test_function_two_arg_two_kwd(self):
        p = self.parser.parse_definition('f(1, 2, a = 4, b=-8)')
        self.assertEqual(p, FuncType('f', [1, 2], {'a': 4, 'b': -8}))

    def test_add_numbers(self):
        p = self.parser.parse_definition('1 + 3.5')
        self.assertEqual(p, 4.5)

    def test_add_number_and_var(self):
        p = self.parser.parse_definition('1 + x')
        self.assertEqual(p, OpType('+', [1, VarType('x', [])]))

    def test_add_func_and_var(self):
        p = self.parser.parse_definition('f(1,2) + x')
        f = FuncType('f', [1, 2], {})
        x = VarType('x', [])
        self.assertEqual(p, OpType('+', [f, x]))

    def test_sub_numbers(self):
        p = self.parser.parse_definition('1 - 3.5')
        self.assertEqual(p, -2.5)

    def test_mul_numbers(self):
        p = self.parser.parse_definition('2 * 3.5')
        self.assertEqual(p, 7.0)

    def test_div_numbers(self):
        p = self.parser.parse_definition('2 / 3.5')
        self.assertEqual(p, 4 / 7.0)

    def test_pow_numbers(self):
        p = self.parser.parse_definition('2 ** 3.5')
        self.assertEqual(p, 2**3.5)

    def test_precedence(self):
        p = self.parser.parse_definition(
            '6 + -5.0/2 ** 3 - 2*3/2.0 + -(2**2) + (2*2)**3')
        self.assertEqual(p, 6 - 5.0 / 8.0 - 3.0 - 4 + 64)

    def test_lt_numbers(self):
        p = self.parser.parse_definition('2 < 3')
        self.assertTrue(p)

    def test_gt_numbers(self):
        p = self.parser.parse_definition('5 > 3')
        self.assertTrue(p)

    def test_leq_numbers(self):
        p = self.parser.parse_definition('3 <= 3')
        self.assertTrue(p)

    def test_geq_numbers(self):
        p = self.parser.parse_definition('3 >= 3')
        self.assertTrue(p)

    def test_eq_numbers(self):
        p = self.parser.parse_definition('3 == 3')
        self.assertTrue(p)

    def test_leq_number_variable(self):
        p = self.parser.parse_definition('x[2,3] > 4.0')
        self.assertEqual(p, OpType('>', [VarType('x', [2, 3]), 4.0]))

    def test_function_variable_group(self):
        p = self.parser.parse_definition('2*(f(1,2, c=4) - x[2:3])')
        f = FuncType('f', [1, 2], {'c': 4})
        x = VarType('x', [slice(2, 3)])
        f_minus_x = OpType('-', [f, x])
        self.assertEqual(p, OpType('*', [2, f_minus_x]))

    def test_sum_vars_factors(self):
        p = self.parser.parse_definition(
            'MEG_ISOP*60/68+MEG_MTERP*120/136+MEG_BCARY*180/204')
        MEG_ISOP = VarType(name='MEG_ISOP', indices=[])
        A = OpType(name='*', arguments=[MEG_ISOP, 60])
        A = OpType(name='/', arguments=[A, 68])
        MEG_MTERP = VarType('MEG_MTERP', [])
        B = OpType(name='*', arguments=[MEG_MTERP, 120])
        B = OpType(name='/', arguments=[B, 136])
        MEG_BCARY = VarType('MEG_BCARY', [])
        C = OpType(name='*', arguments=[MEG_BCARY, 180])
        C = OpType(name='/', arguments=[C, 204])
        A_plus_B = OpType('+', arguments=[A, B])
        A_plus_B_plus_C = OpType(name='+', arguments=[A_plus_B, C])
        self.assertEqual(p, A_plus_B_plus_C)

    def test_pyparsing_killer(self):
        s = ('MEG_ISOP*60/68+MEG_MTERP*120/136+MEG_BCARY*180/204+MEG_CH3OH*12/32+'
             'MEG_CH3COCH3*36/58+MEG_CH3CHO*24/44+MEG_CH2O*12/30+MEG_CO*12/28+'
             'MEG_C2H6*24/30+MEG_C3H8*36/44+MEG_C2H4*24/28+MEG_C3H6*36/42+'
             'MEG_C2H5OH*24/46+MEG_BIGALK*60/72+MEG_BIGENE*48/56+MEG_TOLUENE*84/92+'
             'MEG_HCN*12/27+MEG_HCOOH*12/46+MEG_CH3COOH*24/60')
        self.parser.parse_definition(s)

    def test_floats_variable_dict(self):
        vdict = {'x': 3.5, 'y': 2.5}
        parser = Parser(variables=vdict)
        p = parser.parse_definition('x + y')
        self.assertEqual(p, 6.0)

    def test_array_variable_dict(self):
        vdict = {'x': 3.5, 'y': np.array([1.5, 2.5, 3.5, 4.5])}
        parser = Parser(variables=vdict)
        p = parser.parse_definition('x + y[1]')
        self.assertEqual(p, 6.0)

    def test_array_slice_variable_dict(self):
        vdict = {'x': 3.5, 'y': np.array([1.5, 2.5, 3.5, 4.5])}
        parser = Parser(variables=vdict)
        p = parser.parse_definition('x + y[1:3]')
        np.testing.assert_array_equal(p, np.array([6.0, 7.0]))

    def test_function_registry(self):
        def f(x): return x**2
        freg = {'f': f}
        parser = Parser(functions=freg)
        p = parser.parse_definition('f(3)')
        self.assertEqual(p, 9)


if __name__ == "__main__":
    unittest.main()
