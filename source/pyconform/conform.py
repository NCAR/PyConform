"""
Main Conform Module

This file contains the classes and functions for the main PyConform operation.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from dataset import InputDataset, OutputDataset
from opgraph import OperationGraph
from parsing import DefitionParser
from collections import OrderedDict
from copy import deepcopy


#===============================================================================
# build_opgraphs
#===============================================================================
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
    
    # Parse variable definitions
    dparser = DefitionParser()
    definitions = OrderedDict([(n, dparser.parse_definition(v.definition))
                               for n,v in out.variables.iteritems()])
    
    # Check that all definitions exist for all output variables
    undefd_ovars = set(out.variables.keys()) - set(definitions.keys())
    if len(undefd_ovars) > 0:
        err_msg = ('Some output variables were not defined:{}'
                   '{}').format(linesep, undefd_ovars)
        raise ValueError(err_msg)
    
    # Check that all referenced variables are in the input dataset
    for vname, vdef in definitions.iteritems():
        def_str = out.variables[vname].definition
        check_references(vname, def_str, vdef, inp)
    
    # Compute the dimension mapping from input to output dimensions    
    dim_map = map_dimensions(definitions, inp, out)
    
    # Loop over output variables and create opgraphs
    opgraphs = OrderedDict()
    for vname, vdef in definitions.iteritems():
        opG = OperationGraph()
        
        odims = out.variables[vname].dimensions
        
        opgraphs[vname] = opG
    
    return dim_map


#===============================================================================
# check_references
#===============================================================================
def check_references(vname, def_str, deftuple, inpdataset):
    if isinstance(deftuple, (str, unicode)):
        if deftuple not in inpdataset.variables:
            err_msg = ('Variable {!r} referenced in {!r} output variable '
                       'definition {!r} but not found in input '
                       'dataset').format(deftuple, vname, def_str)
            raise KeyError(err_msg)
    elif isinstance(deftuple, tuple):
        for arg in deftuple:
            check_references(vname, def_str, arg, inpdataset)
    
    
#===============================================================================
# get_dimensions
#===============================================================================
def get_dimensions(deftuple, inpdataset):
    dims = {}
    key = name_deftuple(deftuple)
    if isinstance(deftuple, (str, unicode)):
        dims[key] = inpdataset.variables[deftuple].dimensions 
    elif isinstance(deftuple, tuple):
        dims[key] = {}
        for arg in deftuple[1:]:
            for argname, argdim in get_dimensions(arg, inpdataset).iteritems():
                dims[key][argname] = argdim
    else:
        dims[key] = None
    return dims

#===============================================================================
# reduce_dimensions
#===============================================================================
def reduce_dimensions(argdims):
    if isinstance(argdims, tuple):
        return argdims
    elif isinstance(argdims, dict):
        argscopy = deepcopy(argdims)
        key1 = None
        dims1 = None
        while argscopy:
            key2, val2 = argscopy.popitem()
            dims2 = reduce_dimensions(val2)
            if dims1 and dims2:
                if dims1 != dims2:
                    err_msg = ('Argument {!r} has dimensions {!r} but '
                               'argument {!r} has incompatible dimensions '
                               '{!r}').format(key1, dims1, key2, dims2)
                    raise ValueError(err_msg)
            elif dims2:
                key1 = key2
                dims1 = dims2
        return dims1
            

#===============================================================================
# name_deftuple
#===============================================================================
def name_deftuple(deftuple):
    """
    Compute a string from a definition tuple
    
    Parameters:
        deftuple (tuple): An definition tuple
    """
    strval = ''
    if isinstance(deftuple, tuple):
        strval += deftuple[0].__name__ + '('
        strval += ','.join(name_deftuple(dt) for dt in deftuple[1:])
        strval += ')'
    else:
        strval += str(deftuple)
    return strval


#===============================================================================
# map_dimensions
#===============================================================================
def map_dimensions(deftuples, inpdataset, outdataset):
    """
    Compute the mapping from input dataset dimensions to output dimensions
    
    Parameters:
        deftuples (dict): Dictionary of parsed definitions
        inpdataset (InputDataset): The dataset referenced by the definitions
        outdataset (OutputDataset): The output dataset with variable definitions
    """
    
    dim_map = {}
    for ovar, deftuple in deftuples.iteritems():
        odims = outdataset.variables[ovar].dimensions
        idims = reduce_dimensions(get_dimensions(deftuple, inpdataset))
        if len(odims) != len(idims):
            defstr = name_deftuple(deftuple)
            err_msg = ('Output variable {!r} has {} dimensions while its '
                       'definition {!r} has {} '
                       'dimensions').format(ovar, len(odims), defstr, 
                                            len(idims))
            raise ValueError(err_msg)
        for odim, idim in zip(odims, idims):
            if odim not in dim_map:
                dim_map[odim] = str(idim)
            elif idim != dim_map[odim]:
                err_msg = ('Output dimension {!r} in output variable {!r} '
                           'appears to map to both {!r} and {!r} input '
                           'dimensions').format(odim, ovar, idim, 
                                                dim_map[odim])
                raise ValueError(err_msg)

    return dim_map

