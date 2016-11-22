"""
DatasetDesc Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import remove
from os.path import exists
from pyconform import datasets
from collections import OrderedDict
from netCDF4 import Dataset as NCDataset
from cf_units import Unit
from testutils import print_test_message

import numpy as np
import unittest


#===============================================================================
# DimensionDescTests
#===============================================================================
class DimensionDescTests(unittest.TestCase):
    """
    Unit tests for DimensionDesc objects
    """

    def test_type(self):
        ddesc = datasets.DimensionDesc('x')
        actual = type(ddesc)
        expected = datasets.DimensionDesc
        print_test_message('type(DimensionDesc)', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'DimensionDesc has wrong type')

    def test_name(self):
        indata = 'x'
        ddesc = datasets.DimensionDesc(indata)
        actual = ddesc.name
        expected = indata
        print_test_message('DimensionDesc.name', indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'DimensionDesc.name does not match')

    def test_size_default(self):
        ddesc = datasets.DimensionDesc('x')
        actual = ddesc.size
        expected = None
        print_test_message('DimensionDesc.size == None', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Default DimensionDesc.size is not None')

    def test_size(self):
        indata = 1
        ddesc = datasets.DimensionDesc('x', size=indata)
        actual = ddesc.size
        expected = indata
        print_test_message('DimensionDesc.size', input=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'DimensionDesc.size is not set properly')

    def test_limited_default(self):
        ddesc = datasets.DimensionDesc('x', size=1)
        actual = ddesc.unlimited
        expected = False
        print_test_message('DimensionDesc.unlimited', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Default DimensionDesc.unlimited is wrong')

    def test_limited(self):
        ddesc = datasets.DimensionDesc('x', size=1, unlimited=True)
        actual = ddesc.unlimited
        expected = True
        print_test_message('DimensionDesc.unlimited == True', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'DimensionDesc.unlimited is not True')

    def test_is_set_false(self):
        ddesc = datasets.DimensionDesc('x')
        actual = ddesc.is_set()
        expected = False
        print_test_message('DimensionDesc.is_set == False', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'DimensionDesc is set when it should not be')

    def test_is_set_true(self):
        ddesc = datasets.DimensionDesc('x', 1)
        actual = ddesc.is_set()
        expected = True
        print_test_message('DimensionDesc.is_set == True', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'DimensionDesc is not set when it should be')

    def test_equals_same(self):
        ddesc1 = datasets.DimensionDesc('x', size=1, unlimited=True)
        ddesc2 = datasets.DimensionDesc('x', size=1, unlimited=True)
        actual = ddesc1
        expected = ddesc2
        print_test_message('DimensionDesc == DimensionDesc', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Identical DimensionDesc objects not equal')

    def test_equals_diff_name(self):
        ddesc1 = datasets.DimensionDesc('a', size=1, unlimited=True)
        ddesc2 = datasets.DimensionDesc('b', size=1, unlimited=True)
        actual = ddesc1
        expected = ddesc2
        print_test_message('DimensionDesc(a) != DimensionDesc(b)', actual=actual, expected=expected)
        self.assertNotEqual(actual, expected, 'Differently named DimensionDesc objects equal')

    def test_equals_diff_size(self):
        ddesc1 = datasets.DimensionDesc('x', size=1, unlimited=True)
        ddesc2 = datasets.DimensionDesc('x', size=2, unlimited=True)
        actual = ddesc1
        expected = ddesc2
        print_test_message('DimensionDesc(1) != DimensionDesc(2)', actual=actual, expected=expected)
        self.assertNotEqual(actual, expected, 'Differently sized DimensionDesc objects equal')

    def test_equals_diff_ulim(self):
        ddesc1 = datasets.DimensionDesc('x', size=1, unlimited=False)
        ddesc2 = datasets.DimensionDesc('x', size=1, unlimited=True)
        actual = ddesc1
        expected = ddesc2
        print_test_message('DimensionDesc(1) != DimensionDesc(2)', actual=actual, expected=expected)
        self.assertNotEqual(actual, expected, 'Differently limited DimensionDesc objects equal')

    def test_equals_same_1set(self):
        ddesc1 = datasets.DimensionDesc('x', 1, True)
        ddesc2 = datasets.DimensionDesc('x')
        actual = ddesc1
        expected = ddesc2
        print_test_message('DimensionDesc(1) == DimensionDesc(2)', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Set DimensionsDesc does not equal unset DimensionDesc')

    def test_equals_same_unset(self):
        ddesc1 = datasets.DimensionDesc('x')
        ddesc2 = datasets.DimensionDesc('x')
        actual = ddesc1
        expected = ddesc2
        print_test_message('DimensionDesc(1) == DimensionDesc(2)', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Unset DimensionsDesc not equal to unset DimensionDesc')

    def test_equals_diff_1set(self):
        ddesc1 = datasets.DimensionDesc('y', 1, True)
        ddesc2 = datasets.DimensionDesc('x')
        actual = ddesc1
        expected = ddesc2
        print_test_message('DimensionDesc(1) == DimensionDesc(2)', actual=actual, expected=expected)
        self.assertNotEqual(actual, expected, 'Set DimensionsDesc equal to unset DimensionDesc')


#===============================================================================
# VariableDescTests
#===============================================================================
class VariableDescTests(unittest.TestCase):
    """
    Unit tests for VariableDesc objects
    """

    def test_type(self):
        vdesc = datasets.VariableDesc('x')
        actual = type(vdesc)
        expected = datasets.VariableDesc
        print_test_message('type(VariableDesc)', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'VariableDesc has wrong type')

    def test_name(self):
        indata = 'x'
        vdesc = datasets.VariableDesc(indata)
        actual = vdesc.name
        expected = indata
        print_test_message('VariableDesc.name', indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'VariableDesc.name does not match')

    def test_datatype_default(self):
        vdesc = datasets.VariableDesc('x')
        actual = vdesc.datatype
        expected = 'float32'
        print_test_message('VariableDesc.datatype == float32', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Default VariableDesc.datatype is not float32')

    def test_dimensions_default(self):
        vdesc = datasets.VariableDesc('x')
        actual = vdesc.dimensions
        expected = OrderedDict()
        print_test_message('VariableDesc.dimensions == ()', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Default VariableDesc.dimensions is not ()')

    def test_attributes_default(self):
        vdesc = datasets.VariableDesc('x')
        actual = vdesc.attributes
        expected = {}
        print_test_message('VariableDesc.attributes == ()', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Default VariableDesc.attributes is not OrderedDict()')

    def test_definition_default(self):
        vdesc = datasets.VariableDesc('x')
        actual = vdesc.definition
        expected = None
        print_test_message('VariableDesc.definition == ()', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Default VariableDesc.definition is not None')

    def test_datatype(self):
        vdesc = datasets.VariableDesc('x', datatype='float64')
        actual = vdesc.datatype
        expected = 'float64'
        print_test_message('VariableDesc.datatype == float64', actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'Default VariableDesc.datatype is not float64')

    def test_dimensions(self):
        indata = (datasets.DimensionDesc('y'), datasets.DimensionDesc('z'))
        vdesc = datasets.VariableDesc('x', dimensions=indata)
        actual = vdesc.dimensions
        expected = OrderedDict((d.name, d) for d in indata)
        print_test_message('VariableDesc.dimensions == ()', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.dimensions is not {}'.format(indata))

    def test_attributes(self):
        indata = OrderedDict([('a1', 'attrib1'), ('a2', 'attrib2')])
        vdesc = datasets.VariableDesc('x', attributes=indata)
        actual = vdesc.attributes
        expected = indata
        print_test_message('VariableDesc.attributes', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.attributes is not {}'.format(indata))

    def test_definition(self):
        indata = 'y + z'
        vdesc = datasets.VariableDesc('x', definition=indata)
        actual = vdesc.definition
        expected = indata
        print_test_message('VariableDesc.definition', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.definition is not {!r}'.format(indata))

    def test_data(self):
        indata = (1, 2, 3, 4, 5, 6)
        vdesc = datasets.VariableDesc('x', definition=indata)
        actual = vdesc.definition
        expected = indata
        print_test_message('VariableDesc.definition', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.definition is not {!r}'.format(indata))

    def test_equals_same(self):
        kwargs = {'datatype': 'd',
                  'dimensions': tuple(datasets.DimensionDesc(d) for d in ('a', 'b')),
                  'attributes': {'a1': 'at1', 'a2': 'at2'},
                  'definition': 'y + z'}
        vdesc1 = datasets.VariableDesc('x', **kwargs)
        vdesc2 = datasets.VariableDesc('x', **kwargs)
        actual = vdesc1
        expected = vdesc2
        print_test_message('VariableDesc == VariableDesc',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Identical VariableDesc objects not equal')

    def test_equals_diff_name(self):
        kwargs = {'datatype': 'd',
                  'dimensions': tuple(datasets.DimensionDesc(d) for d in ('a', 'b')),
                  'attributes': {'a1': 'at1', 'a2': 'at2'},
                  'definition': 'y + z'}
        vdesc1 = datasets.VariableDesc('a', **kwargs)
        vdesc2 = datasets.VariableDesc('b', **kwargs)
        actual = vdesc1
        expected = vdesc2
        print_test_message('VariableDesc(a) != VariableDesc(b)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently named VariableDesc objects equal')

    def test_equals_diff_dtype(self):
        vdesc1 = datasets.VariableDesc('x', datatype='d')
        vdesc2 = datasets.VariableDesc('x', datatype='f')
        actual = vdesc1
        expected = vdesc2
        print_test_message('VariableDesc(d) != VariableDesc(f)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently typed VariableDesc objects equal')

    def test_equals_diff_dims(self):
        vdims1 = tuple(datasets.DimensionDesc(d) for d in ('a', 'b'))
        vdims2 = tuple(datasets.DimensionDesc(d) for d in ('a', 'b', 'c'))
        vdesc1 = datasets.VariableDesc('x', dimensions=vdims1)
        vdesc2 = datasets.VariableDesc('x', dimensions=vdims2)
        actual = vdesc1
        expected = vdesc2
        print_test_message('VariableDesc(dims1) != VariableDesc(dims2)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently dimensioned VariableDesc objects equal')

    def test_units_default(self):
        vdesc = datasets.VariableDesc('x')
        actual = vdesc.units()
        expected = Unit('1')
        print_test_message('VariableDesc.units() == 1',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.units() not None')

    def test_units(self):
        indata = 'm'
        vdesc = datasets.VariableDesc('x', attributes={'units': indata})
        actual = vdesc.units()
        expected = indata
        print_test_message('VariableDesc.units()', indata=indata,
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.units() not {}'.format(indata))

    def test_calendar_default(self):
        vdesc = datasets.VariableDesc('x')
        actual = vdesc.calendar()
        expected = None
        print_test_message('VariableDesc.calendar()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.calendar() not None')

    def test_calendar(self):
        indata = 'noleap'
        vdesc = datasets.VariableDesc('x', attributes={'units': 'days',
                                                      'calendar': indata})
        actual = vdesc.calendar()
        expected = indata
        print_test_message('VariableDesc.calendar()', indata=indata,
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'VariableDesc.calendar() not {}'.format(indata))

    def test_cfunits_default(self):
        vdesc = datasets.VariableDesc('time')
        actual = vdesc.cfunits()
        expected = Unit(1)
        print_test_message('VariableDesc.cfunits() == None',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.cfunits() not None')

    def test_cfunits(self):
        units = 'days'
        calendar = 'noleap'
        vdesc = datasets.VariableDesc('x', attributes={'units': units,
                                                      'calendar': calendar})
        actual = vdesc.cfunits()
        expected = Unit(units, calendar=calendar)
        print_test_message('VariableDesc.cfunits()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.cfunits() not {}'.format(expected))


#=========================================================================
# DatasetDescTests - Tests for the datasets module
#=========================================================================
class DatasetDescTests(unittest.TestCase):
    """
    Unit Tests for the pyconform.datasets module
    """

    def setUp(self):
        self.filenames = OrderedDict([('u1', 'u1.nc'), ('u2', 'u2.nc')])
        self._clear_()

        self.fattribs = OrderedDict([('a1', 'attribute 1'),
                                     ('a2', 'attribute 2')])
        self.dims = OrderedDict([('time', 4), ('lat', 3), ('lon', 2)])
        self.vdims = OrderedDict([('u1', ('time', 'lat', 'lon')),
                                  ('u2', ('time', 'lat', 'lon'))])
        self.vattrs = OrderedDict([('lat', {'units': 'degrees_north',
                                            'standard_name': 'latitude'}),
                                   ('lon', {'units': 'degrees_east',
                                            'standard_name': 'longitude'}),
                                   ('time', {'units': 'days since 1979-01-01 0:0:0',
                                             'calendar': 'noleap',
                                             'standard_name': 'time'}),
                                   ('u1', {'units': 'm',
                                           'standard_name': 'u variable 1'}),
                                   ('u2', {'units': 'm',
                                           'standard_name': 'u variable 2'})])
        self.dtypes = {'lat': 'f', 'lon': 'f', 'time': 'f', 'u1': 'd', 'u2': 'd'}
        ydat = np.linspace(-90, 90, num=self.dims['lat'],
                           endpoint=True, dtype=self.dtypes['lat'])
        xdat = np.linspace(-180, 180, num=self.dims['lon'],
                           endpoint=False, dtype=self.dtypes['lon'])
        tdat = np.linspace(0, self.dims['time'], num=self.dims['time'],
                           endpoint=False, dtype=self.dtypes['time'])
        ulen = reduce(lambda x, y: x * y, self.dims.itervalues(), 1)
        ushape = tuple(d for d in self.dims.itervalues())
        u1dat = np.linspace(0, ulen, num=ulen, endpoint=False,
                            dtype=self.dtypes['u1']).reshape(ushape)
        u2dat = np.linspace(0, ulen, num=ulen, endpoint=False,
                            dtype=self.dtypes['u2']).reshape(ushape)
        self.vdat = {'lat': ydat, 'lon': xdat, 'time': tdat,
                     'u1': u1dat, 'u2': u2dat}

        for vname, fname in self.filenames.iteritems():
            ncf = NCDataset(fname, 'w')
            ncf.setncatts(self.fattribs)
            ncvars = {}
            for dname, dvalue in self.dims.iteritems():
                dsize = dvalue if dname != 'time' else None
                ncf.createDimension(dname, dsize)
                ncvars[dname] = ncf.createVariable(dname, 'd', (dname,))
            ncvars[vname] = ncf.createVariable(vname, 'd', self.vdims[vname])
            for vnam, vobj in ncvars.iteritems():
                for aname, avalue in self.vattrs[vnam].iteritems():
                    setattr(vobj, aname, avalue)
                vobj[:] = self.vdat[vnam]
            ncf.close()

        vdicts = OrderedDict()

        vdicts['W'] = OrderedDict()
        vdicts['W']['datatype'] = 'float64'
        vdicts['W']['dimensions'] = ('w',)
        vdicts['W']['definition'] = np.array([1., 2., 3., 4., 5., 6., 7., 8.], dtype='float64')
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'something'
        vattribs['units'] = '1'
        vdicts['W']['attributes'] = vattribs

        vdicts['X'] = OrderedDict()
        vdicts['X']['datatype'] = 'float64'
        vdicts['X']['dimensions'] = ('x',)
        vdicts['X']['definition'] = 'lon'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'longitude'
        vattribs['units'] = 'degrees_east'
        vdicts['X']['attributes'] = vattribs

        vdicts['Y'] = OrderedDict()
        vdicts['Y']['datatype'] = 'float64'
        vdicts['Y']['dimensions'] = ('y',)
        vdicts['Y']['definition'] = 'lat'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'latitude'
        vattribs['units'] = 'degrees_north'
        vdicts['Y']['attributes'] = vattribs

        vdicts['T'] = OrderedDict()
        vdicts['T']['datatype'] = 'float64'
        vdicts['T']['dimensions'] = ('t',)
        vdicts['T']['definition'] = 'time'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'time'
        vattribs['units'] = 'days since 01-01-0001 00:00:00'
        vattribs['calendar'] = 'noleap'
        vdicts['T']['attributes'] = vattribs

        vdicts['V1'] = OrderedDict()
        vdicts['V1']['datatype'] = 'float64'
        vdicts['V1']['dimensions'] = ('t', 'y', 'x')
        vdicts['V1']['definition'] = 'u1 + u2'
        fdict = OrderedDict()
        fdict['filename'] = 'var1.nc'
        fdict['format'] = 'NETCDF4'
        fdict['attributes'] = {'A': 'some attribute', 'B': 'another attribute'}
        vdicts['V1']['file'] = fdict
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 1'
        vattribs['units'] = 'm'
        vdicts['V1']['attributes'] = vattribs

        vdicts['V2'] = OrderedDict()
        vdicts['V2']['datatype'] = 'float64'
        vdicts['V2']['dimensions'] = ('t', 'y', 'x')
        vdicts['V2']['definition'] = 'u2 - u1'
        fdict = OrderedDict()
        fdict['filename'] = 'var2.nc'
        fdict['format'] = 'NETCDF4_CLASSIC'
        fdict['attributes'] = {'Z': 'this attribute', 'Y': 'that attribute'}
        fdict['metavars'] = ['V1']
        vdicts['V2']['file'] = fdict
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 2'
        vattribs['units'] = 'm'
        vdicts['V2']['attributes'] = vattribs

        self.dsdict = vdicts

    def tearDown(self):
        self._clear_()

    def _clear_(self):
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)

    def test_dataset_type(self):
        ds = datasets.DatasetDesc()
        actual = type(ds)
        expected = datasets.DatasetDesc
        print_test_message('type(DatasetDesc)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'DatasetDesc has wrong type')

    def test_input_dataset_type(self):
        inds = datasets.InputDatasetDesc('myinds', self.filenames.values())
        actual = type(inds)
        expected = datasets.InputDatasetDesc
        print_test_message('type(InputDatasetDesc)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'InputDatasetDesc has wrong type')

    def test_output_dataset_type(self):
        outds = datasets.OutputDatasetDesc('myoutds', self.dsdict)
        actual = type(outds)
        expected = datasets.OutputDatasetDesc
        print_test_message('type(OutputDatasetDesc)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'OutputDatasetDesc has wrong type')


#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
