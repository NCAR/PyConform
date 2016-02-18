"""
Parsing Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep, remove
from os.path import exists
from pyconform import dataset
from pyconform import opgraph
from pyconform.operators import InputSliceReader, FunctionEvaluator
from netCDF4 import Dataset as NCDataset
from collections import OrderedDict
from numpy import testing as nptst

import operator
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
    if indata is not None:
        s_indata = str(indata).replace(linesep, indent)
        print '    input:    {}'.format(s_indata)
    if actual is not None:
        s_actual = str(actual).replace(linesep, indent)
        print '    actual:   {}'.format(s_actual)
    if expected is not None:
        s_expected = str(expected).replace(linesep, indent)
        print '    expected: {}'.format(s_expected)
    print
    

#=========================================================================
# OperationGraphTests - Tests for the opgraph.OperationGraph class
#=========================================================================
class OperationGraphTests(unittest.TestCase):
    """
    Unit Tests for the opgraph.OperationGraph class
    """

    def setUp(self):        
        self.filenames = OrderedDict([('u1', 'u1.nc'),
                                      ('u2', 'u2.nc'),
                                      ('u3', 'u3.nc')])
        self._clear_()
        
        self.fattribs = OrderedDict([('a1', 'attribute 1'),
                                     ('a2', 'attribute 2')])
        self.dims = OrderedDict([('time', 4), ('lat', 3), ('lon', 2)])
        self.vdims = OrderedDict([('u1', ('time', 'lat', 'lon')),
                                  ('u2', ('time', 'lat', 'lon')),
                                  ('u3', ('time', 'lat', 'lon'))])
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
                                           'standard_name': 'u variable 2'}),
                                   ('u3', {'units': 'km',
                                           'standard_name': 'u variable 3'})])
        self.dtypes = {'lat': 'f', 'lon': 'f', 'time': 'f',
                       'u1': 'd', 'u2': 'd', 'u3': 'd'}
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
        u3dat = numpy.linspace(0, ulen, num=ulen, endpoint=False,
                               dtype=self.dtypes['u3']).reshape(ushape)
        self.vdat = {'lat': ydat, 'lon': xdat, 'time': tdat,
                     'u1': u1dat, 'u2': u2dat, 'u3': u3dat}

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

    def tearDown(self):
        self._clear_()
        
    def _clear_(self):
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)
    
    def test_init(self):
        g = opgraph.OperationGraph()
        actual = type(g)
        expected = opgraph.OperationGraph
        print_test_message('type(OperationGraph)', 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'OperationGraph type not correct')

    def test_add_op(self):
        g = opgraph.OperationGraph()
        u1Op = InputSliceReader(self.filenames['u1'], 'u1')
        g.add(u1Op)
        actual = g.vertices
        expected = set([u1Op])
        print_test_message('OperationGraph.add(Operator)',
                           actual=actual, expected=expected)
        self.assertSetEqual(actual, expected,
                            'OperationGraph did not add Operators')

    def test_add_int(self):
        g = opgraph.OperationGraph()
        expected = TypeError
        print_test_message('OperationGraph.add(int) TypeError',
                           expected=expected)
        self.assertRaises(expected, g.add, 1)

    def test_call(self):
        g = opgraph.OperationGraph()
        u1Op = InputSliceReader(self.filenames['u1'], 'u1')
        u2Op = InputSliceReader(self.filenames['u2'], 'u2')
        u1plusu2 = FunctionEvaluator('(u1+u2)', operator.add,
                                     args=[None, None],
                                     units=u1Op.units,
                                     dimensions=u1Op.dimensions)
        g.connect(u1Op, u1plusu2)
        g.connect(u2Op, u1plusu2)
        actual = g(u1plusu2)
        expected = self.vdat['u1'] + self.vdat['u2']
        print_test_message('OperationGraph.__call__()', 
                           actual=actual, expected=expected)
        nptst.assert_array_equal(actual, expected,
                                 'OperationGraph() failed')


#===============================================================================
# GraphFillerTests
#===============================================================================
class GraphFillerTests(unittest.TestCase):
    """
    Unit Tests for the opgraph.GraphFiller class
    """

    def setUp(self):        
        self.filenames = OrderedDict([('u1', 'w1.nc'),
                                      ('u2', 'w2.nc'),
                                      ('u3', 'w3.nc')])
        self._clear_()
        
        self.fattribs = OrderedDict([('a1', 'attribute 1'),
                                     ('a2', 'attribute 2')])
        self.dims = OrderedDict([('time', 4), ('lat', 3), ('lon', 2)])
        self.vdims = OrderedDict([('u1', ('time', 'lat', 'lon')),
                                  ('u2', ('time', 'lat', 'lon')),
                                  ('u3', ('time', 'lat', 'lon'))])
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
                                           'standard_name': 'u variable 2'}),
                                   ('u3', {'units': 'km',
                                           'standard_name': 'u variable 3'})])
        self.dtypes = {'lat': 'f', 'lon': 'f', 'time': 'f',
                       'u1': 'd', 'u2': 'd', 'u3': 'd'}
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
        u3dat = numpy.linspace(0, ulen, num=ulen, endpoint=False,
                               dtype=self.dtypes['u3']).reshape(ushape)
        self.vdat = {'lat': ydat, 'lon': xdat, 'time': tdat,
                     'u1': u1dat, 'u2': u2dat, 'u3': u3dat}

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

    def test_init(self):
        gfiller = opgraph.GraphFiller()
        actual = type(gfiller)
        expected = opgraph.GraphFiller
        print_test_message('type(GraphFiller)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'GraphFiller type not correct')

    def test_from_definitions(self):
        g = opgraph.OperationGraph()
        gfiller = opgraph.GraphFiller()
        gfiller.from_definitions(g, self.inpds, self.outds)
        print_test_message('GraphFiller.from_definitions()')

    def test_dimension_map(self):
        g = opgraph.OperationGraph()
        gfiller = opgraph.GraphFiller()
        gfiller.from_definitions(g, self.inpds, self.outds)
        actual = gfiller.dimension_map
        expected = {'x': 'lon', 'y': 'lat', 't': 'time'}
        print_test_message('GraphFiller.from_definitions()')
        self.assertDictEqual(actual, expected,
                             'Dimension map incorrect')


#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
