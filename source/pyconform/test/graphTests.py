"""
DirGraph Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import graph
from os import linesep

import unittest


#===============================================================================
# General Functions
#===============================================================================
def print_test_message(testname, actual, expected):
    indent = ' ' * len(testname)
    print '{} - actual   = {}'.format(testname, actual).replace(linesep, ' ')
    print '{} - expected = {}'.format(indent, expected).replace(linesep, ' ')
    print


#===============================================================================
# GraphTests
#===============================================================================
class GraphTests(unittest.TestCase):
    """
    Unit tests for the graph.DirGraph class
    """

    def test_init(self):
        testname = 'DirGraph.__init__()'
        G = graph.DirGraph()
        actual = type(G)
        expected = graph.DirGraph
        print_test_message(testname, actual, expected)
        self.assertIsInstance(G, expected,
                              '{} returned unexpected result'.format(testname))

    def test_add_hashable(self):
        indata = 1
        testname = 'DirGraph.add({})'.format(indata)
        G = graph.DirGraph()
        G.add(indata)
        actual = G._vertices
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_vertices(self):
        testname = 'DirGraph.vertices()'
        G = graph.DirGraph()
        indata = 1
        G.add(indata)
        actual = G.vertices()
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        
    def test_add_unhashable(self):
        indata = {'a': 1, 'b': 2}
        testname = 'DirGraph.add({})'.format(indata)
        G = graph.DirGraph()
        print_test_message(testname, '???', 'TypeError')
        self.assertRaises(TypeError, G.add, indata)

    def test_remove(self):
        indata = 1
        testname = 'DirGraph.remove({})'.format(indata)
        G = graph.DirGraph()
        G.add(2)
        G.add(indata)
        G.remove(indata)
        actual = G._vertices
        expected = {2}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        
    def test_connect(self):
        indata = (1,'a')
        testname = 'DirGraph.connect({}, {})'.format(*indata)
        G = graph.DirGraph()
        G.add(indata[0])
        G.add(indata[1])
        G.connect(*indata)
        actual = G._edges
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_edges(self):
        indata = (1,'a')
        testname = 'DirGraph.edges()'
        G = graph.DirGraph()
        G.connect(*indata)
        actual = G.edges()
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_disconnect(self):
        indata = (1,'a')
        testname = 'DirGraph.disconnect({}, {})'.format(*indata)
        G = graph.DirGraph()
        G.connect(*indata)
        G.connect(3,5)
        G.disconnect(*indata)
        actual = G.edges()
        expected = {(3,5)}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_neighbors_from(self):
        indata = 1
        testname = 'DirGraph.neighbors_from({})'.format(indata)
        G = graph.DirGraph()
        G.connect(indata, 'a')
        G.connect(indata, 2)
        actual = G.neighbors_from(indata)
        expected = {'a', 2}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_neighbors_to(self):
        indata = 1
        testname = 'DirGraph.neighbors_to({})'.format(indata)
        G = graph.DirGraph()
        G.connect(indata, 'a')
        G.connect(2, indata)
        actual = G.neighbors_to(indata)
        expected = {2}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))



#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
