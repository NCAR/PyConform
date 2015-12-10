"""
Dataset Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from glob import glob
from os import remove
from pyconform import dataset
from collections import OrderedDict

import unittest
import netCDF4
import numpy


class DatasetTests(unittest.TestCase):
    """
    Unit Tests for the pyconform.dataset module
    """

    def setUp(self):
        self.filenames = ['file1.nc', 'file2.nc', 'file3.nc']
        
        self.fattribs = OrderedDict()
        self.fattribs['a1'] = 'attribute 1'
        self.fattribs['a2'] = 'attribute 2'
        
        self.dimensions = OrderedDict()
        self.dimensions['time'] = [4,5,6]
        self.dimensions['lat'] = 3
        self.dimensions['lon'] = 2
        
        self.variables = OrderedDict()
        self.variables['time'] = {'type': 'float64',
                                  'dimensions': ['time'],
                                  'attributes': OrderedDict()}
        self.variables['time']['attributes']['standard_name'] = 'time'
        self.variables['time']['attributes']['units'] = 'days since 01-01-0001'
        self.variables['time']['attributes']['calendar'] = 'noleap'

        self.variables['lat'] = {'type': 'float64',
                                 'dimensions': ['lat'],
                                 'attributes': OrderedDict()}
        self.variables['lat']['attributes']['standard_name'] = 'latitude'
        self.variables['lat']['attributes']['units'] = 'degrees_north'

        self.variables['lon'] = {'type': 'float64',
                                 'dimensions': ['lon'],
                                 'attributes': OrderedDict()}
        self.variables['lon']['attributes']['standard_name'] = 'longitude'
        self.variables['lon']['attributes']['units'] = 'degrees_east'
        
        self.variables['v'] = {'type': 'float32',
                               'dimensions': ['time', 'lat', 'lon'],
                               'attributes': OrderedDict()}
        self.variables['v']['attributes']['standard_name'] = 'variable'
        self.variables['v']['attributes']['units'] = 'unit'        

        self.dsdict = OrderedDict()
        for i,f in enumerate(self.filenames):
            self.dsdict[f] = OrderedDict()
            self.dsdict[f]['attributes'] = OrderedDict(self.fattribs)
            self.dsdict[f]['dimensions'] = OrderedDict()
            self.dsdict[f]['dimensions']['time'] = [self.dimensions['time'][i]]
            self.dsdict[f]['dimensions']['lat'] = self.dimensions['lat']
            self.dsdict[f]['dimensions']['lon'] = self.dimensions['lon']
            self.dsdict[f]['variables'] = OrderedDict(self.variables)
        
        for i,f in enumerate(self.filenames):
            fobj = netCDF4.Dataset(f, 'w')
            fobj.setncatts(self.dsdict[f]['attributes'])
            for name, value in self.dsdict[f]['dimensions'].iteritems():
                if isinstance(value, int):
                    fobj.createDimension(name, value)
                elif isinstance(value, list):
                    fobj.createDimension(name)
            for name, value in self.dsdict[f]['variables'].iteritems():
                var = fobj.createVariable(name, value['type'], value['dimensions'])
                shape = []
                for d in value['dimensions']:
                    if isinstance(self.dimensions[d], int):
                        shape.append(self.dimensions[d])
                    elif isinstance(self.dimensions[d], list):
                        shape.append(self.dimensions[d][i])
                size = reduce(lambda x,y: x*y, shape, 1)
                var[:] = numpy.arange(size).reshape(shape)
            fobj.close()
        
    def tearDown(self):
        for ncf in glob('*.nc'):
            remove(ncf)

    def test_parse_dataset_dictionary(self):
        dataset.parse_dataset_dictionary(self.dsdict)

    def test_parse_dataset_filelist(self):
        dataset.parse_dataset_filelist(self.filenames)
        
    def test_parse_dataset_equal(self):
        dfiles = dataset.parse_dataset_dictionary(self.dsdict)
        ffiles = dataset.parse_dataset_filelist(self.filenames)
        self.assertEqual(len(dfiles), len(ffiles),
                         'Parse methods do not yield same number of files')
        self.assertListEqual(dfiles.keys(), ffiles.keys(), 
                             'Parse methods do not yield same filename keys')
        self.assertListEqual([f.name for f in dfiles.values()], 
                             [f.name for f in ffiles.values()], 
                             'Parse methods do not yield same file names')
        self.assertListEqual([f.attributes for f in dfiles.values()], 
                             [f.attributes for f in ffiles.values()], 
                             'Parse methods do not yield same file attributes')
        self.assertListEqual([f.dimensions for f in dfiles.values()], 
                             [f.dimensions for f in ffiles.values()], 
                             'Parse methods do not yield same file dimensions')
        dvariables = [f.variables for f in dfiles.values()]
        print dvariables
        fvariables = [f.variables for f in ffiles.values()]
        print fvariables
        self.assertListEqual(dvariables, fvariables,
                             'Parse methods do not yield same file variables')
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    