"""
Parsing Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import parsing
from os import linesep

import unittest
import operator as op


#===============================================================================
# General Functions
#===============================================================================
def print_test_message(testname, indata=None, actual=None, expected=None):
    print '{0}:'.format(testname)
    print ' - input    = {0!r}'.format(indata).replace(linesep, ' ')
    print ' - actual   = {0!r}'.format(actual).replace(linesep, ' ')
    print ' - expected = {0!r}'.format(expected).replace(linesep, ' ')
    print


#===============================================================================
# ParsedStringTypeTests
#===============================================================================
class ParsedStringTypeTests(unittest.TestCase):
    
    def test_pst_init(self):
        indata = (['x'], {})
        pst = parsing.ParsedStringType(indata)
        actual = type(pst)
        expected = parsing.ParsedStringType
        testname = 'ParsedStringType.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')
    
    def test_varpst_init(self):
        indata = (['x'], {})
        pst = parsing.VariablePST(indata)
        actual = type(pst)
        expected = parsing.VariablePST
        testname = 'VariablePST.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')
    
    def test_funcpst_init(self):
        indata = (['x'], {})
        pst = parsing.FunctionPST(indata)
        actual = type(pst)
        expected = parsing.FunctionPST
        testname = 'FunctionPST.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')
    
    def test_operpst_init(self):
        indata = (['x'], {})
        pst = parsing.OperatorPST(indata)
        actual = type(pst)
        expected = parsing.OperatorPST
        testname = 'OperatorPST.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')
        
    def test_pst_init_args(self):
        indata = (['x', 1, -3.2], {})
        pst = parsing.ParsedStringType(indata)
        actual = type(pst)
        expected = parsing.ParsedStringType
        testname = 'ParsedStringType.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')

    def test_pst_obj(self):
        indata = (['x', 1, -3.2], {})
        pst = parsing.ParsedStringType(indata)
        actual = pst.obj
        expected = indata[0][0]
        testname = 'ParsedStringType.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Names do not match')

    def test_pst_args(self):
        indata = (['x', 1, -3.2], {})
        pst = parsing.ParsedStringType(indata)
        actual = pst.args
        expected = tuple(indata[0][1:])
        testname = 'ParsedStringType.__init__({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Names do not match')
                

#===============================================================================
# DefinitionParserTests
#===============================================================================
class DefinitionParserTests(unittest.TestCase):

    def test_init(self):
        defp = parsing.DefinitionParser()
        actual = type(defp)
        expected = parsing.DefinitionParser
        testname = 'DefinitionParser.__init__()'
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Types do not match')

#===== INTEGERS ================================================================

    def test_parse_integer(self):
        defp = parsing.DefinitionParser()
        indata = '1'
        actual = defp.parse(indata)
        expected = int(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Integer parsing failed')

    def test_parse_integer_large(self):
        defp = parsing.DefinitionParser()
        indata = '98734786423867234'
        actual = defp.parse(indata)
        expected = int(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Integer parsing failed')

#===== FLOATS ==================================================================

    def test_parse_float_dec(self):
        defp = parsing.DefinitionParser()
        indata = '1.'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_long(self):
        defp = parsing.DefinitionParser()
        indata = '1.8374755'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_nofirst(self):
        defp = parsing.DefinitionParser()
        indata = '.35457'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1e7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_pos_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1e+7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_neg_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1e-7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1.e7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_pos_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1.e+7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_neg_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1.e-7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_long_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1.324523e7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_long_pos_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1.324523e+7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_long_neg_exp(self):
        defp = parsing.DefinitionParser()
        indata = '1.324523e-7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_nofirst_exp(self):
        defp = parsing.DefinitionParser()
        indata = '.324523e7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_nofirst_pos_exp(self):
        defp = parsing.DefinitionParser()
        indata = '.324523e+7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

    def test_parse_float_dec_nofirst_neg_exp(self):
        defp = parsing.DefinitionParser()
        indata = '.324523e-7'
        actual = defp.parse(indata)
        expected = float(indata)
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Float parsing failed')

#===== FUNCTIONS ===============================================================

    def test_parse_func(self):
        defp = parsing.DefinitionParser()
        indata = 'f()'
        actual = defp.parse(indata)
        expected = parsing.FunctionPST(('f', {}))
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Function parsing failed')

    def test_parse_func_arg(self):
        defp = parsing.DefinitionParser()
        indata = 'f(1)'
        actual = defp.parse(indata)
        expected = parsing.FunctionPST([['f', 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Function parsing failed')

    def test_parse_func_nested(self):
        defp = parsing.DefinitionParser()
        g2 = parsing.FunctionPST([['g', 2]])
        f1g = parsing.FunctionPST([['f', 1, g2]])
        indata = 'f(1, g(2))'
        actual = defp.parse(indata)
        expected = f1g
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Function parsing failed')

#===== VARIABLES ===============================================================

    def test_parse_var(self):
        defp = parsing.DefinitionParser()
        indata = 'x'
        actual = defp.parse(indata)
        expected = parsing.VariablePST([['x']])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Variable parsing failed')

    def test_parse_var_index(self):
        defp = parsing.DefinitionParser()
        indata = 'x[1]'
        actual = defp.parse(indata)
        expected = parsing.VariablePST([['x', 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Variable parsing failed')

    def test_parse_var_slice(self):
        defp = parsing.DefinitionParser()
        indata = 'x[1:2:3]'
        actual = defp.parse(indata)
        expected = parsing.VariablePST([['x', slice(1,2,3)]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Variable parsing failed')

    def test_parse_var_index_nested(self):
        defp = parsing.DefinitionParser()
        y0 = parsing.VariablePST([['y', 0]])
        x1y = parsing.VariablePST([['x', 1, y0]])
        indata = 'x[1, y[0]]'
        actual = defp.parse(indata)
        expected = x1y
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Variable parsing failed')

    def test_parse_var_slice_nested(self):
        defp = parsing.DefinitionParser()
        y03 = parsing.VariablePST([['y', slice(0,3)]])
        x14y = parsing.VariablePST([['x', slice(1,4), y03]])
        indata = 'x[1:4, y[0:3]]'
        actual = defp.parse(indata)
        expected = x14y
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Variable parsing failed')

#===== NEGATION ================================================================

    def test_parse_neg_integer(self):
        defp = parsing.DefinitionParser()
        indata = '-1'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.neg, 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Negation parsing failed')

    def test_parse_neg_float(self):
        defp = parsing.DefinitionParser()
        indata = '-1.4'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.neg, 1.4]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Negation parsing failed')

    def test_parse_neg_var(self):
        defp = parsing.DefinitionParser()
        indata = '-x'
        actual = defp.parse(indata)
        x = parsing.VariablePST([['x']])
        expected = parsing.OperatorPST([[op.neg, x]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Negation parsing failed')

    def test_parse_neg_func(self):
        defp = parsing.DefinitionParser()
        indata = '-f()'
        actual = defp.parse(indata)
        f = parsing.FunctionPST([['f']])
        expected = parsing.OperatorPST([[op.neg, f]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Negation parsing failed')

#===== POSITIVE ================================================================

    def test_parse_pos_integer(self):
        defp = parsing.DefinitionParser()
        indata = '+1'
        actual = defp.parse(indata)
        expected = 1
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Positive operator parsing failed')

    def test_parse_pos_float(self):
        defp = parsing.DefinitionParser()
        indata = '+1e7'
        actual = defp.parse(indata)
        expected = 1e7
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Positive operator parsing failed')

    def test_parse_pos_func(self):
        defp = parsing.DefinitionParser()
        indata = '+f()'
        actual = defp.parse(indata)
        expected = parsing.FunctionPST([['f']])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Positive operator parsing failed')

    def test_parse_pos_var(self):
        defp = parsing.DefinitionParser()
        indata = '+x[1]'
        actual = defp.parse(indata)
        expected = parsing.VariablePST([['x', 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Positive operator parsing failed')

#===== POWER ===================================================================

    def test_parse_int_pow_int(self):
        defp = parsing.DefinitionParser()
        indata = '2^1'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.pow, 2, 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Power operator parsing failed')

    def test_parse_float_pow_float(self):
        defp = parsing.DefinitionParser()
        indata = '2.4 ^ 1e7'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.pow, 2.4, 1e7]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Power operator parsing failed')

    def test_parse_func_pow_func(self):
        defp = parsing.DefinitionParser()
        indata = 'f() ^ g(1)'
        actual = defp.parse(indata)
        f = parsing.FunctionPST([['f']])
        g1 = parsing.FunctionPST([['g', 1]])
        expected = parsing.OperatorPST([[op.pow, f, g1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Power operator parsing failed')

    def test_parse_var_pow_var(self):
        defp = parsing.DefinitionParser()
        indata = 'x[1] ^ y'
        actual = defp.parse(indata)
        x1 = parsing.VariablePST([['x', 1]])
        y = parsing.VariablePST([['y']])
        expected = parsing.OperatorPST([[op.pow, x1, y]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Power operator parsing failed')

#===== DIV =====================================================================

    def test_parse_int_div_int(self):
        defp = parsing.DefinitionParser()
        indata = '2/1'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.truediv, 2, 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Division operator parsing failed')

    def test_parse_float_div_float(self):
        defp = parsing.DefinitionParser()
        indata = '2.4/1e7'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.truediv, 2.4, 1e7]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Division operator parsing failed')

    def test_parse_func_div_func(self):
        defp = parsing.DefinitionParser()
        indata = 'f() / g(1)'
        actual = defp.parse(indata)
        f = parsing.FunctionPST([['f']])
        g1 = parsing.FunctionPST([['g', 1]])
        expected = parsing.OperatorPST([[op.truediv, f, g1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Division operator parsing failed')

    def test_parse_var_div_var(self):
        defp = parsing.DefinitionParser()
        indata = 'x[1] / y'
        actual = defp.parse(indata)
        x1 = parsing.VariablePST([['x', 1]])
        y = parsing.VariablePST([['y']])
        expected = parsing.OperatorPST([[op.truediv, x1, y]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Division operator parsing failed')

#===== MUL =====================================================================

    def test_parse_int_mul_int(self):
        defp = parsing.DefinitionParser()
        indata = '2*1'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.mul, 2, 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Multiplication operator parsing failed')

    def test_parse_float_mul_float(self):
        defp = parsing.DefinitionParser()
        indata = '2.4*1e7'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.mul, 2.4, 1e7]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Multiplication operator parsing failed')

    def test_parse_func_mul_func(self):
        defp = parsing.DefinitionParser()
        indata = 'f() * g(1)'
        actual = defp.parse(indata)
        f = parsing.FunctionPST([['f']])
        g1 = parsing.FunctionPST([['g', 1]])
        expected = parsing.OperatorPST([[op.mul, f, g1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Multiplication operator parsing failed')

    def test_parse_var_mul_var(self):
        defp = parsing.DefinitionParser()
        indata = 'x[1] * y'
        actual = defp.parse(indata)
        x1 = parsing.VariablePST([['x', 1]])
        y = parsing.VariablePST([['y']])
        expected = parsing.OperatorPST([[op.mul, x1, y]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Multiplication operator parsing failed')

#===== ADD =====================================================================

    def test_parse_int_add_int(self):
        defp = parsing.DefinitionParser()
        indata = '2+1'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.add, 2, 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Addition operator parsing failed')

    def test_parse_float_add_float(self):
        defp = parsing.DefinitionParser()
        indata = '2.4+1e7'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.add, 2.4, 1e7]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Addition operator parsing failed')

    def test_parse_func_add_func(self):
        defp = parsing.DefinitionParser()
        indata = 'f() + g(1)'
        actual = defp.parse(indata)
        f = parsing.FunctionPST([['f']])
        g1 = parsing.FunctionPST([['g', 1]])
        expected = parsing.OperatorPST([[op.add, f, g1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Addition operator parsing failed')

    def test_parse_var_add_var(self):
        defp = parsing.DefinitionParser()
        indata = 'x[1] + y'
        actual = defp.parse(indata)
        x1 = parsing.VariablePST([['x', 1]])
        y = parsing.VariablePST([['y']])
        expected = parsing.OperatorPST([[op.add, x1, y]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Addition operator parsing failed')

#===== SUB =====================================================================

    def test_parse_int_sub_int(self):
        defp = parsing.DefinitionParser()
        indata = '2-1'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.sub, 2, 1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Subtraction operator parsing failed')

    def test_parse_float_sub_float(self):
        defp = parsing.DefinitionParser()
        indata = '2.4-1e7'
        actual = defp.parse(indata)
        expected = parsing.OperatorPST([[op.sub, 2.4, 1e7]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Subtraction operator parsing failed')

    def test_parse_func_sub_func(self):
        defp = parsing.DefinitionParser()
        indata = 'f() - g(1)'
        actual = defp.parse(indata)
        f = parsing.FunctionPST([['f']])
        g1 = parsing.FunctionPST([['g', 1]])
        expected = parsing.OperatorPST([[op.sub, f, g1]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Subtraction operator parsing failed')

    def test_parse_var_sub_var(self):
        defp = parsing.DefinitionParser()
        indata = 'x[1] - y'
        actual = defp.parse(indata)
        x1 = parsing.VariablePST([['x', 1]])
        y = parsing.VariablePST([['y']])
        expected = parsing.OperatorPST([[op.sub, x1, y]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Subtraction operator parsing failed')

#===== Integration =============================================================

    def test_parse_integrated_1(self):
        defp = parsing.DefinitionParser()
        indata = '2-17.3*x^2'
        actual = defp.parse(indata)
        x = parsing.VariablePST([['x']])
        x2 = parsing.OperatorPST([[op.pow, x, 2]])
        m17p3x2 = parsing.OperatorPST([[op.mul, 17.3, x2]])
        expected = parsing.OperatorPST([[op.sub, 2, m17p3x2]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Integrated operator parsing failed')
        
    def test_parse_integrated_2(self):
        defp = parsing.DefinitionParser()
        indata = '2-17.3*x / f(2.3, x[2:5])'
        actual = defp.parse(indata)
        x = parsing.VariablePST([['x']])
        x25 = parsing.VariablePST([['x', slice(2,5)]])
        f = parsing.FunctionPST([['f', 2.3, x25]])
        dxf = parsing.OperatorPST([[op.truediv, x, f]])
        m17p3dxf = parsing.OperatorPST([[op.mul, 17.3, dxf]])
        expected = parsing.OperatorPST([[op.sub, 2, m17p3dxf]])
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Integrated operator parsing failed')


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
