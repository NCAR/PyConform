"""
FlowNode Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import flownodes, physarray
from testutils import print_test_message
from cf_units import Unit
from os.path import exists
from os import remove
from glob import glob

import unittest
import numpy
import netCDF4


#===================================================================================================
# FlowNodeTests
#===================================================================================================
class FlowNodeTests(unittest.TestCase):
    """
    Unit tests for the flownodes.FlowNode class
    """

    def test_init(self):
        indata = 0
        testname = 'FlowNode.__init__({})'.format(indata)
        N = flownodes.FlowNode(0)
        actual = type(N)
        expected = flownodes.FlowNode
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(N, expected, '{} failed'.format(testname))

    def test_label_int(self):
        indata = 0
        testname = 'FlowNode({}).label'.format(indata)
        N = flownodes.FlowNode(indata)
        actual = N.label
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_label_str(self):
        indata = 'abcd'
        testname = 'FlowNode({}).label'.format(indata)
        N = flownodes.FlowNode(indata)
        actual = N.label
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_inputs(self):
        indata = ['a', 0, 1, 2, 3]
        testname = 'FlowNode{}.inputs'.format(indata)
        N = flownodes.FlowNode(*indata)
        actual = N.inputs
        expected = indata[1:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===================================================================================================
# CreateNodeTests
#===================================================================================================
class CreateNodeTests(unittest.TestCase):
    """
    Unit tests for the flownodes.DataNode class
    """

    def test_getitem_all(self):
        indata = numpy.arange(10)
        testname = 'DataNode.__getitem__(:)'
        N = flownodes.DataNode(0, indata, units='m', dimensions=('x',))
        actual = N[:]
        expected = flownodes.PhysArray(indata, units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = numpy.arange(10)
        testname = 'DataNode.__getitem__(:5)'
        N = flownodes.DataNode(0, indata, units='m', dimensions=('x',))
        actual = N[:5]
        expected = flownodes.PhysArray(indata[:5], units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indata = numpy.arange(10)
        indict = {'a': 4, 'x': slice(1, 5, 2)}
        testname = 'DataNode.__getitem__({})'.format(indict)
        N = flownodes.DataNode(0, indata, units='m', dimensions=('x',))
        actual = N[indict]
        expected = flownodes.PhysArray(indata[indict['x']], units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# ReadNodeTests
#===================================================================================================
class ReadNodeTests(unittest.TestCase):
    """
    Unit tests for the flownodes.ReadNode class
    """

    def setUp(self):
        self.filename = 'test.nc'
        self.varname = 'v'
        self.dimensions = ('x', 'y')
        self.shape = {'x': 5, 'y': 10}
        self.vardata = {'x': flownodes.PhysArray(numpy.arange(self.shape['x'], dtype='f'),
                                                 units='m', dimensions=('x',), name='x'),
                        'y': flownodes.PhysArray(numpy.arange(self.shape['y'], dtype='f'),
                                                 units='km', dimensions=('y',), name='x'),
                        'v': flownodes.PhysArray(numpy.arange(self.shape['x'] * self.shape['y'],
                                                              dtype='d').reshape(self.shape['x'], self.shape['y']),
                                                 units='K', dimensions=self.dimensions, name='v')}

        with netCDF4.Dataset(self.filename, 'w') as ncfile:
            for d in self.dimensions:
                ncfile.createDimension(d, self.shape[d])

            for v in self.vardata:
                ncv = ncfile.createVariable(v, 'f', self.vardata[v].dimensions)
                ncv.setncatts({'units': str(self.vardata[v].units)})
                ncv[:] = self.vardata[v]

    def tearDown(self):
        if exists(self.filename):
            remove(self.filename)

    def test_getitem_all(self):
        testname = 'ReadNode.__getitem__(:)'
        N = flownodes.ReadNode(self.filename, self.varname)
        actual = N[:]
        expected = self.vardata[self.varname]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        testname = 'ReadNode.__getitem__(:2)'
        N = flownodes.ReadNode(self.filename, self.varname)
        actual = N[:2]
        expected = self.vardata[self.varname][:2]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_none(self):
        testname = 'ReadNode.__getitem__(None)'
        N = flownodes.ReadNode(self.filename, self.varname)
        actual = N[None]
        expected = flownodes.PhysArray(numpy.zeros((1,) * len(self.shape), dtype='d'),
                                       units=self.vardata[self.varname].units,
                                       dimensions=self.vardata[self.varname].dimensions)
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_tuple(self):
        intuple = (3, slice(2, 4))
        testname = 'ReadNode.__getitem__({})'.format(intuple)
        N = flownodes.ReadNode(self.filename, self.varname)
        actual = N[intuple]
        expected = flownodes.PhysArray(self.vardata[self.varname][intuple], dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indict = {'a': 4, 'x': slice(1, 5, 2)}
        testname = 'ReadNode.__getitem__({})'.format(indict)
        N = flownodes.ReadNode(self.filename, self.varname)
        actual = N[indict]
        expected = self.vardata[self.varname][slice(1, 5, 2)]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict_2(self):
        indict = {'a': 4, 'y': slice(1, 5, 2)}
        testname = 'ReadNode.__getitem__({})'.format(indict)
        N = flownodes.ReadNode(self.filename, self.varname)
        actual = N[indict]
        expected = self.vardata[self.varname][:, slice(1, 5, 2)]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# EvalNodeTests
#===================================================================================================
class EvalNodeTests(unittest.TestCase):
    """
    Unit tests for the flownodes.EvalNode class
    """

    def test_getitem_all(self):
        indata = flownodes.PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalNode.__getitem__(:)'
        N = flownodes.EvalNode(0, lambda x: x, indata)
        actual = N[:]
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_none(self):
        indata = flownodes.PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalNode.__getitem__(None)'
        N = flownodes.EvalNode(0, lambda x: x, indata)
        actual = N[None]
        expected = flownodes.PhysArray(numpy.zeros((1,), dtype=indata.dtype),
                                       units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = flownodes.PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalNode.__getitem__(:5)'
        N = flownodes.EvalNode(0, lambda x: x, indata)
        actual = N[:5]
        expected = indata[:5]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indata = flownodes.PhysArray(range(10), units='m', dimensions=('x',))
        testname = "EvalNode.__getitem__({'x': slice(5, None), 'y': 6})"
        N = flownodes.EvalNode(0, lambda x: x, indata)
        actual = N[{'x': slice(5, None), 'y': 6}]
        expected = indata[slice(5, None)]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add(self):
        d1 = flownodes.PhysArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = flownodes.PhysArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = flownodes.EvalNode(1, lambda x: x, d1)
        N2 = flownodes.EvalNode(2, lambda x: x, d2)
        N3 = flownodes.EvalNode(3, lambda a, b: a + b, N1, N2)
        testname = 'EvalNode.__getitem__(:)'
        actual = N3[:]
        expected = d1 + d2
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add_slice(self):
        d1 = flownodes.PhysArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = flownodes.PhysArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = flownodes.EvalNode(1, lambda x: x, d1)
        N2 = flownodes.EvalNode(2, lambda x: x, d2)
        N3 = flownodes.EvalNode(3, lambda a, b: a + b, N1, N2)
        testname = 'EvalNode.__getitem__(:2)'
        actual = N3[:2]
        expected = d1[:2] + d2[:2]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add_none(self):
        d1 = flownodes.PhysArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = flownodes.PhysArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = flownodes.EvalNode(1, lambda x: x, d1)
        N2 = flownodes.EvalNode(2, lambda x: x, d2)
        N3 = flownodes.EvalNode(3, lambda a, b: a + b, N1, N2)
        testname = 'EvalNode.__getitem__(None)'
        actual = N3[None]
        expected = flownodes.PhysArray([6], units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# MapNodeTests
#===================================================================================================
class MapNodeTests(unittest.TestCase):
    """
    Unit tests for the flownodes.MapNode class
    """

    def setUp(self):
        self.indata = flownodes.DataNode(0, numpy.arange(10), units='km', dimensions=('x',))

    def test_getitem_all(self):
        testname = 'MapNode.__getitem__(:)'
        N = flownodes.MapNode(0, self.indata, dmap={'x': 'y'})
        actual = N[:]
        expected = flownodes.PhysArray(self.indata[:], dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        testname = 'MapNode.__getitem__(:3)'
        N = flownodes.MapNode(0, self.indata, dmap={'x': 'y'})
        actual = N[:3]
        expected = flownodes.PhysArray(self.indata[:3], dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_none(self):
        testname = 'MapNode.__getitem__(None)'
        N = flownodes.MapNode(0, self.indata, dmap={'x': 'y'})
        actual = N[None]
        expected = flownodes.PhysArray(numpy.arange(1), units='km', dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice_no_dmap(self):
        testname = 'MapNode(dmap={}, dimensions=indims).__getitem__(:3)'
        N = flownodes.MapNode(0, self.indata)
        actual = N[:3]
        expected = flownodes.PhysArray(self.indata[:3], dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# ValidateNodeTests
#===================================================================================================
class ValidateNodeTests(unittest.TestCase):
    """
    Unit tests for the flownodes.ValidateNode class
    """

    def test_nothing(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        testname = 'OK: ValidateNode().__getitem__(:)'
        N1 = flownodes.ValidateNode('validate(x)', N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_units_ok(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'units': Unit('m')}
        testname = ('OK: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_time_units_ok(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='days since 2000-01-01 00:00:00',
                                  dimensions=('x',))
        indata = {'units': 'days since 2000-01-01 00:00:00', 'calendar': 'gregorian'}
        testname = ('OK: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_dimensions_ok(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'dimensions': ('x',)}
        testname = ('OK: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_min_ok(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'valid_min': 0}
        testname = ('OK: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_max_ok(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'valid_max': 10}
        testname = ('OK: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_min_mean_abs_ok(self):
        N0 = flownodes.DataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        indata = {'ok_min_mean_abs': 3}
        testname = ('OK: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_max_mean_abs_ok(self):
        N0 = flownodes.DataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        indata = {'ok_max_mean_abs': 5}
        testname = ('OK: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_units_convert(self):
        N0 = flownodes.DataNode('x', numpy.arange(10, dtype=numpy.float64), units='m', dimensions=('x',))
        indata = {'units': Unit('km')}
        testname = ('WARN: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = (Unit('m').convert(N0[:], Unit('km'))).astype(numpy.float32)
        expected.name = physarray.PhysArray._convert_name_('x', Unit('m'), Unit('km'))
        expected.units = Unit('km')
        expected.mask = False
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_time_units_warn(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='days since 2000-01-01 00:00:00', dimensions=('x',))
        indata = {'units': 'hours since 2000-01-01 00:00:00', 'calendar': 'gregorian'}
        testname = ('WARN: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_time_units_warn_calendar(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='days since 2000-01-01 00:00:00', dimensions=('x',))
        indata = {'units': 'days since 2000-01-01 00:00:00', 'calendar': 'noleap'}
        testname = ('WARN: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_dimensions_error(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'dimensions': ('y',)}
        testname = ('WARN: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, **indata)
        expected = physarray.DimensionsError
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(expected, N1.__getitem__, slice(None))

    def test_min_warn(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'valid_min': 2}
        testname = ('WARN: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_max_warn(self):
        N0 = flownodes.DataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'valid_max': 8}
        testname = ('WARN: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_min_mean_abs_warn(self):
        N0 = flownodes.DataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        indata = {'ok_min_mean_abs': 5}
        testname = ('WARN: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_max_mean_abs_warn(self):
        N0 = flownodes.DataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        indata = {'ok_max_mean_abs': 3}
        testname = ('WARN: ValidateNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = flownodes.ValidateNode('validate(x)', N0, attributes=indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# WriteNodeTests
#===================================================================================================
class WriteNodeTests(unittest.TestCase):
    """
    Unit tests for the flownodes.WriteNode class
    """

    def setUp(self):
        x = flownodes.DataNode('X', numpy.arange(-5, 10), units='m', dimensions=('x',))
        self.x = flownodes.ValidateNode('X', x, attributes={'xa1': 'x attribute 1', 'xa2': 'x attribute 2'})
        y = flownodes.DataNode('Y', numpy.arange(0, 8), units='m', dimensions=('y',))
        self.y = flownodes.ValidateNode('Y', y, attributes={'ya1': 'y attribute 1', 'ya2': 'y attribute 2'})
        vdata = numpy.arange(15 * 8, dtype=numpy.float64).reshape((15, 8))
        v = flownodes.DataNode('V', vdata, units='K', dimensions=('x', 'y'))
        self.v = flownodes.ValidateNode('V', v, attributes={'va1': 'v attribute 1', 'va2': 'v attribute 2'})
        self.vars = [self.x, self.y, self.v]

    def tearDown(self):
        for fname in glob('*.nc'):
            remove(fname)

    def test_init(self):
        filename = 'test.nc'
        testname = 'WriteNode.__init__({})'.format(filename)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        actual = type(N)
        expected = flownodes.WriteNode
        print_test_message(testname, actual=actual, expected=expected)
        self.assertIsInstance(N, expected, '{} failed'.format(testname))

    def test_chunk_iter_all(self):
        filename = 'test.nc'
        testname = 'WriteNode({})._chunk_iter_'.format(filename)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        actual = [chunk for chunk in N._chunk_iter_(('x', 'y'), (2, 3))]
        expected = [slice(None)]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_1D(self):
        filename = 'test.nc'
        testname = 'WriteNode({})._chunk_iter_'.format(filename)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        actual = [chunk for chunk in N._chunk_iter_(('x', 'y'), (4, 5), chunks={'x': 2})]
        expected = [{'x': slice(0, 2)}, {'x': slice(2, None)}]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_1D_unnamed(self):
        filename = 'test.nc'
        testname = 'WriteNode({})._chunk_iter_'.format(filename)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        actual = [chunk for chunk in N._chunk_iter_(('x', 'y'), (4, 5), chunks={'z': 2})]
        expected = [slice(None)]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_2D(self):
        filename = 'test.nc'
        testname = 'WriteNode({})._chunk_iter_'.format(filename)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        actual = [chunk for chunk in N._chunk_iter_(('x', 'y'), (4, 5), chunks={'x': 2, 'y': 3})]
        expected = [{'x': slice(0, 2), 'y': slice(0, 3)},
                    {'x': slice(2, None), 'y': slice(0, 3)},
                    {'x': slice(0, 2), 'y': slice(3, None)},
                    {'x': slice(2, None), 'y': slice(3, None)}]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_2D_unnamed(self):
        filename = 'test.nc'
        testname = 'WriteNode({})._chunk_iter_'.format(filename)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        actual = [chunk for chunk in N._chunk_iter_(('x', 'y'), (4, 5), chunks={'x': 2, 'z': 3})]
        expected = [{'x': slice(0, 2)}, {'x': slice(2, None)}]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_2D_reverse(self):
        filename = 'test.nc'
        testname = 'WriteNode({})._chunk_iter_'.format(filename)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        actual = [chunk for chunk in N._chunk_iter_(('y', 'x'), (5, 4), chunks={'x': 2, 'y': 3})]
        expected = [{'x': slice(0, 2), 'y': slice(0, 3)},
                    {'x': slice(0, 2), 'y': slice(3, None)},
                    {'x': slice(2, None), 'y': slice(0, 3)},
                    {'x': slice(2, None), 'y': slice(3, None)}]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_execute_simple(self):
        filename = 'v_x_y_simple.nc'
        testname = 'WriteNode({}).execute()'.format(filename)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        N.execute()
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print
        with netCDF4.Dataset(filename, 'r') as ncf:
            print ncf

    def test_execute_chunk_1D(self):
        filename = 'v_x_y_chunk_1D.nc'
        chunks = {'x': 6}
        testname = 'WriteNode({}).execute(chunks={})'.format(filename, chunks)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        N.execute(chunks=chunks)
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected, input=chunks)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print
        with netCDF4.Dataset(filename, 'r') as ncf:
            print ncf

    def test_execute_chunk_2D(self):
        filename = 'v_x_y_chunk_2D.nc'
        chunks = {'x': 6, 'y': 3}
        testname = 'WriteNode({}).execute(chunks={})'.format(filename, chunks)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        N.execute(chunks=chunks)
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected, input=chunks)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print
        with netCDF4.Dataset(filename, 'r') as ncf:
            print ncf

    def test_execute_chunk_3D(self):
        filename = 'v_x_y_chunk_2D.nc'
        chunks = {'x': 6, 'y': 3, 'z': 7}
        testname = 'WriteNode({}).execute(chunks={})'.format(filename, chunks)
        N = flownodes.WriteNode(filename, *self.vars, ga='global attribute')
        N.execute(chunks=chunks)
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected, input=chunks)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print
        with netCDF4.Dataset(filename, 'r') as ncf:
            print ncf

#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
