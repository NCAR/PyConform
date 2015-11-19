"""
Operator Vertices

Operator Vertices are defined simply as objects that perform a simple
operation with the "do" method.  Any class with the "do" method can be
considered an Operator Vertex.  During initialization of the Operator Vertex,
it should be validated.

The "do" method must be defined to take only Numpy NDArrays as arguments (or
None), and return a single Numpy NDArray (or None).  Operator Vertices that take
None as arguments represent "sources" in an Operator Graph (i.e., vertices with
only outgoing edges).  Operator Vertices that return None represent "sinks" in
an Operator Graph (i.e., vertices with only incoming edges).

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os.path import exists
import netCDF4


#===============================================================================
# NetCDF Variable Slice Reader
#===============================================================================
class NCVariableSliceReader(object):
    """
    Read and return a slice of data from a NetCDF variable
    """

    def __init__(self, filename, variable, vslice=None):
        """
        Initialization
        
        Parameters:
            filename (str): Name of the NetCDF file
            variable (str): Name of the variable
            vslice (slice): Slice (or slice-tuple) of the variable to read
        """
        if not exists(filename):
            raise OSError('Cannot find NetCDF file {!r}'.format(filename))
        self._filename = str(filename)
        
        ncfile = netCDF4.Dataset(self._filename, 'r')
        ncvar = ncfile.variables[variable]
        self._variable = str(variable)

        if _are_slices_invalid(vslice, ncvar.shape):
            raise IndexError('{} invalid for shape {}'.format(vslice, ncvar.shape))
        self._slice = vslice
        
        ncfile.close()
        
    def do(self):
        """
        Perform the operation
        
        Returns:
            dict: Global attributes of the file
        """
        ncfile = netCDF4.Dataset(self._filename, 'r')
        data = ncfile.variables[self._variable][self._slice]
        ncfile.close()
        return data
    

#===============================================================================
# Helper Functions
#===============================================================================

def _are_slices_invalid(slices, shape):
    """
    Check if a given slice (or tuple of slices) is in bounds of a given shape
    """
    if isinstance(slices, tuple):
        if len(slices) != len(shape):
            return True
        for idx, slc in enumerate(slices):
            if _is_slice_invalid(slc, shape(idx)):
                return True
    elif isinstance(slices, slice):
        if len(shape) != 1:
            return True
        if _is_slice_invalid(slices, shape[0]):
            return True
    else:
        return True
    return False
        
def _is_slice_invalid(slc, size):
    """
    Check if a slice or index is in bounds of a given size dimension
    """
    if isinstance(slc, int):
        if slc < 0 or slc >= size:
            return True
    elif isinstance(slc, slice):
        if slc.start >= slc.stop:
            return True
        elif slc.start < 0 or slc.stop >= size:
            return True
    else:
        return True
    return False

#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == '__main__':
    pass
