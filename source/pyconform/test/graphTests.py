"""
DiGraph Unit Tests

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform import graph
from os import linesep

import unittest
import operator as op


#===============================================================================
# General Functions
#===============================================================================
def print_test_message(testname, actual, expected):
    print '{}:'.format(testname)
    print ' - actual   = {}'.format(actual).replace(linesep, ' ')
    print ' - expected = {}'.format(expected).replace(linesep, ' ')
    print


#===============================================================================
# GraphTests
#===============================================================================
class GraphTests(unittest.TestCase):
    """
    Unit tests for the graph.DiGraph class
    """

    def test_init(self):
        testname = 'DiGraph.__init__()'
        G = graph.DiGraph()
        actual = type(G)
        expected = graph.DiGraph
        print_test_message(testname, actual, expected)
        self.assertIsInstance(G, expected,
                              '{} returned unexpected result'.format(testname))

    def test_equal(self):
        testname = 'DiGraph == DiGraph'
        G = graph.DiGraph()
        G.connect(1,2)
        H = graph.DiGraph()
        H.connect(1,2)
        actual = G == H
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_unequal(self):
        testname = 'DiGraph != DiGraph'
        G = graph.DiGraph()
        G.connect(1,2)
        H = graph.DiGraph()
        H.connect(2,1)
        actual = G != H
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_in(self):
        indata = 1
        testname = '{} in DiGraph'.format(indata)
        G = graph.DiGraph()
        G.add(2)
        G.add(3)
        G.add(indata)
        G.add(5)
        actual = indata in G
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_not_in(self):
        indata = 1
        testname = '{} not in DiGraph'.format(indata)
        G = graph.DiGraph()
        G.add(2)
        G.add(3)
        G.add(5)
        actual = indata not in G
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_copy(self):
        testname = 'DiGraph.copy()'
        G = graph.DiGraph()
        G.connect(1, 2)
        G.connect(1, 3)
        actual = G.copy()
        expected = G
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_vertices(self):
        testname = 'DiGraph.vertices()'
        G = graph.DiGraph()
        indata = 1
        G.add(indata)
        actual = G.vertices()
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_edges(self):
        indata = (1,'a')
        testname = 'DiGraph.edges()'
        G = graph.DiGraph()
        G.connect(*indata)
        actual = G.edges()
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_add_hashable(self):
        indata = 1
        testname = 'DiGraph.add({})'.format(indata)
        G = graph.DiGraph()
        G.add(indata)
        actual = G._vertices
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_add_unhashable(self):
        indata = {'a': 1, 'b': 2}
        testname = 'DiGraph.add({})'.format(indata)
        G = graph.DiGraph()
        print_test_message(testname, '???', 'TypeError')
        self.assertRaises(TypeError, G.add, indata)

    def test_remove(self):
        indata = 1
        testname = 'DiGraph.remove({})'.format(indata)
        G = graph.DiGraph()
        G.add(2)
        G.add(indata)
        G.remove(indata)
        actual = G._vertices
        expected = {2}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_update(self):
        G = graph.DiGraph()
        G.connect(1,2)
        G.connect(1,3)
        H = graph.DiGraph()
        H.connect(1,4)
        H.connect(2,5)
        I = G.copy()
        I.update(H)
        actual = I._vertices
        expected = G._vertices.union(H._vertices)
        testname = 'DiGraph.update(DiGraph)._vertices'
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        actual = I._edges
        expected = G._edges.union(H._edges)
        testname = 'DiGraph.update(DiGraph)._edges'
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_union(self):
        G = graph.DiGraph()
        G.connect(1,2)
        G.connect(1,3)
        H = graph.DiGraph()
        H.connect(1,4)
        H.connect(2,5)
        I = G.union(H)
        actual = I._vertices
        expected = G._vertices.union(H._vertices)
        testname = 'DiGraph.update(DiGraph)._vertices'
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        actual = I._edges
        expected = G._edges.union(H._edges)
        testname = 'DiGraph.update(DiGraph)._edges'
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        
    def test_connect(self):
        indata = (1,'a')
        testname = 'DiGraph.connect({}, {})'.format(*indata)
        G = graph.DiGraph()
        G.add(indata[0])
        G.add(indata[1])
        G.connect(*indata)
        actual = G._edges
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_disconnect(self):
        indata = (1,'a')
        testname = 'DiGraph.disconnect({}, {})'.format(*indata)
        G = graph.DiGraph()
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
        testname = 'DiGraph.neighbors_from({})'.format(indata)
        G = graph.DiGraph()
        G.connect(indata, 'a')
        G.connect(indata, 2)
        actual = G.neighbors_from(indata)
        expected = {'a', 2}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_neighbors_to(self):
        indata = 1
        testname = 'DiGraph.neighbors_to({})'.format(indata)
        G = graph.DiGraph()
        G.connect(indata, 'a')
        G.connect(2, indata)
        actual = G.neighbors_to(indata)
        expected = {2}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_bfs(self):
        indata = 1
        testname = 'DiGraph.iter_bfs({})'.format(indata)
        G = graph.DiGraph()
        G.add(0)
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.connect(3, 5)
        G.connect(4, 5)
        actual = [v for v in G.iter_bfs(indata)]
        expected = ([1,2,3,4,5], [1,2,4,3,5])
        print_test_message(testname, actual, expected)
        self.assertIn(actual, expected,
                      '{} returned unexpected result'.format(testname))

    def test_bfs_reversed(self):
        indata = 5
        testname = 'DiGraph.iter_bfs({}, reverse=True)'.format(indata)
        G = graph.DiGraph()
        G.add(0)
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.connect(3, 5)
        G.connect(4, 5)
        actual = [v for v in G.iter_bfs(indata, reverse=True)]
        expected = ([5,3,4,2,1], [5,4,3,2,1])
        print_test_message(testname, actual, expected)
        self.assertIn(actual, expected,
                      '{} returned unexpected result'.format(testname))

    def test_dfs(self):
        indata = 1
        testname = 'DiGraph.iter_dfs({})'.format(indata)
        G = graph.DiGraph()
        G.add(0)
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.connect(3, 5)
        G.connect(4, 5)
        actual = [v for v in G.iter_dfs(indata)]
        expected = ([1,2,3,5,4], [1,2,4,5,3])
        print_test_message(testname, actual, expected)
        self.assertIn(actual, expected,
                      '{} returned unexpected result'.format(testname))

    def test_dfs_reversed(self):
        indata = 5
        testname = 'DiGraph.iter_dfs({}, reverse=True)'.format(indata)
        G = graph.DiGraph()
        G.add(0)
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.connect(3, 5)
        G.connect(4, 5)
        actual = [v for v in G.iter_dfs(indata, reverse=True)]
        expected = ([5,3,2,1,4], [5,4,2,1,3])
        print_test_message(testname, actual, expected)
        self.assertIn(actual, expected,
                      '{} returned unexpected result'.format(testname))

    def test_toposort_acyclic(self):
        testname = 'DiGraph.toposort(acyclic)'
        G = graph.DiGraph()
        G.add(0)
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.connect(3, 5)
        G.connect(4, 5)
        actual = G.toposort()
        expected = ([0,1,2,3,4,5],[1,2,3,4,5,0],
                    [0,1,2,4,3,5],[1,2,4,3,5,0])
        print_test_message(testname, actual, expected)
        self.assertIn(actual, expected,
                      '{} returned unexpected result'.format(testname))
 
    def test_toposort_cyclic(self):
        testname = 'DiGraph.toposort(cyclic)'
        G = graph.DiGraph()
        G.add(0)
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.connect(3, 5)
        G.connect(4, 5)
        G.connect(5, 1)
        actual = G.toposort()
        expected = None
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))
        
    def test_components(self):
        testname = 'DiGraph.components()'
        G = graph.DiGraph()
        G.connect(1,2)
        G.connect(1,3)
        H = graph.DiGraph()
        H.connect(4, 5)
        H.connect(5, 6)
        I = G.union(H)
        actual = I.components()
        expected = {G,H}
        print_test_message(testname, actual, expected)
        for g in actual:
            self.assertTrue(g==G or g==H, 
                            '{} returned unexpected result'.format(testname))
    
    def test_commutable_call_graph(self):
        testname = 'DiGraph Commutable Call-Graph Evaluation'
        G = graph.DiGraph()
        f1 = lambda: 1
        f2 = lambda: 2
        G.add(f1)
        G.add(f2)
        G.add(op.add)
        G.connect(f1, op.add)
        G.connect(f2, op.add) # 1 + 2 = 3
        G.add(op.sub)
        G.connect(op.add, op.mul)
        G.connect(f2, op.mul) # 3 *2 = 6
        def evaluate_G(v):
            return v(*map(evaluate_G, G.neighbors_to(v)))
        actual = evaluate_G(op.mul)        
        expected = 6
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))
               

#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
