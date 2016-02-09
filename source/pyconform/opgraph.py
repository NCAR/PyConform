"""
Operation Graph Class

This module contains the OperationGraph class to be used with the Operator 
classes and the DiGraph class to build an "operator graph" or "operation graph."
This graph walks through the graph performing the Operator functions connected
by the DiGraph object.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from graph import DiGraph
from operators import Operator


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
        super(OperationGraph, self).__init__()

    def add(self, vertex):
        """
        Add a vertex to the graph
        
        Parameters:
            vertex (Operator): An Operator vertex to be added to the graph
        """
        if not isinstance(vertex, Operator):
            raise TypeError('OperationGraph must consist only of Operators')
        DiGraph.add(self, vertex)

    def __call__(self, root):
        """
        Perform the OperationGraph operations
        
        Parameters:
            root (Operator): The root of the operation, from which data is
                requested from the operation graph
        """
        def evaluate_from(op):
            return op(*map(evaluate_from, self.neighbors_to(op)))
        return evaluate_from(self._root)
    
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
            