"""
FlowNode Unit Tests

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.flownodes import FlowNode, DataNode, ReadNode, EvalNode, MapNode, ValidateNode, WriteNode
from pyconform.physarray import PhysArray, DimensionsError, UnitsError
from pyconform.datasets import DimensionDesc, VariableDesc, FileDesc
from pyconform.functions import Function, find_operator
from testutils import print_test_message, print_ncfile
from cf_units import Unit
from os.path import exists
from os import remove
from glob import glob
from collections import OrderedDict

import unittest
import numpy
import netCDF4


#=======================================================================================================================
# BaseTests
#=======================================================================================================================
class BaseTests(unittest.TestCase):

    def assertPhysArraysEqual(self, left, right, testname='Test', decimal=0):
        if type(left) != type(right):
            self.fail('{} failed - type')
        elif isinstance(left, PhysArray):
            ldata = numpy.ma.asarray(left)
            rdata = numpy.ma.asarray(right)
            if decimal == 0:
                numpy.testing.assert_array_equal(ldata, rdata, '{} failed - data'.format(testname))
            else:
                numpy.testing.assert_array_almost_equal(left, right, decimal, '{} failed - data'.format(testname))
            self.assertEqual(left.dtype, right.dtype, '{} failed - dtype'.format(testname))
            self.assertEqual(left.name, right.name, '{} failed - name'.format(testname))
            self.assertEqual(left.units, right.units, '{} failed - units'.format(testname))
            self.assertEqual(left.dimensions, right.dimensions, '{} failed - dimensions'.format(testname))
            self.assertEqual(left.positive, right.positive, '{} failed - positive'.format(testname))
        else:
            self.assertEqual(left, right, '{} failed')


#=======================================================================================================================
# FlowNodeTests
#=======================================================================================================================
class FlowNodeTests(BaseTests):
    """
    Unit tests for the flownodes.FlowNode class
    """

    def test_init(self):
        indata = 0
        testname = 'FlowNode.__init__({})'.format(indata)
        N = FlowNode(0)
        actual = type(N)
        expected = FlowNode
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertIsInstance(N, expected, '{} failed'.format(testname))

    def test_label_int(self):
        indata = 0
        testname = 'FlowNode({}).label'.format(indata)
        N = FlowNode(indata)
        actual = N.label
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_label_str(self):
        indata = 'abcd'
        testname = 'FlowNode({}).label'.format(indata)
        N = FlowNode(indata)
        actual = N.label
        expected = indata
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_inputs(self):
        indata = ['a', 0, 1, 2, 3]
        testname = 'FlowNode{}.inputs'.format(indata)
        N = FlowNode(*indata)
        actual = N.inputs
        expected = indata[1:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#=======================================================================================================================
# DataNodeTests
#=======================================================================================================================
class DataNodeTests(BaseTests):
    """
    Unit tests for the flownodes.DataNode class
    """

    def test_getitem_all(self):
        indata = PhysArray(numpy.arange(10), units='m', dimensions=('x',))
        testname = 'DataNode.__getitem__(:)'
        N = DataNode(indata)
        actual = N[:]
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = PhysArray(numpy.arange(10), units='m', dimensions=('x',))
        testname = 'DataNode.__getitem__(:5)'
        N = DataNode(indata)
        actual = N[:5]
        expected = PhysArray(indata[:5], units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indata = PhysArray(numpy.arange(10), name=0, units='m', dimensions=('x',))
        indict = {'a': 4, 'x': slice(1, 5, 2)}
        testname = 'DataNode.__getitem__({})'.format(indict)
        N = DataNode(indata)
        actual = N[indict]
        expected = PhysArray(indata[indict['x']], units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))


#=======================================================================================================================
# ReadNodeTests
#=======================================================================================================================
class ReadNodeTests(BaseTests):
    """
    Unit tests for the flownodes.ReadNode class
    """

    def setUp(self):
        self.filename = 'test.nc'
        self.varname = 'v'
        self.dimensions = ('x', 'y')
        self.shape = {'x': 5, 'y': 10}
        self.vardata = {'x': PhysArray(numpy.arange(self.shape['x'], dtype='f'),
                                       units='m', dimensions=('x',), name='x'),
                        'y': PhysArray(numpy.arange(self.shape['y'], dtype='f'),
                                       units='km', dimensions=('y',), name='x'),
                        'v': PhysArray(numpy.arange(self.shape['x'] * self.shape['y'],
                                                    dtype='d').reshape(self.shape['x'], self.shape['y']),
                                       units='K', dimensions=self.dimensions, name='v')}

        dimdescs = {d: DimensionDesc(d, s) for d, s in self.shape.iteritems()}
        vardescs = {vn: VariableDesc(vn, datatype=vd.dtype, attributes={'units': str(vd.units)},
                                     dimensions=[dimdescs[dd] for dd in vd.dimensions])
                    for vn, vd in self.vardata.iteritems()}
        self.filedesc = FileDesc(self.filename, variables=vardescs.values())
        self.vardesc = self.filedesc.variables[self.varname]

        with netCDF4.Dataset(self.filename, 'w') as ncfile:
            for d in self.dimensions:
                ncfile.createDimension(d, self.shape[d])

            for v in self.vardata:
                ncv = ncfile.createVariable(v, self.vardata[v].dtype, self.vardata[v].dimensions)
                ncv.setncatts({'units': str(self.vardata[v].units)})
                ncv[:] = self.vardata[v]

    def tearDown(self):
        if exists(self.filename):
            remove(self.filename)

    def test_getitem_all(self):
        testname = 'ReadNode.__getitem__(:)'
        N = ReadNode(self.vardesc)
        actual = N[:]
        expected = self.vardata[self.varname]
        print_test_message(testname, actual=actual, expected=expected)
        print actual.dtype, expected.dtype
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_slice(self):
        testname = 'ReadNode.__getitem__(:2)'
        N = ReadNode(self.vardesc)
        actual = N[:2]
        expected = self.vardata[self.varname][:2]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_none(self):
        testname = 'ReadNode.__getitem__(None)'
        N = ReadNode(self.vardesc)
        actual = N[None]
        expected = PhysArray(numpy.zeros((0,) * len(self.shape), dtype='d'),
                             units=self.vardata[self.varname].units,
                             dimensions=self.vardata[self.varname].dimensions,
                             name=self.varname)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_tuple(self):
        intuple = (3, slice(2, 4))
        testname = 'ReadNode.__getitem__({})'.format(intuple)
        N = ReadNode(self.vardesc)
        actual = N[intuple]
        expected = PhysArray(self.vardata[self.varname][intuple], dimensions=('y',))
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indict = {'a': 4, 'x': slice(1, 5, 2)}
        testname = 'ReadNode.__getitem__({})'.format(indict)
        N = ReadNode(self.vardesc)
        actual = N[indict]
        expected = self.vardata[self.varname][slice(1, 5, 2)]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_dict_2(self):
        indict = {'a': 4, 'y': slice(1, 5, 2)}
        testname = 'ReadNode.__getitem__({})'.format(indict)
        N = ReadNode(self.vardesc)
        actual = N[indict]
        expected = self.vardata[self.varname][:, slice(1, 5, 2)]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))


#=======================================================================================================================
# EvalNodeTests
#=======================================================================================================================
class EvalNodeTests(BaseTests):
    """
    Unit tests for the flownodes.EvalNode class
    """

    def test_getitem_all(self):
        indata = PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalNode.__getitem__(:)'
        N = EvalNode(0, lambda x: x, indata)
        actual = N[:]
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_none(self):
        indata = PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalNode.__getitem__(None)'
        N = EvalNode(0, lambda x: x, indata)
        actual = N[None]
        expected = PhysArray(numpy.zeros((0,), dtype=indata.dtype),
                             units='m', dimensions=('x',), name='[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]')
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = PhysArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalNode.__getitem__(:5)'
        N = EvalNode(0, lambda x: x, indata)
        actual = N[:5]
        expected = indata[:5]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indata = PhysArray(range(10), units='m', dimensions=('x',))
        testname = "EvalNode.__getitem__({'x': slice(5, None), 'y': 6})"
        N = EvalNode(0, lambda x: x, indata)
        actual = N[{'x': slice(5, None), 'y': 6}]
        expected = indata[slice(5, None)]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_add(self):
        d1 = PhysArray(numpy.arange(1, 5), name='X1', units='m', dimensions=('x',))
        d2 = PhysArray(numpy.arange(5, 9), name='X2', units='m', dimensions=('x',))
        N1 = DataNode(d1)
        N2 = DataNode(d2)
        N3 = EvalNode(3, find_operator('+', numargs=2), N1, N2)
        testname = 'EvalNode.__getitem__(:)'
        actual = N3[:]
        expected = d1 + d2
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_add_slice(self):
        d1 = PhysArray(numpy.arange(1, 5), name='X1', units='m', dimensions=('x',))
        d2 = PhysArray(numpy.arange(5, 9), name='X2', units='m', dimensions=('x',))
        N1 = DataNode(d1)
        N2 = DataNode(d2)
        N3 = EvalNode(3, find_operator('+', numargs=2), N1, N2)
        testname = 'EvalNode.__getitem__(:2)'
        actual = N3[:2]
        expected = d1[:2] + d2[:2]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_add_none(self):
        d1 = PhysArray(numpy.arange(1, 5), name='X1', units='m', dimensions=('x',))
        d2 = PhysArray(numpy.arange(5, 9), name='X2', units='m', dimensions=('x',))
        N1 = DataNode(d1)
        N2 = DataNode(d2)
        N3 = EvalNode(3, find_operator('+', numargs=2), N1, N2)
        testname = 'EvalNode.__getitem__(None)'
        actual = N3[None]
        expected = PhysArray([], dtype='int64', units='m', dimensions=('x',), name='(X1+X2)')
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_sumlike_dimensions(self):
        class myfunc(Function):
            key = 'myfunc'

            def __init__(self, d, *dims):
                super(myfunc, self).__init__(d, *dims)
                self.add_sumlike_dimensions(*dims)

            def __getitem__(self, _):
                return self.arguments[0]
        d = PhysArray(numpy.arange(1, 5), name='d', units='m', dimensions=('x',))
        N = EvalNode(1, myfunc, d, 'x')
        testname = 'EvalNode.sumlike_dimensions'
        actual = N.sumlike_dimensions
        expected = set(['x'])
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        N[0:2]
        actual = N.sumlike_dimensions
        expected = set(['x'])
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#=======================================================================================================================
# MapNodeTests
#=======================================================================================================================
class MapNodeTests(BaseTests):
    """
    Unit tests for the flownodes.MapNode class
    """

    def setUp(self):
        array = PhysArray(numpy.arange(10), name=0, units='km', dimensions=('x',))
        self.indata = DataNode(array)

    def test_getitem_all(self):
        testname = 'MapNode.__getitem__(:)'
        N = MapNode(0, self.indata, dmap={'x': 'y'})
        actual = N[:]
        expected = PhysArray(self.indata[:], dimensions=('y',), name='map(0, from=[x], to=[y])')
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_slice(self):
        testname = 'MapNode.__getitem__(:3)'
        N = MapNode(0, self.indata, dmap={'x': 'y'})
        actual = N[:3]
        expected = PhysArray(self.indata[:3], dimensions=('y',), name='map(0, from=[x], to=[y])',
                             dtype=actual.dtype)
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_none(self):
        testname = 'MapNode.__getitem__(None)'
        N = MapNode(0, self.indata, dmap={'x': 'y'})
        actual = N[None]
        expected = PhysArray(numpy.arange(0), units='km', dimensions=('y',), name='map(0, from=[x], to=[y])')
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_getitem_slice_no_dmap(self):
        testname = 'MapNode(dmap={}, dimensions=indims).__getitem__(:3)'
        N = MapNode(0, self.indata)
        actual = N[:3]
        expected = PhysArray(self.indata[:3], dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))


#=======================================================================================================================
# ValidateNodeTests
#=======================================================================================================================
class ValidateNodeTests(BaseTests):
    """
    Unit tests for the flownodes.ValidateNode class
    """

    def test_nothing(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        V1 = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),))
        testname = 'OK: ValidateNode().__getitem__(:)'
        N1 = ValidateNode(V1, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_units_ok(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'units': 'm'})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_time_units_ok(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='days since 2000-01-01 00:00:00', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={
                              'units': 'days since 2000-01-01 00:00:00', 'calendar': 'gregorian'})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_ok(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),))
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_min_ok(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'valid_min': 0})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_max_ok(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'valid_max': 10})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_minmax_getitem_none(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),),
                              attributes={'valid_min': 0, 'valid_max': 2})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[None]
        expected = N0[None]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_min_mean_abs_ok(self):
        N0 = DataNode(PhysArray(numpy.arange(-5, 10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'ok_min_mean_abs': 3})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_max_mean_abs_ok(self):
        N0 = DataNode(PhysArray(numpy.arange(-5, 10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'ok_max_mean_abs': 5})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_units_convert(self):
        N0 = DataNode(PhysArray(numpy.arange(10.0), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'units': 'km'})
        testname = 'CONVERT: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = (Unit('m').convert(N0[:], Unit('km'))).astype(numpy.float64)
        expected.name = 'convert(x, from=m, to=km)'
        expected.units = Unit('km')
        expected.mask = False
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_units_inherit(self):
        N0 = DataNode(PhysArray(numpy.arange(10.0), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'units': '?'})
        testname = 'INHERIT: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_dimensions_transpose(self):
        N0 = DataNode(PhysArray([[1., 2.], [3., 4.]], name='a', units='m', dimensions=('x', 'y')))
        indata = VariableDesc('validate(a)', dimensions=(DimensionDesc('y'), DimensionDesc('x')))
        testname = 'TRANSPOSE: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:].dimensions
        expected = tuple(indata.dimensions.keys())
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_time_units_convert(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='days since 2000-01-01 00:00:00', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={
                              'units': 'hours since 2000-01-01 00:00:00', 'calendar': 'gregorian'})
        testname = 'CONVERT: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:].convert(Unit('hours since 2000-01-01 00:00:00'))
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_time_units_inherit(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='days since 2000-01-01 00:00:00', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'units': ''})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_time_units_inherit_refdatetime(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='days since 2000-01-01 00:00:00', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'units': 'hours since ?'})
        testname = 'OK: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:].convert('hours since 2000-01-01 00:00:00')
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_time_units_convert_nocal(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', dimensions=('x',),
                                units=Unit('days since 2000-01-01 00:00:00', calendar='noleap')))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),),
                              attributes={'units': 'hours since 2000-01-01 00:00:00'})
        testname = 'CONVERT: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:].convert(Unit('hours since 2000-01-01 00:00:00', calendar='noleap'))
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_time_units_error_calendar(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='days since 2000-01-01 00:00:00', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={
                              'units': 'days since 2000-01-01 00:00:00', 'calendar': 'noleap'})
        testname = 'FAIL: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        print_test_message(testname, indata=indata, expected=UnitsError)
        self.assertRaises(UnitsError, N1.__getitem__, slice(None))

    def test_dimensions_error(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('y'),))
        testname = 'FAIL: ValidateNode({!r}).__getitem__(:)'.format(indata)
        expected = DimensionsError
        V = ValidateNode(indata, N0)
        print_test_message(testname, indata=indata, expected=expected)
        self.assertRaises(expected, V.__getitem__, slice(None))

    def test_min_warn(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'valid_min': 2})
        testname = 'WARN: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_max_warn(self):
        N0 = DataNode(PhysArray(numpy.arange(10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'valid_max': 8})
        testname = 'WARN: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_min_mean_abs_warn(self):
        N0 = DataNode(PhysArray(numpy.arange(-5, 10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'ok_min_mean_abs': 5})
        testname = 'WARN: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))

    def test_max_mean_abs_warn(self):
        N0 = DataNode(PhysArray(numpy.arange(-5, 10), name='x', units='m', dimensions=('x',)))
        indata = VariableDesc('validate(x)', dimensions=(DimensionDesc('x'),), attributes={'ok_max_mean_abs': 3})
        testname = 'WARN: ValidateNode({!r}).__getitem__(:)'.format(indata)
        N1 = ValidateNode(indata, N0)
        actual = N1[:]
        expected = N0[:]
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertPhysArraysEqual(actual, expected, '{} failed'.format(testname))


#=======================================================================================================================
# WriteNodeTests
#=======================================================================================================================
class WriteNodeTests(BaseTests):
    """
    Unit tests for the flownodes.WriteNode class
    """

    def setUp(self):
        NX = 3
        X0 = -1
        xdata = PhysArray(numpy.arange(X0, X0 + NX, dtype='d'), name='X', units='m', dimensions=('x',))

        NY = 4
        Y0 = 0
        ydata = PhysArray(numpy.arange(Y0, Y0 + NY, dtype='d'), name='Y', units='m', dimensions=('y',))

        NT = 2
        tunits = Unit('days since 2000-01-01', calendar='noleap')
        tdata = PhysArray(numpy.arange(0, NT, dtype='d'), name='T', units=tunits, dimensions=('t',))
        t2data = PhysArray(numpy.arange(0, NT, dtype='d') + 2, name='_T', units=tunits, dimensions=('t',))

        vdata = PhysArray(numpy.arange(0, NX * NY * NT, dtype='f').reshape(NX, NY, NT), name='V', units='K',
                          dimensions=('x', 'y', 't'))

        self.data = {'X': xdata, 'Y': ydata, 'T': tdata, '_T': t2data, 'V': vdata}
        self.atts = {'X': {'xa1': 'x attribute 1', 'xa2': 'x attribute 2', 'axis': 'X', 'units': str(xdata.units)},
                     'Y': {'ya1': 'y attribute 1', 'ya2': 'y attribute 2', 'axis': 'Y',
                           'direction': 'decreasing', 'units': str(ydata.units)},
                     'T': {'axis': 'T', 'ta1': 'time attribute', 'units': str(tdata.units),
                           'calendar': tdata.units.calendar},
                     '_T': {'ta1': 'hidden time attribute', 'units': str(t2data.units),
                           'calendar': t2data.units.calendar},
                     'V': {'va1': 'v attribute 1', 'va2': 'v attribute 2', 'units': str(vdata.units)}}

        dimdescs = {n: DimensionDesc(n, s) for x in self.data.itervalues() for n, s in zip(x.dimensions, x.shape)}
        vardescs = {n: VariableDesc(n, datatype=self.data[n].dtype, attributes=self.atts[n],
                                    dimensions=tuple(dimdescs[d] for d in self.data[n].dimensions)) for n in self.data}
        self.vardescs = vardescs
        self.nodes = {n: ValidateNode(self.vardescs[n], DataNode(self.data[n])) for n in self.data}

    def tearDown(self):
        for fname in glob('*.nc'):
            remove(fname)

    def test_init(self):
        filename = 'test.nc'
        testname = 'WriteNode.__init__({})'.format(filename)
        filedesc = FileDesc(filename, variables=self.vardescs.values())
        N = WriteNode(filedesc, inputs=self.nodes.values())
        actual = type(N)
        expected = WriteNode
        print_test_message(testname, actual=actual, expected=expected)
        self.assertIsInstance(N, expected, '{} failed'.format(testname))

    def test_chunk_iter_default(self):
        dsizes = OrderedDict([('x', 2), ('y', 3)])
        testname = 'WriteNode._chunk_iter_({})'.format(dsizes)
        actual = [chunk for chunk in WriteNode._chunk_iter_(dsizes)]
        expected = [OrderedDict([('x', slice(0, None, None)), ('y', slice(0, None, None))])]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_1D(self):
        dsizes = OrderedDict([('x', 4), ('y', 5)])
        chunks = {'x': 2}
        testname = 'WriteNode._chunk_iter_({}, chunks={})'.format(dsizes, chunks)
        actual = [chunk for chunk in WriteNode._chunk_iter_(dsizes, chunks=chunks)]
        expected = [OrderedDict([('x', slice(0, 2)), ('y', slice(0, None))]),
                    OrderedDict([('x', slice(2, None)), ('y', slice(0, None))])]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_1D_unnamed(self):
        dsizes = OrderedDict([('x', 4), ('y', 5)])
        chunks = {'z': 2}
        testname = 'WriteNode._chunk_iter_({}, chunks={})'.format(dsizes, chunks)
        actual = [chunk for chunk in WriteNode._chunk_iter_(dsizes, chunks=chunks)]
        expected = [OrderedDict([('x', slice(0, None, None)), ('y', slice(0, None, None))])]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_2D(self):
        dsizes = OrderedDict([('x', 4), ('y', 5)])
        chunks = {'x': 2, 'y': 3}
        testname = 'WriteNode._chunk_iter_({}, chunks={})'.format(dsizes, chunks)
        actual = [chunk for chunk in WriteNode._chunk_iter_(dsizes, chunks=chunks)]
        expected = [OrderedDict([('x', slice(0, 2, None)), ('y', slice(0, 3, None))]),
                    OrderedDict([('x', slice(0, 2, None)), ('y', slice(3, None, None))]),
                    OrderedDict([('x', slice(2, None, None)), ('y', slice(0, 3, None))]),
                    OrderedDict([('x', slice(2, None, None)), ('y', slice(3, None, None))])]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_2D_unnamed(self):
        dsizes = OrderedDict([('x', 4), ('y', 5)])
        chunks = {'x': 2, 'z': 3}
        testname = 'WriteNode._chunk_iter_({}, chunks={})'.format(dsizes, chunks)
        actual = [chunk for chunk in WriteNode._chunk_iter_(dsizes, chunks=chunks)]
        expected = [OrderedDict([('x', slice(0, 2, None)), ('y', slice(0, None, None))]),
                    OrderedDict([('x', slice(2, None, None)), ('y', slice(0, None, None))])]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_chunk_iter_2D_reverse(self):
        dsizes = OrderedDict([('y', 5), ('x', 4)])
        chunks = {'x': 2, 'y': 3}
        testname = 'WriteNode._chunk_iter_({}, chunks={})'.format(dsizes, chunks)
        actual = [chunk for chunk in WriteNode._chunk_iter_(dsizes, chunks=chunks)]
        expected = [OrderedDict([('y', slice(0, 3, None)), ('x', slice(0, 2, None))]),
                    OrderedDict([('y', slice(3, None, None)), ('x', slice(0, 2, None))]),
                    OrderedDict([('y', slice(0, 3, None)), ('x', slice(2, None, None))]),
                    OrderedDict([('y', slice(3, None, None)), ('x', slice(2, None, None))])]
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_invert_dims(self):
        dsizes = OrderedDict([('x', 4), ('y', 5)])
        chunk = OrderedDict([('x', slice(0, 2)), ('y', slice(1, 3))])
        idims = {'y'}
        testname = 'WriteNode._invert_dims({}, {}, idims={})'.format(dsizes, chunk, idims)
        actual = WriteNode._invert_dims_(dsizes, chunk, idims=idims)
        expected = OrderedDict([('x', slice(0, 2, None)), ('y', slice(3, 1, -1))])
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_execute_simple_default(self):
        filename = 'v_x_y_simple.nc'
        testname = 'WriteNode({}).execute()'.format(filename)
        filedesc = FileDesc(filename, variables=self.vardescs.values(), attributes={'ga': 'global attribute'})
        N = WriteNode(filedesc, inputs=self.nodes.values())
        N.enable_history()
        N.execute()
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print_ncfile(filename)

    def test_execute_simple_autoparse(self):
        filename = 'v.{%Y%m%d-%Y%m%d}.nc'
        testname = 'WriteNode({}).execute()'.format(filename)
        filedesc = FileDesc(filename, variables=self.vardescs.values(), attributes={'ga': 'global attribute'})
        N = WriteNode(filedesc, inputs=self.nodes.values())
        N.enable_history()
        N.execute()
        newfname = 'v.20000101-20000102.nc'
        actual = exists(newfname)
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print_ncfile(newfname)

    def test_execute_simple_autoparse_fail(self):
        filename = 'v.{%Y%m%d-%Y%m%d}.nc'
        vdescs = {n: self.vardescs[n] for n in self.vardescs if n != 'T'}
        filedesc = FileDesc(filename, variables=vdescs.values(), attributes={'ga': 'global attribute'})
        vnodes = {n: self.nodes[n] for n in self.nodes if n != 'T'}
        with self.assertRaises(ValueError):
            WriteNode(filedesc, inputs=vnodes.values())

    def test_execute_simple_autoparse_hidden_time(self):
        filename = 'v.{%Y%m%d-%Y%m%d}.nc'
        testname = 'WriteNode({}).execute()'.format(filename)
        vdescs = {n: self.vardescs[n] for n in self.vardescs if n != 'T'}
        filedesc = FileDesc(filename, variables=vdescs.values(), attributes={'ga': 'global attribute'},
                            autoparse_time_variable='_T')
        vnodes = {n: self.nodes[n] for n in self.nodes if n != 'T'}
        N = WriteNode(filedesc, inputs=vnodes.values())
        N.enable_history()
        N.execute()
        newfname = 'v.20000103-20000104.nc'
        actual = exists(newfname)
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print_ncfile(newfname)

    def test_execute_simple_nc3(self):
        filename = 'v_x_y_simple_nc3.nc'
        testname = 'WriteNode({}).execute()'.format(filename)
        filedesc = FileDesc(filename, format='NETCDF3_CLASSIC', variables=self.vardescs.values(),
                            attributes={'ga': 'global attribute'})
        N = WriteNode(filedesc, inputs=self.nodes.values())
        N.enable_history()
        N.execute()
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print_ncfile(filename)

    def test_execute_simple_nc4(self):
        filename = 'v_x_y_simple_nc4.nc'
        testname = 'WriteNode({}).execute()'.format(filename)
        filedesc = FileDesc(filename, format='NETCDF4', variables=self.vardescs.values(),
                            attributes={'ga': 'global attribute'})
        N = WriteNode(filedesc, inputs=self.nodes.values())
        N.enable_history()
        N.execute()
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print_ncfile(filename)

    def test_execute_chunk_1D(self):
        filename = 'v_x_y_chunk_1D.nc'
        chunks = {'x': 6}
        testname = 'WriteNode({}).execute(chunks={})'.format(filename, chunks)
        filedesc = FileDesc(filename, variables=self.vardescs.values(), attributes={'ga': 'global attribute'})
        N = WriteNode(filedesc, inputs=self.nodes.values())
        N.enable_history()
        N.execute(chunks=chunks)
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected, chunks=chunks)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print_ncfile(filename)

    def test_execute_chunk_2D(self):
        filename = 'v_x_y_chunk_2D.nc'
        chunks = {'x': 6, 'y': 3}
        testname = 'WriteNode({}).execute(chunks={})'.format(filename, chunks)
        filedesc = FileDesc(filename, variables=self.vardescs.values(), attributes={'ga': 'global attribute'})
        N = WriteNode(filedesc, inputs=self.nodes.values())
        N.enable_history()
        N.execute(chunks=chunks)
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected, chunks=chunks)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print_ncfile(filename)

    def test_execute_chunk_3D(self):
        filename = 'v_x_y_chunk_2D.nc'
        chunks = {'x': 6, 'y': 3, 'z': 7}
        testname = 'WriteNode({}).execute(chunks={})'.format(filename, chunks)
        filedesc = FileDesc(filename, variables=self.vardescs.values(), attributes={'ga': 'global attribute'})
        N = WriteNode(filedesc, inputs=self.nodes.values())
        N.enable_history()
        N.execute(chunks=chunks)
        actual = exists(filename)
        expected = True
        print_test_message(testname, actual=actual, expected=expected, chunks=chunks)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        print_ncfile(filename)


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
