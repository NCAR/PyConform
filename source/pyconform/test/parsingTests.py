"""
Parsing Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from pyconform import parsing

import operator
import unittest


#=========================================================================
# print_test_message - Helper function
#=========================================================================
def print_test_message(testname, indata=None, actual=None, expected=None):
    """
    Pretty-print a test message

    Parameters:
        testname: String name of the test
        indata: Input data for testing (if any)
        actual: Actual return value/result
        expected: Expected return value/result
    """
    indent = linesep + ' ' * 14
    print '{}:'.format(testname)
    if indata:
        s_indata = str(indata).replace(linesep, indent)
        print '    input:    {}'.format(s_indata)
    if actual:
        s_actual = str(actual).replace(linesep, indent)
        print '    actual:   {}'.format(s_actual)
    if expected:
        s_expected = str(expected).replace(linesep, indent)
        print '    expected: {}'.format(s_expected)
    print


#=========================================================================
# ParsingTests - Tests for the parsing module
#=========================================================================
class ParsingTests(unittest.TestCase):
    """
    Unit Tests for the pyconform.parsing module
    """

    def test_type(self):
        dparser = parsing.DefitionParser()
        actual = type(dparser)
        expected = parsing.DefitionParser
        print_test_message('type(DefinitionParser)', actual, expected)
        self.assertEqual(actual, expected,
                         'DefinitionParser type not correct')
        
    def test_parse_definition_var_only(self):
        dparser = parsing.DefitionParser()
        indata = 'x'
        actual = dparser.parse_definition(indata)
        expected = indata
        print_test_message('DefinitionParser.parse_definition({})'.format(indata),
                           actual, expected)
        self.assertEqual(actual, expected,
                         'Definition parsed incorrectly')

    def test_parse_definition_add_mul_neg_pow(self):
        dparser = parsing.DefitionParser()
        indata = '((2*x + 1.0)^3 * (-3)) / +5 - 8.3'
        actual = dparser.parse_definition(indata)
        expected = (operator.sub,
                    (operator.div,
                     (operator.mul,
                      (operator.pow,
                       (operator.add, (operator.mul, 2, 'x'), 1),
                       3),
                      (operator.neg, 3)),
                     5),
                    8.3)
        print_test_message('DefinitionParser.parse_definition({})'.format(indata),
                           actual, expected)
        self.assertEqual(actual, expected,
                         'Definition parsed incorrectly')


#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
