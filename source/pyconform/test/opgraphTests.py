"""
Operations Graph Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from mkTestData import DataMaker

from pyconform import opgraph
import netCDF4

class OpGraphTests(unittest.TestCase):
    """
    Units tests for the opgraph module
    """

    def print_assertEqual(self, testname, actual, expected):
        indent = ' ' * len(testname)
        print '{} - actual =   {}'.format(testname, actual)
        print '{} - expected = {}'.format(indent, expected)

    #---------------------
    # OperationNode Tests
    #---------------------

    def test_OperationNode_name(self):
        name = 'xyz'
        onode = opgraph.OperationNode(name)
        self.print_assertEqual('OperationNode.name()', onode.name(), name)

    def test_OperationNode_str(self):
        name = 'xyz'
        onode = opgraph.OperationNode(name)
        self.print_assertEqual('OperationNode.__str__()', str(onode), name)

    def test_OperationNode_repr(self):
        name = 'xyz'
        onode = opgraph.OperationNode(name)
        self.print_assertEqual('OperationNode.__repr__()', 
                               repr(onode), repr(name))

    def test_OperationNode_call(self):
        name = 'xyz'
        onode = opgraph.OperationNode(name)
        self.print_assertEqual('OperationNode.__call__()', onode(), None)

    #------------------------
    # ReadVariableNode Tests
    #------------------------

    def test_ReadVariableNode_filename_call(self):
        filename = 'test.nc'
        dm = DataMaker(filenames=[filename])
        varname = dm.var_dims.keys()[0]
        udim = dm.var_dims[varname].index(dm.unlimited)
        vslice = [slice(None)] * len(dm.var_dims[varname])
        vslice[udim] = slice(0,1)
        
        dm.write()
        rvnode = opgraph.ReadVariableNode(varname, filename, slicetuple=vslice)
        self.print_assertEqual('OperationNode.__call__()', rvnode(), 
                               dm.variables[filename][varname][vslice])
        dm.clear()

    def test_ReadVariableNode_file_call(self):
        filename = 'test.nc'
        dm = DataMaker(filenames=[filename])
        varname = dm.var_dims.keys()[0]
        udim = dm.var_dims[varname].index(dm.unlimited)
        vslice = [slice(None)] * len(dm.var_dims[varname])
        vslice[udim] = slice(0,1)
        
        dm.write()
        ncfile = netCDF4.Dataset(filename, 'r')
        rvnode = opgraph.ReadVariableNode(varname, ncfile, slicetuple=vslice)
        self.print_assertEqual('OperationNode.__call__()', rvnode(), 
                               dm.variables[filename][varname][vslice])
        ncfile.close()
        dm.clear()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()