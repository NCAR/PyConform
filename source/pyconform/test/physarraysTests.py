"""
Physical Array Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import physarrays
from testutils import print_test_message
from cf_units import Unit

import unittest
import numpy


#===============================================================================
# PhysArrayTests
#===============================================================================
class PhysArrayTests(unittest.TestCase):
    """
    Unit tests for the physarrays.PhysArray class
    """

    def test_init_tuple(self):
        indata = (1, 2, 3)
        testname = 'PhysArray.__init__({})'.format(indata)
        X = physarrays.PhysArray(indata)
        actual = type(X)
        expected = physarrays.PhysArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_list(self):
        indata = [1, 2, 3]
        testname = 'PhysArray.__init__({})'.format(indata)
        X = physarrays.PhysArray(indata)
        actual = type(X)
        expected = physarrays.PhysArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_ndarray(self):
        indata = numpy.array([1, 2, 3], dtype=numpy.float64)
        testname = 'PhysArray.__init__({})'.format(indata)
        X = physarrays.PhysArray(indata)
        actual = type(X)
        expected = physarrays.PhysArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_dataarray(self):
        indata = physarrays.PhysArray([1, 2, 3])
        testname = 'PhysArray.__init__({})'.format(indata)
        X = physarrays.PhysArray(indata)
        actual = type(X)
        expected = physarrays.PhysArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_units_obj(self):
        nlist = range(3)
        indata = Unit('m')
        testname = 'PhysArray({}, units={!r}).units'.format(nlist, indata)
        X = physarrays.PhysArray(nlist, units=indata)
        actual = X.units
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_str(self):
        nlist = range(3)
        indata = 'm'
        testname = 'PhysArray({}, units={!r}).units'.format(nlist, indata)
        X = physarrays.PhysArray(nlist, units=indata)
        actual = X.units
        expected = Unit(indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_value_error(self):
        nlist = range(3)
        indata = []
        testname = 'PhysArray({}, units={!r}).units'.format(nlist, indata)
        expected = ValueError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, physarrays.PhysArray, nlist, units=indata)

    def test_dimensions_default(self):
        nlist = range(3)
        testname = 'PhysArray({}).dimensions'.format(nlist)
        X = physarrays.PhysArray(nlist)
        actual = X.dimensions
        expected = (0,)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_tuple(self):
        nlist = range(3)
        indata = ('x',)
        testname = 'PhysArray({}, dimensions={!r}).dimensions'.format(nlist, indata)
        X = physarrays.PhysArray(nlist, dimensions=indata)
        actual = X.dimensions
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_type_error(self):
        nlist = range(3)
        indata = ['x']
        testname = 'PhysArray({}, dimensions={!r}).dimensions'.format(nlist, indata)
        expected = TypeError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, physarrays.PhysArray, nlist, dimensions=indata)

    def test_initialshape_default(self):
        nlist = range(3)
        testname = 'PhysArray({})._shape'.format(nlist)
        X = physarrays.PhysArray(nlist)
        actual = X._shape
        expected = numpy.shape(nlist)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_initialshape_tuple(self):
        nlist = range(3)
        indata = (5,)
        testname = 'PhysArray({}, _shape={!r})._shape'.format(nlist, indata)
        X = physarrays.PhysArray(nlist, _shape=indata)
        actual = X._shape
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_initialshape_getitem(self):
        indata = physarrays.PhysArray([1, 2, 3])
        testname = 'X[0:1]._shape'.format(indata)
        X = indata[0:1]
        actual = X._shape
        expected = indata._shape
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_initialshape_getitem_eliminate_dim(self):
        indata = physarrays.PhysArray([[1, 2, 3], [4, 5, 6]])
        testname = 'X[1, 0:2]._shape'.format(indata)
        X = indata[1, 0:2]
        actual = X._shape
        expected = indata._shape
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_units(self):
        indata = physarrays.PhysArray([1, 2, 3], units='m')
        testname = 'PhysArray({}).units'.format(indata)
        X = physarrays.PhysArray(indata)
        actual = X.units
        expected = indata.units
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_units_override(self):
        indata = physarrays.PhysArray([1, 2, 3], units='m')
        testname = 'PhysArray({}, units={}).units'.format(indata, 'km')
        X = physarrays.PhysArray(indata, units='km')
        actual = X.units
        expected = Unit('km')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions(self):
        indata = physarrays.PhysArray([1, 2, 3], dimensions=('x',))
        testname = 'PhysArray({}).dimensions'.format(indata)
        X = physarrays.PhysArray(indata)
        actual = X.dimensions
        expected = indata.dimensions
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions_override(self):
        indata = physarrays.PhysArray([1, 2, 3], dimensions=('x',))
        testname = 'PhysArray({}, dimensions={}).dimensions'.format(indata, ('y',))
        X = physarrays.PhysArray(indata, dimensions=('y',))
        actual = X.dimensions
        expected = ('y',)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_initialshape(self):
        indata = physarrays.PhysArray([1, 2, 3])
        testname = 'PhysArray({})._shape'.format(indata)
        X = physarrays.PhysArray(indata)
        actual = X._shape
        expected = indata._shape
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_initialshape_override(self):
        indata = physarrays.PhysArray([1, 2, 3])
        testname = 'PhysArray({}, _shape=(5,))._shape'.format(indata)
        X = physarrays.PhysArray(indata, _shape=(5,))
        actual = X._shape
        expected = (5,)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_units(self):
        X = physarrays.PhysArray([1, 2, 3], units='m')
        Y = physarrays.PhysArray([4, 5, 6], units='km')
        testname = 'X.__mul__(Y).units'
        Z = X * Y
        actual = Z.units
        expected = X.units * Y.units
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_dimensions_same(self):
        X = physarrays.PhysArray([1, 2, 3], dimensions=('x',))
        Y = physarrays.PhysArray([4, 5, 6], dimensions=('x',))
        testname = 'X.__mul__(Y).dimensions'
        Z = X * Y
        actual = Z.dimensions
        expected = X.dimensions
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_dimensions_diff(self):
        X = physarrays.PhysArray([1, 2, 3], dimensions=('x',))
        Y = physarrays.PhysArray([4, 5, 6], dimensions=('y',))
        testname = 'X.__mul__(Y).dimensions'
        expected = physarrays.DimensionsError
        print_test_message(testname, expected=expected, X=X, Y=Y)
        self.assertRaises(expected, X.__mul__, Y)

    def test_add_units_same(self):
        X = physarrays.PhysArray([1, 2, 3], units='m')
        Y = physarrays.PhysArray([4, 5, 6], units='m')
        testname = 'X.__add__(Y).units'
        Z = X + Y
        actual = Z.units
        expected = X.units
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_add_units_diff(self):
        X = physarrays.PhysArray([1, 2, 3], units='m')
        Y = physarrays.PhysArray([4, 5, 6], units='km')
        testname = 'X.__add__(Y).units'
        expected = physarrays.UnitsError
        print_test_message(testname, expected=expected, X=X, Y=Y)
        self.assertRaises(expected, X.__add__, Y)

    def test_add_dimensions_same(self):
        X = physarrays.PhysArray([1, 2, 3], dimensions=('x',))
        Y = physarrays.PhysArray([4, 5, 6], dimensions=('x',))
        testname = 'X.__add__(Y).dimensions'
        Z = X + Y
        actual = Z.dimensions
        expected = X.dimensions
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_add_dimensions_diff(self):
        X = physarrays.PhysArray([1, 2, 3], dimensions=('x',))
        Y = physarrays.PhysArray([4, 5, 6], dimensions=('y',))
        testname = 'X.__add__(Y).dimensions'
        expected = physarrays.DimensionsError
        print_test_message(testname, expected=expected, X=X, Y=Y)
        self.assertRaises(expected, X.__add__, Y)

    def test_ufunc_add_units(self):
        X = physarrays.PhysArray([1, 2, 3], units='m')
        Y = physarrays.PhysArray([4, 5, 6], units='km')
        testname = 'add(X, Y).units'
        Z = numpy.add(X, Y)
        actual = Z.units
        expected = X.units
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_multiply_units(self):
        X = physarrays.PhysArray([1, 2, 3], units='m')
        Y = physarrays.PhysArray([4, 5, 6], units='km')
        testname = 'multiply(X, Y).units'
        Z = numpy.multiply(X, Y)
        actual = Z.units
        expected = X.units
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_add_dimensions(self):
        X = physarrays.PhysArray([1, 2, 3], dimensions=('x',))
        Y = physarrays.PhysArray([4, 5, 6], dimensions=('y',))
        testname = 'add(X, Y).dimensions'
        Z = numpy.add(X, Y)
        actual = Z.dimensions
        expected = X.dimensions
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_multiply_dimensions(self):
        X = physarrays.PhysArray([1, 2, 3], dimensions=('x',))
        Y = physarrays.PhysArray([4, 5, 6], dimensions=('y',))
        testname = 'multiply(X, Y).dimensions'
        Z = numpy.multiply(X, Y)
        actual = Z.dimensions
        expected = X.dimensions
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
