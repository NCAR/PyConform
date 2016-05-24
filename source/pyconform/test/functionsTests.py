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
        self.all_functions = set((('transpose', 2), ('sqrt', 1), ('convert', 3)))
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
# UnitsTests
#===============================================================================
class UnitsTests(unittest.TestCase):
    """
    Unit tests for the units methods of the functions.FunctionAbstract classes
    """
    
    def test_units_neg_m(self):
        indata = (Unit('m'),)
        testname = 'NegationOperator.units({!r})'.format(*indata)
        actual = functions.NegationOperator.units(*indata)
        expected = Unit(indata[0]), (None,)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_neg_1(self):
        indata = (1,)
        testname = 'NegationOperator.units({!r})'.format(*indata)
        actual = functions.NegationOperator.units(*indata)
        expected = Unit(indata[0]), (None,)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_add_m_m(self):
        indata = (Unit('m'), Unit('m'))
        testname = 'AdditionOperator.units({!r})'.format(*indata)
        actual = functions.AdditionOperator.units(*indata)
        expected = Unit(indata[0]), (None, None)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_add_m_km(self):
        indata = (Unit('m'), Unit('km'))
        testname = 'AdditionOperator.units({!r})'.format(*indata)
        actual = functions.AdditionOperator.units(*indata)
        expected = Unit(indata[0]), (None, Unit('m'))
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_add_m_g(self):
        indata = (Unit('m'), Unit('g'))
        testname = 'AdditionOperator.units({!r})'.format(*indata)
        expected = functions.UnitsError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(expected, functions.AdditionOperator.units, *indata)

    def test_units_add_1_u1(self):
        indata = (1, Unit(1))
        testname = 'AdditionOperator.units({!r})'.format(*indata)
        actual = functions.AdditionOperator.units(*indata)
        expected = Unit(indata[0]), (None, None)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_add_m_2(self):
        indata = (Unit('m'), 2)
        testname = 'AdditionOperator.units({!r})'.format(*indata)
        expected = functions.UnitsError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(expected, functions.AdditionOperator.units, *indata)

    def test_units_sub_m_km(self):
        indata = (Unit('m'), Unit('km'))
        testname = 'SubtractionOperator.units({!r})'.format(*indata)
        actual = functions.SubtractionOperator.units(*indata)
        expected = Unit(indata[0]), (None, Unit('m'))
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_mul_m_m(self):
        indata = (Unit('m'), Unit('m'))
        testname = 'MultiplicationOperator.units({!r})'.format(*indata)
        actual = functions.MultiplicationOperator.units(*indata)
        expected = Unit(op.mul(*indata)), (None, None)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_mul_1_m(self):
        indata = (1, Unit('m'))
        testname = 'MultiplicationOperator.units({!r})'.format(*indata)
        actual = functions.MultiplicationOperator.units(*indata)
        expected = Unit(op.mul(*indata)), (None, None)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_div_1_m(self):
        indata = (1, Unit('m'))
        testname = 'DivisionOperator.units({!r})'.format(*indata)
        actual = functions.DivisionOperator.units(*indata)
        expected = Unit(1)/Unit('m'), (None, None)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_units_sqrt_m2(self):
        indata = (Unit('m')**2,)
        testname = 'SquareRootFunction.units({!r})'.format(*indata)
        actual = functions.SquareRootFunction.units(*indata)
        expected = Unit('m'), (None,)
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertTupleEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        
#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
