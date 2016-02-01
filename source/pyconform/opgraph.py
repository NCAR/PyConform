"""
Operation Graph Class

This module contains the OperationGraph class to be used with the Operator 
classes and the DiGraph class to build an "operator graph" or "operation graph."
This graph walks through the graph performing the Operator functions connected
by the DiGraph object.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from copy import copy
from mpi4py import MPI
from graph import DiGraph

import operators


#===============================================================================
# OperationGraph
#===============================================================================
class OperationGraph(DiGraph):
    """
    Operation Graph
    
    A directed graph defining a connected set of operations whose results
    are used as input to adjacent operators.
    """

    def __init__(self):
        """
        Initialize
        """
        self._root = None
    
    @classmethod
    def from_tree(cls, treerep):
        """
        Initialize from a tree (nested-tuple) representation
        
        Parameters:
            treerep (tuple): A tuple, or nested tuple, containing Operators
        """
        def append_tree_to_graph(opgraph, lastop, treerep):
            if not isinstance(opgraph, OperationGraph):
                raise TypeError('Can add tree element only to OperationGraph')
            if lastop and not isinstance(lastop, operators.Operator):
                raise TypeError('Vertices in OperationGraphs must be Operators')
            if not isinstance(treerep, tuple):
                raise TypeError('Tree representation must be a tuple')
            for elem in treerep:
                if isinstance(elem, operators.Operator):
                    if lastop is None:
                        opgraph.add(elem)
                        opgraph._root = elem
                    else:
                        opgraph.connect(elem, lastop)
                elif isinstance(elem, tuple):
                    opgraph.connect(elem[0], lastop)
                    append_tree_to_graph(opgraph, elem[0], elem[1:])
        opgraph = cls()
        append_tree_to_graph(opgraph, None, treerep)
        return opgraph
    
    def add(self, vertex):
        """
        Add a vertex to the graph
        
        Parameters:
            vertex (Operator): An Operator vertex to be added to the graph
        """
        if not isinstance(vertex, operators.Operator):
            raise TypeError('OperationGraph must consist only of Operators')
        DiGraph.add(self, vertex)

    def __call__(self):
        """
        Perform the OperationGraph operations
        """
        def evaluate_from(op):
            return op(*map(evaluate_from, self.neighbors_to(op)))
        return evaluate_from(self._root)
    
    def iter_bfs(self):
        super(OperationGraph, self).iter_bfs(self._root, reverse=True)

    def iter_dfs(self):
        super(OperationGraph, self).iter_dfs(self._root, reverse=True)

    def distribute(self, ranks=[]):
        """
        Distribute the graph operations to other ranks
        
        Parameters:
            ranks (list): A list of worker rank numbers to use for distribution
        """
        if not isinstance(ranks, (list, tuple)):
            raise TypeError('Ranks must be specified as a list of integers')
        if not all([isinstance(rank, int) for rank in ranks]):
            raise TypeError('Ranks must be specified as a list of integers')

        pass
            