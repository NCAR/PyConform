"""
Data Flow Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import dataflows
from testutils import print_test_message
from cf_units import Unit
from os.path import exists
from os import remove
from glob import glob

import unittest
import numpy
import netCDF4


#===================================================================================================
# DataNodeTests
#===================================================================================================
# For testing only
class MockDataNode(dataflows.DataNode):
    def __getitem__(self, index):
        return index

class DataNodeTests(unittest.TestCase):
    """
    Unit tests for the dataflows.DataNode class
    """

    def test_init(self):
        indata = 0
        testname = 'DataNode.__init__({})'.format(indata)
        N = MockDataNode(0)
        actual = type(N)
        expected = dataflows.DataNode
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(N, expected, '{} failed'.format(testname))

    def test_label_int(self):
        indata = 0
        testname = 'DataNode({}).label'.format(indata)
        N = MockDataNode(indata)
        actual = N.label
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_label_str(self):
        indata = 'abcd'
        testname = 'DataNode({}).label'.format(indata)
        N = MockDataNode(indata)
        actual = N.label
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_inputs(self):
        indata = ['a', 0, 1, 2, 3]
        testname = 'DataNode{}.inputs'.format(indata)
        N = MockDataNode(*indata)
        actual = N.inputs
        expected = indata[1:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===================================================================================================
# CreateDataNodeTests
#===================================================================================================
class CreateDataNodeTests(unittest.TestCase):
    """
    Unit tests for the dataflows.CreateDataNode class
    """

    def test_getitem_all(self):
        indata = numpy.arange(10)
        testname = 'CreateDataNode.__getitem__(:)'
        N = dataflows.CreateDataNode(0, indata, units='m', dimensions=('x',))
        actual = N[:]
        expected = dataflows.PhysArray(indata, units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = numpy.arange(10)
        testname = 'CreateDataNode.__getitem__(:5)'
        N = dataflows.CreateDataNode(0, indata, units='m', dimensions=('x',))
        actual = N[:5]
        expected = dataflows.PhysArray(indata[:5], units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indata = numpy.arange(10)
        indict = {'a': 4, 'x': slice(1, 5, 2)}
        testname = 'CreateDataNode.__getitem__({})'.format(indict)
        N = dataflows.CreateDataNode(0, indata, units='m', dimensions=('x',))
        actual = N[indict]
        expected = dataflows.PhysArray(indata[indict['x']], units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# ReadDataNodeTests
#===================================================================================================
class ReadDataNodeTests(unittest.TestCase):
    """
    Unit tests for the dataflows.ReadDataNode class
    """

    def setUp(self):
        self.filename = 'test.nc'
        self.varname = 'v'
        self.dimensions = ('x', 'y')
        self.shape = {'x': 5, 'y': 10}
        self.vardata = {'x': dataflows.PhysArray(numpy.arange(self.shape['x'], dtype='f'),
                                                 units='m', dimensions=('x',)),
                        'y': dataflows.PhysArray(numpy.arange(self.shape['y'], dtype='f'),
                                                 units='km', dimensions=('y',)),
                        'v': dataflows.PhysArray(numpy.arange(self.shape['x'] * self.shape['y'],
                                                              dtype='d').reshape(self.shape['x'], self.shape['y']),
                                                 units='K', dimensions=self.dimensions)}

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
        testname = 'ReadDataNode.__getitem__(:)'
        N = dataflows.ReadDataNode(self.filename, self.varname)
        actual = N[:]
        expected = self.vardata[self.varname]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        testname = 'ReadDataNode.__getitem__(:2)'
        N = dataflows.ReadDataNode(self.filename, self.varname)
        actual = N[:2]
        expected = self.vardata[self.varname][:2]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_none(self):
        testname = 'ReadDataNode.__getitem__(None)'
        N = dataflows.ReadDataNode(self.filename, self.varname)
        actual = N[None]
        expected = dataflows.PhysArray(numpy.empty((0,) * len(self.shape), dtype='d'),
                                       units=self.vardata[self.varname].units,
                                       dimensions=self.vardata[self.varname].dimensions)
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_tuple(self):
        intuple = (3, slice(2, 4))
        testname = 'ReadDataNode.__getitem__({})'.format(intuple)
        N = dataflows.ReadDataNode(self.filename, self.varname)
        actual = N[intuple]
        expected = dataflows.PhysArray(self.vardata[self.varname][intuple], dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indict = {'a': 4, 'x': slice(1, 5, 2)}
        testname = 'ReadDataNode.__getitem__({})'.format(indict)
        N = dataflows.ReadDataNode(self.filename, self.varname)
        actual = N[indict]
        expected = self.vardata[self.varname][slice(1, 5, 2)]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict_2(self):
        indict = {'a': 4, 'y': slice(1, 5, 2)}
        testname = 'ReadDataNode.__getitem__({})'.format(indict)
        N = dataflows.ReadDataNode(self.filename, self.varname)
        actual = N[indict]
        expected = self.vardata[self.varname][:, slice(1, 5, 2)]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# EvalDataNodeTests
#===================================================================================================
class EvalDataNodeTests(unittest.TestCase):
    """
    Unit tests for the dataflows.EvalDataNode class
    """

    def test_getitem_all(self):
        indata = dataflows.PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalDataNode.__getitem__(:)'
        N = dataflows.EvalDataNode(0, lambda x: x, indata)
        actual = N[:]
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_none(self):
        indata = dataflows.PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalDataNode.__getitem__(None)'
        N = dataflows.EvalDataNode(0, lambda x: x, indata)
        actual = N[None]
        expected = dataflows.PhysArray(numpy.empty((0,), dtype=indata.dtype),
                                       units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = dataflows.PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalDataNode.__getitem__(:5)'
        N = dataflows.EvalDataNode(0, lambda x: x, indata)
        actual = N[:5]
        expected = indata[:5]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indata = dataflows.PhysArray(range(10), units='m', dimensions=('x',))
        testname = "EvalDataNode.__getitem__({'x': slice(5, None), 'y': 6})"
        N = dataflows.EvalDataNode(0, lambda x: x, indata)
        actual = N[{'x': slice(5, None), 'y': 6}]
        expected = indata[slice(5, None)]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add(self):
        d1 = dataflows.PhysArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = dataflows.PhysArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = dataflows.EvalDataNode(1, lambda x: x, d1)
        N2 = dataflows.EvalDataNode(2, lambda x: x, d2)
        N3 = dataflows.EvalDataNode(3, lambda a, b: a + b, N1, N2)
        testname = 'EvalDataNode.__getitem__(:)'
        actual = N3[:]
        expected = d1 + d2
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add_slice(self):
        d1 = dataflows.PhysArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = dataflows.PhysArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = dataflows.EvalDataNode(1, lambda x: x, d1)
        N2 = dataflows.EvalDataNode(2, lambda x: x, d2)
        N3 = dataflows.EvalDataNode(3, lambda a, b: a + b, N1, N2)
        testname = 'EvalDataNode.__getitem__(:2)'
        actual = N3[:2]
        expected = d1[:2] + d2[:2]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add_none(self):
        d1 = dataflows.PhysArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = dataflows.PhysArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = dataflows.EvalDataNode(1, lambda x: x, d1)
        N2 = dataflows.EvalDataNode(2, lambda x: x, d2)
        N3 = dataflows.EvalDataNode(3, lambda a, b: a + b, N1, N2)
        testname = 'EvalDataNode.__getitem__(None)'
        actual = N3[None]
        expected = dataflows.PhysArray(numpy.arange(0), units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# MapDataNodeTests
#===================================================================================================
class MapDataNodeTests(unittest.TestCase):
    """
    Unit tests for the dataflows.MapDataNode class
    """

    def setUp(self):
        self.indata = dataflows.CreateDataNode(0, numpy.arange(10), units='km', dimensions=('x',))

    def test_getitem_all(self):
        testname = 'MapDataNode.__getitem__(:)'
        N = dataflows.MapDataNode(0, self.indata, dmap={'x': 'y'})
        actual = N[:]
        expected = dataflows.PhysArray(self.indata[:], dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        testname = 'MapDataNode.__getitem__(:3)'
        N = dataflows.MapDataNode(0, self.indata, dmap={'x': 'y'})
        actual = N[:3]
        expected = dataflows.PhysArray(self.indata[:3], dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_none(self):
        testname = 'MapDataNode.__getitem__(None)'
        N = dataflows.MapDataNode(0, self.indata, dmap={'x': 'y'})
        actual = N[None]
        expected = dataflows.PhysArray(numpy.arange(0), units='km', dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice_no_dmap(self):
        testname = 'MapDataNode(dmap={}, dimensions=indims).__getitem__(:3)'
        N = dataflows.MapDataNode(0, self.indata)
        actual = N[:3]
        expected = dataflows.PhysArray(self.indata[:3], dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# ValidateDataNodeTests
#===================================================================================================
class ValidateDataNodeTests(unittest.TestCase):
    """
    Unit tests for the dataflows.ValidateDataNode class
    """

    def test_nothing(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        testname = 'OK: ValidateDataNode().__getitem__(:)'
        N1 = dataflows.ValidateDataNode('validate(x)', N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_units_ok(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'units': Unit('m')}
        testname = ('OK: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_time_units_ok(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='days since 2000-01-01 00:00:00', dimensions=('x',))
        indata = {'units': 'days since 2000-01-01 00:00:00', 'calendar': 'gregorian'}
        testname = ('OK: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_dimensions_ok(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'dimensions': ('x',)}
        testname = ('OK: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_min_ok(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'valid_min': 0}
        testname = ('OK: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_max_ok(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'valid_max': 10}
        testname = ('OK: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_min_mean_abs_ok(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        indata = {'ok_min_mean_abs': 3}
        testname = ('OK: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_max_mean_abs_ok(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        indata = {'ok_max_mean_abs': 5}
        testname = ('OK: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_units_warn(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'units': Unit('km')}
        testname = ('WARN: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_time_units_warn(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='days since 2000-01-01 00:00:00', dimensions=('x',))
        indata = {'units': 'hours since 2000-01-01 00:00:00', 'calendar': 'gregorian'}
        testname = ('WARN: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_time_units_warn_calendar(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='days since 2000-01-01 00:00:00', dimensions=('x',))
        indata = {'units': 'days since 2000-01-01 00:00:00', 'calendar': 'noleap'}
        testname = ('WARN: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_dimensions_warn(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'dimensions': ('y',)}
        testname = ('WARN: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_min_warn(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'valid_min': 2}
        testname = ('WARN: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_max_warn(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(10), units='m', dimensions=('x',))
        indata = {'valid_max': 8}
        testname = ('WARN: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_min_mean_abs_warn(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        indata = {'ok_min_mean_abs': 5}
        testname = ('WARN: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_max_mean_abs_warn(self):
        N0 = dataflows.CreateDataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        indata = {'ok_max_mean_abs': 3}
        testname = ('WARN: ValidateDataNode({}).__getitem__(:)'
                    '').format(', '.join('{!s}={!r}'.format(k, v) for k, v in indata.iteritems()))
        N1 = dataflows.ValidateDataNode('validate(x)', N0, **indata)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))


#===================================================================================================
# WriteDataNodeTests
#===================================================================================================
class WriteDataNodeTests(unittest.TestCase):
    """
    Unit tests for the dataflows.WriteDataNode class
    """

    def setUp(self):
        x = dataflows.CreateDataNode('x', numpy.arange(-5, 10), units='m', dimensions=('x',))
        self.x = dataflows.ValidateDataNode('x', x, xa1='x attribute 1', xa2='x attribute 2')
        y = dataflows.CreateDataNode('y', numpy.arange(0, 8), units='m', dimensions=('y',))
        self.y = dataflows.ValidateDataNode('y', y, ya1='y attribute 1', ya2='y attribute 2')
        vdata = numpy.arange(15*8, dtype=numpy.float64).reshape((15,8))
        v = dataflows.CreateDataNode('v', vdata, units='K', dimensions=('x', 'y'))
        self.v = dataflows.ValidateDataNode('v', v, va1='v attribute 1', va2='v attribute 2')
        self.vars = [self.x, self.y, self.v]

    def tearDown(self):
        for fname in glob('*.nc'):
            remove(fname)

    def test_init(self):
        filename = 'test.nc'
        testname = 'WriteDataNode.__init__({})'.format(filename)
        N = dataflows.WriteDataNode(filename, *self.vars, ga='global attribute')
        actual = type(N)
        expected = dataflows.WriteDataNode
        print_test_message(testname, actual=actual, expected=expected)
        self.assertIsInstance(N, expected, '{} failed'.format(testname))

    def test_simple(self):
        filename = 'v_x_y_simple.nc'
        testname = 'WriteDataNode({})[:]'.format(filename)
        N = dataflows.WriteDataNode(filename, *self.vars, ga='global attribute')
        N[:]
        N.close()
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print
        with netCDF4.Dataset(filename, 'r') as ncf:
            print ncf

    def test_chunk(self):
        filename = 'v_x_y_chunk.nc'
        testname = 'WriteDataNode({})[chunk]'.format(filename)
        N = dataflows.WriteDataNode(filename, *self.vars, ga='global attribute')
        for ix in range(15):
            N[{'x': ix}]
        N.close()
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
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
