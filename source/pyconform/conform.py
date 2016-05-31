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


#===============================================================================
# setup
#===============================================================================
def setup(inp, out):
    """
    Setup the conform operation

    Parameters:
        inp (InputDataset): The input Dataset
        out (OutputDataset): The output Dataset
    """
    if not isinstance(inp, InputDataset):
        raise TypeError('Input dataset must be of InputDataset type')
    if not isinstance(out, OutputDataset):
        raise TypeError('Output dataset must be of OutputDataset type')

    # Compute the operation graph
    agraph = ActionGraph()
    
    # Create a Graph Filler object to fill the graph
    filler = GraphFiller(inp)

    # Fill the Graph with initial definitions
    filler.from_definitions(agraph, out)
    
    # Attempt to match dimensions in the graph
    filler.match_dimensions(agraph)

    # Attempt to match units in the graph
    filler.match_units(agraph)

    return agraph


#===============================================================================
# run
#===============================================================================
def run(inp, out, agraph):
    """
    Run the conform operation

    Parameters:
        inp (InputDataset): The input Dataset
        out (OutputDataset): The output Dataset
        agraph (ActionGraph): The action graph needed to get the data
    """

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
        print 'Starting to writing output variable: {0}'.format(tsvar)
        
        # Get the time-series variable info object
        tsinfo = out.variables[tsvar]
        
        # Create the output file
        ncf = NCDataset(tsinfo.filename, 'w')
        
        # Write the file attributes
        ncf.setncatts(out.attributes)

        # Create the required dimensions
        tsdims = req_dims.union(set(tsinfo.dimensions))
        for odim in tsdims:
            if odim in agraph.dimension_map:
                idim = agraph.dimension_map[odim]
                dinfo = inp.dimensions[idim]
            elif odim in out.dimensions:
                dinfo = out.dimensions[odim]
            else:
                raise RuntimeError('Cannot find dimension {0}'.format(odim))
            if dinfo.unlimited:
                ncf.createDimension(odim)
            else:
                ncf.createDimension(odim, dinfo.size)
        
        # Create the variables and write their attributes
        ncvars = {}
        for mvar in meta_vars:
            mvinfo = out.variables[mvar]
            ncvar = ncf.createVariable(mvar, mvinfo.datatype, mvinfo.dimensions)
            for aname, avalue in mvinfo.attributes.iteritems():
                ncvar.setncattr(aname, avalue)
            ncvars[mvar] = ncvar

        ncvar = ncf.createVariable(tsvar, tsinfo.datatype, tsinfo.dimensions)
        for aname, avalue in tsinfo.attributes.iteritems():
            ncvar.setncattr(aname, avalue)
        ncvars[tsvar] = ncvar
        
        # Now perform the operation graphs and write data to variables
        for vname, vobj in ncvars.iteritems():
            groot = handles[vname]
            vobj[:] = agraph(groot)
        
        ncf.close()
        print 'Finished writing output variable: {0}'.format(tsvar)
