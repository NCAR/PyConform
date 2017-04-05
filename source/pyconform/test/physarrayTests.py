"""
Physical Array Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import physarray
from testutils import print_test_message
from cf_units import Unit

import unittest
import numpy


#===============================================================================
# PhysArrayTests
#===============================================================================
class PhysArrayTests(unittest.TestCase):
    """
    Unit tests for the physarray.PhysArray class
    """

    def test_init_tuple(self):
        indata = (1, 2, 3)
        testname = 'PhysArray.__init__({})'.format(indata)
        X = physarray.PhysArray(indata, name='X')
        actual = type(X)
        expected = physarray.PhysArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_list(self):
        indata = [1, 2, 3]
        testname = 'PhysArray.__init__({})'.format(indata)
        X = physarray.PhysArray(indata, name='X')
        actual = type(X)
        expected = physarray.PhysArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_ndarray(self):
        indata = numpy.array([1, 2, 3], dtype=numpy.float64)
        testname = 'PhysArray.__init__({})'.format(indata)
        X = physarray.PhysArray(indata, name='X')
        actual = type(X)
        expected = physarray.PhysArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_physarray(self):
        indata = physarray.PhysArray([1, 2, 3])
        testname = 'PhysArray.__init__({})'.format(indata)
        X = physarray.PhysArray(indata, name='X')
        actual = type(X)
        expected = physarray.PhysArray
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_units_obj(self):
        nlist = range(3)
        indata = Unit('m')
        testname = 'PhysArray({}, units={!r}).units'.format(nlist, indata)
        X = physarray.PhysArray(nlist, units=indata, name='X')
        actual = X.units
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_units_str(self):
        nlist = range(3)
        indata = 'm'
        testname = 'PhysArray({}, units={!r}).units'.format(nlist, indata)
        X = physarray.PhysArray(nlist, units=indata, name='X')
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
        self.assertRaises(expected, physarray.PhysArray, nlist, units=indata, name='X')

    def test_dimensions_default(self):
        nlist = range(3)
        testname = 'PhysArray({}).dimensions'.format(nlist)
        X = physarray.PhysArray(nlist, name='X')
        actual = X.dimensions
        expected = (0,)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_tuple(self):
        nlist = range(3)
        indata = ('x',)
        testname = 'PhysArray({}, dimensions={!r}).dimensions'.format(nlist, indata)
        X = physarray.PhysArray(nlist, dimensions=indata, name='X')
        actual = X.dimensions
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_list(self):
        nlist = range(3)
        indata = ['x']
        testname = 'PhysArray({}, dimensions={!r}).dimensions'.format(nlist, indata)
        X = physarray.PhysArray(nlist, dimensions=indata, name='X')
        actual = X.dimensions
        expected = tuple(indata)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_positive_default(self):
        nlist = range(3)
        testname = 'PhysArray({}).positive'.format(nlist)
        X = physarray.PhysArray(nlist, name='X')
        actual = X.positive
        expected = None
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_positive_none(self):
        nlist = range(3)
        indata = None
        testname = 'PhysArray({}, positive={!r}).positive'.format(nlist, indata)
        X = physarray.PhysArray(nlist, positive=indata, name='X')
        actual = X.positive
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_positive_valid_str(self):
        nlist = range(3)
        valid_indata = ['up', 'Up', 'UP', 'down', 'Down', 'DOWN', 'doWN']
        for indata in valid_indata:
            testname = 'PhysArray({}, positive={!r}).positive'.format(nlist, indata)
            X = physarray.PhysArray(nlist, positive=indata, name='X')
            actual = X.positive
            expected = indata.lower()
            print_test_message(testname, actual=actual, expected=expected)
            self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_positive_invalid(self):
        nlist = range(3)
        invalid_indata = ['x', 'y', 1, -1.0]
        for indata in invalid_indata:
            testname = 'PhysArray({}, positive={!r}).positive'.format(nlist, indata)
            expected = ValueError
            print_test_message(testname, expected=expected)
            self.assertRaises(expected, physarray.PhysArray, nlist, positive=indata, name='X')

    def test_cast_name(self):
        indata = physarray.PhysArray([1, 2, 3], name='X')
        testname = 'PhysArray({}).dimensions'.format(indata)
        X = physarray.PhysArray(indata)
        actual = X.name
        expected = indata.name
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_name_override(self):
        indata = physarray.PhysArray([1, 2, 3], name='A')
        testname = 'PhysArray({}).dimensions'.format(indata)
        X = physarray.PhysArray(indata, name='X')
        actual = X.name
        expected = 'X'
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_units(self):
        indata = physarray.PhysArray([1, 2, 3], name='X', units='m')
        testname = 'PhysArray({}).units'.format(indata)
        X = physarray.PhysArray(indata)
        actual = X.units
        expected = indata.units
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_units_override(self):
        indata = physarray.PhysArray([1, 2, 3], name='X', units='m')
        testname = 'PhysArray({}, units={}).units'.format(indata, 'km')
        X = physarray.PhysArray(indata, units='km')
        actual = X.units
        expected = Unit('km')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions(self):
        indata = physarray.PhysArray([1, 2, 3], name='X', dimensions=('x',))
        testname = 'PhysArray({}).dimensions'.format(indata)
        X = physarray.PhysArray(indata)
        actual = X.dimensions
        expected = indata.dimensions
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_dimensions_override(self):
        indata = physarray.PhysArray([1, 2, 3], name='X', dimensions=('x',))
        testname = 'PhysArray({}, dimensions={}).dimensions'.format(indata, ('y',))
        X = physarray.PhysArray(indata, dimensions=('y',))
        actual = X.dimensions
        expected = ('y',)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_positive(self):
        indata = physarray.PhysArray([1, 2, 3], name='X', dimensions=('x',), positive='up')
        testname = 'PhysArray({}).positive'.format(indata)
        X = physarray.PhysArray(indata)
        actual = X.positive
        expected = indata.positive
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_cast_positive_override(self):
        indata = physarray.PhysArray([1, 2, 3], name='X', dimensions=('x',), positive='up')
        testname = 'PhysArray({}).positive'.format(indata)
        X = physarray.PhysArray(indata, positive='down')
        actual = X.positive
        expected = 'down'
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        numpy.testing.assert_array_equal(X.data, numpy.array([1,2,3]), '{} failed'.format(testname))
    
    def test_add_positive(self):
        test_inputs = [(None, None), (None, 'up'), ('down', None), ('up', 'up'), ('up', 'down')]
        test_names = ['(X+Y)', '(X+Y)', '(X+Y)', '(X+Y)', '(X+up(Y))']
        test_values = [3.0, 3.0, 3.0, 3.0, -1.0]
        test_positives = [None, 'up', 'down', 'up', 'up']
        for (xpos, ypos), name, value, positive in zip(test_inputs, test_names, test_values, test_positives):
            testname = 'X(positive={!r}).__add__(Y(positive={!r}))'.format(xpos, ypos)
            X = physarray.PhysArray(1.0, name='X', positive=xpos)
            Y = physarray.PhysArray(2.0, name='Y', positive=ypos)
            actual = X + Y
            expected = physarray.PhysArray(value, name=name, positive=positive)
            print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
            numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
            self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
            self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
            self.assertEqual(actual.positive, expected.positive, '{} failed - positive'.format(testname))

    def test_add_array_array(self):
        X = physarray.PhysArray([[1, 2], [3, 4]], name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__add__(Y)'
        actual = X + Y
        new_name = ("({}+transpose(convert({}, from={}, to={}), from=[v,u], to=[u,v]))"
                    "").format(X.name, Y.name, Y.units, X.units)
        expected = physarray.PhysArray([[5001, 7002], [6003, 8004]], units=X.units,
                                       name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_add_num_array(self):
        X = 1.0
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='0.1', dimensions=('v', 'u'))
        testname = 'X.__radd__(Y)'
        actual = X + Y
        expected = physarray.PhysArray([[1.5, 1.6], [1.7, 1.8]],
                                       name='(1.0+convert(Y, from=0.1, to=1))',
                                       units=Unit(1), dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_almost_equal(actual, expected, 4, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_add_scalar_array(self):
        X = physarray.PhysArray(1.)
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='0.1', dimensions=('v', 'u'))
        testname = 'X.__add__(Y)'
        actual = X + Y
        expected = physarray.PhysArray([[1.5, 1.6], [1.7, 1.8]],
                                       name='(1.0+convert(Y, from=0.1, to=1))',
                                       units=X.units, dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_almost_equal(actual, expected, 4, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_add_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='0.1', dimensions=('u', 'v'))
        Y = 1
        testname = 'X.__add__(Y)'
        actual = X + Y
        expected = physarray.PhysArray([[15, 16], [17, 18]], name='(X+convert(1, from=1, to=0.1))',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_add_array_scalar(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='0.1', dimensions=('u', 'v'))
        Y = physarray.PhysArray(1)
        testname = 'X.__add__(Y)'
        actual = X + Y
        expected = physarray.PhysArray([[15, 16], [17, 18]], name='(X+convert(1, from=1, to=0.1))',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_iadd_array(self):
        xdata = numpy.array([[1, 2], [3, 4]], dtype='d')
        ydata = numpy.array([[5, 6], [7, 8]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray(ydata, name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__iadd__(Y)'
        actual = X.copy()
        actual += Y
        new_name = ("({}+transpose(convert({}, from={}, to={}), from=[v,u], to=[u,v]))"
                    "").format(X.name, Y.name, Y.units, X.units)
        expected = physarray.PhysArray([[5001., 7002.], [6003., 8004.]], name=new_name,
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_iadd_scalar(self):
        xdata = numpy.array([[1, 2], [3, 4]], dtype='d')
        ydata = numpy.array(2, dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray(ydata, name='Y', units='km')
        testname = 'X.__iadd__(Y)'
        actual = X.copy()
        actual += Y
        new_name = "({}+convert({}, from={}, to={}))".format(X.name, Y.name, Y.units, X.units)
        expected = physarray.PhysArray([[2001., 2002.], [2003., 2004.]], name=new_name,
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_sub_positive(self):
        test_inputs = [(None, None), (None, 'up'), ('down', None), ('up', 'up'), ('up', 'down')]
        test_names = ['(X-Y)', '(X-Y)', '(X-Y)', '(X-Y)', '(X-up(Y))']
        test_values = [-1.0, -1.0, -1.0, -1.0, 3.0]
        test_positives = [None, 'up', 'down', 'up', 'up']
        for (xpos, ypos), name, value, positive in zip(test_inputs, test_names, test_values, test_positives):
            testname = 'X(positive={!r}).__sub__(Y(positive={!r}))'.format(xpos, ypos)
            X = physarray.PhysArray(1.0, name='X', positive=xpos)
            Y = physarray.PhysArray(2.0, name='Y', positive=ypos)
            actual = X - Y
            expected = physarray.PhysArray(value, name=name, positive=positive)
            print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
            numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
            self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
            self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
            self.assertEqual(actual.positive, expected.positive, '{} failed - positive'.format(testname))

    def test_sub_array_array(self):
        X = physarray.PhysArray([[1, 2], [3, 4]], name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__sub__(Y)'
        actual = X - Y
        new_name = ("({}-transpose(convert({}, from={}, to={}), from=[v,u], to=[u,v]))"
                    "").format(X.name, Y.name, Y.units, X.units)
        expected = physarray.PhysArray([[-4999., -6998.], [-5997., -7996.]], units=X.units,
                                       name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_sub_num_array(self):
        X = 1.0
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='0.1', dimensions=('v', 'u'))
        testname = 'X.__rsub_(Y)'
        actual = X - Y
        expected = physarray.PhysArray([[.5, .4], [.3, .2]], name='(1.0-convert(Y, from=0.1, to=1))',
                                       units=Unit(1), dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_almost_equal(actual, expected, 4, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_sub_scalar_array(self):
        X = physarray.PhysArray(1.0)
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='0.1', dimensions=('v', 'u'))
        testname = 'X.__rsub_(Y)'
        actual = X - Y
        expected = physarray.PhysArray([[.5, .4], [.3, .2]], name='(1.0-convert(Y, from=0.1, to=1))',
                                       units=X.units, dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_almost_equal(actual, expected, 4, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_sub_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='0.1', dimensions=('u', 'v'))
        Y = 1
        testname = 'X.__sub__(Y)'
        actual = X - Y
        expected = physarray.PhysArray([[-5., -4.], [-3., -2.]], name='(X-convert(1, from=1, to=0.1))',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_sub_array_scalar(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='0.1', dimensions=('u', 'v'))
        Y = physarray.PhysArray(1)
        testname = 'X.__sub__(Y)'
        actual = X - Y
        expected = physarray.PhysArray([[-5., -4.], [-3., -2.]], name='(X-convert(1, from=1, to=0.1))',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_isub_array(self):
        xdata = numpy.array([[1, 2], [3, 4]], dtype='d')
        ydata = numpy.array([[5, 6], [7, 8]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray(ydata, name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__isub__(Y)'
        actual = X.copy()
        actual -= Y
        new_name = ("({}-transpose(convert({}, from={}, to={}), from=[v,u], to=[u,v]))"
                    "").format(X.name, Y.name, Y.units, X.units)
        expected = physarray.PhysArray([[-4999., -6998.], [-5997., -7996.]], name=new_name,
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_mul_positive(self):
        test_inputs = [(None, None), (None, 'up'), ('down', None), ('up', 'up'), ('up', 'down')]
        test_names = ['(X*Y)', '(X*Y)', '(X*Y)', '(X*Y)', '(X*up(Y))']
        test_values = [21.0, 21.0, 21.0, 21.0, -21.0]
        test_positives = [None, 'up', 'down', None, None]
        for (xpos, ypos), name, value, positive in zip(test_inputs, test_names, test_values, test_positives):
            testname = 'X(positive={!r}).__mul__(Y(positive={!r}))'.format(xpos, ypos)
            X = physarray.PhysArray(3.0, name='X', positive=xpos)
            Y = physarray.PhysArray(7.0, name='Y', positive=ypos)
            actual = X * Y
            expected = physarray.PhysArray(value, name=name, positive=positive)
            print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
            numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
            self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
            self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
            self.assertEqual(actual.positive, expected.positive, '{} failed - positive'.format(testname))
            
    def test_mul_array_array_extend_dims(self):
        X = physarray.PhysArray([[1, 2], [3, 4]], name='X', units='m', dimensions=('t', 'u'))
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='km', dimensions=('u', 'v'))
        testname = 'X.__mul__(Y)'
        actual = X * Y
        new_name = "({}*{})".format(X, Y)
        new_units = Unit('m') * Unit('km')
        expected = physarray.PhysArray([[[5, 6], [14, 16]], [[15, 18], [28, 32]]], units=new_units,
                                       name=new_name, dimensions=('t', 'u', 'v'))
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_mul_array_array(self):
        X = physarray.PhysArray([[1, 2], [3, 4]], name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__mul__(Y)'
        actual = X * Y
        new_name = "({}*{})".format(X.name, Y.name)
        new_units = Unit('m') * Unit('km')
        expected = physarray.PhysArray([[5, 14], [18, 32]], units=new_units,
                                       name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_mul_num_array(self):
        X = 2
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__rmul__(Y)'
        actual = X * Y
        expected = physarray.PhysArray([[10, 12], [14, 16]], name='(2*Y)',
                                       units=Y.units, dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_mul_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2
        testname = 'X.__mul__(Y)'
        actual = X * Y
        expected = physarray.PhysArray([[10, 12], [14, 16]], name='(X*2)',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_imul_array(self):
        xdata = numpy.array([[1, 2], [3, 4]], dtype='d')
        ydata = numpy.array([[5, 6], [7, 8]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray(ydata, name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__imul__(Y)'
        actual = X.copy()
        actual *= Y
        new_name = "({}*{})".format(X, Y)
        new_units = Unit('m') * Unit('km')
        expected = physarray.PhysArray([[5, 14], [18, 32]], name=new_name,
                                       units=new_units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_div_positive(self):
        test_inputs = [(None, None), (None, 'up'), ('down', None), ('up', 'up'), ('up', 'down')]
        test_names = ['(X/Y)', '(X/Y)', '(X/Y)', '(X/Y)', '(X/up(Y))']
        test_values = [2.0, 2.0, 2.0, 2.0, -2.0]
        test_positives = [None, 'up', 'down', None, None]
        for (xpos, ypos), name, value, positive in zip(test_inputs, test_names, test_values, test_positives):
            testname = 'X(positive={!r}).__div__(Y(positive={!r}))'.format(xpos, ypos)
            X = physarray.PhysArray(8.0, name='X', positive=xpos)
            Y = physarray.PhysArray(4.0, name='Y', positive=ypos)
            actual = X / Y
            expected = physarray.PhysArray(value, name=name, positive=positive)
            print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
            numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
            self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
            self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
            self.assertEqual(actual.positive, expected.positive, '{} failed - positive'.format(testname))
            
    def test_div_array_array(self):
        X = physarray.PhysArray([[1., 2.], [3., 4.]], name='X', units='km', dimensions=('u', 'v'))
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__div__(Y)'
        actual = X / Y
        new_name = "({}/{})".format(X.name, Y.name)
        new_units = Unit('km') / Unit('m')
        expected = physarray.PhysArray([[1 / 5., 2 / 7.], [3 / 6., 4 / 8.]],
                                       units=new_units, name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_div_num_array(self):
        X = 2.
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__rdiv__(Y)'
        actual = X / Y
        expected = physarray.PhysArray([[2. / 5, 2. / 6], [2. / 7, 2. / 8]], name='(2.0/Y)',
                                       units='1/m', dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_div_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2.
        testname = 'X.__div__(Y)'
        actual = X / Y
        expected = physarray.PhysArray([[5 / 2., 6 / 2.], [7 / 2., 8 / 2.]], name='(X/2.0)',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_idiv_array(self):
        xdata = numpy.array([[1, 2], [3, 4]], dtype='d')
        ydata = numpy.array([[5, 6], [7, 8]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray(ydata, name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__idiv__(Y)'
        actual = X.copy()
        actual /= Y
        new_name = "({}/{})".format(X, Y)
        new_units = Unit('m') / Unit('km')
        expected = physarray.PhysArray([[1. / 5, 2. / 7], [3. / 6, 4. / 8]], name=new_name,
                                       units=new_units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_floordiv_positive(self):
        test_inputs = [(None, None), (None, 'up'), ('down', None), ('up', 'up'), ('up', 'down')]
        test_names = ['(X//Y)', '(X//Y)', '(X//Y)', '(X//Y)', '(X//up(Y))']
        test_values = [2.0, 2.0, 2.0, 2.0, -3.0]
        test_positives = [None, 'up', 'down', None, None]
        for (xpos, ypos), name, value, positive in zip(test_inputs, test_names, test_values, test_positives):
            testname = 'X(positive={!r}).__floordiv__(Y(positive={!r}))'.format(xpos, ypos)
            X = physarray.PhysArray(9.0, name='X', positive=xpos)
            Y = physarray.PhysArray(4.0, name='Y', positive=ypos)
            actual = X // Y
            expected = physarray.PhysArray(value, name=name, positive=positive)
            print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
            numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
            self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
            self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
            self.assertEqual(actual.positive, expected.positive, '{} failed - positive'.format(testname))
            
    def test_floordiv_array_array(self):
        X = physarray.PhysArray([[1., 2.], [3., 4.]], name='X', units='km', dimensions=('u', 'v'))
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__floordiv__(Y)'
        actual = X // Y
        new_name = "({}//{})".format(X, Y)
        new_units = Unit('km') / Unit('m')
        expected = physarray.PhysArray([[1 // 5., 2 // 7.], [3 // 6., 4 // 8.]],
                                       units=new_units, name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_floordiv_num_array(self):
        X = 20.
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__rfloordiv__(Y)'
        actual = X // Y
        expected = physarray.PhysArray([[20. // 5, 20. // 6], [20. // 7, 20. // 8]], name='(20.0//Y)',
                                       units='1/m', dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_floordiv_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2.
        testname = 'X.__floordiv__(Y)'
        actual = X // Y
        expected = physarray.PhysArray([[5 // 2., 6 // 2.], [7 // 2., 8 // 2.]], name='(X//2.0)',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_ifloordiv_array(self):
        xdata = numpy.array([[5., 6.], [7., 8.]], dtype='d')
        ydata = numpy.array([[1., 2.], [3., 4.]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray(ydata, name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__ifloordiv__(Y)'
        actual = X.copy()
        actual //= Y
        new_name = "({}//{})".format(X, Y)
        new_units = Unit('m') / Unit('km')
        expected = physarray.PhysArray([[5 // 1., 6 // 3.], [7 // 2., 8 // 4.]], name=new_name,
                                       units=new_units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_mod_positive(self):
        test_inputs = [(None, None), (None, 'up'), ('down', None), ('up', 'up'), ('up', 'down')]
        test_names = ['(X%Y)', '(X%Y)', '(X%Y)', '(X%Y)', '(X%up(Y))']
        test_values = [1.0, 1.0, 1.0, 1.0, -3.0]
        test_positives = [None, None, 'down', 'up', 'up']
        for (xpos, ypos), name, value, positive in zip(test_inputs, test_names, test_values, test_positives):
            testname = 'X(positive={!r}).__mod__(Y(positive={!r}))'.format(xpos, ypos)
            X = physarray.PhysArray(9.0, name='X', positive=xpos)
            Y = physarray.PhysArray(4.0, name='Y', positive=ypos)
            actual = X % Y
            expected = physarray.PhysArray(value, name=name, positive=positive)
            print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
            numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
            self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
            self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
            self.assertEqual(actual.positive, expected.positive, '{} failed - positive'.format(testname))
            
    def test_mod_array_array(self):
        X = physarray.PhysArray([[1., 2.], [3., 4.]], name='X', units='km', dimensions=('u', 'v'))
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__mod__(Y)'
        actual = X % Y
        new_name = "({}%transpose({}, from=[v,u], to=[u,v]))".format(X.name, Y.name)
        expected = physarray.PhysArray([[1 % 5., 2 % 7.], [3 % 6., 4 % 8.]],
                                       units=X.units, name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_mod_num_array(self):
        X = 20.
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__rmod__(Y)'
        actual = X % Y
        expected = physarray.PhysArray([[20. % 5, 20. % 6], [20. % 7, 20. % 8]], name='(20.0%Y)',
                                       units='1', dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_mod_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2.
        testname = 'X.__mod__(Y)'
        actual = X % Y
        expected = physarray.PhysArray([[5 % 2., 6 % 2.], [7 % 2., 8 % 2.]], name='(X%2.0)',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_imod_array(self):
        xdata = numpy.array([[1, 2], [3, 4]], dtype='d')
        ydata = numpy.array([[5, 6], [7, 8]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray(ydata, name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__imod__(Y)'
        actual = X.copy()
        actual %= Y
        new_name = "({}%transpose({}, from=[{}], to=[{}]))".format(X, Y, ','.join(Y.dimensions),
                                                                   ','.join(X.dimensions))
        expected = physarray.PhysArray([[1. % 5000, 2. % 7000], [3. % 6000, 4. % 8000]],
                                       name=new_name, units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_pow_positive(self):
        test_inputs = [(None, 2), (None, 3), ('up', 2), ('down', 3)]
        test_values = [9.0, 27.0, 9.0, 27.0]
        test_positives = [None, None, None, 'down']
        for (xpos, yval), value, positive in zip(test_inputs, test_values, test_positives):
            testname = 'X(positive={!r}).__pow__(Y)'.format(xpos)
            X = physarray.PhysArray(3.0, name='X', positive=xpos)
            Y = physarray.PhysArray(yval, name='Y')
            actual = X ** Y
            expected = physarray.PhysArray(value, name='(X**Y)', positive=positive)
            print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
            numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
            self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
            self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
            self.assertEqual(actual.positive, expected.positive, '{} failed - positive'.format(testname))
            
    def test_pow_array_array(self):
        X = physarray.PhysArray([[1., 2.], [3., 4.]], name='X', units='km', dimensions=('u', 'v'))
        Y = physarray.PhysArray(2., name='Y', units='2')
        testname = 'X.__pow__(Y)'
        actual = X ** Y
        new_name = "({}**convert({}, from=2, to=1))".format(X.name, Y.name)
        new_units = X.units ** 4
        expected = physarray.PhysArray([[1 ** 4., 2 ** 4.], [3 ** 4., 4 ** 4.]],
                                       units=new_units, name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_pow_num_array(self):
        X = 2.
        Y = physarray.PhysArray(2.0, name='Y', units='2')
        testname = 'X.__rpow__(Y)'
        actual = X ** Y
        expected = physarray.PhysArray(2. ** 4, name='(2.0**convert(Y, from=2, to=1))',
                                       units='1', dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_pow_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2.
        testname = 'X.__pow__(Y)'
        actual = X ** Y
        expected = physarray.PhysArray([[5 ** 2., 6 ** 2.], [7 ** 2., 8 ** 2.]], name='(X**2.0)',
                                       units=X.units ** 2, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_ipow_array(self):
        xdata = numpy.array([[1, 2], [3, 4]], dtype='d')
        ydata = numpy.array(2., dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray(ydata, name='Y', units='2')
        testname = 'X.__ipow__(Y)'
        actual = X.copy()
        actual **= Y
        new_name = "({}**convert({}, from=2, to=1))".format(X.name, Y.name)
        expected = physarray.PhysArray([[1. ** 4, 2. ** 4], [3. ** 4, 4. ** 4]], name=new_name,
                                       units=X.units ** 4, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_convert(self):
        xdata = numpy.array(2., dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='km')
        indata = 'm'
        testname = 'X.convert({})'.format(indata)
        actual = X.convert(Unit(indata))
        new_name = "convert({}, from={}, to={})".format(X.name, X.units, indata)
        expected = physarray.PhysArray(2000., name=new_name, units=indata)
        print_test_message(testname, actual=actual, expected=expected, X=X)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_convert_error(self):
        xdata = numpy.array(2., dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='km')
        indata = 'g'
        testname = 'X.convert({})'.format(indata)
        expected = physarray.UnitsError
        print_test_message(testname, expected=expected, X=X)
        self.assertRaises(expected, X.convert, indata)

    def test_transpose_dims(self):
        xdata = numpy.array([[1., 2.], [3., 4.]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        indata = ('v', 'u')
        testname = 'X.transpose({}, {})'.format(*indata)
        actual = X.transpose(*indata)
        new_name = "transpose({}, from=[u,v], to=[v,u])".format(X.name, indata)
        expected = physarray.PhysArray([[1., 3.], [2., 4.]], units=X.units,
                                       name=new_name, dimensions=indata)
        print_test_message(testname, actual=actual, expected=expected, X=X)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_transpose_axes(self):
        xdata = numpy.array([[1., 2.], [3., 4.]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        indata = (1, 0)
        testname = 'X.transpose({}, {})'.format(*indata)
        actual = X.transpose(*indata)
        new_dims = ('v', 'u')
        new_name = "transpose({}, from=[u,v], to=[v,u])".format(X.name)
        expected = physarray.PhysArray([[1., 3.], [2., 4.]], units=X.units,
                                       name=new_name, dimensions=new_dims)
        print_test_message(testname, actual=actual, expected=expected, X=X)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))

    def test_transpose_axes_tuple(self):
        xdata = numpy.array([[1., 2.], [3., 4.]], dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='m', dimensions=('u', 'v'))
        indata = (1, 0)
        testname = 'X.transpose({})'.format(indata)
        actual = X.transpose(indata)
        new_dims = ('v', 'u')
        new_name = "transpose({}, from=[u,v], to=[v,u])".format(X.name, new_dims)
        expected = physarray.PhysArray([[1., 3.], [2., 4.]], units=X.units,
                                       name=new_name, dimensions=new_dims)
        print_test_message(testname, actual=actual, expected=expected, X=X)
        numpy.testing.assert_array_equal(actual, expected, '{} failed - data'.format(testname))
        self.assertEqual(actual.name, expected.name, '{} failed - name'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed - units'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions,
                         '{} failed - dimensions'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
