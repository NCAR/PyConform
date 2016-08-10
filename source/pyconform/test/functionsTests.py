"""
Functions Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import functions
from pyconform.dataarrays import DataArray
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
        indata = ('-', 1)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.NegationOperator
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_add(self):
        indata = ('+', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.AdditionOperator
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_sub(self):
        indata = ('-', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.SubtractionOperator
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_mul(self):
        indata = ('*', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.MultiplicationOperator
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_div(self):
        indata = ('/', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.DivisionOperator
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_pow(self):
        indata = ('^', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        actual = functions.find_operator(*indata)
        expected = functions.PowerOperator
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_operator_key_failure(self):
        indata = ('?', 2)
        testname = 'find_operator({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find_operator, *indata)

    def test_operator_numargs_failure(self):
        indata = ('*', 1)
        testname = 'find_operator({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find_operator, *indata)

    def test_function_sqrt(self):
        indata = ('sqrt', 1)
        testname = 'find_function({!r}, {})'.format(*indata)
        actual = functions.find_function(*indata)
        expected = functions.SquareRootFunction
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_function_key_failure(self):
        indata = ('f', 1)
        testname = 'find_function({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find_function, *indata)

    def test_function_numargs_failure(self):
        indata = ('sqrt', 2)
        testname = 'find_function({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find_function, *indata)

    def test_sqrt(self):
        indata = ('sqrt', 1)
        testname = 'find({!r}, {})'.format(*indata)
        actual = functions.find(*indata)
        expected = functions.SquareRootFunction
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_mul(self):
        indata = ('*', 2)
        testname = 'find({!r}, {})'.format(*indata)
        actual = functions.find(*indata)
        expected = functions.MultiplicationOperator
        print_test_message(testname, indata=indata,
                           actual=actual, expected=expected)
        self.assertIsInstance(actual, expected, '{} failed'.format(testname))

    def test_failure(self):
        indata = ('*', 3)
        testname = 'find({!r}, {})'.format(*indata)
        expected = KeyError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(KeyError, functions.find, *indata)

    def test_user_defined(self):
        class myfunc(functions.Function):
            key = 'myfunc'
            numargs = 3
            def __call__(self, x, y, z):
                return x

        indata = 'myfunc'
        testname = 'find({})'.format(indata)
        actual = functions.find(indata)
        expected = myfunc
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
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
        key = 'C'
        indata = (0.1, Unit(0.1))
        testname = '{}({}, to={})'.format(key, *indata)
        func = functions.find(key)
        actual = func(*indata)
        expected = 1.0
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_func_transpose_array(self):
        key = 'T'
        indata = (DataArray(np.array([[1, 2, 3], [4, 5, 6]]), dimensions=('x', 'y')), ('y', 'x'))
        testname = '{}({}, to={})'.format(key, *indata)
        func = functions.find(key)
        actual = func(*indata)
        expected = DataArray(np.array([[1, 4], [2, 5], [3, 6]]), dimensions=('x', 'y'))
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
        testname = 'NegationOperator().cfunits'
        func = functions.NegationOperator()
        actual = func(indata).cfunits
        expected = Unit(1)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_neg_m(self):
        indata = DataArray(5.0, cfunits=Unit('m'))
        testname = 'NegationOperator().cfunits'
        func = functions.NegationOperator()
        actual = func(indata).cfunits
        expected = indata.cfunits
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_add_m_m(self):
        indata = (DataArray(1.0, cfunits=Unit('m')), DataArray(2.0, cfunits=Unit('m')))
        testname = 'AdditionOperator().cfunits'
        func = functions.AdditionOperator()
        actual = func(*indata).cfunits
        expected = Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_add_m_km(self):
        indata = (DataArray(1.0, cfunits=Unit('m')), DataArray(2.0, cfunits=Unit('km')))
        testname = 'AdditionOperator().cfunits'
        func = functions.AdditionOperator()
        expected = functions.UnitsError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(expected, func, *indata)

    def test_units_mul_m_m(self):
        indata = (DataArray(1.0, cfunits=Unit('m')), DataArray(2.0, cfunits=Unit('m')))
        testname = 'MultiplicationOperator().cfunits'
        func = functions.MultiplicationOperator()
        actual = func(*indata).cfunits
        expected = Unit('m^2')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_mul_1_m(self):
        indata = (1, DataArray(1.0, cfunits=Unit('m')))
        testname = 'MultiplicationOperator().cfunits'
        func = functions.MultiplicationOperator()
        actual = func(*indata).cfunits
        expected = Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_div_1_m(self):
        indata = (1, DataArray(1.0, cfunits=Unit('m')))
        testname = 'DivisionOperator().cfunits'
        func = functions.DivisionOperator()
        actual = func(*indata).cfunits
        expected = Unit(1) / Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_sqrt_m2(self):
        indata = (DataArray(4.0, cfunits=Unit('m^2')),)
        testname = 'SquareRootFunction().cfunits'
        func = functions.SquareRootFunction()
        actual = func(*indata).cfunits
        expected = Unit('m')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
