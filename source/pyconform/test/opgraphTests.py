"""
Operations Graph Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from mkTestData import DataMaker
from pyconform import opgraph
from numpy.testing import assert_array_equal

import unittest
import netCDF4


#===============================================================================
# General Functions
#===============================================================================
def print_test_message(testname, actual, expected):
    indent = ' ' * len(testname)
    print '{} - actual =   {}'.format(testname, actual)
    print '{} - expected = {}'.format(indent, expected)


#===============================================================================
# OperationNodeTests - Unit tests of the opgraph.OperationNode base class
#===============================================================================
class DummyOperationNode(opgraph.OperationNode):
    def __call__(self):
        pass


class OperationNodeTests(unittest.TestCase):
    """
    Unit tests for the opgraph.OperationNode class
    """

    def test_name(self):
        name = 'xyz'
        opnode = DummyOperationNode(name)
        testname = 'OperationNode.name()'
        actual = opnode.name()
        expected = name
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_str(self):
        name = 'xyz'
        opnode = DummyOperationNode(name)
        testname = 'OperationNode.__str__()'
        actual = str(opnode)
        expected = name
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_repr(self):
        name = 'xyz'
        opnode = DummyOperationNode(name)
        testname = 'OperationNode.__repr__()'
        actual = repr(opnode)
        expected = repr(name)
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))


#===============================================================================
# ReadNetCDF4SliceNodeTests - OpGraph.ReadNetCDF4SliceNode Tests
#===============================================================================
class ReadNetCDF4SliceNodeTests(unittest.TestCase):
    """
    Units tests for the opgraph.ReadNetCDF4SliceNode class
    """
    
    def setUp(self):
        self.filename = 'test.nc'
        self.dm = DataMaker(filenames=[self.filename])
        self.varname = self.dm.var_dims.keys()[0]
        udim = self.dm.var_dims[self.varname].index(self.dm.unlimited)
        self.vslice = [slice(None)] * len(self.dm.var_dims[self.varname])
        self.vslice[udim] = slice(0,1)
        self.dm.write()
        self.expected = self.dm.variables[self.filename][self.varname][self.vslice]
        
    def tearDown(self):
        self.dm.clear()

    def test_call_filename(self):
        testname = 'ReadNetCDF4SliceNode(filename).__call__()'
        rvnode = opgraph.ReadNetCDF4SliceNode(self.varname, self.filename, 
                                               slicetuple=self.vslice)
        actual = rvnode()
        expected = self.expected
        print_test_message(testname, actual, expected)
        assert_array_equal(actual, expected,
                           '{} returned unexpected result'.format(testname))

    def test_call_fileobj(self):
        ncfile = netCDF4.Dataset(self.filename, 'r')
        testname = 'ReadNetCDF4SliceNode(file).__call__()'
        rvnode = opgraph.ReadNetCDF4SliceNode(self.varname, ncfile, 
                                               slicetuple=self.vslice)
        actual = rvnode()
        expected = self.expected
        print_test_message(testname, actual, expected)
        assert_array_equal(actual, expected,
                           '{} returned unexpected result'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
