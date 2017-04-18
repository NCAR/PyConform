"""
Functions Unit Tests

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import functions
from pyconform.physarray import PhysArray
from cf_units import Unit
from testutils import print_test_message

import unittest
import numpy as np
import operator as op


#===================================================================================================
# FindTests
#===================================================================================================
class FindTests(unittest.TestCase):
    """
    Unit tests for finding functions and operators
    """

    def setUp(self):
        self.all_operators = set((('-', 1), ('^', 2), ('+', 2),
                                  ('-', 2), ('*', 2), ('/', 2)))
        self.all_functions = set((('T', 2), ('sqrt', 1), ('C', 2)))
        self.all = (self.all_operators).union(self.all_functions)

    def test_operator_neg(self):
        key = '-'
        numargs = 1
        testname = 'find_operator({!r}, {})'.format(key, numargs)
        actual = functions.find_operator(key, numargs)
        expected = functions.NegationOperator
        print_test_message(testname, actual=actual, expected=expected, key=key, numargs=numargs)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_add(self):
        key = '+'
        numargs = 2
        testname = 'find_operator({!r}, {})'.format(key, numargs)
        actual = functions.find_operator(key, numargs)
        expected = functions.AdditionOperator
        print_test_message(testname, actual=actual, expected=expected, key=key, numargs=numargs)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_sub(self):
        key = '-'
        numargs = 2
        testname = 'find_operator({!r}, {})'.format(key, numargs)
        actual = functions.find_operator(key, numargs)
        expected = functions.SubtractionOperator
        print_test_message(testname, actual=actual, expected=expected, key=key, numargs=numargs)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_mul(self):
        key = '*'
        testname = 'find_operator({!r})'.format(key)
        actual = functions.find_operator(key)
        expected = functions.MultiplicationOperator
        print_test_message(testname, key=key, actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_div(self):
        key = '/'
        testname = 'find_operator({!r})'.format(key)
        actual = functions.find_operator(key)
        expected = functions.DivisionOperator
        print_test_message(testname, key=key, actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_pow(self):
        key = '**'
        testname = 'find_operator({!r})'.format(key)
        actual = functions.find_operator(key)
        expected = functions.PowerOperator
        print_test_message(testname, key=key, actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_key_failure(self):
        key = '?'
        testname = 'find_operator({!r})'.format(key)
        expected = KeyError
        print_test_message(testname, key=key, expected=expected)
        self.assertRaises(KeyError, functions.find_operator, key)

    def test_operator_numargs_failure(self):
        key = '*'
        numargs = 1
        testname = 'find_operator({!r}, {})'.format(key, numargs)
        expected = KeyError
        print_test_message(testname, key=key, numargs=numargs, expected=expected)
        self.assertRaises(KeyError, functions.find_operator, key, numargs)

    def test_function_sqrt(self):
        key = 'sqrt'
        testname = 'find_function({!r})'.format(key)
        actual = functions.find_function(key)
        expected = functions.SquareRootFunction
        print_test_message(testname, key=key, actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_function_key_failure(self):
        key = 'f'
        testname = 'find_function({!r})'.format(key)
        expected = KeyError
        print_test_message(testname, key=key, expected=expected)
        self.assertRaises(KeyError, functions.find_function, key)

    def test_sqrt(self):
        key = 'sqrt'
        testname = 'find({!r})'.format(key)
        actual = functions.find(key)
        expected = functions.SquareRootFunction
        print_test_message(testname, key=key, actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_mul(self):
        key = '*'
        testname = 'find({!r})'.format(key)
        actual = functions.find(key)
        expected = functions.MultiplicationOperator
        print_test_message(testname, key=key, actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))
        
    def test_key_failure(self):
        key = '?'
        testname = 'find({!r})'.format(key)
        expected = KeyError
        print_test_message(testname, key=key, expected=expected)
        self.assertRaises(KeyError, functions.find, key)

    def test_numargs_failure(self):
        key = '*'
        numargs = 3
        testname = 'find({!r}, {})'.format(key, numargs)
        expected = KeyError
        print_test_message(testname, key=key, numargs=numargs, expected=expected)
        self.assertRaises(KeyError, functions.find, key, numargs)

    def test_user_defined(self):
        class myfunc(functions.Function):
            key = 'myfunc'
            def __call__(self, x, y, z):
                return x

        key = 'myfunc'
        testname = 'find({})'.format(key)
        actual = functions.find(key)
        expected = myfunc
        print_test_message(testname, key=key, actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))
    
    def test_list_operators(self):
        testname = 'list_operators()'
        actual = functions.list_operators()
        expected = list(functions.__OPERATORS__.keys())
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_list_functions(self):
        testname = 'list_functions()'
        actual = functions.list_functions()
        expected = ['sqrt']
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        

#===============================================================================
# EvaluationTests
#===============================================================================
class EvaluationTests(unittest.TestCase):
    """
    Unit tests for evaluating functions and operators
    """

    def test_op_neg_int(self):
        key = '-'
        indata = 3
        testname = '({}{})'.format(key, indata)
        func = functions.find(key, 1)
        actual = func(indata)
        expected = op.neg(indata)
        print_test_message(testname, input=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_neg_float(self):
        key = '-'
        indata = 3.1
        testname = '({}{})'.format(key, indata)
        func = functions.find(key, 1)
        actual = func(indata)
        expected = op.neg(indata)
        print_test_message(testname, input=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_neg_physarray(self):
        key = '-'
        indata = PhysArray(3, units='m')
        testname = '({}{})'.format(key, indata)
        func = functions.find(key, 1)
        actual = func(indata)
        expected = PhysArray(-3, name='3', units='m')
        print_test_message(testname, input=indata, actual=actual, expected=expected)
        np.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))

    def test_op_add_int(self):
        key = '+'
        left = 2
        right = 3
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 5
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_add_float(self):
        key = '+'
        left = 2.4
        right = 3.2
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 5.6
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_add_physarray(self):
        key = '+'
        x = PhysArray(1.5, name='x', units='m')
        y = PhysArray(7.9, name='y', units='km')
        testname = '({} {} {})'.format(x, key, y)
        func = functions.find(key, 2)
        actual = func(x, y)
        expected = PhysArray(7901.5, name='(x+convert(y, from=km, to=m))', units='m')
        print_test_message(testname, actual=actual, expected=expected, x=x, y=y)
        self.assertEqual(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))

    def test_op_sub_int(self):
        key = '-'
        left = 2
        right = 3
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = -1
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_sub_float(self):
        key = '-'
        left = 2.4
        right = 3.2
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 2.4 - 3.2
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_sub_physarray(self):
        key = '-'
        x = PhysArray(1.5, name='x', units='m')
        y = PhysArray(7.9, name='y', units='km')
        testname = '({} {} {})'.format(x, key, y)
        func = functions.find(key, 2)
        actual = func(x, y)
        expected = PhysArray(-7898.5, name='(x-convert(y, from=km, to=m))', units='m')
        print_test_message(testname, actual=actual, expected=expected, x=x, y=y)
        self.assertEqual(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))

    def test_op_mul_int(self):
        key = '*'
        left = 2
        right = 3
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 6
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_mul_float(self):
        key = '*'
        left = 2.4
        right = 3.2
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 2.4 * 3.2
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_mul_physarray(self):
        key = '*'
        x = PhysArray(1.5, name='x', units='m')
        y = PhysArray(7.9, name='y', units='km')
        testname = '({} {} {})'.format(x, key, y)
        func = functions.find(key, 2)
        actual = func(x, y)
        expected = PhysArray(1.5 * 7.9, name='(x*y)', units='m-km')
        print_test_message(testname, actual=actual, expected=expected, x=x, y=y)
        self.assertEqual(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))

    def test_op_div_int(self):
        key = '/'
        left = 7
        right = 3
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 2
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_div_float(self):
        key = '/'
        left = 2.4
        right = 3.2
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 2.4 / 3.2
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_div_physarray(self):
        key = '/'
        x = PhysArray(1.5, name='x', units='m')
        y = PhysArray(7.9, name='y', units='km')
        testname = '({} {} {})'.format(x, key, y)
        func = functions.find(key, 2)
        actual = func(x, y)
        expected = PhysArray(1.5 / 7.9, name='(x/y)', units='0.001 1')
        print_test_message(testname, actual=actual, expected=expected, x=x, y=y)
        np.testing.assert_array_almost_equal(actual, expected, 16,
                                             '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))

    def test_op_pow_int(self):
        key = '**'
        left = 7
        right = 3
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 7 ** 3
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_pow_float(self):
        key = '**'
        left = 2.4
        right = 3.2
        testname = '({} {} {})'.format(left, key, right)
        func = functions.find(key, 2)
        actual = func(left, right)
        expected = 2.4 ** 3.2
        print_test_message(testname, actual=actual, expected=expected, left=left, right=right)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_pow_physarray(self):
        key = '**'
        x = PhysArray(4.3, name='x', units='m')
        y = PhysArray(2, name='y')
        testname = '({} {} {})'.format(x, key, y)
        func = functions.find(key, 2)
        actual = func(x, y)
        expected = PhysArray(4.3 ** 2, name='(x**y)', units=Unit('m') ** 2)
        print_test_message(testname, actual=actual, expected=expected, x=x, y=y)
        self.assertEqual(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))

    def test_func_sqrt_int(self):
        key = 'sqrt'
        indata = 4
        testname = '{}({})'.format(key, indata)
        func = functions.find(key)
        actual = func(indata)
        expected = np.sqrt(indata)
        print_test_message(testname, input=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))\

    def test_func_sqrt_float(self):
        key = 'sqrt'
        indata = 4.0
        testname = '{}({})'.format(key, indata)
        func = functions.find(key)
        actual = func(indata)
        expected = np.sqrt(indata)
        print_test_message(testname, input=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_func_sqrt_physarray(self):
        key = 'sqrt'
        indata = PhysArray([9.0, 16.0, 4.0], name='x', units='m^2')
        testname = '{}({})'.format(key, indata)
        func = functions.find(key)
        actual = func(indata)
        expected = PhysArray([3.0, 4.0, 2.0], name='sqrt(x)', units='m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        np.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
