"""
Data Flow Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import dataarrays
from testutils import print_test_message
from cf_units import Unit

import unittest
import numpy


#===============================================================================
# DataArrayTests
#===============================================================================
class DataArrayTests(unittest.TestCase):
    """
    Unit tests for the dataarrays.DataArray class
    """

    def test_init_tuple(self):
        indata = (1, 2, 3)
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataarrays.DataArray(indata)
        actual = type(A)
        expected = dataarrays.DataArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(A, expected, '{} failed'.format(testname))

    def test_init_list(self):
        indata = [1, 2, 3]
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataarrays.DataArray(indata)
        actual = type(A)
        expected = dataarrays.DataArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(A, expected, '{} failed'.format(testname))

    def test_init_ndarray(self):
        indata = numpy.array([1, 2, 3], dtype=numpy.float64)
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataarrays.DataArray(indata)
        actual = type(A)
        expected = dataarrays.DataArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(A, expected, '{} failed'.format(testname))

    def test_init_dataarray(self):
        indata = dataarrays.DataArray([1, 2, 3])
        testname = 'DataArray.__init__({})'.format(indata)
        A = dataarrays.DataArray(indata)
        actual = type(A)
        expected = dataarrays.DataArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(A, expected, '{} failed'.format(testname))

    def test_units_obj(self):
        nlist = range(3)
        indata = Unit('m')
        testname = 'DataArray({}, cfunits={!r}).cfunits'.format(nlist, indata)
        A = dataarrays.DataArray(nlist, cfunits=indata)
        actual = A.cfunits
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_str(self):
        nlist = range(3)
        indata = 'm'
        testname = 'DataArray({}, cfunits={!r}).cfunits'.format(nlist, indata)
        A = dataarrays.DataArray(nlist, cfunits=indata)
        actual = A.cfunits
        expected = Unit(indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_value_error(self):
        nlist = range(3)
        indata = []
        testname = 'DataArray({}, cfunits={!r}).cfunits'.format(nlist, indata)
        expected = ValueError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, dataarrays.DataArray, nlist, cfunits=indata)

    def test_dimensions_default(self):
        nlist = range(3)
        testname = 'DataArray({}).dimensions'.format(nlist)
        A = dataarrays.DataArray(nlist)
        actual = A.dimensions
        expected = (None,)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_tuple(self):
        nlist = range(3)
        indata = ('x',)
        testname = 'DataArray({}, dimensions={!r}).dimensions'.format(nlist, indata)
        A = dataarrays.DataArray(nlist, dimensions=indata)
        actual = A.dimensions
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_type_error(self):
        nlist = range(3)
        indata = ['x']
        testname = 'DataArray({}, dimensions={!r}).dimensions'.format(nlist, indata)
        expected = TypeError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, dataarrays.DataArray, nlist, dimensions=indata)

    def test_cast_units(self):
        indata = dataarrays.DataArray([1, 2, 3], cfunits='m')
        testname = 'DataArray({}).cfunits'.format(indata)
        A = dataarrays.DataArray(indata)
        actual = A.cfunits
        expected = indata.cfunits
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_units_override(self):
        indata = dataarrays.DataArray([1, 2, 3], cfunits='m')
        testname = 'DataArray({}, cfunits={}).cfunits'.format(indata, 'km')
        A = dataarrays.DataArray(indata, cfunits='km')
        actual = A.cfunits
        expected = Unit('km')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions(self):
        indata = dataarrays.DataArray([1, 2, 3], dimensions=('x',))
        testname = 'DataArray({}).dimensions'.format(indata)
        A = dataarrays.DataArray(indata)
        actual = A.dimensions
        expected = indata.dimensions
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions_override(self):
        indata = dataarrays.DataArray([1, 2, 3], dimensions=('x',))
        testname = 'DataArray({}, dimensions={}).dimensions'.format(indata, ('y',))
        A = dataarrays.DataArray(indata, dimensions=('y',))
        actual = A.dimensions
        expected = ('y',)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_units(self):
        A = dataarrays.DataArray([1, 2, 3], cfunits='m')
        B = dataarrays.DataArray([4, 5, 6], cfunits='km')
        testname = 'DataArray.__mul__(...).cfunits'
        C = A * B
        actual = C.cfunits
        expected = A.cfunits
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_dimensions(self):
        A = dataarrays.DataArray([1, 2, 3], dimensions=('x',))
        B = dataarrays.DataArray([4, 5, 6], dimensions=('y',))
        testname = 'DataArray.__mul__(...).dimensions'
        C = A * B
        actual = C.dimensions
        expected = A.dimensions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_add_units(self):
        A = dataarrays.DataArray([1, 2, 3], cfunits='m')
        B = dataarrays.DataArray([4, 5, 6], cfunits='km')
        testname = 'DataArray.__add__(...).cfunits'
        C = A + B
        actual = C.cfunits
        expected = A.cfunits
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_add_dimensions(self):
        A = dataarrays.DataArray([1, 2, 3], dimensions=('x',))
        B = dataarrays.DataArray([4, 5, 6], dimensions=('y',))
        testname = 'DataArray.__add__(...).dimensions'
        C = A + B
        actual = C.dimensions
        expected = A.dimensions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_add_units(self):
        A = dataarrays.DataArray([1, 2, 3], cfunits='m')
        B = dataarrays.DataArray([4, 5, 6], cfunits='km')
        testname = 'add(DataArray, DataArray).cfunits'
        C = numpy.add(A, B)
        actual = C.cfunits
        expected = A.cfunits
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_multiply_units(self):
        A = dataarrays.DataArray([1, 2, 3], cfunits='m')
        B = dataarrays.DataArray([4, 5, 6], cfunits='km')
        testname = 'multiply(DataArray, DataArray).cfunits'
        C = numpy.multiply(A, B)
        actual = C.cfunits
        expected = A.cfunits
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_add_dimensions(self):
        A = dataarrays.DataArray([1, 2, 3], dimensions=('x',))
        B = dataarrays.DataArray([4, 5, 6], dimensions=('y',))
        testname = 'add(DataArray, DataArray).dimensions'
        C = numpy.add(A, B)
        actual = C.dimensions
        expected = A.dimensions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_multiply_dimensions(self):
        A = dataarrays.DataArray([1, 2, 3], dimensions=('x',))
        B = dataarrays.DataArray([4, 5, 6], dimensions=('y',))
        testname = 'multiply(DataArray, DataArray).dimensions'
        C = numpy.multiply(A, B)
        actual = C.dimensions
        expected = A.dimensions
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
