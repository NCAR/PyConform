"""
Dataset Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from glob import glob
from os import remove, linesep
from pyconform import dataset
from collections import OrderedDict

import unittest
import netCDF4
import numpy


#===============================================================================
# print_test_message - Helper function
#===============================================================================
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
# DatasetTests - Tests for the dataset module
#===============================================================================
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
                for aname, aval in value['attributes'].iteritems():
                    var.setncattr(aname, aval)
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
        
        actual = len(dfiles)
        expected = len(ffiles)
        print_test_message('len(InputDataset) == len(OutputDataset)',
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         'Parse methods do not yield same number of files')

        actual = dfiles.keys()
        expected = ffiles.keys()
        print_test_message('InputDataset.keys() == OutputDataset.keys()',
                           actual=actual, expected=expected)
        self.assertListEqual(actual, expected,
                             'Parse methods do not yield same filename keys')

        actual = [f.name for f in dfiles.values()]
        expected = [f.name for f in ffiles.values()]
        print_test_message('InputDataset.names() == OutputDataset.names()',
                           actual=actual, expected=expected)
        self.assertListEqual(actual, expected,
                             'Parse methods do not yield same file names')
        
        actual = [f.attributes for f in dfiles.values()]
        expected = [f.attributes for f in ffiles.values()]
        print_test_message('InputDataset.attributes() == OutputDataset.attributes()',
                           actual=actual, expected=expected)
        self.assertListEqual(actual, expected,
                             'Parse methods do not yield same file attributes')

        actual = [f.dimensions for f in dfiles.values()]
        expected = [f.dimensions for f in ffiles.values()]
        print_test_message('InputDataset.dimensions() == OutputDataset.dimensions()',
                           actual=actual, expected=expected)
        self.assertListEqual(actual, expected,
                             'Parse methods do not yield same file dimensions')

        actual = [f.variables for f in dfiles.values()]
        expected = [f.variables for f in ffiles.values()]
        print_test_message('InputDataset.variables() == OutputDataset.variables()',
                           actual=actual, expected=expected)
        self.assertListEqual(actual, expected,
                             'Parse methods do not yield same file variables')
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    