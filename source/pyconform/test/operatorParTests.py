"""
Fundamental Operators for the Operation Graph Unit Tests - Parallel

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import operators as ops
from os import linesep
from mpi4py import MPI

import numpy as np
import unittest


#===============================================================================
# General Functions
#===============================================================================
def print_test_message(testname, actual, expected):
    rank = MPI.COMM_WORLD.Get_rank()
    size = MPI.COMM_WORLD.Get_size()
    msg = '[{}/{}] {}:{}'.format(rank, size, testname, linesep)
    msg += ' - actual   = {}'.format(actual).replace(linesep, ' ') + linesep
    msg += ' - expected = {}'.format(expected).replace(linesep, ' ') + linesep
    print msg


#===============================================================================
# MPISendRecvTests
#===============================================================================
class MPISendRecvTests(unittest.TestCase):
    """
    Unit tests for the operators.SendOperator and operators.RecvOperator classes
    """
    
    def setUp(self):
        self.params = [np.arange(2*3, dtype=np.float64).reshape((2,3)),
                       np.arange(2*3, dtype=np.float64).reshape((2,3)) + 10.]
        
    def tearDown(self):
        pass

    def test_sendop_init(self):
        testname = 'SendOperator.__init__(1)'
        SO = ops.SendOperator(1)
        actual = type(SO)
        expected = ops.SendOperator
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_recvop_init(self):
        testname = 'RecvOperator.__init__(1)'
        RO = ops.RecvOperator(1)
        actual = type(RO)
        expected = ops.RecvOperator
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected, '{} failed'.format(testname))

    def test_send_recv(self):
        testname = 'SendOperator() -> RecvOperator()'
        data = np.arange(0,10)
        if MPI.COMM_WORLD.Get_rank() == 0:
            op = ops.SendOperator(dest=1)
            actual = op(data)
            expected = None
            print_test_message(testname, actual, expected)
            self.assertEqual(actual, expected, '{} failed'.format(testname))
        elif MPI.COMM_WORLD.Get_rank() == 1:
            op = ops.RecvOperator(source=0)
            actual = op()
            expected = data
            print_test_message(testname, actual, expected)
            np.testing.assert_equal(actual, expected, '{} failed'.format(testname))
        else:
            actual = None
            expected = None
            print_test_message(testname, actual, expected)
            self.assertEqual(actual, expected, '{} failed'.format(testname))


#===============================================================================
# Command-Line Operation - For parallel tests only!
#===============================================================================
if __name__ == "__main__":
    hline = '=' * 70
    if MPI.COMM_WORLD.Get_rank() == 0:
        print hline
        print 'STANDARD OUTPUT FROM ALL TESTS:'
        print hline
    MPI.COMM_WORLD.Barrier()

    from cStringIO import StringIO
    mystream = StringIO()
    tests = unittest.TestLoader().loadTestsFromTestCase(MPISendRecvTests)
    unittest.TextTestRunner(stream=mystream).run(tests)
    MPI.COMM_WORLD.Barrier()

    results = MPI.COMM_WORLD.gather(mystream.getvalue())
    if MPI.COMM_WORLD.Get_rank() == 0:
        for rank, result in enumerate(results):
            print hline
            print 'TESTS RESULTS FOR RANK ' + str(rank) + ':'
            print hline
            print str(result)
