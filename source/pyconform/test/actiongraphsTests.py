"""
ActionGraph Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep, remove
from os.path import exists
from pyconform import datasets, actiongraphs, actions
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
# ActionGraphTests - Tests for the actiongraphs.ActionGraph class
#=========================================================================
class ActionGraphTests(unittest.TestCase):
    """
    Unit Tests for the actiongraphs.ActionGraph class
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
            
        self.inpds = datasets.InputDataset('inpds', self.filenames.values())

    def tearDown(self):
        self._clear_()
        
    def _clear_(self):
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)
    
    def test_init(self):
        g = actiongraphs.ActionGraph()
        actual = type(g)
        expected = actiongraphs.ActionGraph
        print_test_message('type(ActionGraph)', 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'ActionGraph type not correct')

    def test_add_op(self):
        g = actiongraphs.ActionGraph()
        u1r = actions.Reader(self.filenames['u1'], 'u1')
        g.add(u1r)
        actual = g.vertices
        expected = [u1r]
        print_test_message('ActionGraph.add(Action)',
                           actual=actual, expected=expected)
        self.assertListEqual(actual, expected,
                            'ActionGraph did not add Action')

    def test_add_int(self):
        g = actiongraphs.ActionGraph()
        expected = TypeError
        print_test_message('ActionGraph.add(int) TypeError',
                           expected=expected)
        self.assertRaises(expected, g.add, 1)

    def test_call(self):
        g = actiongraphs.ActionGraph()
        u1read = actions.Reader(self.filenames['u1'], 'u1')
        u2read = actions.Reader(self.filenames['u2'], 'u2')
        u1plusu2 = actions.Evaluator('+', '(u1+u2)', operator.add,
                                             signature=[None, None])
        g.connect(u1read, u1plusu2)
        g.connect(u2read, u1plusu2)
        actual = g(u1plusu2)
        expected = self.vdat['u1'] + self.vdat['u2']
        print_test_message('ActionGraph.__call__()', 
                           actual=actual, expected=expected)
        nptst.assert_array_equal(actual, expected,
                                 'ActionGraph() failed')

    def test_print(self):
        g = actiongraphs.ActionGraph()
        u1read = actions.Reader(self.filenames['u1'], 'u1')
        u2read = actions.Reader(self.filenames['u2'], 'u2')
        u1plusu2 = actions.Evaluator('+', '(u1+u2)', operator.add,
                                             signature=[None, None])
        vhandle = actions.Finalizer('V')
        g.connect(u1read, u1plusu2)
        g.connect(u2read, u1plusu2)
        g.connect(u1plusu2, vhandle)
        print g
        
    def test_handles(self):
        g = actiongraphs.ActionGraph()
        u1read = actions.Reader(self.filenames['u1'], 'u1')
        u2read = actions.Reader(self.filenames['u2'], 'u2')
        u1plusu2 = actions.Evaluator('+', '(u1+u2)', operator.add,
                                             signature=[None, None])
        vhandle = actions.Finalizer('V')
        g.connect(u1read, u1plusu2)
        g.connect(u2read, u1plusu2)
        g.connect(u1plusu2, vhandle)
        actual = g.handles()[0]
        expected = vhandle
        print_test_message('ActionGraph.handles()', 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected, 'ActionGraph() failed')


#===============================================================================
# GraphFillerTests
#===============================================================================
class GraphFillerTests(unittest.TestCase):
    """
    Unit Tests for the actiongraphs.GraphFiller class
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
                                   ('u2', {'units': 'ft',
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
            
        self.inpds = datasets.InputDataset('inpds', self.filenames.values())

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
        vattribs['units'] = 'hours since 0001-01-01 00:00:00'
        vattribs['calendar'] = 'noleap'
        vdicts['T']['attributes'] = vattribs

        vdicts['V1'] = OrderedDict()
        vdicts['V1']['datatype'] = 'float64'
        vdicts['V1']['dimensions'] = ('t', 'x', 'y')
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
        
        vdicts['V3'] = OrderedDict()
        vdicts['V3']['datatype'] = 'float64'
        vdicts['V3']['dimensions'] = ('t', 'y', 'x')
        vdicts['V3']['definition'] = '(u2 + u1) / u3'
        vdicts['V3']['filename'] = 'var3.nc'
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'variable 2'
        vattribs['units'] = '1'
        vdicts['V3']['attributes'] = vattribs
        
        self.outds = datasets.OutputDataset('outds', self.dsdict)
        
    def tearDown(self):
        self._clear_()
        
    def _clear_(self):
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)

    def test_init(self):
        gfiller = actiongraphs.GraphFiller(self.inpds)
        actual = type(gfiller)
        expected = actiongraphs.GraphFiller
        print_test_message('type(GraphFiller)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'GraphFiller type not correct')

    def test_from_definitions(self):
        print_test_message('GraphFiller.from_definitions()')
        g = actiongraphs.ActionGraph()
        gfiller = actiongraphs.GraphFiller(self.inpds)
        gfiller.from_definitions(g, self.outds)
        print g

    def test_from_definitions_components(self):
        print_test_message('GraphFiller.from_definitions().components()')
        g = actiongraphs.ActionGraph()
        gfiller = actiongraphs.GraphFiller(self.inpds)
        gfiller.from_definitions(g, self.outds)
        glist = g.components()
        for ig in glist:
            print 'GRAPH:'
            print ig

    def test_match_units(self):
        print_test_message('GraphFiller.match_units()')
        g = actiongraphs.ActionGraph()
        gfiller = actiongraphs.GraphFiller(self.inpds)
        gfiller.from_definitions(g, self.outds)
        gfiller.match_units(g)
        print g

    def test_match_units_reapply(self):
        g = actiongraphs.ActionGraph()
        gfiller = actiongraphs.GraphFiller(self.inpds)
        gfiller.from_definitions(g, self.outds)
        gfiller.match_units(g)
        expected = str(g)
        gfiller.match_units(g)
        actual = str(g)
        print_test_message('GraphFiller.match_units() Reapplied',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'GraphFiller.match_units() reapplied failed')
        
    def test_match_dimensions(self):
        print_test_message('GraphFiller.match_dimensions()')
        g = actiongraphs.ActionGraph()
        gfiller = actiongraphs.GraphFiller(self.inpds)
        gfiller.from_definitions(g, self.outds)
        gfiller.match_dimensions(g)
        print g

    def test_match_dimensions_reapply(self):
        g = actiongraphs.ActionGraph()
        gfiller = actiongraphs.GraphFiller(self.inpds)
        gfiller.from_definitions(g, self.outds)
        indata = str(g)
        gfiller.match_dimensions(g)
        expected = str(g)
        gfiller.match_dimensions(g)
        actual = str(g)
        print_test_message('GraphFiller.match_dimensions() Reapplied',
                           indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'GraphFiller.match_dimensions() reapplied failed')

    def test_match_units_dimensions(self):
        print_test_message('GraphFiller.match_dimensions()')
        g = actiongraphs.ActionGraph()
        gfiller = actiongraphs.GraphFiller(self.inpds)
        gfiller.from_definitions(g, self.outds)
        gfiller.match_units(g)
        gfiller.match_dimensions(g)
        print g

    def test_match_dimensions_units(self):
        print_test_message('GraphFiller.match_dimensions()')
        g = actiongraphs.ActionGraph()
        gfiller = actiongraphs.GraphFiller(self.inpds)
        gfiller.from_definitions(g, self.outds)
        gfiller.match_dimensions(g)
        gfiller.match_units(g)
        print g

#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
