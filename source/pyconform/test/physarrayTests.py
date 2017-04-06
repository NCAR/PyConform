"""
Physical Array Unit Tests

Copyright 2017, University Corporation for Atmospheric Research
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

    def assertPhysArraysEqual(self, left, right, testname='Test', decimal=0):
        if decimal == 0:
            numpy.testing.assert_array_equal(left, right, '{} failed - data'.format(testname))
        else:
            numpy.testing.assert_array_almost_equal(left, right, decimal, '{} failed - data'.format(testname))
        self.assertEqual(left.dtype, right.dtype, '{} failed - dtype'.format(testname))
        self.assertEqual(left.name, right.name, '{} failed - name'.format(testname))
        self.assertEqual(left.units, right.units, '{} failed - units'.format(testname))
        self.assertEqual(left.dimensions, right.dimensions, '{} failed - dimensions'.format(testname))
        self.assertEqual(left.positive, right.positive, '{} failed - positive'.format(testname))

    def test_init_data_valid(self):
        valid_input = [1, 1.3, (1, 2, 3), [1, 2, 3],  numpy.array([1, 2, 3], dtype=numpy.float64),
                       physarray.PhysArray([1, 2, 3]), 'asfeasefa']
        for indata in valid_input:
            testname = 'PhysArray.__init__({}, name="X")'.format(indata)
            X = physarray.PhysArray(indata, name='X')
            actual = type(X)
            expected = physarray.PhysArray
            print_test_message(testname, indata=indata, actual=actual, expected=expected)
            self.assertIsInstance(X, expected, '{} failed'.format(testname))

    def test_init_units_default(self):
        testname = 'PhysArray(1.2, name="X").units'
        X = physarray.PhysArray(1.2, name='X')
        actual = X.units
        expected = Unit(1)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_init_units_valid(self):
        valid_input = [Unit('m'), 'm', 1, 1e-7]
        for indata in valid_input:
            testname = 'PhysArray(1.2, name="X", units={!r}).units'.format(indata)
            X = physarray.PhysArray(1.2, name='X', units=indata)
            actual = X.units
            expected = Unit(indata)
            print_test_message(testname, units=indata, actual=actual, expected=expected)
            self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_init_units_value_error(self):
        invalid_input = [[], (), 'alksfhenliaunseca']
        for indata in invalid_input:
            testname = 'PhysArray(1.2, name="X", units={!r})'.format(indata)
            expected = ValueError
            print_test_message(testname, units=indata, expected=expected)
            self.assertRaises(expected, physarray.PhysArray, 1.2, units=indata, name='X')

    def test_init_dimensions_default(self):
        testname = 'PhysArray([[1,2],[3,4]], name="X").dimensions'
        X = physarray.PhysArray([[1,2],[3,4]], name='X')
        actual = X.dimensions
        expected = (0,1)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
            
    def test_init_dimensions_valid(self):
        valid_input = [(1,), (1.4,), ('x',), [-1]]
        for indata in valid_input:
            testname = 'PhysArray([1,2,3], name="X", dimensions={!r}).dimensions'.format(indata)
            X = physarray.PhysArray([1,2,3], name='X', dimensions=indata)
            actual = X.dimensions
            expected = tuple(indata)
            print_test_message(testname, dimensions=indata, actual=actual, expected=expected)
            self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_init_dimensions_type_error(self):
        invalid_input = [1, 'x', -3.4]
        for indata in invalid_input:
            testname = 'PhysArray([1,2,3], name="X", dimensions={!r})'.format(indata)
            expected = TypeError
            print_test_message(testname, units=indata, expected=expected)
            self.assertRaises(expected, physarray.PhysArray, [1,2,3], dimensions=indata, name='X')

    def test_init_dimensions_value_error(self):
        invalid_input = [(1,2), ['a', 'b', 'c'], []]
        for indata in invalid_input:
            testname = 'PhysArray([1,2,3], name="X", dimensions={!r})'.format(indata)
            expected = ValueError
            print_test_message(testname, units=indata, expected=expected)
            self.assertRaises(expected, physarray.PhysArray, [1,2,3], dimensions=indata, name='X')

    def test_positive_default(self):
        nlist = range(3)
        testname = 'PhysArray({}, name="X").positive'.format(nlist)
        X = physarray.PhysArray(nlist, name='X')
        actual = X.positive
        expected = None
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_positive_none(self):
        nlist = range(3)
        indata = None
        testname = 'PhysArray({}, name="X", positive={!r}).positive'.format(nlist, indata)
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
            testname = 'PhysArray({}, name="X", positive={!r}).positive'.format(nlist, indata)
            expected = ValueError
            print_test_message(testname, expected=expected)
            self.assertRaises(expected, physarray.PhysArray, nlist, positive=indata, name='X')

    def test_cast(self):
        indata = physarray.PhysArray([1, 2, 3], name='X', units='m', dimensions=('x',), positive='up')
        testname = 'PhysArray({!r})'.format(indata)
        actual = physarray.PhysArray(indata)
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsNot(actual, expected, '{} failed - same objects'.format(testname))
        self.assertPhysArraysEqual(actual, expected, testname)

    def test_cast_override(self):
        indata = physarray.PhysArray([1, 2, 3], name='X', units='m', dimensions=('x',), positive='up')
        overrides = {'name':"Y", 'units':1, 'dimensions': (5,), 'positive': "down"}
        overridestr = ','.join('{!s}={!r}'.format(k,overrides[k]) for k in overrides)
        testname = 'PhysArray({!r}, {})'.format(indata, overridestr)
        actual = physarray.PhysArray(indata, **overrides)
        expected = physarray.PhysArray([1, 2, 3], **overrides)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsNot(actual, expected, '{} failed - same objects'.format(testname))
        self.assertPhysArraysEqual(actual, expected, testname)

    def test_flip(self):
        valid_input = [physarray.PhysArray(1.0, name='X', units='m'),
                       physarray.PhysArray(1.0, name='X', units='m', positive='up'),
                       physarray.PhysArray(1.0, name='X', units='m', positive='down')]
        valid_output = [physarray.PhysArray(1.0, name='X', units='m'),
                        physarray.PhysArray(-1.0, name='down(X)', units='m', positive='down'),
                        physarray.PhysArray(-1.0, name='up(X)', units='m', positive='up')]
        for inp, out in zip(valid_input, valid_output):
            testname = '{!r}.flip()'.format(inp)
            actual = inp.flip()
            expected = physarray.PhysArray(out)
            print_test_message(testname, actual=actual, expected=expected)
            self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_up(self):
        valid_input = [physarray.PhysArray(1.0, name='X', units='m'),
                       physarray.PhysArray(1.0, name='X', units='m', positive='up'),
                       physarray.PhysArray(1.0, name='X', units='m', positive='down')]
        valid_output = [physarray.PhysArray(1.0, name='X', units='m', positive='up'),
                        physarray.PhysArray(1.0, name='X', units='m', positive='up'),
                        physarray.PhysArray(-1.0, name='up(X)', units='m', positive='up')]
        for inp, out in zip(valid_input, valid_output):
            testname = '{!r}.up()'.format(inp)
            actual = inp.up()
            expected = physarray.PhysArray(out)
            print_test_message(testname, actual=actual, expected=expected)
            self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_down(self):
        valid_input = [physarray.PhysArray(1.0, name='X', units='m'),
                       physarray.PhysArray(1.0, name='X', units='m', positive='up'),
                       physarray.PhysArray(1.0, name='X', units='m', positive='down')]
        valid_output = [physarray.PhysArray(1.0, name='X', units='m', positive='down'),
                        physarray.PhysArray(-1.0, name='down(X)', units='m', positive='down'),
                        physarray.PhysArray(1.0, name='X', units='m', positive='down')]
        for inp, out in zip(valid_input, valid_output):
            testname = '{!r}.down()'.format(inp)
            actual = inp.down()
            expected = physarray.PhysArray(out)
            print_test_message(testname, actual=actual, expected=expected)
            self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_add_valid(self):
        valid_XYs = [(physarray.PhysArray(1.0, name='X', units='m'),
                      physarray.PhysArray(1.0, name='Y', units='m')),
                     (physarray.PhysArray(1.0, name='X', units='m', positive='up'),
                      physarray.PhysArray(1.0, name='Y', units='m', positive='up')),
                     (physarray.PhysArray(1.0, name='X', units='m', positive='down'),
                      physarray.PhysArray(1.0, name='Y', units='m', positive='down')),
                     (physarray.PhysArray(range(5), name='X', units='m', dimensions=('t',)),
                      physarray.PhysArray(range(5), name='Y', units='m', dimensions=('t',))),
                     (physarray.PhysArray(range(5), name='X', units='m', dimensions=('t',), positive='up'),
                      physarray.PhysArray(range(5), name='Y', units='m', dimensions=('t',), positive='up')),
                     (physarray.PhysArray(range(5), name='X', units='m', dimensions=('t',), positive='down'),
                      physarray.PhysArray(range(5), name='Y', units='m', dimensions=('t',), positive='down')),
                     (physarray.PhysArray([[1,2],[3,4]], name='X', units='m', dimensions=('a', 'b'), positive='down'),
                      physarray.PhysArray([[1,2],[3,4]], name='Y', units='m', dimensions=('a', 'b'), positive='down')),
                     (physarray.PhysArray([[1,2],[3,4]], name='X', units='m', dimensions=('a', 'b'), positive='down'),
                      physarray.PhysArray([[1,2],[3,4]], name='Y', units='m', dimensions=('a', 'b'), positive='down'))]
        valid_out = [physarray.PhysArray(2.0, name='(X+Y)', units='m'),
                     physarray.PhysArray(2.0, name='(X+Y)', units='m', positive='up'),
                     physarray.PhysArray(2.0, name='(X+Y)', units='m', positive='down'),
                     physarray.PhysArray(range(0,10,2), name='(X+Y)', units='m', dimensions=('t',)),
                     physarray.PhysArray(range(0,10,2), name='(X+Y)', units='m', dimensions=('t',), positive='up'),
                     physarray.PhysArray(range(0,10,2), name='(X+Y)', units='m', dimensions=('t',), positive='down'),
                     physarray.PhysArray([[2,4],[6,8]], name='(X+Y)', units='m', dimensions=('a', 'b'), positive='down'),
                     physarray.PhysArray([[2,4],[6,8]], name='(X+Y)', units='m', dimensions=('a', 'b'), positive='down')]
        testname = 'X + Y'
        for (X, Y), expected in zip(valid_XYs, valid_out):
            actual = X + Y
            print_test_message(testname, X=X, Y=Y, actual=actual, expected=expected)
            self.assertPhysArraysEqual(actual, expected, testname=testname)
            
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
            self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_add_num_array(self):
        X = 1.0
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='0.1', dimensions=('v', 'u'))
        testname = 'X.__radd__(Y)'
        actual = X + Y
        expected = physarray.PhysArray([[1.5, 1.6], [1.7, 1.8]],
                                       name='(1.0+convert(Y, from=0.1, to=1))',
                                       units=Unit(1), dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname, decimal=8)

    def test_add_scalar_array(self):
        X = physarray.PhysArray(1.)
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='0.1', dimensions=('v', 'u'))
        testname = 'X.__add__(Y)'
        actual = X + Y
        expected = physarray.PhysArray([[1.5, 1.6], [1.7, 1.8]],
                                       name='(1.0+convert(Y, from=0.1, to=1))',
                                       units=X.units, dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname, decimal=8)

    def test_add_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='0.1', dimensions=('u', 'v'))
        Y = 1
        testname = 'X.__add__(Y)'
        actual = X + Y
        expected = physarray.PhysArray([[15, 16], [17, 18]], name='(X+convert(1, from=1, to=0.1))',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_add_array_scalar(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='0.1', dimensions=('u', 'v'))
        Y = physarray.PhysArray(1)
        testname = 'X.__add__(Y)'
        actual = X + Y
        expected = physarray.PhysArray([[15, 16], [17, 18]], name='(X+convert(1, from=1, to=0.1))',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
            self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_sub_array_array(self):
        X = physarray.PhysArray([[1, 2], [3, 4]], name='X', units='m', dimensions=('u', 'v'))
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='km', dimensions=('v', 'u'))
        testname = 'X.__sub__(Y)'
        actual = X - Y
        new_name = ("({}-transpose(convert({}, from={}, to={}), from=[v,u], to=[u,v]))"
                    "").format(X.name, Y.name, Y.units, X.units)
        expected = physarray.PhysArray([[-4999, -6998], [-5997, -7996]], units=X.units,
                                       name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_sub_num_array(self):
        X = 1.0
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='0.1', dimensions=('v', 'u'))
        testname = 'X.__rsub_(Y)'
        actual = X - Y
        expected = physarray.PhysArray([[.5, .4], [.3, .2]], name='(1.0-convert(Y, from=0.1, to=1))',
                                       units=Unit(1), dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname, decimal=8)

    def test_sub_scalar_array(self):
        X = physarray.PhysArray(1.0)
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='0.1', dimensions=('v', 'u'))
        testname = 'X.__rsub_(Y)'
        actual = X - Y
        expected = physarray.PhysArray([[.5, .4], [.3, .2]], name='(1.0-convert(Y, from=0.1, to=1))',
                                       units=X.units, dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname, decimal=8)

    def test_sub_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='0.1', dimensions=('u', 'v'))
        Y = 1
        testname = 'X.__sub__(Y)'
        actual = X - Y
        expected = physarray.PhysArray([[-5, -4], [-3, -2]], name='(X-convert(1, from=1, to=0.1))',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_sub_array_scalar(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='0.1', dimensions=('u', 'v'))
        Y = physarray.PhysArray(1)
        testname = 'X.__sub__(Y)'
        actual = X - Y
        expected = physarray.PhysArray([[-5, -4], [-3, -2]], name='(X-convert(1, from=1, to=0.1))',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
            self.assertPhysArraysEqual(actual, expected, testname=testname)
            
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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_mul_num_array(self):
        X = 2
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__rmul__(Y)'
        actual = X * Y
        expected = physarray.PhysArray([[10, 12], [14, 16]], name='(2*Y)',
                                       units=Y.units, dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_mul_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2
        testname = 'X.__mul__(Y)'
        actual = X * Y
        expected = physarray.PhysArray([[10, 12], [14, 16]], name='(X*2)',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        expected = physarray.PhysArray([[5., 14.], [18., 32.]], name=new_name,
                                       units=new_units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
            self.assertPhysArraysEqual(actual, expected, testname=testname)
            
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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_div_num_array(self):
        X = 2.
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__rdiv__(Y)'
        actual = X / Y
        expected = physarray.PhysArray([[2. / 5, 2. / 6], [2. / 7, 2. / 8]], name='(2.0/Y)',
                                       units='1/m', dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_div_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2.
        testname = 'X.__div__(Y)'
        actual = X / Y
        expected = physarray.PhysArray([[5 / 2., 6 / 2.], [7 / 2., 8 / 2.]], name='(X/2.0)',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
            self.assertPhysArraysEqual(actual, expected, testname=testname)
            
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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_floordiv_num_array(self):
        X = 20.
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__rfloordiv__(Y)'
        actual = X // Y
        expected = physarray.PhysArray([[20. // 5, 20. // 6], [20. // 7, 20. // 8]], name='(20.0//Y)',
                                       units='1/m', dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_floordiv_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2.
        testname = 'X.__floordiv__(Y)'
        actual = X // Y
        expected = physarray.PhysArray([[5 // 2., 6 // 2.], [7 // 2., 8 // 2.]], name='(X//2.0)',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
            self.assertPhysArraysEqual(actual, expected, testname=testname)
            
    def test_mod_array_array(self):
        X = physarray.PhysArray([[1., 2.], [3., 4.]], name='X', units='km', dimensions=('u', 'v'))
        Y = physarray.PhysArray([[5., 6.], [7., 8.]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__mod__(Y)'
        actual = X % Y
        new_name = "({}%transpose({}, from=[v,u], to=[u,v]))".format(X.name, Y.name)
        expected = physarray.PhysArray([[1 % 5., 2 % 7.], [3 % 6., 4 % 8.]],
                                       units=X.units, name=new_name, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_mod_num_array(self):
        X = 20.
        Y = physarray.PhysArray([[5, 6], [7, 8]], name='Y', units='m', dimensions=('v', 'u'))
        testname = 'X.__rmod__(Y)'
        actual = X % Y
        expected = physarray.PhysArray([[20. % 5, 20. % 6], [20. % 7, 20. % 8]], name='(20.0%Y)',
                                       units='1', dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_mod_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2.
        testname = 'X.__mod__(Y)'
        actual = X % Y
        expected = physarray.PhysArray([[5 % 2., 6 % 2.], [7 % 2., 8 % 2.]], name='(X%2.0)',
                                       units=X.units, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
            self.assertPhysArraysEqual(actual, expected, testname=testname)
            
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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_pow_num_array(self):
        X = 2.
        Y = physarray.PhysArray(2.0, name='Y', units='2')
        testname = 'X.__rpow__(Y)'
        actual = X ** Y
        expected = physarray.PhysArray(2. ** 4, name='(2.0**convert(Y, from=2, to=1))',
                                       units='1', dimensions=Y.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_pow_array_num(self):
        X = physarray.PhysArray([[5, 6], [7, 8]], name='X', units='m', dimensions=('u', 'v'))
        Y = 2.
        testname = 'X.__pow__(Y)'
        actual = X ** Y
        expected = physarray.PhysArray([[5 ** 2., 6 ** 2.], [7 ** 2., 8 ** 2.]], name='(X**2.0)',
                                       units=X.units ** 2, dimensions=X.dimensions)
        print_test_message(testname, actual=actual, expected=expected, X=X, Y=Y)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

    def test_convert(self):
        xdata = numpy.array(2., dtype='d')
        X = physarray.PhysArray(xdata, name='X', units='km')
        indata = 'm'
        testname = 'X.convert({})'.format(indata)
        actual = X.convert(Unit(indata))
        new_name = "convert({}, from={}, to={})".format(X.name, X.units, indata)
        expected = physarray.PhysArray(2000., name=new_name, units=indata)
        print_test_message(testname, actual=actual, expected=expected, X=X)
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)

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
        self.assertPhysArraysEqual(actual, expected, testname=testname)


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
