"""
DiGraph Unit Tests

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from copy import deepcopy
from pyconform import graphs2 as graphs
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
    Unit tests for the graphs.DiGraph class
    """

    def test_init(self):
        testname = 'DiGraph.__init__()'
        G = graphs.DiGraph()
        actual = type(G)
        expected = graphs.DiGraph
        print_test_message(testname, actual, expected)
        self.assertIsInstance(G, expected,
                              '{} returned unexpected result'.format(testname))

    def test_equal(self):
        testname = 'DiGraph == DiGraph'
        G = graphs.DiGraph()
        G.connect(1,2)
        H = graphs.DiGraph()
        H.connect(1,2)
        actual = G == H
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_unequal(self):
        testname = 'DiGraph != DiGraph'
        G = graphs.DiGraph()
        G.connect(1,2)
        H = graphs.DiGraph()
        H.connect(2,1)
        actual = G != H
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                        '{} returned unexpected result'.format(testname))

    def test_in(self):
        indata = 1
        testname = '{} in DiGraph'.format(indata)
        G = graphs.DiGraph()
        G.add(2)
        G.add(3)
        G.add(indata)
        G.add(5)
        G.connect(4, 5)
        actual = indata in G
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_not_in(self):
        indata = 1
        testname = '{} not in DiGraph'.format(indata)
        G = graphs.DiGraph()
        G.add(2)
        G.add(3)
        G.connect(4, 5)
        actual = indata not in G
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_len(self):
        testname = 'len(DiGraph)'
        G = graphs.DiGraph()
        G.add(2)
        G.add(3)
        G.add(5)
        actual = len(G)
        expected = 3
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_str(self):
        G = graphs.DiGraph()
        G.add(1)
        G.connect(2,3)
        G.connect(3,4)
        G.connect(2,5)
        print G

    def test_clear(self):
        G = graphs.DiGraph()
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.clear()
        testname = 'DiGraph.clear() vertices'
        actual = G.vertices
        expected = []
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))
        testname = 'DiGraph.clear() - edges'
        actual = G.edges
        expected = []
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_vertices(self):
        testname = 'DiGraph.vertices()'
        G = graphs.DiGraph()
        indata = 1
        G.add(indata)
        actual = G.vertices
        expected = set([indata])
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_edges(self):
        indata = (1,'a')
        testname = 'DiGraph.edges()'
        G = graphs.DiGraph()
        G.connect(*indata)
        actual = G.edges
        expected = [indata]
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_add_hashable(self):
        indata = 1
        testname = 'DiGraph.add({})'.format(indata)
        G = graphs.DiGraph()
        G.add(indata)
        actual = G.vertices
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_add_unhashable(self):
        indata = {'a': 1, 'b': 2}
        testname = 'DiGraph.add({})'.format(indata)
        G = graphs.DiGraph()
        print_test_message(testname, '???', 'TypeError')
        self.assertRaises(TypeError, G.add, indata)

    def test_remove(self):
        indata = 1
        testname = 'DiGraph.remove({})'.format(indata)
        G = graphs.DiGraph()
        G.add(2)
        G.add(indata)
        G.remove(indata)
        actual = G.vertices
        expected = {2}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_update(self):
        G = graphs.DiGraph()
        G.connect(1,2)
        G.connect(1,3)
        H = graphs.DiGraph()
        H.connect(1,4)
        H.connect(2,5)
        I = deepcopy(G)
        I.update(H)
        actual = I.vertices
        expected = [v for v in G.vertices]
        expected.extend(v for v in H.vertices if v not in G.vertices)
        testname = 'DiGraph.update(DiGraph).vertices'
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        actual = I.edges
        expected = set(G.edges)
        expected.update(H.edges)
        testname = 'DiGraph.update(DiGraph).edges'
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_union(self):
        G = graphs.DiGraph()
        G.connect(1,2)
        G.connect(1,3)
        H = graphs.DiGraph()
        H.connect(1,4)
        H.connect(2,5)
        I = G.union(H)
        actual = I.vertices
        expected = [v for v in G.vertices]
        expected.extend(v for v in H.vertices if v not in G.vertices)
        testname = 'DiGraph.union(DiGraph).vertices'
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        actual = I.edges
        expected = set(G.edges)
        expected.update(H.edges)
        testname = 'DiGraph.union(DiGraph).edges'
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))
        
    def test_connect(self):
        indata = (1,'a')
        testname = 'DiGraph.connect({}, {})'.format(*indata)
        G = graphs.DiGraph()
        G.add(indata[0])
        G.add(indata[1])
        G.connect(*indata)
        actual = G.edges
        expected = {indata}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_disconnect(self):
        indata = (1,'a')
        testname = 'DiGraph.disconnect({}, {})'.format(*indata)
        G = graphs.DiGraph()
        G.connect(*indata)
        G.connect(3,5)
        G.disconnect(*indata)
        actual = G.edges
        expected = {(3,5)}
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_neighbors_from(self):
        indata = 1
        testname = 'DiGraph.neighbors_from({})'.format(indata)
        G = graphs.DiGraph()
        G.connect(indata, 'a')
        G.connect(indata, 2)
        actual = G.neighbors_from(indata)
        expected = ['a', 2]
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_neighbors_to(self):
        indata = 1
        testname = 'DiGraph.neighbors_to({})'.format(indata)
        G = graphs.DiGraph()
        G.connect(indata, 'a')
        G.connect(2, indata)
        actual = G.neighbors_to(indata)
        expected = [2]
        print_test_message(testname, actual, expected)
        self.assertItemsEqual(actual, expected,
                              '{} returned unexpected result'.format(testname))

    def test_sinks(self):
        testname = 'DiGraph.sinks()'
        G = graphs.DiGraph()
        G.connect(1, 3)
        G.connect(2, 3)
        G.connect(3, 4)
        G.connect(3, 5)
        actual = G.sinks()
        expected = set([4, 5])
        print_test_message(testname, actual, expected)
        self.assertSetEqual(actual, expected,
                            '{} returned unexpected result'.format(testname))

    def test_sources(self):
        testname = 'DiGraph.sources()'
        G = graphs.DiGraph()
        G.connect(1, 3)
        G.connect(2, 3)
        G.connect(3, 4)
        G.connect(3, 5)
        actual = G.sources()
        expected = set([1, 2])
        print_test_message(testname, actual, expected)
        self.assertSetEqual(actual, expected,
                            '{} returned unexpected result'.format(testname))
                
    def test_bfs(self):
        indata = 1
        testname = 'DiGraph.iter_bfs({})'.format(indata)
        G = graphs.DiGraph()
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
        G = graphs.DiGraph()
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
        G = graphs.DiGraph()
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
        G = graphs.DiGraph()
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
        G = graphs.DiGraph()
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
        G = graphs.DiGraph()
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

    def test_is_not_cyclic(self):
        testname = 'DiGraph.is_cyclic(acyclic)'
        G = graphs.DiGraph()
        G.add(0)
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.connect(3, 5)
        G.connect(4, 5)
        actual = G.is_cyclic()
        expected = False
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))
 
    def test_is_cyclic(self):
        testname = 'DiGraph.is_cyclic(cyclic)'
        G = graphs.DiGraph()
        G.add(0)
        G.connect(1, 2)
        G.connect(2, 3)
        G.connect(2, 4)
        G.connect(3, 5)
        G.connect(4, 5)
        G.connect(5, 1)
        actual = G.is_cyclic()
        expected = True
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))
        
    def test_components(self):
        testname = 'DiGraph.components()'
        G = graphs.DiGraph()
        G.connect(1,2)
        G.connect(1,3)
        H = graphs.DiGraph()
        H.connect(4, 5)
        H.connect(5, 6)
        I = G.union(H)
        actual = I.components()
        expected = [G,H]
        print_test_message(testname, actual, expected)
        for g in actual:
            self.assertTrue(g==G or g==H, 
                            '{} returned unexpected result'.format(testname))
    
    def test_commutative_call_graph(self):
        testname = 'DiGraph Commutative Call-Graph Evaluation'
        G = graphs.DiGraph()
        f1 = lambda: 1
        f2 = lambda: 2
        G.add(f1)
        G.add(f2)
        G.add(op.add)
        G.connect(f1, op.add)
        G.connect(f2, op.add) # 1 + 2 = 3
        G.add(op.mul)
        G.connect(op.add, op.mul)
        G.connect(f2, op.mul) # 3 * 2 = 6
        def evaluate_G(v):
            return v(*map(evaluate_G, G.neighbors_to(v)))
        actual = evaluate_G(op.mul)        
        expected = 6
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_noncommutative_call_graph(self):
        testname = 'DiGraph Non-Commutative Call-Graph Evaluation'
        G = graphs.DiGraph()
        f6 = lambda: 6
        f2 = lambda: 2
        G.add(f6)
        G.add(f2)
        G.add(op.div)
        G.connect(f6, op.div)
        G.connect(f2, op.div) # 6 / 2 = 3
        G.add(op.sub)
        G.connect(op.div, op.sub)
        G.connect(f2, op.sub) # 3 - 2 = 1
        def evaluate_G(v):
            return v(*map(evaluate_G, G.neighbors_to(v)))
        actual = evaluate_G(op.sub)        
        expected = 1
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))

    def test_incremented_call_graph(self):
        testname = 'DiGraph Incremented Call-Graph Evaluation'
        G = graphs.DiGraph()
        f1 = lambda: 1
        finc = lambda x: x+1
        G.connect((0, f1), (1, finc)) # 1 + 1 = 2
        G.connect((1, finc), (2, finc)) # 2 + 1 = 3
        G.connect((2, finc), (3, finc)) # 3 + 1 = 4
        def evaluate_G(v):
            return v[1](*map(evaluate_G, G.neighbors_to(v)))
        actual = evaluate_G((3, finc))        
        expected = 4
        print_test_message(testname, actual, expected)
        self.assertEqual(actual, expected,
                         '{} returned unexpected result'.format(testname))


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
