"""
Dataset Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep, remove
from os.path import exists
from pyconform import conform, datasets
from collections import OrderedDict
from netCDF4 import Dataset as NCDataset

import json
import numpy
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
# ConformTests - Tests for the conform module
#=========================================================================
class ConformTests(unittest.TestCase):
    """
    Unit Tests for the pyconform.dataset module
    """

    def setUp(self):        
        self.filenames = OrderedDict([('u1', 'u1.nc'),
                                      ('u2', 'u2.nc')])
        self._clear_()
        
        self.fattribs = OrderedDict([('a1', 'attribute 1'),
                                     ('a2', 'attribute 2')])
        self.dims = OrderedDict([('time', 8), ('lat', 7), ('lon', 6)])
        self.vdims = OrderedDict([('u1', ('time', 'lat', 'lon')),
                                  ('u2', ('time', 'lat', 'lon'))])
        self.vattrs = OrderedDict([('lat', {'units': 'degrees_north',
                                            'standard_name': 'latitude'}),
                                   ('lon', {'units': 'degrees_east',
                                            'standard_name': 'longitude'}),
                                   ('time', {'units': 'days since 1979-01-01 0:0:0',
                                             'calendar': 'noleap',
                                             'standard_name': 'time'}),
                                   ('u1', {'units': 'km',
                                           'standard_name': 'u variable 1'}),
                                   ('u2', {'units': 'm',
                                           'standard_name': 'u variable 2'})])
        self.dtypes = {'lat': 'f', 'lon': 'f', 'time': 'f', 'u1': 'd', 'u2': 'd'}
        ydat = numpy.linspace(-90, 90, num=self.dims['lat'],
                              endpoint=True, dtype=self.dtypes['lat'])
        xdat = numpy.linspace(-180, 180, num=self.dims['lon'],
                              endpoint=False, dtype=self.dtypes['lon'])
        xdat = -xdat[::-1]
        tdat = numpy.linspace(0, self.dims['time'], num=self.dims['time'],
                              endpoint=False, dtype=self.dtypes['time'])
        ulen = reduce(lambda x,y: x*y, self.dims.itervalues(), 1)
        ushape = tuple(d for d in self.dims.itervalues())
        u1dat = numpy.linspace(0, ulen, num=ulen, endpoint=False,
                               dtype=self.dtypes['u1']).reshape(ushape)
        u2dat = numpy.linspace(0, ulen, num=ulen, endpoint=False,
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
            
        self.inpds = datasets.InputDataset('inpds', self.filenames.values())

        self.dsdict = OrderedDict()
        self.dsdict['attributes'] = self.fattribs
        self.dsdict['variables'] = OrderedDict()
        vdicts = self.dsdict['variables']

        vdicts['L'] = OrderedDict()
        vdicts['L']['datatype'] = 'float32'
        vdicts['L']['dimensions'] = ('l',)
        vdicts['L']['data'] = tuple(range(5))
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'level'
        vattribs['units'] = '1'
        vdicts['L']['attributes'] = vattribs
        
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
        vattribs['units'] = 'days since 0001-01-01 00:00:00'
        vattribs['calendar'] = 'noleap'
        vdicts['T']['attributes'] = vattribs

        vdicts['V1'] = OrderedDict()
        vdicts['V1']['datatype'] = 'float64'
        vdicts['V1']['dimensions'] = ('t', 'y', 'x')
        vdicts['V1']['definition'] = 'u1 + u2'
        vdicts['V1']['filename'] = 'var1.nc'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 1'
        vattribs['units'] = 'cm'
        vdicts['V1']['attributes'] = vattribs

        vdicts['V2'] = OrderedDict()
        vdicts['V2']['datatype'] = 'float64'
        vdicts['V2']['dimensions'] = ('t', 'y', 'x')
        vdicts['V2']['definition'] = 'u2 - u1'
        vdicts['V2']['filename'] = 'var2.nc'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 2'
        vattribs['units'] = 'cm'
        vdicts['V2']['attributes'] = vattribs

        vdicts['V3'] = OrderedDict()
        vdicts['V3']['datatype'] = 'float64'
        vdicts['V3']['dimensions'] = ('x', 'y', 't')
        vdicts['V3']['definition'] = 'u2'
        vdicts['V3']['filename'] = 'var3.nc'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 3'
        vattribs['units'] = 'cm'
        vdicts['V3']['attributes'] = vattribs

        vdicts['V4'] = OrderedDict()
        vdicts['V4']['datatype'] = 'float64'
        vdicts['V4']['dimensions'] = ('t', 'x', 'y')
        vdicts['V4']['definition'] = 'u1'
        vdicts['V4']['filename'] = 'var4.nc'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 4'
        vattribs['units'] = 'km'
        vattribs['valid_min'] = 1.0
        vattribs['valid_max'] = 100.0
        vdicts['V4']['attributes'] = vattribs
                
        self.outds = datasets.OutputDataset('outds', self.dsdict)

    def tearDown(self):
        self._clear_()
        
    def _clear_(self):
        return
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)

    def test_conform(self):
        with open('conform.spec', 'w') as fp:
            json.dump(self.outds.get_dict(), fp, indent=4)
        actual = conform.conform(self.inpds, self.outds)
        expected = None
        print_test_message('conform()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'conform() incorrect')


#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
