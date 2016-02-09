"""
Fundamental Operators for the Operation Graph Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import remove
from os.path import exists
from pyconform import operators as ops
from os import linesep
from cf_units import Unit

import operator
import numpy as np
import numpy.testing as npt
import netCDF4 as nc
import unittest


#===============================================================================
# General Functions
#===============================================================================
def print_test_message(testname, actual, expected):
    print '{}:'.format(testname)
    print ' - actual   = {}'.format(actual).replace(linesep, ' ')
    print ' - expected = {}'.format(expected).replace(linesep, ' ')
    print


#===============================================================================
# OperatorTests
#===============================================================================
class MockOp(ops.Operator):
    def __init__(self, name, units=Unit(1)):
        super(MockOp, self).__init__(name)
    def units(self):
        super(MockOp, self).units()
    def __call__(self):
        super(MockOp, self).__call__()

class OperatorTests(unittest.TestCase):
    """
    Unit tests for the operators.Operator class
    """
    def setUp(self):
        ops.Operator._id_ = 0
    
    def test_abc(self):
        opname = 'xop'
        testname = 'Operator.__init__()'
        self.assertRaises(TypeError, ops.Operator, opname)
        print_test_message(testname, TypeError, TypeError)

    def test_init(self):
        opname = 'xop'
        testname = 'Mock Operator.__init__()'
        O = MockOp(opname)
        actual = isinstance(O, ops.Operator)
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Could not create mock Operator object')

    def test_name(self):
        opname = 'xop'
        testname = 'Mock Operator.__init__({!r})'.format(opname)
        O = MockOp(opname)
        actual = O.name()
        expected = opname
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Operator name incorrect')

    def test_str(self):
        opname = 'xop'
        testname = 'Mock Operator.__str__()'.format(opname)
        O = MockOp(opname)
        actual = str(O)
        expected = opname
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Operator string conversion incorrect')
    
    def test_register_same(self):
        opname = 'abc'
        testname = 'Mock Operator.register({!r})'.format(opname)
        O1 = MockOp.register(opname)
        O2 = MockOp.register(opname)
        print_test_message(testname, id(O1), id(O2))
        self.assertEqual(id(O1), id(O2),
                         'Identical operators not registered properly')

    def test_register_different(self):
        opname = 'abc'
        testname = 'Mock Operator.register({!r}, units)'.format(opname)
        O1 = MockOp.register(opname, units=Unit('m'))
        O2 = MockOp.register(opname)
        print_test_message(testname, id(O1), id(O2))
        self.assertNotEqual(id(O1), id(O2),
                            'Operators not registered properly')
        
    def test_units(self):
        opname = 'xop'
        testname = 'Mock Operator.units({!r})'.format(opname)
        O = MockOp(opname)
        actual = O.units()
        expected = None
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Operator name incorrect')



#===============================================================================
# VariableSliceReaderTests
#===============================================================================
class VariableSliceReaderTests(unittest.TestCase):
    """
    Unit tests for the operators.VariableSliceReader class
    """
    
    def setUp(self):
        self.ncfile = 'vslicetest.nc'
        self.shape = (2,4)
        self.size = reduce(lambda x,y: x*y, self.shape, 1)
        dataset = nc.Dataset(self.ncfile, 'w')
        dataset.createDimension('x', self.shape[0])
        dataset.createDimension('t')
        dataset.createVariable('x', 'd', ('x',))
        dataset.variables['x'][:] = np.arange(self.shape[0])
        dataset.createVariable('t', 'd', ('t',))
        dataset.variables['t'][:] = np.arange(self.shape[1])
        self.var = 'v'
        dataset.createVariable(self.var, 'd', ('x', 't'))
        self.vardata = np.arange(self.size, dtype=np.float64).reshape(self.shape)
        dataset.variables[self.var][:] = self.vardata
        dataset.close()
        self.slice = (slice(0, 1), slice(1, 3))
        
    def tearDown(self):
        if exists(self.ncfile):
            remove(self.ncfile)

    def test_init(self):
        testname = 'VariableSliceReader.__init__()'
        VSR = ops.VariableSliceReader(self.ncfile, self.var)
        actual = type(VSR)
        expected = ops.VariableSliceReader
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_init_filename_failure(self):
        testname = 'VariableSliceReader.__init__(bad filename)'
        actual = OSError
        expected = OSError
        self.assertRaises(OSError, 
                          ops.VariableSliceReader, 'badname.nc', self.var)
        print_test_message(testname, actual, expected)

    def test_init_varname_failure(self):
        testname = 'VariableSliceReader.__init__(bad variable name)'
        actual = OSError
        expected = OSError
        self.assertRaises(OSError, 
                          ops.VariableSliceReader, self.ncfile, 'badvar')
        print_test_message(testname, actual, expected)

    def test_init_with_slice(self):
        testname = 'VariableSliceReader.__init__(slice)'
        VSR = ops.VariableSliceReader(self.ncfile, self.var, self.slice)
        actual = type(VSR)
        expected = ops.VariableSliceReader
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_call(self):
        testname = 'VariableSliceReader().__call__()'
        VSR = ops.VariableSliceReader(self.ncfile, self.var)
        actual = VSR()
        expected = self.vardata
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected,
                               '{} failed'.format(testname))

    def test_call_slice(self):
        testname = 'VariableSliceReader(slice).__call__()'
        VSR = ops.VariableSliceReader(self.ncfile, self.var, self.slice)
        actual = VSR()
        expected = self.vardata[self.slice]
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected,
                               '{} failed'.format(testname))


#===============================================================================
# FunctionEvaluatorTests
#===============================================================================
class FunctionEvaluatorTests(unittest.TestCase):
    """
    Unit tests for the operators.FunctionEvaluator class
    """
    
    def setUp(self):
        self.params = [np.arange(2*3, dtype=np.float64).reshape((2,3)),
                       np.arange(2*3, dtype=np.float64).reshape((2,3)) + 10.]
        
    def tearDown(self):
        pass

    def test_init(self):
        opname = '1'
        testname = 'FunctionEvaluator.__init__(function)'
        FE = ops.FunctionEvaluator(opname, lambda: 1)
        actual = type(FE)
        expected = ops.FunctionEvaluator
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_init_fail(self):
        opname = 'int(1)'
        testname = 'FunctionEvaluator.__init__(non-function)'
        self.assertRaises(TypeError, ops.FunctionEvaluator, opname, 1)
        actual = TypeError
        expected = TypeError
        print_test_message(testname, actual, expected)

    def test_unity(self):
        opname = 'identity'
        testname = 'FunctionEvaluator(lambda x: x).__call__(x)'
        FE = ops.FunctionEvaluator(opname, lambda x: x)
        actual = FE(self.params[0])
        expected = self.params[0]
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))
        
    def test_add(self):
        opname = 'add(a,b)'
        testname = 'FunctionEvaluator(add).__call__(a, b)'
        FE = ops.FunctionEvaluator(opname, operator.add)
        actual = FE(*self.params)
        expected = operator.add(*self.params)
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))

    def test_add_constant_1st(self):
        opname = 'add(1,a)'
        testname = 'FunctionEvaluator(add, 1).__call__(a)'
        FE = ops.FunctionEvaluator(opname, operator.add, args=[1])
        actual = FE(self.params[0])
        expected = operator.add(1, self.params[0])
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))

    def test_add_constant_2nd(self):
        opname = 'add(a,2)'
        testname = 'FunctionEvaluator(add, None, 2).__call__(a)'
        FE = ops.FunctionEvaluator(opname, operator.add, args=[None, 2])
        actual = FE(self.params[0])
        expected = operator.add(self.params[0], 2)
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))

    def test_sub(self):
        opname = 'sub(a,b)'
        testname = 'FunctionEvaluator(sub).__call__(a, b)'
        FE = ops.FunctionEvaluator(opname, operator.sub)
        actual = FE(*self.params)
        expected = operator.sub(*self.params)
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
