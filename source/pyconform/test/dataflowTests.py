"""
DataFlow Unit Tests

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import remove
from os.path import exists
from pyconform import dataflow, datasets
from testutils import print_test_message, print_ncfile
from collections import OrderedDict
from netCDF4 import Dataset as NCDataset

import unittest
import numpy


#===================================================================================================
# DataFlowTests
#===================================================================================================
class DataFlowTests(unittest.TestCase):
    """
    Unit tests for the flownodes.FlowNode class
    """

    def setUp(self):
        self.filenames = OrderedDict([('u1', 'u1.nc'),
                                      ('u2', 'u2.nc')])
        self.cleanInputFiles()

        self.fattribs = OrderedDict([('a1', 'attribute 1'),
                                     ('a2', 'attribute 2')])
        self.dims = OrderedDict([('time', 4), ('lat', 7), ('lon', 9)])
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
        ulen = reduce(lambda x, y: x * y, self.dims.itervalues(), 1)
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
                dsize = dvalue if dname != 'time' else None
                ncf.createDimension(dname, dsize)
                ncvars[dname] = ncf.createVariable(dname, 'd', (dname,))
            ncvars[vname] = ncf.createVariable(vname, 'd', self.vdims[vname])
            for vnam, vobj in ncvars.iteritems():
                for aname, avalue in self.vattrs[vnam].iteritems():
                    setattr(vobj, aname, avalue)
                vobj[:] = self.vdat[vnam]
            ncf.close()

        self.inpds = datasets.InputDatasetDesc('inpds', self.filenames.values())

        vdicts = OrderedDict()

        vdicts['L'] = OrderedDict()
        vdicts['L']['datatype'] = 'float32'
        vdicts['L']['dimensions'] = ('l',)
        vdicts['L']['definition'] = tuple(range(5))
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
        vdicts['V1']['definition'] = '0.5*(u1 + u2)'
        fdict = OrderedDict()
        fdict['filename'] = 'var1.nc'
        fdict['attributes'] = {'variable': 'V1'}
        fdict['metavars'] = ['L']
        vdicts['V1']['file'] = fdict
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'element-wise average of u1 and u2'
        vattribs['units'] = 'cm'
        vdicts['V1']['attributes'] = vattribs

        vdicts['V2'] = OrderedDict()
        vdicts['V2']['datatype'] = 'float64'
        vdicts['V2']['dimensions'] = ('t', 'y', 'x')
        vdicts['V2']['definition'] = 'u2 - u1'
        fdict = OrderedDict()
        fdict['filename'] = 'var2.nc'
        fdict['attributes'] = {'variable': 'V2'}
        fdict['metavars'] = ['L']
        vdicts['V2']['file'] = fdict
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'difference of u2 and u1'
        vattribs['units'] = 'cm'
        vdicts['V2']['attributes'] = vattribs

        vdicts['V3'] = OrderedDict()
        vdicts['V3']['datatype'] = 'float64'
        vdicts['V3']['dimensions'] = ('x', 'y', 't')
        vdicts['V3']['definition'] = 'u2'
        fdict = OrderedDict()
        fdict['filename'] = 'var3.nc'
        fdict['attributes'] = {'variable': 'V3'}
        fdict['metavars'] = ['L']
        vdicts['V3']['file'] = fdict
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'originally u2'
        vattribs['units'] = 'cm'
        vdicts['V3']['attributes'] = vattribs

        vdicts['V4'] = OrderedDict()
        vdicts['V4']['datatype'] = 'float64'
        vdicts['V4']['dimensions'] = ('t', 'x', 'y')
        vdicts['V4']['definition'] = 'u1'
        fdict = OrderedDict()
        fdict['filename'] = 'var4.nc'
        fdict['attributes'] = {'variable': 'V4'}
        fdict['metavars'] = ['L']
        vdicts['V4']['file'] = fdict
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'transposed u1'
        vattribs['units'] = 'km'
        vattribs['valid_min'] = 1.0
        vattribs['valid_max'] = 20.0
        vdicts['V4']['attributes'] = vattribs
        
        vdicts['V5'] = OrderedDict()
        vdicts['V5']['datatype'] = 'float64'
        vdicts['V5']['dimensions'] = ('t', 'y')
        vdicts['V5']['definition'] = 'mean(u1, "lon")'
        fdict = OrderedDict()
        fdict['filename'] = 'var5.nc'
        fdict['attributes'] = {'variable': 'V5'}
        vdicts['V5']['file'] = fdict
        vattribs = OrderedDict()
        vattribs['standard_name'] = 'mean of u1 along the lon dimension'
        vattribs['units'] = 'km'
        vattribs['valid_min'] = 1.0
        vattribs['valid_max'] = 20.0
        vdicts['V5']['attributes'] = vattribs

        self.dsdict = vdicts

        self.outds = datasets.OutputDatasetDesc('outds', self.dsdict)

        self.outfiles = dict((vname, vdict['file']['filename']) for vname, vdict
                             in vdicts.iteritems() if 'file' in vdict)
        self.cleanOutputFiles()

    def cleanInputFiles(self):
        for fname in self.filenames.itervalues():
            if exists(fname):
                remove(fname)

    def cleanOutputFiles(self):
        for fname in self.outfiles.itervalues():
            if exists(fname):
                remove(fname)

    def tearDown(self):
        self.cleanInputFiles()
        self.cleanOutputFiles()

    def test_init(self):
        testname = 'DataFlow.__init__()'
        df = dataflow.DataFlow(self.inpds, self.outds)
        actual = type(df)
        expected = dataflow.DataFlow
        print_test_message(testname, actual=actual, expected=expected)
        self.assertIsInstance(df, expected, '{} failed'.format(testname))

    def test_dimension_map(self):
        testname = 'DataFlow().dimension_map'
        df = dataflow.DataFlow(self.inpds, self.outds)
        actual = df.dimension_map
        expected = {'lat': 'y', 'lon': 'x', 'time': 't'}
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_execute_all(self):
        testname = 'DataFlow().execute()'
        df = dataflow.DataFlow(self.inpds, self.outds)
        df.execute()
        actual = all(exists(f) for f in self.outfiles.itervalues())
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        for f in self.outfiles:
            print_ncfile(self.outfiles[f])
            print

    def test_execute_chunks_1D_x(self):
        testname = 'DataFlow().execute()'
        df = dataflow.DataFlow(self.inpds, self.outds)
        expected = ValueError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, df.execute, chunks={'x': 4})

    def test_execute_chunks_1D_y(self):
        testname = 'DataFlow().execute()'
        df = dataflow.DataFlow(self.inpds, self.outds)
        df.execute(chunks={'y': 3})
        actual = all(exists(f) for f in self.outfiles.itervalues())
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        for f in self.outfiles:
            print_ncfile(self.outfiles[f])
            print

    def test_execute_chunks_2D_x_y(self):
        testname = 'DataFlow().execute()'
        df = dataflow.DataFlow(self.inpds, self.outds)
        expected = ValueError
        print_test_message(testname, expected=expected)
        self.assertRaises(expected, df.execute, chunks=OrderedDict([('x', 4), ('y', 3)]))

    def test_execute_chunks_2D_t_y(self):
        testname = 'DataFlow().execute()'
        df = dataflow.DataFlow(self.inpds, self.outds)
        df.execute(chunks=OrderedDict([('t', 2), ('y', 3)]))
        actual = all(exists(f) for f in self.outfiles.itervalues())
        expected = True
        print_test_message(testname, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        for f in self.outfiles:
            print_ncfile(self.outfiles[f])
            print


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
