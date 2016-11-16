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
import numpy.testing as npt
import unittest


#===============================================================================
# DimensionDescTests
#===============================================================================
class DimensionDescTests(unittest.TestCase):
    """
    Unit tests for DimensionDesc objects
    """

    def test_dinfo_type(self):
        dinfo = datasets.DimensionDesc('x')
        actual = type(dinfo)
        expected = datasets.DimensionDesc
        print_test_message('type(DimensionDesc)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'DimensionDesc has wrong type')

    def test_dinfo_name(self):
        indata = 'x'
        dinfo = datasets.DimensionDesc(indata)
        actual = dinfo.name
        expected = indata
        print_test_message('DimensionDesc.name', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'DimensionDesc.name does not match')

    def test_dinfo_size_default(self):
        dinfo = datasets.DimensionDesc('x')
        actual = dinfo.size
        expected = None
        print_test_message('DimensionDesc.size == None',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default DimensionDesc.size is not None')

    def test_dinfo_size(self):
        indata = 1
        dinfo = datasets.DimensionDesc('x', size=indata)
        actual = dinfo.size
        expected = indata
        print_test_message('DimensionDesc.size', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'DimensionDesc.size is not set properly')

    def test_dinfo_limited_default(self):
        dinfo = datasets.DimensionDesc('x', size=1)
        actual = dinfo.unlimited
        expected = False
        print_test_message('DimensionDesc.unlimited',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default DimensionDesc.unlimited is False')

    def test_dinfo_limited(self):
        dinfo = datasets.DimensionDesc('x', size=1, unlimited=True)
        actual = dinfo.unlimited
        expected = True
        print_test_message('DimensionDesc.unlimited == True',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'DimensionDesc.unlimited is not True')

    def test_dinfo_equals_same(self):
        dinfo1 = datasets.DimensionDesc('x', size=1, unlimited=True)
        dinfo2 = datasets.DimensionDesc('x', size=1, unlimited=True)
        actual = dinfo1
        expected = dinfo2
        print_test_message('DimensionDesc == DimensionDesc',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Identical DimensionDesc objects not equal')

    def test_dinfo_equals_diff_name(self):
        dinfo1 = datasets.DimensionDesc('a', size=1, unlimited=True)
        dinfo2 = datasets.DimensionDesc('b', size=1, unlimited=True)
        actual = dinfo1
        expected = dinfo2
        print_test_message('DimensionDesc(a) != DimensionDesc(b)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently named DimensionDesc objects equal')

    def test_dinfo_equals_diff_size(self):
        dinfo1 = datasets.DimensionDesc('x', size=1, unlimited=True)
        dinfo2 = datasets.DimensionDesc('x', size=2, unlimited=True)
        actual = dinfo1
        expected = dinfo2
        print_test_message('DimensionDesc(1) != DimensionDesc(2)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently sized DimensionDesc objects equal')

    def test_dinfo_equals_diff_ulim(self):
        dinfo1 = datasets.DimensionDesc('x', size=1, unlimited=False)
        dinfo2 = datasets.DimensionDesc('x', size=1, unlimited=True)
        actual = dinfo1
        expected = dinfo2
        print_test_message('DimensionDesc(1) != DimensionDesc(2)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently limited DimensionDesc objects equal')


#===============================================================================
# VariableDescTests
#===============================================================================
class VariableDescTests(unittest.TestCase):
    """
    Unit tests for VariableDesc objects
    """

    def test_vinfo_type(self):
        vinfo = datasets.VariableDesc('x')
        actual = type(vinfo)
        expected = datasets.VariableDesc
        print_test_message('type(VariableDesc)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'VariableDesc has wrong type')

    def test_vinfo_name(self):
        indata = 'x'
        vinfo = datasets.VariableDesc(indata)
        actual = vinfo.name
        expected = indata
        print_test_message('VariableDesc.name', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'VariableDesc.name does not match')

    def test_vinfo_dtype_default(self):
        vinfo = datasets.VariableDesc('x')
        actual = vinfo.datatype
        expected = 'float32'
        print_test_message('VariableDesc.datatype == float32',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.datatype is not float32')

    def test_vinfo_dimensions_default(self):
        vinfo = datasets.VariableDesc('x')
        actual = vinfo.dimensions
        expected = tuple()
        print_test_message('VariableDesc.dimensions == ()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.dimensions is not ()')

    def test_vinfo_attributes_default(self):
        vinfo = datasets.VariableDesc('x')
        actual = vinfo.attributes
        expected = OrderedDict()
        print_test_message('VariableDesc.attributes == ()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.attributes is not OrderedDict()')

    def test_vinfo_definition_default(self):
        vinfo = datasets.VariableDesc('x')
        actual = vinfo.definition
        expected = None
        print_test_message('VariableDesc.definition == ()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.definition is not None')

    def test_vinfo_filename_default(self):
        vinfo = datasets.VariableDesc('x')
        actual = vinfo.filenames
        expected = None
        print_test_message('VariableDesc.filename == ()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.filename is not None')

    def test_vinfo_dtype(self):
        vinfo = datasets.VariableDesc('x', datatype='float64')
        actual = vinfo.datatype
        expected = 'float64'
        print_test_message('VariableDesc.datatype == float64',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.datatype is not float64')

    def test_vinfo_dimensions(self):
        indata = ('y', 'z')
        vinfo = datasets.VariableDesc('x', dimensions=indata)
        actual = vinfo.dimensions
        expected = indata
        print_test_message('VariableDesc.dimensions == ()', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.dimensions is not {}'.format(indata))

    def test_vinfo_attributes(self):
        indata = OrderedDict([('a1', 'attrib1'), ('a2', 'attrib2')])
        vinfo = datasets.VariableDesc('x', attributes=indata)
        actual = vinfo.attributes
        expected = indata
        print_test_message('VariableDesc.attributes', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.attributes is not {}'.format(indata))

    def test_vinfo_definition(self):
        indata = 'y + z'
        vinfo = datasets.VariableDesc('x', definition=indata)
        actual = vinfo.definition
        expected = indata
        print_test_message('VariableDesc.definition', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.definition is not {!r}'.format(indata))

    def test_vinfo_data(self):
        indata = (1, 2, 3, 4, 5, 6)
        vinfo = datasets.VariableDesc('x', definition=indata)
        actual = vinfo.definition
        expected = indata
        print_test_message('VariableDesc.definition', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.definition is not {!r}'.format(indata))

    def test_vinfo_filename(self):
        indata = ('nc1.nc',)
        vinfo = datasets.VariableDesc('x', filenames=indata)
        actual = vinfo.filenames
        expected = indata
        print_test_message('VariableDesc.filename', indata=indata,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Default VariableDesc.filename is not {!r}'.format(indata))

    def test_vinfo_equals_same(self):
        kwargs = {'datatype': 'd', 'dimensions': ('a', 'b'),
                  'attributes': {'a1': 'at1', 'a2': 'at2'},
                  'definition': 'y + z', 'filenames': ('out.nc',)}
        vinfo1 = datasets.VariableDesc('x', **kwargs)
        vinfo2 = datasets.VariableDesc('x', **kwargs)
        actual = vinfo1
        expected = vinfo2
        print_test_message('VariableDesc == VariableDesc',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Identical VariableDesc objects not equal')

    def test_vinfo_equals_diff_name(self):
        kwargs = {'datatype': 'd', 'dimensions': ('a', 'b'),
                  'attributes': {'a1': 'at1', 'a2': 'at2'},
                  'definition': 'y + z', 'filenames': ('out.nc',)}
        vinfo1 = datasets.VariableDesc('a', **kwargs)
        vinfo2 = datasets.VariableDesc('b', **kwargs)
        actual = vinfo1
        expected = vinfo2
        print_test_message('VariableDesc(a) != VariableDesc(b)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently named VariableDesc objects equal')

    def test_vinfo_equals_diff_dtype(self):
        vinfo1 = datasets.VariableDesc('x', datatype='d')
        vinfo2 = datasets.VariableDesc('x', datatype='f')
        actual = vinfo1
        expected = vinfo2
        print_test_message('VariableDesc(d) != VariableDesc(f)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently typed VariableDesc objects equal')

    def test_vinfo_equals_diff_dims(self):
        vinfo1 = datasets.VariableDesc('x', dimensions=('a', 'b'))
        vinfo2 = datasets.VariableDesc('x', dimensions=('a', 'b', 'c'))
        actual = vinfo1
        expected = vinfo2
        print_test_message('VariableDesc(dims1) != VariableDesc(dims2)',
                           actual=str(actual), expected=str(expected))
        self.assertNotEqual(actual, expected,
                            'Differently dimensioned VariableDesc objects equal')

    def test_vinfo_units_default(self):
        vinfo = datasets.VariableDesc('x')
        actual = vinfo.units()
        expected = Unit('1')
        print_test_message('VariableDesc.units() == 1',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.units() not None')

    def test_vinfo_units(self):
        indata = 'm'
        vinfo = datasets.VariableDesc('x', attributes={'units': indata})
        actual = vinfo.units()
        expected = indata
        print_test_message('VariableDesc.units()', indata=indata,
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.units() not {}'.format(indata))

    def test_vinfo_calendar_default(self):
        vinfo = datasets.VariableDesc('x')
        actual = vinfo.calendar()
        expected = None
        print_test_message('VariableDesc.calendar()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.calendar() not None')

    def test_vinfo_calendar(self):
        indata = 'noleap'
        vinfo = datasets.VariableDesc('x', attributes={'units': 'days',
                                                      'calendar': indata})
        actual = vinfo.calendar()
        expected = indata
        print_test_message('VariableDesc.calendar()', indata=indata,
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'VariableDesc.calendar() not {}'.format(indata))

    def test_vinfo_cfunits_default(self):
        vinfo = datasets.VariableDesc('time')
        actual = vinfo.cfunits()
        expected = Unit(1)
        print_test_message('VariableDesc.cfunits() == None',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.cfunits() not None')

    def test_vinfo_cfunits(self):
        units = 'days'
        calendar = 'noleap'
        vinfo = datasets.VariableDesc('x', attributes={'units': units,
                                                      'calendar': calendar})
        actual = vinfo.cfunits()
        expected = Unit(units, calendar=calendar)
        print_test_message('VariableDesc.cfunits()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.cfunits() not {}'.format(expected))

    def test_vinfo_standard_name(self):
        indata = 'X var'
        vinfo = datasets.VariableDesc('x', attributes={'standard_name': indata})
        actual = vinfo.standard_name()
        expected = indata
        print_test_message('VariableDesc.standard_name()', indata=indata,
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                         'Default VariableDesc.standard_name() not {}'.format(indata))

    def test_vinfo_standard_name_default(self):
        vinfo = datasets.VariableDesc('x')
        actual = vinfo.standard_name()
        expected = None
        print_test_message('VariableDesc.standard_name() == None',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected,
                            'Default VariableDesc.standard_name() not None')


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

        self.dsdict = OrderedDict()
        self.dsdict['attributes'] = self.fattribs
        self.dsdict['variables'] = OrderedDict()
        vdicts = self.dsdict['variables']

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
        vdicts['V1']['filenames'] = ['var1.nc']
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 1'
        vattribs['units'] = 'm'
        vdicts['V1']['attributes'] = vattribs

        vdicts['V2'] = OrderedDict()
        vdicts['V2']['datatype'] = 'float64'
        vdicts['V2']['dimensions'] = ('t', 'y', 'x')
        vdicts['V2']['definition'] = 'u2 - u1'
        vdicts['V2']['filenames'] = ['var2.nc']
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

    def test_dataset_get_dict_from_output(self):
        outds = datasets.OutputDatasetDesc('myoutds', self.dsdict)
        actual = outds.get_dict()
        expected = self.dsdict
        print_test_message('OutputDatasetDesc.get_dict()',
                           actual=actual, expected=expected)
        npt.assert_equal(actual, expected,
                         'OutputDatasetDesc.get_dict() returns wrong data')

    def test_dataset_get_dict_from_input(self):
        inds = datasets.InputDatasetDesc('myinds', self.filenames.values())
        actual = inds.get_dict()
        print_test_message('InputDatasetDesc.get_dict()', actual=actual)


#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
