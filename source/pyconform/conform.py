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
from random import choice
from mpi4py import MPI
from netCDF4 import Dataset as NCDataset

from pyconform import operators


#===============================================================================
# conform
#===============================================================================
def conform(inp, out):
    """
    Perform the conform operation

    Parameters:
        inp (InputDataset): The input Dataset
        out (OutputDataset): The output Dataset
    """
    # MPI rank and size
    mpirank = MPI.COMM_WORLD.Get_rank()
    mpisize = MPI.COMM_WORLD.Get_size()
    
    # Get time-series names and metadata names
    tservars = [vname for vname, vinfo in out.variables.iteritems()
                if vinfo.filename is not None]
    metavars = [vname for vname in out.variables if vname not in tservars]

    # Get the set of necessary dimensions for the metavars
    req_dims = set()
    for mvar in metavars:
        for d in out.variables[mvar].dimensions:
            req_dims.add(d)
    
    # Get the local list of tseries variable names
    loc_vars = tservars[mpirank::mpisize]
    
    # Parse the output variable definitions
    vdefs = parse_definitions(inp, out)
    
    # Map the input/output dimension names
    dim_map = map_dimensions(inp, out, vdefs)
     
    # Build all operation graphs (might only need to build local)
    opgraphs = build_opgraphs(inp, vdefs)
    
    # Write each local time-series file
    for tsvar in loc_vars:
        
        # Get the time-series variable info object
        tsinfo = out.variables[tsvar]
        
        # Create the output file
        ncf = NCDataset(tsinfo.filename, 'w')
        
        # Write the file attributes
        ncf.setncatts(out.attributes)

        # Create the required dimensions
        tsdims = req_dims.union(set(tsinfo.dimensions))
        for dname in tsdims:
            idim = inp.dimensions[dim_map[dname]]
            if idim.unlimited:
                ncf.createDimension(dname)
            else:
                ncf.createDimension(dname, idim.size)
        
        # Create the variables and write their attributes
        ncvars = {}
        for mvar in metavars:
            mvinfo = out.variables[mvar]
            ncvar = ncf.createVariable(mvar, mvinfo.datatype, mvinfo.dimensions)
            for aname, avalue in mvinfo.attributes.iteritems():
                setattr(ncvar, aname, avalue)
            ncvars[mvar] = ncvar

        ncvar = ncf.createVariable(tsvar, tsinfo.datatype, tsinfo.dimensions)
        for aname, avalue in tsinfo.attributes.iteritems():
            setattr(ncvar, aname, avalue)
        ncvars[tsvar] = ncvar
        
        # Now perform the operation graphs and write data to variables
        for vname, vobj in ncvars.iteritems():
            vobj[:] = opgraphs[vname]()
            
#===============================================================================
# build_opgraphs
#===============================================================================
def build_opgraphs(inp, definitions):
    # Compute the dimensional slices needed for each variable
    # Not implemented (reads entire variable at the moment)
    
    # Loop over output variables and create opgraphs
    opgraphs = OrderedDict()
    for vname, vdef in definitions.iteritems():
        opG = OperationGraph()
        rootOp = fill_opgraph(vdef, inp, opG)
        opG.set_root(rootOp)
        opgraphs[vname] = opG
    
    return opgraphs


#===============================================================================
# map_dimensions
#===============================================================================
def map_dimensions(inp, out, definitions):

    # Gather the dimensions at each operation in the definition
    def_dims_maps = {}
    for vname, vdef in definitions.iteritems():
        def_dims_maps[vname] = gather_dimensions(vdef, inp)

    # Compute the dimension mapping from input to output dimensions    
    dim_map = {}
    for vname, def_dims in def_dims_maps.iteritems():
        odims = out.variables[vname].dimensions
        idims = reduce_dimensions(def_dims)
        if len(odims) != len(idims):
            defstr = name_definition(definitions[vname])
            err_msg = ('Output variable {!r} has dimensions {} while its '
                       'definition {!r} has dimensions '
                       '{}').format(vname, len(odims), defstr, len(idims))
            raise ValueError(err_msg)
        for odim, idim in zip(odims, idims):
            if odim not in dim_map:
                dim_map[odim] = str(idim)
            elif idim != dim_map[odim]:
                err_msg = ('Output dimension {!r} in output variable {!r} '
                           'appears to map to both input dimensions {!r} and '
                           '{!r}').format(odim, vname, idim, dim_map[odim])
                raise ValueError(err_msg)
    
    return dim_map
            

#===============================================================================
# parse_definitions
#===============================================================================
def parse_definitions(inp, out):
    """
    Parse the output dataset definitions
    
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
    
    # Parse variable definitions - definitions are tuples of strs/numbers/funcs
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
        invalid_ref = check_references(vdef, inp)
        if invalid_ref:
            def_str = out.variables[vname].definition
            err_msg = ('Variable {!r} referenced in output variable {!r} '
               'definition {!r} but not found in input '
               'dataset').format(invalid_ref, vname, def_str)
            raise KeyError(err_msg)

    return definitions

#===============================================================================
# check_references recursively for a single definition
#===============================================================================
def check_references(definition, inpdataset):
    """
    Check a definition's references to input variables
    
    Parameters:
        definition (tuple): A parsed definition tuple
        inpdataset (InputDataset): The input dataset
        
    Returns:
        str: Name of referenced variable, if not found in input dataset
        None: If all references are valid
    """
    if isinstance(definition, (str, unicode)):
        if definition not in inpdataset.variables:
            return definition        
    elif isinstance(definition, tuple):
        for arg in definition:
            check_references(arg, inpdataset)
    
    
#===============================================================================
# gather_dimensions recursively for a single definition
#===============================================================================
def gather_dimensions(definition, inpdataset):
    """
    Gather the dimension tuples for each level in a definition's operation
    
    Parameters:
        definition (tuple): A parsed definition tuple
        inpdataset (InputDataset): The input dataset
    
    Returns:
        dict: Nested dictionary of definition names (keys) mapped to dimension
            tuples (values)
    """
    dims = {}
    key = name_definition(definition)
    if isinstance(definition, (str, unicode)):
        dims[key] = inpdataset.variables[definition].dimensions 
    elif isinstance(definition, tuple):
        dims[key] = {}
        for arg in definition[1:]:
            argdims = gather_dimensions(arg, inpdataset)
            for argname, argdim in argdims.iteritems():
                dims[key][argname] = argdim
    else:
        dims[key] = None
    return dims

#===============================================================================
# reduce_dimensions recursively for a definition dimension dict
#===============================================================================
def reduce_dimensions(def_dims):
    """
    Reduces a dictionary of definition dimensions to one dimension tuple
    
    Parameters:
        def_dims (dict): A definition dimension dictionary
    """
    if isinstance(def_dims, tuple):
        return def_dims
    elif isinstance(def_dims, dict):
        dimscopy = deepcopy(def_dims)
        key1 = None
        dims1 = None
        while dimscopy:
            key2, val2 = dimscopy.popitem()
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
# name_definition
#===============================================================================
def name_definition(definition):
    """
    Compute a string from a definition tuple
    
    Parameters:
        definition (tuple): An definition tuple
    """
    strval = ''
    if isinstance(definition, tuple):
        strval += definition[0].__name__ + '('
        strval += ','.join(name_definition(dt) for dt in definition[1:])
        strval += ')'
    else:
        strval += str(definition)
    return strval


#===============================================================================
# fill_opgraph
#===============================================================================
def fill_opgraph(definition, inp, G):
    """
    Fill an operation graph from a parsed definition
    
    Parameters:
        definition (tuple): The parsed definition tuple
        inp (InputDataset): InputDataset
        G (OperationGraph): The operation graph to fill
    """
    if isinstance(definition, (str, unicode)):
        if inp.variables[definition].filename:
            fname = inp.variables[definition].filename
        else:
            fname = choice(filter(None, [v.filename for v in inp.variables.values()]))
        op = operators.VariableSliceReader(fname, definition)
        G.add(op)
        return op
    elif isinstance(definition, (int, float)):
        return definition
    elif isinstance(definition, tuple):
        fname = name_definition(definition)
        func = definition[0]
        fargs = []
        argops = []
        for arg in definition[1:]:
            argop = fill_opgraph(arg, inp, G)
            if isinstance(argop, operators.Operator):
                argops.append(argop)
                fargs.append(None)
            else:
                fargs.append(argop)
        rootOp = operators.FunctionEvaluator(fname, func, *fargs)
        for argop in argops:
            G.connect(argop, rootOp)
        return rootOp
