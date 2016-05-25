"""
Fundamental Actions for the Action Graph Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import remove
from os.path import exists
from pyconform import actions as acts
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
# ActionTests
#===============================================================================
class MockAction(acts.Action):
    def __init__(self, key, name):
        super(MockAction, self).__init__(key, name)
    def __call__(self):
        super(MockAction, self).__call__()


class ActionTests(unittest.TestCase):
    """
    Unit tests for the operators.Action class
    """
    def setUp(self):
        acts.Action._id_ = 0
    
    def test_abc(self):
        opname = 'xop'
        testname = 'Action.__init__()'
        self.assertRaises(TypeError, acts.Action, opname)
        print_test_message(testname, TypeError, TypeError)

    def test_init(self):
        opname = 'xop'
        testname = 'Mock Action.__init__()'
        O = MockAction(0, opname)
        actual = isinstance(O, acts.Action)
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Could not create mock Action object')

    def test_name(self):
        opname = 'xop'
        testname = 'Mock Action.__init__({!r})'.format(opname)
        O = MockAction(0, opname)
        actual = O.name
        expected = opname
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action name incorrect')

    def test_str(self):
        opname = 'xop'
        testname = 'Mock Action.__str__()'
        O = MockAction('0', opname)
        actual = str(O)
        expected = opname
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action string conversion incorrect')
    
    def test_units_default(self):
        opname = 'xop'
        testname = 'Mock Action.units'
        O = MockAction(0, opname)
        actual = O.units
        expected = None
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action units incorrect')

    def test_units_from_Unit(self):
        opname = 'xop'
        testname = 'Mock Action.units = Unit(m)'
        O = MockAction(0, opname)
        O.units = Unit('m')
        actual = O.units
        expected = Unit('m')
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action units incorrect')

    def test_units_from_str(self):
        opname = 'xop'
        testname = 'Mock Action.units = m'
        O = MockAction(0, opname)
        O.units = 'm'
        actual = O.units
        expected = Unit('m')
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action units incorrect')
    
    def test_units_from_tuple(self):
        opname = 'xop'
        testname = 'Mock Action.units = (days, standard)'
        O = MockAction(0, opname)
        O.units = ('days from 0001-01-01 00:00:00', 'standard')
        actual = O.units
        expected = Unit('days from 0001-01-01 00:00:00', calendar='standard')
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action units incorrect')
    
    def test_units_bad_unit(self):
        opname = 'xop'
        testname = 'Mock Action.units = ncxedajbec'
        O = MockAction(0, opname)
        expected = ValueError
        try:
            O.units = 'ncxedajbec'
        except ValueError:
            actual = ValueError
        else:
            actual = None
            self.assertTrue(False, 'Action units did not fail')
        print_test_message(testname, actual, expected)

    def test_units_bad_calendar(self):
        opname = 'xop'
        testname = 'Mock Action.units = (days, ncxedajbec)'
        O = MockAction(0, opname)
        expected = ValueError
        try:
            O.units = ('days since 0001-01-01 00:00:00', 'ncxedajbec')
        except ValueError:
            actual = ValueError
        else:
            actual = None
            self.assertTrue(False, 'Action units did not fail')
        print_test_message(testname, actual, expected)

    def test_dimensions_default(self):
        opname = 'xop'
        testname = 'Mock Action.dimensions'
        O = MockAction(0, opname)
        actual = O.dimensions
        expected = None
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action dimensions incorrect')

    def test_dimensions_from_tuple(self):
        opname = 'xop'
        testname = 'Mock Action.dimensions = Unit(m)'.format(opname)
        indata = ('t', 'x')
        O = MockAction(0, opname)
        O.dimensions = indata
        actual = O.dimensions
        expected = indata
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action dimensions incorrect')
        
    def test_equal_same(self):
        nm = 'xop'
        testname = ('Mock Action({!r}) == Action('
                    '{!r})').format(nm, nm)
        O1 = MockAction(1, nm)
        O2 = MockAction(1, nm)
        actual = (O1 == O2)
        expected = False
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action equality not correct')

    def test_equal_diff_names(self):
        nm1 = 'xop'
        nm2 = 'yop'
        testname = ('Mock Action({!r}) == Action('
                    '{!r})').format(nm1, nm2)
        O1 = MockAction(1, nm1)
        O2 = MockAction(1, nm2)
        actual = (O1 == O2)
        expected = False
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action equality not correct')    

    def test_equal_diff_keys(self):
        nm = 'xop'
        testname = ('Mock Action(1, {!r}) == Action(2, '
                    '{!r})').format(nm, nm)
        O1 = MockAction(1, nm)
        O2 = MockAction(2, nm)
        actual = (O1 == O2)
        expected = False
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         'Action equality not correct')    


#===============================================================================
# InputSliceReaderTests
#===============================================================================
class InputSliceReaderTests(unittest.TestCase):
    """
    Unit tests for the operators.Reader class
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
        testname = 'Reader.__init__()'
        VSR = acts.Reader(self.ncfile, self.var)
        actual = type(VSR)
        expected = acts.Reader
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_init_filename_failure(self):
        testname = 'Reader.__init__(bad filename)'
        actual = OSError
        expected = OSError
        self.assertRaises(OSError, 
                          acts.Reader, 'badname.nc', self.var)
        print_test_message(testname, actual, expected)

    def test_init_varname_failure(self):
        testname = 'Reader.__init__(bad variable name)'
        actual = OSError
        expected = OSError
        self.assertRaises(OSError, 
                          acts.Reader, self.ncfile, 'badvar')
        print_test_message(testname, actual, expected)

    def test_init_with_slice(self):
        testname = 'Reader.__init__(slice)'
        VSR = acts.Reader(self.ncfile, self.var, self.slice)
        actual = type(VSR)
        expected = acts.Reader
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_call(self):
        testname = 'Reader().__call__()'
        VSR = acts.Reader(self.ncfile, self.var)
        actual = VSR()
        expected = self.vardata
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected,
                               '{} failed'.format(testname))

    def test_call_slice(self):
        testname = 'Reader(slice).__call__()'
        VSR = acts.Reader(self.ncfile, self.var, self.slice)
        actual = VSR()
        expected = self.vardata[self.slice]
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected,
                               '{} failed'.format(testname))

    def test_equal(self):
        testname = 'Reader() == Reader()'
        VSR1 = acts.Reader(self.ncfile, self.var, self.slice)
        VSR2 = acts.Reader(self.ncfile, self.var, self.slice)
        actual = VSR1 == VSR2
        expected = False
        print_test_message(testname, actual, expected)
        self.assertFalse(actual, '{} failed'.format(testname))


#===============================================================================
# FunctionEvaluatorTests
#===============================================================================
class FunctionEvaluatorTests(unittest.TestCase):
    """
    Unit tests for the operators.Evaluator class
    """
    
    def setUp(self):
        self.params = [np.arange(2*3, dtype=np.float64).reshape((2,3)),
                       np.arange(2*3, dtype=np.float64).reshape((2,3)) + 10.]
        
    def tearDown(self):
        pass

    def test_init(self):
        opname = '1'
        testname = 'Evaluator.__init__(function)'
        FE = acts.Evaluator('1', opname, lambda: 1)
        actual = type(FE)
        expected = acts.Evaluator
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_init_fail(self):
        opname = 'int(1)'
        testname = 'Evaluator.__init__(non-function)'
        self.assertRaises(TypeError, acts.Evaluator, 1, opname, 1)
        actual = TypeError
        expected = TypeError
        print_test_message(testname, actual, expected)

    def test_unity(self):
        opname = 'identity'
        testname = 'Evaluator(lambda x: x).__call__(x)'
        FE = acts.Evaluator('I', opname, lambda x: x)
        actual = FE(self.params[0])
        expected = self.params[0]
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))
        
    def test_add(self):
        opname = 'add(a,b)'
        testname = 'Evaluator(add).__call__(a, b)'
        FE = acts.Evaluator('+', opname, operator.add)
        actual = FE(*self.params)
        expected = operator.add(*self.params)
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))

    def test_add_constant_1st(self):
        opname = 'add(1,a)'
        testname = 'Evaluator(add, 1).__call__(a)'
        FE = acts.Evaluator('+', opname, operator.add, signature=[1])
        actual = FE(self.params[0])
        expected = operator.add(1, self.params[0])
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))

    def test_add_constant_2nd(self):
        opname = 'add(a,2)'
        testname = 'Evaluator(add, None, 2).__call__(a)'
        FE = acts.Evaluator('+', opname, operator.add, signature=[None, 2])
        actual = FE(self.params[0])
        expected = operator.add(self.params[0], 2)
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))

    def test_sub(self):
        opname = 'sub(a,b)'
        testname = 'Evaluator(sub).__call__(a, b)'
        FE = acts.Evaluator('-', opname, operator.sub)
        actual = FE(*self.params)
        expected = operator.sub(*self.params)
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected, '{} failed'.format(testname))

    def test_equal(self):
        opname = 'sub(a,b)'
        testname = 'Evaluator() == Evaluator()'
        FE1 = acts.Evaluator('-', opname, operator.sub)
        FE2 = acts.Evaluator('-', opname, operator.sub)
        actual = FE1 == FE2
        expected = False
        print_test_message(testname, actual, expected)
        npt.assert_array_equal(actual, expected,
                               '{} failed'.format(testname))


#===============================================================================
# OutputSliceHandleTests
#===============================================================================
class OutputSliceHandleTests(unittest.TestCase):
    """
    Unit tests for the operators.Handle class
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
        testname = 'Handle.__init__()'
        OSH = acts.Handle('x')
        actual = type(OSH)
        expected = acts.Handle
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_min_ok(self):
        indata = 1.0
        testname = 'Handle({})'.format(indata)
        OSH = acts.Handle('x', minimum=0.0)
        actual = OSH(indata)
        expected = indata
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        
    def test_min_warn(self):
        indata = -1.0
        testname = 'Handle({})'.format(indata)
        OSH = acts.Handle('x', minimum=0.0)
        actual = OSH(indata)
        expected = indata
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_max_ok(self):
        indata = 1.0
        testname = 'Handle({})'.format(indata)
        OSH = acts.Handle('x', maximum=10.0)
        actual = OSH(indata)
        expected = indata
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))
        
    def test_max_warn(self):
        indata = 11.0
        testname = 'Handle({})'.format(indata)
        OSH = acts.Handle('x', maximum=10.0)
        actual = OSH(indata)
        expected = indata
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===============================================================================
# Command-Line Action
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
