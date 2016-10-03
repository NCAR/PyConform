"""
Parsing Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import parsing
from testutils import print_test_message

import unittest


#===============================================================================
# ParsedStringTypeTests
#===============================================================================
class ParsedStringTypeTests(unittest.TestCase):

    def test_pst_init(self):
        indata = (['x'], {})
        pst = parsing.ParsedFunction(indata)
        actual = type(pst)
        expected = parsing.ParsedFunction
        testname = 'ParsedFunction.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')

    def test_varpst_init(self):
        indata = (['x'], {})
        pst = parsing.ParsedVariable(indata)
        actual = type(pst)
        expected = parsing.ParsedVariable
        testname = 'ParsedVariable.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')

    def test_funcpst_init(self):
        indata = (['x'], {})
        pst = parsing.ParsedFunction(indata)
        actual = type(pst)
        expected = parsing.ParsedFunction
        testname = 'ParsedFunction.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')

    def test_operpst_init(self):
        indata = (['x'], {})
        pst = parsing.ParsedBinOp(indata)
        actual = type(pst)
        expected = parsing.ParsedBinOp
        testname = 'ParsedBinOp.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')

    def test_pst_init_args(self):
        indata = (['x', 1, -3.2], {})
        pst = parsing.ParsedFunction(indata)
        actual = type(pst)
        expected = parsing.ParsedFunction
        testname = 'ParsedFunction.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')

    def test_pst_obj(self):
        indata = (['x', 1, -3.2], {})
        pst = parsing.ParsedFunction(indata)
        actual = pst.key
        expected = indata[0][0]
        testname = 'ParsedFunction.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Names do not match')

    def test_pst_args(self):
        indata = (['x', 1, -3.2], {})
        pst = parsing.ParsedFunction(indata)
        actual = pst.args
        expected = tuple(indata[0][1:])
        testname = 'ParsedFunction.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Names do not match')


#===============================================================================
# DefinitionParserTests
#===============================================================================
class DefinitionParserTests(unittest.TestCase):

#===== QUOTED STRINGS ==========================================================

    def test_parse_quote_int(self):
        indata = '"1"'
        actual = parsing.parse_definition(indata)
        expected = '1'
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'String parsing failed')

    def test_parse_quote_escaped(self):
        indata = '"\\"1\\""'
        actual = parsing.parse_definition(indata)
        expected = '"1"'
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'String parsing failed')

    def test_parse_quote_literal(self):
        indata = 'Hello, World!'
        actual = parsing.parse_definition('"' + indata + '"')
        expected = indata
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'String parsing failed')

    def test_parse_quote_func(self):
        indata = 'f(x,y,z)'
        actual = parsing.parse_definition('"' + indata + '"')
        expected = indata
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'String parsing failed')

#===== INTEGERS ================================================================

    def test_parse_integer(self):
        indata = '1'
        actual = parsing.parse_definition(indata)
        expected = int(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Integer parsing failed')

    def test_parse_integer_large(self):
        indata = '98734786423867234'
        actual = parsing.parse_definition(indata)
        expected = int(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Integer parsing failed')

#===== FLOATS ==================================================================

    def test_parse_float_dec(self):
        indata = '1.'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_long(self):
        indata = '1.8374755'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_nofirst(self):
        indata = '.35457'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_exp(self):
        indata = '1e7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_pos_exp(self):
        indata = '1e+7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_neg_exp(self):
        indata = '1e-7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_exp(self):
        indata = '1.e7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_pos_exp(self):
        indata = '1.e+7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_neg_exp(self):
        indata = '1.e-7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_long_exp(self):
        indata = '1.324523e7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_long_pos_exp(self):
        indata = '1.324523e+7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_long_neg_exp(self):
        indata = '1.324523e-7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_nofirst_exp(self):
        indata = '.324523e7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_nofirst_pos_exp(self):
        indata = '.324523e+7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_nofirst_neg_exp(self):
        indata = '.324523e-7'
        actual = parsing.parse_definition(indata)
        expected = float(indata)
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

#===== FUNCTIONS ===============================================================

    def test_parse_func(self):
        indata = 'f()'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedFunction(('f', {}))
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Function parsing failed')

    def test_parse_func_arg(self):
        indata = 'f(1)'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedFunction([['f', 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Function parsing failed')

    def test_parse_func_nested(self):
        g2 = parsing.ParsedFunction([['g', 2]])
        f1g = parsing.ParsedFunction([['f', 1, g2]])
        indata = 'f(1, g(2))'
        actual = parsing.parse_definition(indata)
        expected = f1g
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Function parsing failed')

#===== VARIABLES ===============================================================

    def test_parse_var(self):
        indata = 'x'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedVariable([['x']])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Variable parsing failed')

    def test_parse_var_index(self):
        indata = 'x[1]'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedVariable([['x', 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Variable parsing failed')

    def test_parse_var_slice(self):
        indata = 'x[1:2:3]'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedVariable([['x', slice(1, 2, 3)]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Variable parsing failed')

#     def test_parse_var_index_nested(self):
#         y0 = parsing.ParsedVariable([['y', 0]])
#         x1y = parsing.ParsedVariable([['x', 1, y0]])
#         indata = 'x[1, y[0]]'
#         actual = parsing.parse_definition(indata)
#         expected = x1y
#         testname = 'parse_definition({0!r})'.format(indata)
#         print_test_message(testname, indata=indata,
#                            actual=actual, expected=expected)
#         self.assertEqual(actual, expected,
#                          'Variable parsing failed')

#     def test_parse_var_slice_nested(self):
#         y03 = parsing.ParsedVariable([['y', slice(0,3)]])
#         x14y = parsing.ParsedVariable([['x', slice(1,4), y03]])
#         indata = 'x[1:4, y[0:3]]'
#         actual = parsing.parse_definition(indata)
#         expected = x14y
#         testname = 'parse_definition({0!r})'.format(indata)
#         print_test_message(testname, indata=indata,
#                            actual=actual, expected=expected)
#         self.assertEqual(actual, expected,
#                          'Variable parsing failed')

#===== NEGATION ================================================================

    def test_parse_neg_integer(self):
        indata = '-1'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedUniOp([['-', 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Negation parsing failed')

    def test_parse_neg_float(self):
        indata = '-1.4'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedUniOp([['-', 1.4]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Negation parsing failed')

    def test_parse_neg_var(self):
        indata = '-x'
        actual = parsing.parse_definition(indata)
        x = parsing.ParsedVariable([['x']])
        expected = parsing.ParsedUniOp([['-', x]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Negation parsing failed')

    def test_parse_neg_func(self):
        indata = '-f()'
        actual = parsing.parse_definition(indata)
        f = parsing.ParsedFunction([['f']])
        expected = parsing.ParsedUniOp([['-', f]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Negation parsing failed')

#===== POSITIVE ================================================================

    def test_parse_pos_integer(self):
        indata = '+1'
        actual = parsing.parse_definition(indata)
        expected = 1
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Positive operator parsing failed')

    def test_parse_pos_float(self):
        indata = '+1e7'
        actual = parsing.parse_definition(indata)
        expected = 1e7
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Positive operator parsing failed')

    def test_parse_pos_func(self):
        indata = '+f()'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedFunction([['f']])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Positive operator parsing failed')

    def test_parse_pos_var(self):
        indata = '+x[1]'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedVariable([['x', 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Positive operator parsing failed')

#===== POWER ===================================================================

    def test_parse_int_pow_int(self):
        indata = '2^1'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['^', 2, 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Power operator parsing failed')

    def test_parse_float_pow_float(self):
        indata = '2.4 ^ 1e7'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['^', 2.4, 1e7]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Power operator parsing failed')

    def test_parse_func_pow_func(self):
        indata = 'f() ^ g(1)'
        actual = parsing.parse_definition(indata)
        f = parsing.ParsedFunction([['f']])
        g1 = parsing.ParsedFunction([['g', 1]])
        expected = parsing.ParsedBinOp([['^', f, g1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Power operator parsing failed')

    def test_parse_var_pow_var(self):
        indata = 'x[1] ^ y'
        actual = parsing.parse_definition(indata)
        x1 = parsing.ParsedVariable([['x', 1]])
        y = parsing.ParsedVariable([['y']])
        expected = parsing.ParsedBinOp([['^', x1, y]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Power operator parsing failed')

#===== DIV =====================================================================

    def test_parse_int_div_int(self):
        indata = '2/1'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['/', 2, 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Division operator parsing failed')

    def test_parse_float_div_float(self):
        indata = '2.4/1e7'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['/', 2.4, 1e7]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Division operator parsing failed')

    def test_parse_func_div_func(self):
        indata = 'f() / g(1)'
        actual = parsing.parse_definition(indata)
        f = parsing.ParsedFunction([['f']])
        g1 = parsing.ParsedFunction([['g', 1]])
        expected = parsing.ParsedBinOp([['/', f, g1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Division operator parsing failed')

    def test_parse_var_div_var(self):
        indata = 'x[1] / y'
        actual = parsing.parse_definition(indata)
        x1 = parsing.ParsedVariable([['x', 1]])
        y = parsing.ParsedVariable([['y']])
        expected = parsing.ParsedBinOp([['/', x1, y]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Division operator parsing failed')

#===== MUL =====================================================================

    def test_parse_int_mul_int(self):
        indata = '2*1'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['*', 2, 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Multiplication operator parsing failed')

    def test_parse_float_mul_float(self):
        indata = '2.4*1e7'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['*', 2.4, 1e7]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Multiplication operator parsing failed')

    def test_parse_func_mul_func(self):
        indata = 'f() * g(1)'
        actual = parsing.parse_definition(indata)
        f = parsing.ParsedFunction([['f']])
        g1 = parsing.ParsedFunction([['g', 1]])
        expected = parsing.ParsedBinOp([['*', f, g1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Multiplication operator parsing failed')

    def test_parse_var_mul_var(self):
        indata = 'x[1] * y'
        actual = parsing.parse_definition(indata)
        x1 = parsing.ParsedVariable([['x', 1]])
        y = parsing.ParsedVariable([['y']])
        expected = parsing.ParsedBinOp([['*', x1, y]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Multiplication operator parsing failed')

#===== ADD =====================================================================

    def test_parse_int_add_int(self):
        indata = '2+1'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['+', 2, 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Addition operator parsing failed')

    def test_parse_float_add_float(self):
        indata = '2.4+1e7'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['+', 2.4, 1e7]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Addition operator parsing failed')

    def test_parse_func_add_func(self):
        indata = 'f() + g(1)'
        actual = parsing.parse_definition(indata)
        f = parsing.ParsedFunction([['f']])
        g1 = parsing.ParsedFunction([['g', 1]])
        expected = parsing.ParsedBinOp([['+', f, g1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Addition operator parsing failed')

    def test_parse_var_add_var(self):
        indata = 'x[1] + y'
        actual = parsing.parse_definition(indata)
        x1 = parsing.ParsedVariable([['x', 1]])
        y = parsing.ParsedVariable([['y']])
        expected = parsing.ParsedBinOp([['+', x1, y]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Addition operator parsing failed')

#===== SUB =====================================================================

    def test_parse_int_sub_int(self):
        indata = '2-1'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['-', 2, 1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Subtraction operator parsing failed')

    def test_parse_float_sub_float(self):
        indata = '2.4-1e7'
        actual = parsing.parse_definition(indata)
        expected = parsing.ParsedBinOp([['-', 2.4, 1e7]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Subtraction operator parsing failed')

    def test_parse_func_sub_func(self):
        indata = 'f() - g(1)'
        actual = parsing.parse_definition(indata)
        f = parsing.ParsedFunction([['f']])
        g1 = parsing.ParsedFunction([['g', 1]])
        expected = parsing.ParsedBinOp([['-', f, g1]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Subtraction operator parsing failed')

    def test_parse_var_sub_var(self):
        indata = 'x[1] - y'
        actual = parsing.parse_definition(indata)
        x1 = parsing.ParsedVariable([['x', 1]])
        y = parsing.ParsedVariable([['y']])
        expected = parsing.ParsedBinOp([['-', x1, y]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Subtraction operator parsing failed')

#===== Integration =============================================================

    def test_parse_integrated_1(self):
        indata = '2-17.3*x^2'
        actual = parsing.parse_definition(indata)
        x = parsing.ParsedVariable([['x']])
        x2 = parsing.ParsedBinOp([['^', x, 2]])
        m17p3x2 = parsing.ParsedBinOp([['*', 17.3, x2]])
        expected = parsing.ParsedBinOp([['-', 2, m17p3x2]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Integrated operator parsing failed')

    def test_parse_integrated_2(self):
        indata = '2-17.3*x / f(2.3, x[2:5])'
        actual = parsing.parse_definition(indata)
        x = parsing.ParsedVariable([['x']])
        x25 = parsing.ParsedVariable([['x', slice(2, 5)]])
        f = parsing.ParsedFunction([['f', 2.3, x25]])
        dxf = parsing.ParsedBinOp([['/', x, f]])
        m17p3dxf = parsing.ParsedBinOp([['*', 17.3, dxf]])
        expected = parsing.ParsedBinOp([['-', 2, m17p3dxf]])
        testname = 'parse_definition({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Integrated operator parsing failed')


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
