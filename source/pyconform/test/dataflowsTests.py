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

import unittest
import numpy
import netCDF4


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
        indata = ('a', 0, 1, 2, 3)
        testname = 'DataNode{}._inputs'.format(indata)
        N = MockDataNode(*indata)
        actual = N._inputs
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
        expected = dataflows.DataArray(indata, units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = numpy.arange(10)
        testname = 'CreateDataNode.__getitem__(:5)'
        N = dataflows.CreateDataNode(0, indata, units='m', dimensions=('x',))
        actual = N[:5]
        expected = dataflows.DataArray(indata[:5], units='m', dimensions=('x',))
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
        expected = dataflows.DataArray(indata[indict['x']], units='m', dimensions=('x',))
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
        self.vardata = {'x': dataflows.DataArray(numpy.arange(self.shape['x'], dtype='f'),
                                                 units='m', dimensions=('x',)),
                        'y': dataflows.DataArray(numpy.arange(self.shape['y'], dtype='f'),
                                                 units='km', dimensions=('y',)),
                        'v': dataflows.DataArray(numpy.arange(self.shape['x'] * self.shape['y'],
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
        expected = dataflows.DataArray(numpy.empty((0,) * len(self.shape), dtype='d'),
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
        expected = dataflows.DataArray(self.vardata[self.varname][intuple], dimensions=('y',))
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
        indata = dataflows.DataArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalDataNode.__getitem__(:)'
        N = dataflows.EvalDataNode(0, lambda x: x, indata)
        actual = N[:]
        expected = indata
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_none(self):
        indata = dataflows.DataArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalDataNode.__getitem__(None)'
        N = dataflows.EvalDataNode(0, lambda x: x, indata)
        actual = N[None]
        expected = dataflows.DataArray(numpy.empty((0,), dtype=indata.dtype),
                                       units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_slice(self):
        indata = dataflows.DataArray(range(10), units='m', dimensions=('x',))
        testname = 'EvalDataNode.__getitem__(:5)'
        N = dataflows.EvalDataNode(0, lambda x: x, indata)
        actual = N[:5]
        expected = indata[:5]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_dict(self):
        indata = dataflows.DataArray(range(10), units='m', dimensions=('x',))
        testname = "EvalDataNode.__getitem__({'x': slice(5, None), 'y': 6})"
        N = dataflows.EvalDataNode(0, lambda x: x, indata)
        actual = N[{'x': slice(5, None), 'y': 6}]
        expected = indata[slice(5, None)]
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_add(self):
        d1 = dataflows.DataArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = dataflows.DataArray(numpy.arange(5, 9), units='m', dimensions=('x',))
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
        d1 = dataflows.DataArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = dataflows.DataArray(numpy.arange(5, 9), units='m', dimensions=('x',))
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
        d1 = dataflows.DataArray(numpy.arange(1, 5), units='m', dimensions=('x',))
        d2 = dataflows.DataArray(numpy.arange(5, 9), units='m', dimensions=('x',))
        N1 = dataflows.EvalDataNode(1, lambda x: x, d1)
        N2 = dataflows.EvalDataNode(2, lambda x: x, d2)
        N3 = dataflows.EvalDataNode(3, lambda a, b: a + b, N1, N2)
        testname = 'EvalDataNode.__getitem__(None)'
        actual = N3[None]
        expected = dataflows.DataArray(numpy.arange(0), units='m', dimensions=('x',))
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

    def test_getitem_all(self):
        indata = dataflows.CreateDataNode(0, numpy.arange(10), units='km', dimensions=('y',))
        dmap = {'x': 'y'}
        testname = 'MapDataNode.__getitem__(:)'
        N = dataflows.MapDataNode(0, indata, dmap, dimensions=('x',), units='m')
        actual = N[:]
        expected = dataflows.DataArray(indata[:], units='m', dimensions=('x',))
        print_test_message(testname, actual=actual, expected=expected)
        numpy.testing.assert_array_equal(actual, expected, '{} failed'.format(testname))
        self.assertEqual(actual.units, expected.units, '{} failed'.format(testname))
        self.assertEqual(actual.dimensions, expected.dimensions, '{} failed'.format(testname))

    def test_getitem_none(self):
        indata = dataflows.CreateDataNode(0, numpy.arange(10), units='km', dimensions=('y',))
        dmap = {'x': 'y'}
        testname = 'MapDataNode.__getitem__(None)'
        N = dataflows.MapDataNode(0, indata, dmap, dimensions=('x',), units='m')
        actual = N[None]
        expected = dataflows.DataArray(numpy.arange(0), units='m', dimensions=('x',))
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
