"""
Operations Graph

This module contains the necessary pieces to define and construct the 
"operation graph", in which the operations that transform the initial dataset 
into the final dataset are defined and performed.

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os.path import exists
from abc import ABCMeta
from abc import abstractmethod
import netCDF4


#===============================================================================
# OperationNode
#===============================================================================
class OperationNode(object):
    """
    Basic named node object in an operation graph
    
    By design, the node objects contain a list of neighbor nodes that
    are referenced when performing the node's designed operation (i.e., when
    the node is called as a function).  Not all types of OperationNode
    objects have neighbors, however.
    """
    
    __metaclass__ = ABCMeta
    
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
    
    @abstractmethod
    def __call__(self):
        """
        Perform the operation associated with the node
        """
        return None
    

#===============================================================================
# ReadNetCDF4SliceNode
#===============================================================================
class ReadNetCDF4SliceNode(OperationNode):
    """
    OperationNode object where data is read from a NetCDF file
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
        super(ReadNetCDF4SliceNode, self).__init__(variable)

        # Filename (or fileobject) in which the data exists
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
        
        # Check on file contents (variable exists and get units)
        if self._file:
            ncfile = self._file
        else:
            ncfile = netCDF4.Dataset(self._filepath, 'r')
        if self._name not in ncfile.variables:
            err_msg = ("Variable {!r} does not exist in file "
                       "{!r}").format(self._name, self._filepath)
            raise KeyError(err_msg)
        if hasattr(ncfile.variables[self._name], 'units'):
            self._units = ncfile.variables[self._name].units
        else:
            self._units = 1
        if not self._file:
            ncfile.close()
        
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
# CalculateSliceNode
#===============================================================================
class CalculateSliceNode(OperationNode):
    """
    OperationNode object where data is calculated from the data of other nodes
    """

    def __init__(self, formula):
        """
        Initializer
        
        Parameters:
            formula (str): Formula referencing other nodes by name
        """
        # Call to base class
        super(CalculateSliceNode, self).__init__(formula)

        # 
        
    def __call__(self):
        """
        Retrieve data and write to file
        """
        ncfile = netCDF4.Dataset(self._filename, 'w', self._format)
        self._data = ncfile.variables[self._variable][self._slice]
        ncfile.close()
        return self._data
    