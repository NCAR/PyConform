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

    def test_pst_name(self):
        indata = (['x', 1, -3.2], {})
        pst = parsing.ParsedStringType(indata)
        actual = pst.name
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

    def test_parse_integer_1(self):
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
        expected = parsing.FunctionPST((['f', 1], {}))
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Function parsing failed')

    def test_parse_func_nested(self):
        defp = parsing.DefinitionParser()
        indata = 'f(1, g(2))'
        actual = defp.parse(indata)
        expected = parsing.FunctionPST((['f', 1,
                                         parsing.FunctionPST((['g', 2], {}))],
                                        {}))
        testname = 'DefinitionParser.parse({0!r})'.format(indata)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Function parsing failed')


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
