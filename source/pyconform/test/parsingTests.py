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



#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
