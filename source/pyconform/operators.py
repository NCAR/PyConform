"""
Fundamental Operators for the Operation Graphs

This module contains the Operator objects to be used in the DiGraph-based
Operation Graphs that implement the data transformation operations.

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from abc import ABCMeta, abstractmethod
from netCDF4 import Dataset
from os.path import exists
from mpi4py import MPI

import operator
import numpy as np

#===============================================================================
# Operator
#===============================================================================
class Operator(object):
    """
    The abstract base class for the Operator objects used in Operation Graphs
    """
    
    __metaclass__ = ABCMeta
    _id_ = 0
    
    @abstractmethod
    def __init__(self):
        """
        Initializer
        """
        self._id = Operator._id_
        Operator._id_ += 1
    
    def id(self):
        """
        Return the internal ID of the Operator
        """
        return self._id

    @abstractmethod
    def __call__(self):
        """
        Make callable like a function
        """
        pass
    

#===============================================================================
# VariableSliceReader
#===============================================================================
class VariableSliceReader(Operator):
    """
    Operator that reads a variable slice upon calling
    """
    
    def __init__(self, filepath, variable, slicetuple=(slice(None),)):
        """
        Initializer
        
        Parameters:
            filepath (str): A string filepath to a NetCDF file 
            variable (str): A string variable name to read
            slicetuple (tuple): A tuple of slice objects specifying the
                range of data to read from the file (in file-local indices)
        """
        # Call base class initializer
        super(VariableSliceReader, self).__init__()
        
        # Parse File Path
        if not isinstance(filepath, (str, unicode)):
            raise TypeError('Unrecognized file path object of type '
                            '{!r}: {!r}'.format(type(filepath), filepath))
        if not exists(filepath):
            raise OSError('File path not found: {!r}'.format(filepath))
        self._filepath = filepath
            
        # Attempt to open the NetCDF file
        try:
            ncfile = Dataset(self._filepath, 'r')
        except:
            raise OSError('Cannot open as a NetCDF file: '
                          '{!r}'.format(self._filepath))
        
        # Parse variable name
        if not isinstance(variable, (str, unicode)):
            raise TypeError('Unrecognized variable name object of type '
                            '{!r}: {!r}'.format(type(variable), variable))
        if variable not in ncfile.variables:
            raise OSError('Variable {!r} not found in NetCDF file: '
                          '{!r}'.format(variable, self._filepath))            
        self._variable = str(variable)
        
        # Parse slice tuple
        if isinstance(slicetuple, (list, tuple)):
            if not all([isinstance(s, (int, slice)) for s in slicetuple]):
                raise TypeError('Slice-tuple object {!r} must contain int '
                                'indices or slices only, not objects of type '
                                '{!r}'.format(slicetuple,
                                              [type(s) for s in slicetuple]))
        elif not isinstance(slicetuple, (int, slice)):
            raise TypeError('Unrecognized slice-tuple object of type '
                            '{!r}: {!r}'.format(type(slicetuple), slicetuple))
        self._slice = slicetuple
        
        # Close the NetCDF file
        ncfile.close()

    def __call__(self):
        """
        Make callable like a function
        """
        ncfile = Dataset(self._filepath, 'r')
        data = ncfile.variables[self._variable][self._slice]
        ncfile.close()
        return data


#===============================================================================
# FunctionEvaluator
#===============================================================================
class FunctionEvaluator(Operator):
    """
    Generic function operator that acts on two operands
    """
    
    def __init__(self, func, *args):
        """
        Initializer
        
        Parameters:
            func (Function): A function with arguments taken from other operators
            args (list): Arguments to the function, in order, where 'None'
                indicates an argument passed in at runtime
        """
        # Call base class initializer
        super(FunctionEvaluator, self).__init__()
        
        # Check if the function is callable
        if not hasattr(func, '__call__'):
            raise TypeError('Function object not callable: {!r}'.format(func))
        
        # Store the function pointer
        self._function = func
        
        # Store the arguments
        self._arguments = args
        
        # Count the number of runtime arguments needed
        self._nargs = sum(i is None for i in args)
        
    def __call__(self, *args):
        """
        Make callable like a function
        
        Parameters:
            args: List of arguments passed to the function
        """
        if len(args) < self._nargs:
            raise RuntimeError('Received {} arguments, expected '
                               '{}'.format(len(args), self._nargs))
        tmp_args = list(args)
        rtargs = [arg if arg else tmp_args.pop(0) for arg in self._arguments]
        rtargs.extend(tmp_args)
        return self._function(*rtargs)
