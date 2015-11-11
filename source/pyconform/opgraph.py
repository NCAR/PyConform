"""
Operations Graph

This module contains the necessary pieces to define and construct the 
"operation graph", in which the operations that transform the initial dataset 
into the final dataset are defined and performed.

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os.path import exists
import netCDF4


#===============================================================================
# OperationNode
#===============================================================================
class OperationNode(object):
    """
    Basic named node object in a operation graph
    """
    
    def __init__(self, name):
        """
        Initializer
        
        Parameters:
            name (str): Name associated with the operation or its data
        """
        
        # Data name
        try:
            self._name = str(name)
        except:
            err_msg = "OperationNode name must be convertable to a string"
            raise TypeError(err_msg)
        
    def name(self):
        """
        Get the name of the node
        """
        return self._name
    
    def __str__(self):
        """
        Return the string name of the node
        """
        return self.name()

    def __repr__(self):
        """
        Return the string representation of the node
        """
        return repr(self.name())
    
    def __call__(self):
        """
        Perform the operation associated with the node
        """
        pass
    

#===============================================================================
# ReadVariableNode
#===============================================================================
class ReadVariableNode(OperationNode):
    """
    OperationNode object where data is read from a file
    """

    def __init__(self, variable, file_or_path, slicetuple=(slice(None),)):
        """
        Initializer
        
        Parameters:
            variable (str): Variable name to associate with the node
            file_or_path (str): Path to the file from which data is to be read
                or the open NetCDF file object itself
            slicetuple (tuple): A tuple of slices indicating the range/subset
                of the variable data to read
        """
        # Call to base class
        super(ReadVariableNode, self).__init__(variable)

        # Filename in which the data exists
        if isinstance(file_or_path, netCDF4.Dataset):
            self._file = file_or_path
            self._filepath = file_or_path.filepath()
        elif isinstance(file_or_path, (str, unicode)) and exists(file_or_path):
            self._filepath = str(file_or_path)
            self._file = None
        else:
            err_msg = ("File or path object must be an open NetCDF file "
                       "or a path to an existing NetCDF file")
            raise TypeError(err_msg)
        
        # Range within the given file of the variable's data
        try:
            self._slice = tuple(slicetuple)
        except:
            err_msg = "Slice tuple must be convertable to a tuple"
            raise TypeError(err_msg)
        if not all([isinstance(s, slice) for s in self._slice]):
            err_msg = "Slice tuple must be a tuple of slices"
            raise TypeError(err_msg)
        
    def __call__(self):
        """
        Read the variable slice from file
        """
        if self._file:
            data = self._file.variables[self._name][self._slice]
        else:
            ncfile = netCDF4.Dataset(self._filepath, 'r')
            data = ncfile.variables[self._name][self._slice]
            ncfile.close()
        return data


#===============================================================================
# CalculateNode
#===============================================================================
class CalculateNode(OperationNode):
    """
    OperationNode object where data is calculated from other data
    """

    def __init__(self, name, file_or_path, ncfmt='NETCDF4'):
        """
        Initializer
        
        Parameters:
            name (str): Variable name to associate with the node
            file_or_path (str): Path to the file from which data is to be read
                or the open NetCDF file object itself
            ncfmt (str): The string NetCDF format of the output file
                to write
        """
        # Call to base class
        super(CalculateNode, self).__init__(name)

        # NetCDF file format
        try:
            self._format = str(ncfmt)
        except:
            err_msg = "File format must be convertable to a string"
            raise TypeError(err_msg)

        # Make sure the format is valid
        valid_formats = ['NETCDF3_CLASSIC', 'NETCDF3_64BIT',
                         'NETCDF4_CLASSIC', 'NETCDF4']
        if self._format not in valid_formats:
            err_msg = "File format {!r} is not a valid format".format(self._format)
            raise TypeError(err_msg)
        
        # Filename in which the data exists
        if isinstance(file_or_path, netCDF4.Dataset):
            self._file = file_or_path
            self._filepath = file_or_path.filepath()
        elif isinstance(file_or_path, (str, unicode)) and exists(file_or_path):
            self._filepath = str(file_or_path)
            self._file = None
        else:
            err_msg = ("File or path object must be an open NetCDF file "
                       "or a path to an existing NetCDF file")
            raise TypeError(err_msg)
        
    def __call__(self):
        """
        Retrieve data and write to file
        """
        ncfile = netCDF4.Dataset(self._filename, 'w', self._format)
        self._data = ncfile.variables[self._variable][self._slice]
        ncfile.close()
        return self._data
    