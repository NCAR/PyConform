"""
Dataset Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from glob import glob
from os import remove, linesep
from pyconform import dataset
from collections import OrderedDict
from mkTestData import DataMaker

import unittest
import netCDF4
import numpy


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
        self.dm = DataMaker(filenames=['file1.nc', 'file2.nc', 'file3.nc'],
                            dimensions=OrderedDict([('time', [4,5,6]),
                                                    ('lat', 3),
                                                    ('lon', 2)]),
                            vardims=OrderedDict([('v', ('time', 'lat', 'lon'))]),
                            vartypes=OrderedDict([('v', 'float32')]),
                            varattribs=OrderedDict([('time', OrderedDict([('standard_name', 'time'),
                                                                          ('units', 'days since 01-01-0001'),
                                                                          ('calendar', 'noleap')])),
                                                    ('lat', OrderedDict([('standard_name', 'latitude'),
                                                                         ('units', 'degrees_north')])),
                                                    ('lon', OrderedDict([('standard_name', 'longitude'),
                                                                         ('units', 'degrees_east')])),
                                                    ('v', OrderedDict([('standard_name', 'variable'),
                                                                       ('units', 'unit')]))]))

        self.dsdict = OrderedDict()
        for i, f in enumerate(self.dm.filenames):
            self.dsdict[f] = OrderedDict()
            self.dsdict[f]['attributes'] = OrderedDict(self.dm.fileattribs[i])
            self.dsdict[f]['dimensions'] = OrderedDict()
            self.dsdict[f]['dimensions']['time'] = [self.dm.dimensions['time'][i]]
            self.dsdict[f]['dimensions']['lat'] = self.dm.dimensions['lat']
            self.dsdict[f]['dimensions']['lon'] = self.dm.dimensions['lon']
            self.dsdict[f]['variables'] = OrderedDict()
            for vname, vdict in self.dm.varattribs.iteritems():
                self.dsdict[f]['variables'][vname] = OrderedDict()
                if vname in self.dm.vartypes:
                    self.dsdict[f]['variables'][vname]['dtype'] = self.dm.vartypes[vname]
                else:
                    self.dsdict[f]['variables'][vname]['dtype'] = 'float64'
                if vname in self.dm.vardims:
                    self.dsdict[f]['variables'][vname]['dimensions'] = self.dm.vardims[vname]
                else:
                    self.dsdict[f]['variables'][vname]['dimensions'] = (vname,)
                self.dsdict[f]['variables'][vname]['attributes'] = OrderedDict()
                for aname, avalue in vdict.iteritems():
                    self.dsdict[f]['variables'][vname]['attributes'][aname] = avalue
        
        self.dm.write()

    def tearDown(self):
        self.dm.clear()

    def test_parse_dataset_dictionary(self):
        dataset.parse_dataset_dictionary(self.dsdict)

    def test_parse_dataset_filelist(self):
        dataset.parse_dataset_filelist(self.dm.filenames)

    def test_parse_dataset_equal(self):
        dfiles = dataset.parse_dataset_dictionary(self.dsdict)
        ffiles = dataset.parse_dataset_filelist(self.dm.filenames)

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

        for df, ff in zip(dfiles.values(), ffiles.values()):
            actual = df.name
            expected = ff.name
            print_test_message('InputDataset.name() == OutputDataset.name()',
                               actual=actual, expected=expected)
            self.assertEqual(actual, expected,
                             'Parse methods do not yield same file names')

            actual = df.attributes
            expected = ff.attributes
            print_test_message('InputDataset.attributes() == OutputDataset.attributes()',
                               actual=actual, expected=expected)
            self.assertEqual(actual, expected,
                             'Parse methods do not yield same file attributes')

            actual = df.dimensions
            expected = ff.dimensions
            print_test_message('InputDataset.dimensions() == OutputDataset.dimensions()',
                               actual=actual, expected=expected)
            self.assertEqual(actual, expected,
                             'Parse methods do not yield same file dimensions')

            actual = df.variables
            expected = ff.variables
            print_test_message('InputDataset.variables() == OutputDataset.variables()',
                               actual=actual, expected=expected)
            self.assertEqual(actual, expected,
                             'Parse methods do not yield same file variables')

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
