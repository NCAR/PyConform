"""
Dataset Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep, remove
from os.path import exists
from pyconform import datasets
from collections import OrderedDict
from netCDF4 import Dataset as NCDataset
from cf_units import Unit

import numpy as np
import unittest


#=========================================================================
# print_test_message - Helper function
#=========================================================================
def print_test_message(testname, indata=None, actual=None, expected=None):
    """
    Pretty-print a test message

    Parameters:
        testname: String name of the test
        indata: Input data for testing (if any)
        actual: Actual return value/result
        expected: Expected return value/result
    """
    indent = linesep + ' ' * 14
    print '{}:'.format(testname)
    if indata:
        s_indata = str(indata).replace(linesep, indent)
        print '    input:    {}'.format(s_indata)
    if actual:
        s_actual = str(actual).replace(linesep, indent)
        print '    actual:   {}'.format(s_actual)
    if expected:
        s_expected = str(expected).replace(linesep, indent)
        print '    expected: {}'.format(s_expected)
    print


#===============================================================================
# InfoObjTests
#===============================================================================
class InfoObjTests(unittest.TestCase):
    """
    Unit tests for Info objects
    """
    
    def test_dinfo_type(self):
        dinfo = datasets.DimensionInfo('x')
        actual = type(dinfo)
        expected = datasets.DimensionInfo
        print_test_message('type(DimensionInfo)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'DimensionInfo has wrong type')

    def test_dinfo_name(self):
        indata = 'x'
        dinfo = datasets.DimensionInfo(indata)
        actual = dinfo.name
        expected = indata
        print_test_message('DimensionInfo.name', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'DimensionInfo.name does not match')

    def test_dinfo_size_default(self):
        dinfo = datasets.DimensionInfo('x')
        actual = dinfo.size
        expected = None
        print_test_message('DimensionInfo.size == None',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default DimensionInfo.size is not None')

    def test_dinfo_size(self):
        indata = 1
        dinfo = datasets.DimensionInfo('x', size=indata)
        actual = dinfo.size
        expected = indata
        print_test_message('DimensionInfo.size', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'DimensionInfo.size is not set properly')

    def test_dinfo_limited_default(self):
        dinfo = datasets.DimensionInfo('x', size=1)
        actual = dinfo.unlimited
        expected = False
        print_test_message('DimensionInfo.unlimited',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default DimensionInfo.unlimited is False')

    def test_dinfo_limited(self):
        dinfo = datasets.DimensionInfo('x', size=1, unlimited=True)
        actual = dinfo.unlimited
        expected = True
        print_test_message('DimensionInfo.unlimited == True',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'DimensionInfo.unlimited is not True')

    def test_dinfo_equals_same(self):
        dinfo1 = datasets.DimensionInfo('x', size=1, unlimited=True)
        dinfo2 = datasets.DimensionInfo('x', size=1, unlimited=True)
        actual = dinfo1
        expected = dinfo2
        print_test_message('DimensionInfo == DimensionInfo',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Identical DimensionInfo objects not equal')

    def test_dinfo_equals_diff_name(self):
        dinfo1 = datasets.DimensionInfo('a', size=1, unlimited=True)
        dinfo2 = datasets.DimensionInfo('b', size=1, unlimited=True)
        actual = dinfo1
        expected = dinfo2
        print_test_message('DimensionInfo(a) != DimensionInfo(b)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently named DimensionInfo objects equal')

    def test_dinfo_equals_diff_size(self):
        dinfo1 = datasets.DimensionInfo('x', size=1, unlimited=True)
        dinfo2 = datasets.DimensionInfo('x', size=2, unlimited=True)
        actual = dinfo1
        expected = dinfo2
        print_test_message('DimensionInfo(1) != DimensionInfo(2)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently sized DimensionInfo objects equal')

    def test_dinfo_equals_diff_ulim(self):
        dinfo1 = datasets.DimensionInfo('x', size=1, unlimited=False)
        dinfo2 = datasets.DimensionInfo('x', size=1, unlimited=True)
        actual = dinfo1
        expected = dinfo2
        print_test_message('DimensionInfo(1) != DimensionInfo(2)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently limited DimensionInfo objects equal')

    def test_vinfo_type(self):
        vinfo = datasets.VariableInfo('x')
        actual = type(vinfo)
        expected = datasets.VariableInfo
        print_test_message('type(VariableInfo)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'VariableInfo has wrong type')

    def test_vinfo_name(self):
        indata = 'x'
        vinfo = datasets.VariableInfo(indata)
        actual = vinfo.name
        expected = indata
        print_test_message('VariableInfo.name', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'VariableInfo.name does not match')

    def test_vinfo_dtype_default(self):
        vinfo = datasets.VariableInfo('x')
        actual = vinfo.datatype
        expected = 'float32'
        print_test_message('VariableInfo.datatype == float32',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.datatype is not float32')

    def test_vinfo_dimensions_default(self):
        vinfo = datasets.VariableInfo('x')
        actual = vinfo.dimensions
        expected = tuple()
        print_test_message('VariableInfo.dimensions == ()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.dimensions is not ()')

    def test_vinfo_attributes_default(self):
        vinfo = datasets.VariableInfo('x')
        actual = vinfo.attributes
        expected = OrderedDict()
        print_test_message('VariableInfo.attributes == ()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.attributes is not OrderedDict()')

    def test_vinfo_definition_default(self):
        vinfo = datasets.VariableInfo('x')
        actual = vinfo.definition
        expected = None
        print_test_message('VariableInfo.definition == ()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.definition is not None')

    def test_vinfo_filename_default(self):
        vinfo = datasets.VariableInfo('x')
        actual = vinfo.filename
        expected = None
        print_test_message('VariableInfo.filename == ()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.filename is not None')

    def test_vinfo_dtype(self):
        vinfo = datasets.VariableInfo('x', datatype='float64')
        actual = vinfo.datatype
        expected = 'float64'
        print_test_message('VariableInfo.datatype == float64',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.datatype is not float64')

    def test_vinfo_dimensions(self):
        indata = ('y', 'z')
        vinfo = datasets.VariableInfo('x', dimensions=indata)
        actual = vinfo.dimensions
        expected = indata
        print_test_message('VariableInfo.dimensions == ()', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.dimensions is not {}'.format(indata))

    def test_vinfo_attributes(self):
        indata = OrderedDict([('a1', 'attrib1'), ('a2', 'attrib2')])
        vinfo = datasets.VariableInfo('x', attributes=indata)
        actual = vinfo.attributes
        expected = indata
        print_test_message('VariableInfo.attributes', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.attributes is not {}'.format(indata))

    def test_vinfo_definition(self):
        indata = 'y + z'
        vinfo = datasets.VariableInfo('x', definition=indata)
        actual = vinfo.definition
        expected = indata
        print_test_message('VariableInfo.definition', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.definition is not {!r}'.format(indata))

    def test_vinfo_filename(self):
        indata = 'nc1.nc'
        vinfo = datasets.VariableInfo('x', filename=indata)
        actual = vinfo.filename
        expected = indata
        print_test_message('VariableInfo.filename', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableInfo.filename is not {!r}'.format(indata))
        
    def test_vinfo_equals_same(self):
        kwargs = {'datatype': 'd', 'dimensions': ('a', 'b'),
                  'attributes': {'a1': 'at1', 'a2': 'at2'},
                  'definition': 'y + z', 'filename': 'out.nc'}
        vinfo1 = datasets.VariableInfo('x', **kwargs)
        vinfo2 = datasets.VariableInfo('x', **kwargs)
        actual = vinfo1
        expected = vinfo2
        print_test_message('VariableInfo == VariableInfo',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Identical VariableInfo objects not equal')

    def test_vinfo_equals_diff_name(self):
        kwargs = {'datatype': 'd', 'dimensions': ('a', 'b'),
                  'attributes': {'a1': 'at1', 'a2': 'at2'},
                  'definition': 'y + z', 'filename': 'out.nc'}
        vinfo1 = datasets.VariableInfo('a', **kwargs)
        vinfo2 = datasets.VariableInfo('b', **kwargs)
        actual = vinfo1
        expected = vinfo2
        print_test_message('VariableInfo(a) != VariableInfo(b)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently named VariableInfo objects equal')

    def test_vinfo_equals_diff_dtype(self):
        vinfo1 = datasets.VariableInfo('x', datatype='d')
        vinfo2 = datasets.VariableInfo('x', datatype='f')
        actual = vinfo1
        expected = vinfo2
        print_test_message('VariableInfo(d) != VariableInfo(f)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently typed VariableInfo objects equal')

    def test_vinfo_equals_diff_dims(self):
        vinfo1 = datasets.VariableInfo('x', dimensions=('a', 'b'))
        vinfo2 = datasets.VariableInfo('x', dimensions=('a', 'b', 'c'))
        actual = vinfo1
        expected = vinfo2
        print_test_message('VariableInfo(dims1) != VariableInfo(dims2)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently dimensioned VariableInfo objects equal')

    def test_vinfo_units_default(self):
        vinfo = datasets.VariableInfo('x')
        actual = vinfo.units()
        expected = None
        print_test_message('VariableInfo.units() == None',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableInfo.units() not None')

    def test_vinfo_units(self):
        indata = 'm'
        vinfo = datasets.VariableInfo('x', attributes={'units': indata})
        actual = vinfo.units()
        expected = indata
        print_test_message('VariableInfo.units()', indata=indata,
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableInfo.units() not {}'.format(indata))

    def test_vinfo_calendar_default(self):
        vinfo = datasets.VariableInfo('x')
        actual = vinfo.calendar()
        expected = None
        print_test_message('VariableInfo.calendar()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableInfo.calendar() not None')

    def test_vinfo_calendar(self):
        indata = 'noleap'
        vinfo = datasets.VariableInfo('x', attributes={'units': 'days',
                                                      'calendar': indata})
        actual = vinfo.calendar()
        expected = indata
        print_test_message('VariableInfo.calendar()', indata=indata,
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'VariableInfo.calendar() not {}'.format(indata))

    def test_vinfo_cfunits_default(self):
        vinfo = datasets.VariableInfo('time')
        actual = vinfo.cfunits()
        expected = Unit(None)
        print_test_message('VariableInfo.cfunits() == None',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableInfo.cfunits() not None')

    def test_vinfo_cfunits(self):
        units = 'days'
        calendar = 'noleap'
        vinfo = datasets.VariableInfo('x', attributes={'units': units,
                                                      'calendar': calendar})
        actual = vinfo.cfunits()
        expected = Unit(units, calendar=calendar)
        print_test_message('VariableInfo.cfunits()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableInfo.cfunits() not {}'.format(expected))
        
    def test_vinfo_standard_name(self):
        indata = 'X var'
        vinfo = datasets.VariableInfo('x', attributes={'standard_name': indata})
        actual = vinfo.standard_name()
        expected = indata
        print_test_message('VariableInfo.standard_name()', indata=indata,
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableInfo.standard_name() not {}'.format(indata))

    def test_vinfo_standard_name_default(self):
        vinfo = datasets.VariableInfo('x')
        actual = vinfo.standard_name()
        expected = None
        print_test_message('VariableInfo.standard_name() == None',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                            'Default VariableInfo.standard_name() not None')
        

#=========================================================================
# DatasetTests - Tests for the datasets module
#=========================================================================
class DatasetTests(unittest.TestCase):
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
        ulen = reduce(lambda x,y: x*y, self.dims.itervalues(), 1)
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
                dsize = dvalue if dname!='time' else None
                ncf.createDimension(dname, dsize)
                ncvars[dname] = ncf.createVariable(dname, 'd', (dname,))
            ncvars[vname] = ncf.createVariable(vname, 'd', self.vdims[vname])
            for vnam, vobj in ncvars.iteritems():
                for aname, avalue in self.vattrs[vnam].iteritems():
                    setattr(vobj, aname, avalue)
                vobj[:] = self.vdat[vnam]
            ncf.close()

        self.dsdict = OrderedDict()
        self.dsdict['attributes'] = self.fattribs
        self.dsdict['variables'] = OrderedDict()
        vdicts = self.dsdict['variables']
        
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
        vdicts['V1']['filename'] = 'var1.nc'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 1'
        vattribs['units'] = 'm'
        vdicts['V1']['attributes'] = vattribs

        vdicts['V2'] = OrderedDict()
        vdicts['V2']['datatype'] = 'float64'
        vdicts['V2']['dimensions'] = ('t', 'y', 'x')
        vdicts['V2']['definition'] = 'u2 - u1'
        vdicts['V2']['filename'] = 'var2.nc'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 2'
        vattribs['units'] = 'm'
        vdicts['V2']['attributes'] = vattribs

    def tearDown(self):
        self._clear_()
        
    def _clear_(self):
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)

    def test_datasets_type(self):
        ds = datasets.Dataset()
        actual = type(ds)
        expected = datasets.Dataset
        print_test_message('type(Dataset)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Dataset has wrong type')

    def test_input_datasets_type(self):
        inds = datasets.InputDataset('myinds', self.filenames.values())
        actual = type(inds)
        expected = datasets.InputDataset
        print_test_message('type(InputDataset)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'InputDataset has wrong type')

    def test_output_datasets_type(self):
        outds = datasets.OutputDataset('myoutds', self.dsdict)
        actual = type(outds)
        expected = datasets.OutputDataset
        print_test_message('type(OutputDataset)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'OutputDataset has wrong type')

    def test_datasets_get_dict_from_output(self):
        outds = datasets.OutputDataset('myoutds', self.dsdict)
        actual = outds.get_dict()
        expected = self.dsdict
        print_test_message('OutputDataset.get_dict()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'OutputDataset.get_dict() returns wrong data')
        
    def test_datasets_get_dict_from_input(self):
        inds = datasets.InputDataset('myinds', self.filenames.values())
        actual = inds.get_dict()
        print_test_message('InputDataset.get_dict()', actual=actual)
        

#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
