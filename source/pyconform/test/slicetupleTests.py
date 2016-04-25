"""
DiGraph Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import slicetuple
from os import linesep

import unittest


#===============================================================================
# General Functions
#===============================================================================
def print_test_message(testname, indata=None, actual=None, expected=None):
    print '{}:'.format(testname)
    print ' - indata   = {0}'.format(indata).replace(linesep, ' ')
    print ' - actual   = {0}'.format(actual).replace(linesep, ' ')
    print ' - expected = {0}'.format(expected).replace(linesep, ' ')
    print


#===============================================================================
# SliceTupleTests
#===============================================================================
class SliceTupleTests(unittest.TestCase):
    """
    Unit tests for the slicetuple.SliceTuple class
    """

    def test_init_default(self):
        testname = 'SliceTuple.__init__()'
        s = slicetuple.SliceTuple()
        actual = type(s)
        expected = slicetuple.SliceTuple
        print_test_message(testname,
                           actual=actual, expected=expected)
        self.assertIsInstance(s, expected,
                              '{0} returned unexpected result'.format(testname))

    def test_init_int(self):
        indata = 1
        testname = 'SliceTuple.__init__({0})'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = type(s)
        expected = slicetuple.SliceTuple
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertIsInstance(s, expected,
                              '{0} returned unexpected result'.format(testname))

    def test_init_slice(self):
        indata = slice(1,4)
        testname = 'SliceTuple.__init__({0})'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = type(s)
        expected = slicetuple.SliceTuple
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertIsInstance(s, expected,
                              '{0} returned unexpected result'.format(testname))

    def test_init_tuple(self):
        indata = (1, slice(2,5))
        testname = 'SliceTuple.__init__({0})'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = type(s)
        expected = slicetuple.SliceTuple
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertIsInstance(s, expected,
                              '{0} returned unexpected result'.format(testname))

    def test_str_default(self):
        testname = 'str(SliceTuple())'
        s = slicetuple.SliceTuple()
        actual = str(s)
        expected = '::'
        print_test_message(testname,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))
        
    def test_str_int(self):
        indata = 1
        testname = 'str(SliceTuple({0}))'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = str(s)
        expected = str(indata)
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))

    def test_str_slice_int(self):
        indata = slice(1)
        testname = 'str(SliceTuple({0}))'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = str(s)
        expected = ':1:'
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))

    def test_str_slice_none_int(self):
        indata = slice(None,4)
        testname = 'str(SliceTuple({0}))'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = str(s)
        expected = ':4:'
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))
        
    def test_str_slice_int_int(self):
        indata = slice(1,4)
        testname = 'str(SliceTuple({0}))'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = str(s)
        expected = '1:4:'
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))
        
    def test_str_slice_int_int_int(self):
        indata = slice(1,4,2)
        testname = 'str(SliceTuple.({0}))'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = str(s)
        expected = '1:4:2'
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))

    def test_str_tuple(self):
        indata = (1, slice(2,5))
        testname = 'str(SliceTuple({0}))'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = str(s)
        expected = '(1,2:5:)'
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))

    def test_index_default(self):
        testname = 'SliceTuple().index'
        s = slicetuple.SliceTuple()
        actual = s.index
        expected = slice(None)
        print_test_message(testname,
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))

    def test_index_int(self):
        indata = 1
        testname = 'SliceTuple({0}).index'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = s.index
        expected = indata
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))

    def test_index_slice(self):
        indata = slice(1,4,2)
        testname = 'SliceTuple({0}).index'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = s.index
        expected = indata
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))

    def test_index_tuple(self):
        indata = (7, slice(1,4,2), 3)
        testname = 'SliceTuple({0}).index'.format(indata)
        s = slicetuple.SliceTuple(indata)
        actual = s.index
        expected = indata
        print_test_message(testname, indata=indata, 
                           actual=actual, expected=expected)
        self.assertEqual(actual, expected,
                         '{0} returned unexpected result'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
