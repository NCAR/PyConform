"""
Main Conform Module

This file contains the classes and functions for the main PyConform operation.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from dataset import InputDataset, OutputDataset
from opgraph import OperationGraph
from collections import OrderedDict

def build_opgraphs(inp, out):
    """
    Build all of the OpGraphs for given input and output Datasets
    
    Parameters:
        inp (InputDataset): The input Dataset
        out (OutputDataset): The output Dataset
        
    Returns:
        dict: Dictionary of output variables names mapped to OperationGraphs
    """
    if not isinstance(inp, InputDataset):
        err_msg = 'Input dataset must be of InputDataset type'
        raise TypeError(err_msg)
    if not isinstance(out, OutputDataset):
        err_msg = 'Output dataset must be of OutputDataset type'
        raise TypeError(err_msg)
    
    opgraphs = OrderedDict()
    for ovname, ovinfo in out.variables.iteritems():
        opG = OperationGraph()

        
        
        opgraphs[ovname] = opG

    return opgraphs
