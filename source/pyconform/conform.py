"""
Main Conform Module

This file contains the classes and functions for the main PyConform operation.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.datasets import InputDataset, OutputDataset
from pyconform.actiongraphs import ActionGraph, GraphFiller
from netCDF4 import Dataset as NCDataset
from mpi4py import MPI
from os import linesep


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
    if not isinstance(inp, InputDataset):
        raise TypeError('Input dataset must be of InputDataset type')
    if not isinstance(out, OutputDataset):
        raise TypeError('Output dataset must be of OutputDataset type')
    
    # MPI rank and size
    mpi_rank = MPI.COMM_WORLD.Get_rank()
    mpi_size = MPI.COMM_WORLD.Get_size()
    
    # Get time-series names and metadata names
    tser_vars = [vname for vname, vinfo in out.variables.iteritems()
                if vinfo.filename is not None]
    meta_vars = [vname for vname in out.variables if vname not in tser_vars]

    # Get the set of necessary dimensions for the meta_vars
    req_dims = set(d for mvar in meta_vars
                   for d in out.variables[mvar].dimensions)
    
    # Get the local list of tseries variable names
    loc_vars = tser_vars[mpi_rank::mpi_size]
    
    # Compute the operation graph
    agraph = ActionGraph()
    
    # Fill the operation graph
    filler = GraphFiller(inp)
    filler.from_definitions(agraph, out)
    filler.match_dimensions(agraph)
    filler.match_units(agraph)

    str_graph = str(agraph).replace(linesep, '{0}        '.format(linesep))
    print 'GRAPH:  {0}'.format(str_graph)
    
    print 'DIMENSIONS:'
    for out_dim, inp_dim in agraph.dimension_map.iteritems():
        print '    {0} --> {1}'.format(inp_dim, out_dim)
    print
    
    # Fill a map of variable name to graph handle
    # CURRENT: handle.key maps to output variable name
    # FUTURE: handle.name (Key+Slice) should map to output identifier
    handles = {}
    for handle in agraph.handles():        
        if handle.key in handles:
            raise KeyError(('Doubly-mapped handle key in ActionGraph: '
                            '{0!r}').format(handle.key))
        else:
            handles[handle.key] = handle

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
            name = agraph.dimension_map[dname]
            if name in inp.dimensions:
                dim = inp.dimensions[name]
            elif name in out.dimensions:
                dim = out.dimensions[name]
            if dim.unlimited:
                ncf.createDimension(dname)
            else:
                ncf.createDimension(dname, dim.size)
        
        # Create the variables and write their attributes
        ncvars = {}
        for mvar in meta_vars:
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
            groot = handles[vname]
            vobj[:] = agraph(groot)
