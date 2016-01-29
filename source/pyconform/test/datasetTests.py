"""
Dataset Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep, remove
from os.path import exists
from pyconform import dataset
from collections import OrderedDict
from netCDF4 import Dataset as NCDataset

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


#=========================================================================
# DatasetTests - Tests for the dataset module
#=========================================================================
class DatasetTests(unittest.TestCase):
    """
    Unit Tests for the pyconform.dataset module
    """

    def setUp(self):
        self._clear_()
        
        self.filenames = OrderedDict([('u1', 'u1.nc'), ('u2', 'u2.nc')])
        self.fattribs = {'u1': OrderedDict([('a1', 'u1 attrib 1'),
                                            ('a2', 'u1 attrib 2')]),
                         'u2': OrderedDict([('a1', 'u2 attrib 1'),
                                            ('a2', 'u2 attrib 2')])}
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
                                   ('u1', {'units': 'm'}),
                                   ('u2', {'units': 'm'})])
        self.dtypes = {'lat': 'f', 'lon': 'f', 'time': 'f', 'u1': 'd', 'u2': 'd'}
        ydat = np.linspace(-90, 90, num=self.dims['lat'],
                           endpoint=True, dtype=self.dtypes['lat'])
        xdat = np.linspace(-180, 180, num=self.dims['lon'],
                           endpoint=False, dtype=self.dtypes['lon'])
        tdat = np.linspace(0, self.dims['time'], num=self.dims['time'],
                           endpoint=False, dtype=self.dtypes['time'])
        u1dat = np.linspace(0, self.dims['time'], num=self.dims['time'],
                            endpoint=False, dtype=self.dtypes['u1'])
        u2dat = np.linspace(0, self.dims['time'], num=self.dims['time'],
                            endpoint=False, dtype=self.dtypes['u2'])
        self.vdat = {'lat': ydat, 'lon': xdat, 'time': tdat,
                     'u1': u1dat, 'u2': u2dat}

        for vname, fname in self.filenames.iteritems():
            ncf = NCDataset(fname, 'w')
            ncf.setncatts(self.fattribs[vname])
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

        self.dsdict['X'] = OrderedDict()
        self.dsdict['X']['definition'] = 'lon'
        self.dsdict['X']['dimensions'] = ('x',)
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'longitude'
        vattribs['units'] = 'degrees_east'
        self.dsdict['X']['attributes'] = vattribs

        self.dsdict['Y'] = OrderedDict()
        self.dsdict['Y']['definition'] = 'lat'
        self.dsdict['Y']['dimensions'] = ('y',)
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'latitude'
        vattribs['units'] = 'degrees_north'
        self.dsdict['Y']['attributes'] = vattribs

        self.dsdict['T'] = OrderedDict()
        self.dsdict['T']['definition'] = 'time'
        self.dsdict['T']['dimensions'] = ('t',)
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'time'
        vattribs['units'] = 'days since 01-01-0001 00:00:00'
        self.dsdict['T']['attributes'] = vattribs

        self.dsdict['V1'] = OrderedDict()
        self.dsdict['V1']['definition'] = 'u1 + u2'
        self.dsdict['V1']['dimensions'] = ('t', 'y', 'x')
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 1'
        vattribs['units'] = 'm'
        self.dsdict['V1']['attributes'] = vattribs
        self.dsdict['V1']['filename'] = 'var1.nc'

        self.dsdict['V2'] = OrderedDict()
        self.dsdict['V2']['definition'] = 'u2 - u1'
        self.dsdict['V2']['dimensions'] = ('t', 'y', 'x')
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 2'
        vattribs['units'] = 'm'
        self.dsdict['V2']['attributes'] = vattribs
        self.dsdict['V2']['filename'] = 'var2.nc'

    def tearDown(self):
        self._clear_()
        
    def _clear_(self):
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)

    def test_dataset_type(self):
        ds = dataset.Dataset()
        actual = type(ds)
        expected = dataset.Dataset
        print_test_message('type(Dataset)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Dataset has wrong type')

    def test_input_dataset_type(self):
        inds = dataset.InputDataset('myinds', self.dm.filenames)
        actual = type(inds)
        expected = dataset.InputDataset
        print_test_message('type(InputDataset)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'InputDataset has wrong type')

    def test_output_dataset_type(self):
        outds = dataset.OutputDataset('myoutds', self.dsdict)
        actual = type(outds)
        expected = dataset.OutputDataset
        print_test_message('type(OutputDataset)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'OutputDataset has wrong type')

    def test_dataset_get_dict_from_output(self):
        outds = dataset.OutputDataset('myoutds', self.dsdict)
        actual = outds.get_dict()
        expected = self.dsdict
        print_test_message('get_dict()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Dataset.get_dict() returns wrong data')
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
