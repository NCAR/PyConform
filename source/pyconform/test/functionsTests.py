"""
Functions Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import functions
from cf_units import Unit
from os import linesep

import unittest
import numpy as np
import operator as op


#===============================================================================
# General Functions
#===============================================================================
def print_test_message(testname, indata=None, actual=None, expected=None):
    print '{}:'.format(testname)
    print ' - indata   = {}'.format(indata)
    print ' - actual   = {}'.format(actual).replace(linesep, ' ')
    print ' - expected = {}'.format(expected).replace(linesep, ' ')
    print


#===============================================================================
# FunctionsTests
#===============================================================================
class FunctionsTests(unittest.TestCase):
    """
    Unit tests for the functions module
    """
    
    def setUp(self):
        self.all_operators = set((('-', 1), ('^', 2), ('+', 2),
                                  ('-', 2), ('*', 2), ('/', 2)))
        self.all_functions = set((('sqrt', 1),))
        self.all = (self.all_operators).union(self.all_functions)

    def test_available_operators(self):
        testname = 'available_operators()'
        actual = functions.available_operators()
        expected = self.all_operators
        print_test_message(testname, actual=actual, expected=expected)
        self.assertSetEqual(actual, expected,
                            '{} returned unexpected result'.format(testname))

    def test_find_operator_neg(self):
        indata = ('-', 1)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.NegationOperator
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_operator_add(self):
        indata = ('+', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.AdditionOperator
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_operator_sub(self):
        indata = ('-', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.SubtractionOperator
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_operator_mul(self):
        indata = ('*', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.MultiplicationOperator
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_operator_div(self):
        indata = ('/', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.DivisionOperator
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_operator_pow(self):
        indata = ('^', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.PowerOperator
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_operator_key_failure(self):
        indata = ('?', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find_operator, *indata)

    def test_find_operator_numargs_failure(self):
        indata = ('*', 1)
        testname = 'find_operator({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find_operator, *indata)

    def test_available_functions(self):
        testname = 'available_functions()'
        actual = functions.available_functions()
        expected = self.all_functions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertSetEqual(actual, expected,
                            '{} returned unexpected result'.format(testname))

    def test_find_function_sqrt(self):
        indata = ('sqrt', 1)
        testname = 'find_function({!r}, {})'.format(*indata)
        actual = functions.find_function(*indata)
        expected = functions.SquareRootFunction
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_function_key_failure(self):
        indata = ('f', 1)
        testname = 'find_function({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find_function, *indata)

    def test_find_function_numargs_failure(self):
        indata = ('sqrt', 2)
        testname = 'find_function({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find_function, *indata)
        
    def test_available(self):
        testname = 'available()'
        actual = functions.available()
        expected = self.all
        print_test_message(testname, actual=actual, expected=expected)
        self.assertSetEqual(actual, expected,
                            '{} returned unexpected result'.format(testname))

    def test_find_sqrt(self):
        indata = ('sqrt', 1)
        testname = 'find({!r}, {})'.format(*indata)
        actual = functions.find(*indata)
        expected = functions.SquareRootFunction
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_mul(self):
        indata = ('*', 2)
        testname = 'find({!r}, {})'.format(*indata)
        actual = functions.find(*indata)
        expected = functions.MultiplicationOperator
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_find_failure(self):
        indata = ('*', 3)
        testname = 'find({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find, *indata)

    def test_function_attribute_mul(self):
        indata = ('*', 2)
        testname = 'find({!r}, {}).function'.format(*indata)
        actual = functions.find(*indata).function
        expected = op.mul
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_function_attribute_sqrt(self):
        indata = ('sqrt', 1)
        testname = 'find({!r}, {}).function'.format(*indata)
        actual = functions.find(*indata).function
        expected = np.sqrt
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))
    
    def test_user_defined_function(self):
        class myfunc(functions.Function):
            key = 'myfunc'
            numargs = 3
            function = lambda x,y,z: x
            def units(self, *arg_units):
                uret = arg_units[0] if isinstance(arg_units[0], Unit) else Unit(1)
                return uret, (None, None, None)

        indata = ('myfunc', 3)
        testname = 'find({!r}, {}).function'.format(*indata)
        actual = functions.find(*indata).function
        expected = myfunc.function
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
