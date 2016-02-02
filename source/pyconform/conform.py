"""
Main Conform Module

This file contains the classes and functions for the main PyConform operation.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from dataset import InputDataset, OutputDataset
from parsing import DefitionParser
from collections import OrderedDict


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

    # Compute the dimension mapping from input to output dimensions    
    dim_map = map_dimensions(definitions, inp, out)
    
    return dim_map


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
                if argdim is not None:
                    dims[key][argname] = argdim
    else:
        dims[key] = None
    return dims

#===============================================================================
# reduce_dimensions
#===============================================================================
def reduce_dimensions(argdims):
    if isinstance(argdims, dict):
        if len(argdims) > 0:
            key0, val0 = argdims.popitem()
            dims0 = reduce_dimensions(val0)
            for key, val in argdims.iteritems():
                dims = reduce_dimensions(val)
                if dims0 != dims:
                    err_msg = ('Argument {!r} has dimensions {!r} '
                               'but argument {!r} has dimensions '
                               '{!r}').format(key0, dims0, key, dims)
                    raise ValueError(err_msg)
            return dims0
        else:
            return tuple()
    else:
        return tuple(argdims)
            

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
        idims = reduce_dimensions(get_dimensions(deftuple))
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

