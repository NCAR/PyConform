"""
Parsing Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from pyconform import parsing, dataset
from mkTestData import DataMaker
from collections import OrderedDict
from copy import deepcopy

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
# ParsingTests - Tests for the parsing module
#=========================================================================
class ParsingTests(unittest.TestCase):
    """
    Unit Tests for the pyconform.parsing module
    """

    def setUp(self):
        
        #-----------------------------------------------------------------------
        # Input Dataset Dictionary
        idict_default = OrderedDict([('attributes', OrderedDict()),
                                     ('dimensions', OrderedDict()),
                                     ('variables', OrderedDict())])
        tmp = idict_default['attributes']
        tmp['a1'] = 'attribute 1'
        tmp['a2'] = 'attribute 2'
        tmp = idict_default['dimensions']
        tmp['time'] = [4]
        tmp['lat'] = 2
        tmp['lon'] = 3
        tmp = idict_default['variables']
        tmp['time'] = OrderedDict()
        tmp['time']['dtype'] = 'd'
        tmp['time']['dimensions'] = ('time',)
        tmp['time']['attributes'] = OrderedDict()
        tmp['time']['attributes']['standard_name'] = 'time'
        tmp['time']['attributes']['units'] = 'days since 01-01-0001 0:0:0'
        tmp['time']['attributes']['calendar'] = 'noleap'
        tmp['lat'] = OrderedDict()
        tmp['lat']['dtype'] = 'd'
        tmp['lat']['dimensions'] = ('lat',)
        tmp['lat']['attributes'] = OrderedDict()
        tmp['lat']['attributes']['standard_name'] = 'latitude'
        tmp['lat']['attributes']['units'] = 'degrees_north'
        tmp['lon'] = OrderedDict()
        tmp['lon']['dtype'] = 'd'
        tmp['lon']['dimensions'] = ('lon',)
        tmp['lon']['attributes'] = OrderedDict()
        tmp['lon']['attributes']['standard_name'] = 'longitude'
        tmp['lon']['attributes']['units'] = 'degrees_east'
        tmp['u1'] = OrderedDict()
        tmp['u1']['dtype'] = 'd'
        tmp['u1']['dimensions'] = ('time', 'lat', 'lon')
        tmp['u1']['attributes'] = OrderedDict()
        tmp['u1']['attributes']['standard_name'] = 'input variable 1'
        tmp['u1']['attributes']['units'] = 'm'
        tmp['u2'] = OrderedDict()
        tmp['u2']['dtype'] = 'd'
        tmp['u2']['dimensions'] = ('time', 'lat', 'lon')
        tmp['u2']['attributes'] = OrderedDict()
        tmp['u2']['attributes']['standard_name'] = 'input variable 2'
        tmp['u2']['attributes']['units'] = 'm'
        
        self.idict = OrderedDict([('file1.nc', deepcopy(idict_default)),
                                  ('file2.nc', deepcopy(idict_default)),
                                  ('file3.nc', deepcopy(idict_default))])
        self.idict['file1.nc']['dimensions']['time'] = [4]
        self.idict['file2.nc']['dimensions']['time'] = [5]
        self.idict['file3.nc']['dimensions']['time'] = [6]

        #-----------------------------------------------------------------------
        # Output Dataset Dictionary
        odict_default = OrderedDict([('attributes', OrderedDict()),
                                     ('dimensions', OrderedDict()),
                                     ('variables', OrderedDict())])
        tmp = odict_default['attributes']
        tmp['a1'] = 'attribute 1'
        tmp['a2'] = 'attribute 2'
        tmp = odict_default['dimensions']
        tmp['T'] = [4+5+6]
        tmp['Y'] = 2
        tmp['X'] = 3
        tmp = odict_default['variables']
        tmp['time'] = OrderedDict()
        tmp['time']['dtype'] = 'd'
        tmp['time']['dimensions'] = ('T',)
        tmp['time']['attributes'] = OrderedDict()
        tmp['time']['attributes']['standard_name'] = 'time'
        tmp['time']['attributes']['units'] = 'days since 01-01-0001 0:0:0'
        tmp['time']['attributes']['calendar'] = 'noleap'
        tmp['latitude'] = OrderedDict()
        tmp['latitude']['dtype'] = 'd'
        tmp['latitude']['dimensions'] = ('Y',)
        tmp['latitude']['attributes'] = OrderedDict()
        tmp['latitude']['attributes']['standard_name'] = 'latitude'
        tmp['latitude']['attributes']['units'] = 'degrees_north'
        tmp['longitude'] = OrderedDict()
        tmp['longitude']['dtype'] = 'd'
        tmp['longitude']['dimensions'] = ('X',)
        tmp['longitude']['attributes'] = OrderedDict()
        tmp['longitude']['attributes']['standard_name'] = 'longitude'
        tmp['longitude']['attributes']['units'] = 'degrees_east'
                
        self.odict = OrderedDict([('var1.nc', deepcopy(odict_default)),
                                  ('var2.nc', deepcopy(odict_default))])
        tmp = self.odict['var1.nc']['variables']
        tmp['v1'] = OrderedDict()
        tmp['v1']['dtype'] = 'd'
        tmp['v1']['dimensions'] = ('T', 'Y', 'X')
        tmp['v1']['attributes'] = OrderedDict()
        tmp['v1']['attributes']['standard_name'] = 'variable 1'
        tmp['v1']['attributes']['units'] = 'm'
        tmp = self.odict['var2.nc']['variables']
        tmp['v2'] = OrderedDict()
        tmp['v2']['dtype'] = 'd'
        tmp['v2']['dimensions'] = ('T', 'Y', 'X')
        tmp['v2']['attributes'] = OrderedDict()
        tmp['v2']['attributes']['standard_name'] = 'variable 2'
        tmp['v2']['attributes']['units'] = 'm'
        
        # Write input dataset
        self.dm = DataMaker.from_dict(self.idict)
        self.dm.write()
        
    def tearDown(self):
        self.dm.clear()

    def test_type(self):
        defmap = {'time': 'time',
                  'latitude': 'lat',
                  'longitude': 'lon',
                  'v1': '0.5*(u1 + u2)',
                  'v2': 'u2 - u1'}
        ids = dataset.InputDataset(filenames=self.dm.filenames)
        ods = dataset.OutputDataset(dsdict=self.odict)
        print ids
        print ods
        defparser = parsing.DefitionParser(ids, ods, defmap)
        actual = type(defparser)
        expected = parsing.DefitionParser
        print_test_message('type(DefinitionParser)', actual, expected)
        self.assertEqual(actual, expected,
                         'DefinitionParser type not correct')


#===============================================================================
# Command-Line Execution
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
