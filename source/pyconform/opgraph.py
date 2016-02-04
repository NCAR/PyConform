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
from parsing import DefitionParser
from dataset import InputDataset
from itertools import cycle
from cf_units import Unit

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

    def __init__(self, definitions={}, inputdataset=InputDataset()):
        """
        Initialize
        
        Parameters:
            definitions (dict): Dictionary of variable names and definitions
            inputdataset (InputDataset): The input dataset into which the 
                definition variable references are found 
        """
        super(OperationGraph, self).__init__()

        # Type Checking Definitions Dicitonary
        if not isinstance(definitions, dict):
            err_msg = 'Variable definitions must be of dict type'
            raise TypeError(err_msg)
        self._defs = definitions
        
        # Type Checking Input Dataset
        if not isinstance(inputdataset, InputDataset):
            err_msg = 'Input dataset must be of InputDataset type'
            raise TypeError(err_msg)
        self._ids = inputdataset
        
        # Cyclic iterator over available input filenames
        fnames = [v.filename for v in self._ids.variables.itervalues()]
        self._fncycle = cycle(filter(None, fnames))
        
        # The definition parser
        self._dparser = DefitionParser()
        
        # Construct the OperationGraph
        for vname, vdef in self._defs.iteritems():
            vdeftree = self._dparser.parse_definition(vdef)
        
        self._root = None

    def _from_deftree_(self, deftree):
        """
        Fill an operation graph from a parsed definition syntax tree
        
        Parameters:
            deftree (tuple): The parsed definition tuple
        """
        if isinstance(deftree, (str, unicode)):
            if self._ids.variables[deftree].filename:
                fname = self._ids.variables[deftree].filename
            else:
                fname = self._fncycle.next()
            op = operators.VariableSliceReader(fname, deftree)
            self.add(op)
            return op
        elif isinstance(deftree, (int, float)):
            return deftree
        elif isinstance(deftree, tuple):
            fname = self._dparser.name_definition(deftree)
            func = deftree[0]
            fargs = []
            argops = []
            for arg in deftree[1:]:
                argop = self._from_deftree_(arg)
                if isinstance(argop, operators.Operator):
                    argops.append(argop)
                    fargs.append(None)
                else:
                    fargs.append(argop)
                    
            argunits = [op.units() for op in argops]
            if argunits:
                units = argunits.pop(0)
            else:
                units = Unit(None)
            for opidx, argunit in enumerate(argunits,1):
                if argunit == units:
                    continue
                elif argunit.is_convertible(units):
                    argop = argops[opidx]
                    
                    argops[opidx] = operators.FunctionEvaluator()
            rootOp = operators.FunctionEvaluator(fname, func, fargs, units)
            for argop in argops:
                self.connect(argop, rootOp)
            return rootOp

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
    
    def set_root(self, op):
        if op in self:
            self._root = op
    
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
            