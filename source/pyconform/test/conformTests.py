"""
Dataset Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep, remove
from os.path import exists
from pyconform import conform, dataset
from collections import OrderedDict
from netCDF4 import Dataset as NCDataset

import numpy
import operator
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
        ydat = numpy.linspace(-90, 90, num=self.dims['lat'],
                              endpoint=True, dtype=self.dtypes['lat'])
        xdat = numpy.linspace(-180, 180, num=self.dims['lon'],
                              endpoint=False, dtype=self.dtypes['lon'])
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
            
        self.inpds = dataset.InputDataset('inpds', self.filenames.values())

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
        
        self.outds = dataset.OutputDataset('outds', self.dsdict)

    def tearDown(self):
        self._clear_()
        
    def _clear_(self):
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)

    #===== name_definition tests =================================================

    def test_name_definition(self):
        indata = (operator.add, (operator.div, 'y', 3), 'x')
        actual = conform.name_definition(indata)
        expected = 'add(div(y,3),x)'
        print_test_message('name_definition({!r})'.format(indata),
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'name_definition() incorrect')

    def test_name_definition_var_only(self):
        indata = 'xyz'
        actual = conform.name_definition(indata)
        expected = indata
        print_test_message('name_definition({!r})'.format(indata),
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'name_definition() incorrect')

    #===== gather_dimensions tests =============================================
    
    def test_gather_dimensions(self):
        indata = (operator.mul, 0.5, (operator.add, 'u1', 'u2'))
        actual = conform.gather_dimensions(indata, self.inpds)
        expected = {'mul(0.5,add(u1,u2))':
                    {'add(u1,u2)':
                     {'u1': self.inpds.variables['u1'].dimensions, 
                      'u2': self.inpds.variables['u2'].dimensions},
                     '0.5': None}}
        print_test_message('gather_dimensions()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected, 'gather_dimensions() incorrect')

    def test_gather_dimensions_var_only(self):
        indata = 'u1'
        actual = conform.gather_dimensions(indata, self.inpds)
        expected = {'u1': self.inpds.variables['u1'].dimensions}
        print_test_message('gather_dimensions()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected, 'gather_dimensions() incorrect')

    def test_gather_dimensions_number_only(self):
        indata = 1
        actual = conform.gather_dimensions(indata, self.inpds)
        expected = {str(indata): None}
        print_test_message('gather_dimensions()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected, 'gather_dimensions() incorrect')

    #===== reduce_dimensions tests =============================================

    def test_reduce_dimensions(self):
        indata = {'mul(0.5,add(u1,u2))':
                  {'add(u1,u2)':
                   {'u1': self.inpds.variables['u1'].dimensions, 
                    'u2': self.inpds.variables['u2'].dimensions}}}
        actual = conform.reduce_dimensions(indata)
        expected = self.inpds.variables['u1'].dimensions
        print_test_message('reduce_dimensions()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected, 'reduce_dimensions() incorrect')

    def test_reduce_dimensions_number_only(self):
        indata = {'1': None}
        actual = conform.reduce_dimensions(indata)
        expected = None
        print_test_message('reduce_dimensions()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected, 'reduce_dimensions() incorrect')

    def test_reduce_dimensions_dims_only(self):
        indata = ('x', 'y', 't')
        actual = conform.reduce_dimensions(indata)
        expected = indata
        print_test_message('reduce_dimensions()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected, 'reduce_dimensions() incorrect')
                
    def test_reduce_dimensions_var_only(self):
        indata = {'u': ('x', 'y')}
        actual = conform.reduce_dimensions(indata)
        expected = indata['u']
        print_test_message('reduce_dimensions()',
                           actual=str(actual), expected=str(expected))
        self.assertEqual(actual, expected, 'reduce_dimensions() incorrect')

    #===== build_opgraphs tests ================================================
    
    def test_build_opgraphs(self):
        actual = conform.build_opgraphs(self.inpds, self.outds)
        expected = None
        print_test_message('build_opgraphs()',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'build_opgraphs() incorrect')


#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
