"""
Functions Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import functions
from pyconform.physarrays import PhysArray
from cf_units import Unit
from testutils import print_test_message

import unittest
import numpy as np
import operator as op


#===============================================================================
# FindTests
#===============================================================================
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
        key = '^'
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

    def test_function_numargs_failure(self):
        key = 'sqrt'
        numargs = 2
        testname = 'find_function({!r}, {})'.format(key, numargs)
        expected = KeyError
        print_test_message(testname, key=key, numargs=numargs, expected=expected)
        self.assertRaises(KeyError, functions.find_function, key, numargs)

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
            numargs = 3
            def __call__(self, x, y, z):
                return x

        key = 'myfunc'
        testname = 'find({})'.format(key)
        actual = functions.find(key)
        expected = myfunc
        print_test_message(testname, key=key, actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

#===============================================================================
# EvaluationTests
#===============================================================================
class EvaluationTests(unittest.TestCase):
    """
    Unit tests for evaluating functions and operators
    """

    def test_op_neg_float(self):
        key = '-'
        indata = (3.1,)
        testname = '({}{})'.format(key, indata[0])
        func = functions.find(key, 1)
        actual = func(*indata)
        expected = op.neg(*indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_sub_float(self):
        key = '-'
        indata = (2.4, 3.2)
        testname = '({} {} {})'.format(indata[0], key, indata[1])
        func = functions.find(key, 2)
        actual = func(*indata)
        expected = op.sub(*indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_op_mul_float(self):
        key = '*'
        indata = (2.4, 3.2)
        testname = '({} {} {})'.format(indata[0], key, indata[1])
        func = functions.find(key)
        actual = func(*indata)
        expected = op.mul(*indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_func_sqrt_float(self):
        key = 'sqrt'
        indata = (4.0,)
        testname = '{}{}'.format(key, *indata)
        func = functions.find(key)
        actual = func(*indata)
        expected = np.sqrt(*indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_func_convert_float(self):
        key = 'convert'
        indata = (0.1, Unit(0.1))
        testname = '{}({}, to={})'.format(key, *indata)
        func = functions.find(key)
        actual = func(*indata)
        expected = 1.0
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_func_transpose_array(self):
        key = 'transpose'
        indata = (PhysArray(np.array([[1, 2, 3], [4, 5, 6]]), dimensions=('x', 'y')), ('y', 'x'))
        testname = '{}({}, to={})'.format(key, *indata)
        func = functions.find(key)
        actual = func(*indata)
        expected = PhysArray(np.array([[1, 4], [2, 5], [3, 6]]), dimensions=('x', 'y'))
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        np.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))


#===============================================================================
# UnitsTests
#===============================================================================
class UnitsTests(unittest.TestCase):
    """
    Unit tests for evaluating functions and operators units
    """

    def test_units_neg_1(self):
        indata = 1
        testname = 'NegationOperator().units'
        func = functions.NegationOperator()
        actual = func(indata).units
        expected = Unit(1)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_neg_m(self):
        indata = PhysArray(5.0, units=Unit('m'))
        testname = 'NegationOperator().units'
        func = functions.NegationOperator()
        actual = func(indata).units
        expected = indata.units
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_add_m_m(self):
        indata = (PhysArray(1.0, units=Unit('m')), PhysArray(2.0, units=Unit('m')))
        testname = 'AdditionOperator().units'
        func = functions.AdditionOperator()
        actual = func(*indata).units
        expected = Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_add_m_km(self):
        indata = (PhysArray(1.0, units=Unit('m')), PhysArray(2.0, units=Unit('km')))
        testname = 'AdditionOperator().units'
        func = functions.AdditionOperator()
        actual = func(*indata).units
        expected = Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_mul_m_m(self):
        indata = (PhysArray(1.0, units=Unit('m')), PhysArray(2.0, units=Unit('m')))
        testname = 'MultiplicationOperator().units'
        func = functions.MultiplicationOperator()
        actual = func(*indata).units
        expected = Unit('m^2')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_mul_1_m(self):
        indata = (1, PhysArray(1.0, units=Unit('m')))
        testname = 'MultiplicationOperator().units'
        func = functions.MultiplicationOperator()
        actual = func(*indata).units
        expected = Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_div_1_m(self):
        indata = (1, PhysArray(1.0, units=Unit('m')))
        testname = 'DivisionOperator().units'
        func = functions.DivisionOperator()
        actual = func(*indata).units
        expected = Unit(1) / Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_sqrt_m2(self):
        indata = (PhysArray(4.0, units=Unit('m^2')),)
        testname = 'SquareRootFunction().units'
        func = functions.SquareRootFunction()
        actual = func(*indata).units
        expected = Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
