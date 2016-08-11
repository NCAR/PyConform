"""
Physical Array Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import physicalarrays
from testutils import print_test_message
from cf_units import Unit

import unittest
import numpy


#===============================================================================
# PhysicalArrayTests
#===============================================================================
class PhysicalArrayTests(unittest.TestCase):
    """
    Unit tests for the physicalarrays.PhysicalArray class
    """

    def test_init_tuple(self):
        indata = (1, 2, 3)
        testname = 'PhysicalArray.__init__({})'.format(indata)
        X = physicalarrays.PhysicalArray(indata)
        actual = type(X)
        expected = physicalarrays.PhysicalArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_list(self):
        indata = [1, 2, 3]
        testname = 'PhysicalArray.__init__({})'.format(indata)
        X = physicalarrays.PhysicalArray(indata)
        actual = type(X)
        expected = physicalarrays.PhysicalArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_ndarray(self):
        indata = numpy.array([1, 2, 3], dtype=numpy.float64)
        testname = 'PhysicalArray.__init__({})'.format(indata)
        X = physicalarrays.PhysicalArray(indata)
        actual = type(X)
        expected = physicalarrays.PhysicalArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_dataarray(self):
        indata = physicalarrays.PhysicalArray([1, 2, 3])
        testname = 'PhysicalArray.__init__({})'.format(indata)
        X = physicalarrays.PhysicalArray(indata)
        actual = type(X)
        expected = physicalarrays.PhysicalArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_units_obj(self):
        nlist = range(3)
        indata = Unit('m')
        testname = 'PhysicalArray({}, cfunits={!r}).cfunits'.format(nlist, indata)
        X = physicalarrays.PhysicalArray(nlist, cfunits=indata)
        actual = X.cfunits
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_str(self):
        nlist = range(3)
        indata = 'm'
        testname = 'PhysicalArray({}, cfunits={!r}).cfunits'.format(nlist, indata)
        X = physicalarrays.PhysicalArray(nlist, cfunits=indata)
        actual = X.cfunits
        expected = Unit(indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_value_error(self):
        nlist = range(3)
        indata = []
        testname = 'PhysicalArray({}, cfunits={!r}).cfunits'.format(nlist, indata)
        expected = ValueError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, physicalarrays.PhysicalArray, nlist, cfunits=indata)

    def test_dimensions_default(self):
        nlist = range(3)
        testname = 'PhysicalArray({}).dimensions'.format(nlist)
        X = physicalarrays.PhysicalArray(nlist)
        actual = X.dimensions
        expected = (None,)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_tuple(self):
        nlist = range(3)
        indata = ('x',)
        testname = 'PhysicalArray({}, dimensions={!r}).dimensions'.format(nlist, indata)
        X = physicalarrays.PhysicalArray(nlist, dimensions=indata)
        actual = X.dimensions
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_type_error(self):
        nlist = range(3)
        indata = ['x']
        testname = 'PhysicalArray({}, dimensions={!r}).dimensions'.format(nlist, indata)
        expected = TypeError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, physicalarrays.PhysicalArray, nlist, dimensions=indata)

    def test_initialshape_default(self):
        nlist = range(3)
        testname = 'PhysicalArray({}).initialshape'.format(nlist)
        X = physicalarrays.PhysicalArray(nlist)
        actual = X.initialshape
        expected = numpy.shape(nlist)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_initialshape_tuple(self):
        nlist = range(3)
        indata = (5,)
        testname = 'PhysicalArray({}, initialshape={!r}).initialshape'.format(nlist, indata)
        X = physicalarrays.PhysicalArray(nlist, initialshape=indata)
        actual = X.initialshape
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_initialshape_getitem(self):
        indata = physicalarrays.PhysicalArray([1, 2, 3])
        testname = 'X[0:1].initialshape'.format(indata)
        X = indata[0:1]
        actual = X.initialshape
        expected = indata.initialshape
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_initialshape_getitem_eliminate_dim(self):
        indata = physicalarrays.PhysicalArray([[1, 2, 3], [4, 5, 6]])
        testname = 'X[1, 0:2].initialshape'.format(indata)
        X = indata[1, 0:2]
        actual = X.initialshape
        expected = indata.initialshape[1:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_units(self):
        indata = physicalarrays.PhysicalArray([1, 2, 3], cfunits='m')
        testname = 'PhysicalArray({}).cfunits'.format(indata)
        X = physicalarrays.PhysicalArray(indata)
        actual = X.cfunits
        expected = indata.cfunits
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_units_override(self):
        indata = physicalarrays.PhysicalArray([1, 2, 3], cfunits='m')
        testname = 'PhysicalArray({}, cfunits={}).cfunits'.format(indata, 'km')
        X = physicalarrays.PhysicalArray(indata, cfunits='km')
        actual = X.cfunits
        expected = Unit('km')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions(self):
        indata = physicalarrays.PhysicalArray([1, 2, 3], dimensions=('x',))
        testname = 'PhysicalArray({}).dimensions'.format(indata)
        X = physicalarrays.PhysicalArray(indata)
        actual = X.dimensions
        expected = indata.dimensions
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions_override(self):
        indata = physicalarrays.PhysicalArray([1, 2, 3], dimensions=('x',))
        testname = 'PhysicalArray({}, dimensions={}).dimensions'.format(indata, ('y',))
        X = physicalarrays.PhysicalArray(indata, dimensions=('y',))
        actual = X.dimensions
        expected = ('y',)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_initialshape(self):
        indata = physicalarrays.PhysicalArray([1, 2, 3])
        testname = 'PhysicalArray({}).initialshape'.format(indata)
        X = physicalarrays.PhysicalArray(indata)
        actual = X.initialshape
        expected = indata.initialshape
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_initialshape_override(self):
        indata = physicalarrays.PhysicalArray([1, 2, 3])
        testname = 'PhysicalArray({}, initialshape=(5,)).initialshape'.format(indata)
        X = physicalarrays.PhysicalArray(indata, initialshape=(5,))
        actual = X.initialshape
        expected = (5,)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_units(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], cfunits='m')
        Y = physicalarrays.PhysicalArray([4, 5, 6], cfunits='km')
        testname = 'X.__mul__(Y).cfunits'
        Z = X * Y
        actual = Z.cfunits
        expected = X.cfunits * Y.cfunits
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_dimensions_same(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], dimensions=('x',))
        Y = physicalarrays.PhysicalArray([4, 5, 6], dimensions=('x',))
        testname = 'X.__mul__(Y).dimensions'
        Z = X * Y
        actual = Z.dimensions
        expected = X.dimensions
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_mul_dimensions_diff(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], dimensions=('x',))
        Y = physicalarrays.PhysicalArray([4, 5, 6], dimensions=('y',))
        testname = 'X.__mul__(Y).dimensions'
        expected = physicalarrays.DimensionsError
        print_test_message(testname, expected=expected, X=X, Y=Y)
        self.assertRaises(expected, X.__mul__, Y)

    def test_add_units_same(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], cfunits='m')
        Y = physicalarrays.PhysicalArray([4, 5, 6], cfunits='m')
        testname = 'X.__add__(Y).cfunits'
        Z = X + Y
        actual = Z.cfunits
        expected = X.cfunits
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_add_units_diff(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], cfunits='m')
        Y = physicalarrays.PhysicalArray([4, 5, 6], cfunits='km')
        testname = 'X.__add__(Y).cfunits'
        expected = physicalarrays.UnitsError
        print_test_message(testname, expected=expected, X=X, Y=Y)
        self.assertRaises(expected, X.__add__, Y)

    def test_add_dimensions_same(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], dimensions=('x',))
        Y = physicalarrays.PhysicalArray([4, 5, 6], dimensions=('x',))
        testname = 'X.__add__(Y).dimensions'
        Z = X + Y
        actual = Z.dimensions
        expected = X.dimensions
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_add_dimensions_diff(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], dimensions=('x',))
        Y = physicalarrays.PhysicalArray([4, 5, 6], dimensions=('y',))
        testname = 'X.__add__(Y).dimensions'
        expected = physicalarrays.DimensionsError
        print_test_message(testname, expected=expected, X=X, Y=Y)
        self.assertRaises(expected, X.__add__, Y)

    def test_ufunc_add_units(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], cfunits='m')
        Y = physicalarrays.PhysicalArray([4, 5, 6], cfunits='km')
        testname = 'add(X, Y).cfunits'
        Z = numpy.add(X, Y)
        actual = Z.cfunits
        expected = X.cfunits
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_multiply_units(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], cfunits='m')
        Y = physicalarrays.PhysicalArray([4, 5, 6], cfunits='km')
        testname = 'multiply(X, Y).cfunits'
        Z = numpy.multiply(X, Y)
        actual = Z.cfunits
        expected = X.cfunits
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_add_dimensions(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], dimensions=('x',))
        Y = physicalarrays.PhysicalArray([4, 5, 6], dimensions=('y',))
        testname = 'add(X, Y).dimensions'
        Z = numpy.add(X, Y)
        actual = Z.dimensions
        expected = X.dimensions
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y, Z=Z)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_ufunc_multiply_dimensions(self):
        X = physicalarrays.PhysicalArray([1, 2, 3], dimensions=('x',))
        Y = physicalarrays.PhysicalArray([4, 5, 6], dimensions=('y',))
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
