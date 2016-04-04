"""
Parsing Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from pyconform.parsingdir import operands
from pyparsing import Word, ParseException

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
    if indata is not None:
        s_indata = str(indata).replace(linesep, indent)
        print '    input:    {}'.format(s_indata)
    if actual is not None:
        s_actual = str(actual).replace(linesep, indent)
        print '    actual:   {}'.format(s_actual)
    if expected is not None:
        s_expected = str(expected).replace(linesep, indent)
        print '    expected: {}'.format(s_expected)
    print
    

#===============================================================================
# OperandParserTests
#===============================================================================
class OperandParserTests(unittest.TestCase):
    
    def test_init(self):
        testname = 'OperandParser.__init__(token)'
        indata = Word('acdfh')
        op = operands.OperandParser(indata)
        actual = type(op)
        expected = operands.OperandParser
        print_test_message(testname, indata, actual, expected)
        self.assertEqual(actual, expected, '{} failed.'.format(testname))

    def test_init_action(self):
        testname = 'OperandParser.__init__(token, action)'
        indata = lambda t: '*{}*'.format(t[0])
        op = operands.OperandParser(Word('xyz'), action=indata)
        actual = type(op)
        expected = operands.OperandParser
        print_test_message(testname, indata, actual, expected)
        self.assertEqual(actual, expected, '{} failed.'.format(testname))
    
    def test_ident(self):
        testname = 'OperandParser.ident'
        indata = Word('xyz')
        op = operands.OperandParser(indata)
        actual = op.ident
        expected = indata
        print_test_message(testname, indata, actual, expected)
        self.assertEqual(actual, expected, '{} failed.'.format(testname))

    def test_ident_parseString(self):
        testname = 'OperandParser.ident.parseString()'
        indata = 'x'
        op = operands.OperandParser(Word('xyz'))
        actual = op.ident.parseString(indata)[0]
        expected = indata
        print_test_message(testname, indata, actual, expected)
        self.assertEqual(actual, expected, '{} failed.'.format(testname))

    def test_ident_parseString_exception(self):
        testname = 'OperandParser.ident.parseString(): Exception'
        indata = '1'
        op = operands.OperandParser(Word('xyz'))
        actual = ParseException
        expected = ParseException
        print_test_message(testname, indata, actual, expected)
        self.assertRaises(expected, op.ident.parseString, indata)

#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
