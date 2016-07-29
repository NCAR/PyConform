"""
Indexing Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.indexing import index_str, join
from testutils import print_test_message

import unittest
import numpy


#===================================================================================================
# IndexStrTests
#===================================================================================================
class IndexStrTests(unittest.TestCase):
    """
    Unit tests for the indexing.index_str function
    """

    def test_index_str_int(self):
        indata = 3
        testname = 'index_str({!r})'.format(indata)
        actual = index_str(indata)
        expected = str(indata)
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_index_str_slice(self):
        indata = slice(1,2,3)
        testname = 'index_str({!r})'.format(indata)
        actual = index_str(indata)
        expected = '1:2:3'
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_index_str_tuple(self):
        indata = (4, slice(3,1,-4))
        testname = 'index_str({!r})'.format(indata)
        actual = index_str(indata)
        expected = '4, 3:1:-4'
        print_test_message(testname, indata=indata, actual=actual, expected=expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))


#===================================================================================================
# JoinTests
#===================================================================================================
class JoinTests(unittest.TestCase):
    """
    Unit tests for the indexing.join function
    """
    
    def setUp(self):
        indices = [None, -100, -10, -1, 0, 1, 10, 100]
        steps = [None, -100, -2, -1, 1, 2, 100]
        self.slices = [slice(i,j,k) for i in indices for j in indices for k in steps]

    def test_join_20_slice_slice(self):
        indata = 20
        A = numpy.arange(indata)
        results = []
        for s1 in self.slices:
            for s2 in self.slices:
                result = numpy.array_equal(A[s1][s2], A[join((indata,), s1, s2)])
                print 'join(({},), {}, {}): {}'.format(indata, s1, s2, result)
                results.append(result)
        self.assertTrue(all(results), 'join(20, slice, slice) failed')

#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
