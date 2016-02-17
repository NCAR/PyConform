"""
Main Conform Module

This file contains the classes and functions for the main PyConform operation.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from dataset import InputDataset, OutputDataset
from opgraph import OperationGraph, GraphFiller
from mpi4py import MPI
from netCDF4 import Dataset as NCDataset


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
    
    # Compute the operation graph
    opgraph = OperationGraph() 
    
    # Fill the operation graph
    gfiller = GraphFiller()
    groots = gfiller.from_definitions(opgraph, inp, out)
    dim_map = gfiller.dimension_map
    
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
            vobj[:] = opgraph(groots[vname])
