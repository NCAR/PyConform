"""
Data Flow Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import dataflows
from testutils import print_test_message
from cf_units import Unit

import unittest
import numpy


#===============================================================================
# DataArrayTests
#===============================================================================
class DataArrayTests(unittest.TestCase):
    """
    Unit tests for the dataflows.DataArray class
    """

    def test_init_tuple(self):
        indata = (1, 2, 3)
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataflows.DataArray(indata)
        actual = type(A)
        expected = dataflows.DataArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(A, expected, '{} failed'.format(testname))

    def test_init_list(self):
        indata = [1, 2, 3]
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataflows.DataArray(indata)
        actual = type(A)
        expected = dataflows.DataArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(A, expected, '{} failed'.format(testname))

    def test_init_ndarray(self):
        indata = numpy.array([1, 2, 3], dtype=numpy.float64)
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataflows.DataArray(indata)
        actual = type(A)
        expected = dataflows.DataArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(A, expected, '{} failed'.format(testname))

    def test_init_dataarray(self):
        indata = dataflows.DataArray([1, 2, 3])
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataflows.DataArray(indata)
        actual = type(A)
        expected = dataflows.DataArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(A, expected, '{} failed'.format(testname))

    def test_units_obj(self):
        nlist = range(3)
        indata = Unit('m')
        testname = 'DataArray.__init__({}, units={!r})'.format(nlist, indata)
        A = dataflows.DataArray(nlist, units=indata)
        actual = A.units
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_str(self):
        nlist = range(3)
        indata = 'm'
        testname = 'DataArray.__init__({}, units={!r})'.format(nlist, indata)
        A = dataflows.DataArray(nlist, units=indata)
        actual = A.units
        expected = Unit(indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_value_error(self):
        nlist = range(3)
        indata = []
        testname = 'DataArray.__init__({}, units={!r})'.format(nlist, indata)
        expected = ValueError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, dataflows.DataArray, nlist, units=indata)

    def test_dimensions_default(self):
        nlist = range(3)
        testname = 'DataArray.__init__({})'.format(nlist)
        A = dataflows.DataArray(nlist)
        actual = A.dimensions
        expected = (None,)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_tuple(self):
        nlist = range(3)
        indata = ('x',)
        testname = 'DataArray.__init__({}, dimensions={!r})'.format(nlist, indata)
        A = dataflows.DataArray(nlist, dimensions=indata)
        actual = A.dimensions
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_type_error(self):
        nlist = range(3)
        indata = ['x']
        testname = 'DataArray.__init__({}, dimensions={!r})'.format(nlist, indata)
        expected = TypeError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, dataflows.DataArray, nlist, dimensions=indata)

    def test_cast_units(self):
        indata = dataflows.DataArray([1, 2, 3], units='m')
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataflows.DataArray(indata)
        actual = A.units
        expected = indata.units
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions(self):
        indata = dataflows.DataArray([1, 2, 3], dimensions=('x',))
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataflows.DataArray(indata)
        actual = A.dimensions
        expected = indata.dimensions
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_units(self):
        A = dataflows.DataArray([1, 2, 3], units='m')
        B = dataflows.DataArray([4, 5, 6], units='km')
        testname = 'DataArray.__mul__(...).units'
        C = A * B
        actual = C.units
        expected = A.units
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_dimensions(self):
        A = dataflows.DataArray([1, 2, 3], dimensions=('x',))
        B = dataflows.DataArray([4, 5, 6], dimensions=('y',))
        testname = 'DataArray.__mul__(...).dimensions'
        C = A * B
        actual = C.dimensions
        expected = A.dimensions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_add_units(self):
        A = dataflows.DataArray([1, 2, 3], units='m')
        B = dataflows.DataArray([4, 5, 6], units='km')
        testname = 'DataArray.__add__(...).units'
        C = A + B
        actual = C.units
        expected = A.units
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_add_dimensions(self):
        A = dataflows.DataArray([1, 2, 3], dimensions=('x',))
        B = dataflows.DataArray([4, 5, 6], dimensions=('y',))
        testname = 'DataArray.__add__(...).dimensions'
        C = A + B
        actual = C.dimensions
        expected = A.dimensions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_add_units(self):
        A = dataflows.DataArray([1, 2, 3], units='m')
        B = dataflows.DataArray([4, 5, 6], units='km')
        testname = 'add(DataArray, DataArray).units'
        C = numpy.add(A, B)
        actual = C.units
        expected = A.units
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_multiply_units(self):
        A = dataflows.DataArray([1, 2, 3], units='m')
        B = dataflows.DataArray([4, 5, 6], units='km')
        testname = 'multiply(DataArray, DataArray).units'
        C = numpy.multiply(A, B)
        actual = C.units
        expected = A.units
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_add_dimensions(self):
        A = dataflows.DataArray([1, 2, 3], dimensions=('x',))
        B = dataflows.DataArray([4, 5, 6], dimensions=('y',))
        testname = 'add(DataArray, DataArray).dimensions'
        C = numpy.add(A, B)
        actual = C.dimensions
        expected = A.dimensions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_multiply_dimensions(self):
        A = dataflows.DataArray([1, 2, 3], dimensions=('x',))
        B = dataflows.DataArray([4, 5, 6], dimensions=('y',))
        testname = 'multiply(DataArray, DataArray).dimensions'
        C = numpy.multiply(A, B)
        actual = C.dimensions
        expected = A.dimensions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===================================================================================================
# DataNodeTests
#===================================================================================================
class DataNodeTests(unittest.TestCase):
    """
    Unit tests for the dataflows.DataNode class
    """

    def test_init(self):
        indata = lambda: 1
        testname = 'DataNode.__init__({})'.format(indata)
        N = dataflows.DataNode(0, indata)
        actual = type(N)
        expected = dataflows.DataNode
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(N, expected, '{} failed'.format(testname))

    def test_label(self):
        indata = 'abcd'
        testname = 'DataNode(..., label={}).label'.format(indata)
        N = dataflows.DataNode(indata, lambda i: i, 1)
        actual = N.label
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem(self):
        indata = dataflows.DataArray(range(10), units='m', dimensions=('x',))
        testname = 'DataNode.__getitem__(:)'
        N = dataflows.DataNode(0, lambda x: x, indata)
        actual = N[:]
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = dataflows.DataArray(range(10), units='m', dimensions=('x',))
        testname = 'DataNode.__getitem__(:5)'
        N = dataflows.DataNode(0, lambda x: x, indata)
        actual = N[:5]
        expected = indata[:5]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add(self):
        d1 = dataflows.DataArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = dataflows.DataArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = dataflows.DataNode(1, lambda x: x, d1)
        N2 = dataflows.DataNode(2, lambda x: x, d2)
        N3 = dataflows.DataNode(3, lambda a, b: a + b, N1, N2)
        testname = 'DataNode.__getitem__()'
        actual = N3[:]
        expected = d1 + d2
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add_slice(self):
        d1 = dataflows.DataArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = dataflows.DataArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = dataflows.DataNode(1, lambda x: x, d1)
        N2 = dataflows.DataNode(2, lambda x: x, d2)
        N3 = dataflows.DataNode(3, lambda a, b: a + b, N1, N2)
        testname = 'DataNode.__getitem__()'
        actual = N3[:2]
        expected = d1[:2] + d2[:2]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
