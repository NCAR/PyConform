"""
Data Flow Classes and Functions

This module contains the classes and functions needed to define Data Flows.

A Data Flow is a directed acyclic graph (DAG) that describes the flow of data
from one node in the graph to another.  Each node in the flow represents a
data action of some sort, such as reading data from file, transposing data,
unit conversion, addition, subtraction, etc.  The data transmitted along the
graph edges is assumed to a Numpy.NDArray-like object.

The action associated with each node is not performed until the data is
"requested" with the __getitem__ interface, via Node[key].  

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from __future__ import print_function
from abc import ABCMeta, abstractmethod
from pyconform.indexing import index_str, join
from cf_units import Unit
from inspect import getargspec, isfunction
from os.path import exists
from netCDF4 import Dataset
from sys import stderr

import numpy


#===============================================================================
# warning - Helper function
#===============================================================================
def warning(*objs):
    print("WARNING:", *objs, file=stderr)


#===================================================================================================
# UnitsError
#===================================================================================================
class UnitsError(ValueError):
    """Exception for when DataArray Units are invalid"""
    pass


#===================================================================================================
# DimensionsError
#===================================================================================================
class DimensionsError(ValueError):
    """Exception for when DataArray Dimensions are invalid"""
    pass


#===================================================================================================
# DataArray
#===================================================================================================
class DataArray(numpy.ma.MaskedArray):
    """
    A DataArray is the basic object passed along the edges of a Data Flow graph
    
    Derived from Numpy MaskedArray, the DataArray contains additional information
    about the array data, including units and dimensions.
    """

    def __new__(cls, inarray, units=None, dimensions=None):
        obj = numpy.ma.asarray(inarray).view(cls)

        if units is None:
            if 'units' not in obj._optinfo:
                obj._optinfo['units'] = Unit(1)
        elif isinstance(units, Unit):
            obj._optinfo['units'] = units
        else:
            obj._optinfo['units'] = Unit(units)

        if dimensions is None:
            if 'dimensions' not in obj._optinfo:
                obj._optinfo['dimensions'] = tuple([None] * len(obj.shape))
        elif isinstance(dimensions, tuple):
            if len(dimensions) != len(obj.shape):
                raise ValueError(('Dimensions {} length does not match DataArray with {} '
                                  'axes').format(dimensions, len(obj.shape)))
            obj._optinfo['dimensions'] = dimensions
        else:
            raise TypeError(('Cannot set DataArray object with dimensions of type '
                             '{}').format(type(dimensions)))

        return obj

    def __repr__(self):
        return ('{!s}(data = {!s}, mask = {!s}, fill_value = {!s}, units = {!s}, '
                'dimensions = {!s})').format(self.__class__.__name__, self.data, self.mask,
                                             self.fill_value, self.units, self.dimensions)

    @property
    def units(self):
        return self._optinfo['units']

    @property
    def dimensions(self):
        return self._optinfo['dimensions']


#===================================================================================================
# DataNode
#===================================================================================================
class DataNode(object):
    """
    The base class for objects that can appear in a data flow
    
    The DataNode object represents a point in the directed acyclic graph where multiple
    edges meet.  It represents a functional operation on the DataArrays coming into it from
    its adjacent DataNodes.  The DataNode itself outputs the result of this operation
    through the __getitem__ interface (i.e., DataNode[item]), returning a slice of a
    DataArray.
    """
    
    __metaclass__ = ABCMeta

    def __init__(self, label, *inputs):
        """
        Initializer
        
        Parameters:
            label: A label to give the DataNode
            inputs (tuple): DataNodes that provide input into this DataNode
        """
        self._label = label
        self._inputs = inputs

    @abstractmethod
    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """
        pass

    @property
    def label(self):
        return self._label


#===================================================================================================
# EvalDataNode
#===================================================================================================
class EvalDataNode(DataNode):
    """
    DataNode class for evaluating a function on input from neighboring DataNodes
    """

    def __init__(self, label, func, *args):
        """
        Initializer
        
        Parameters:
            label: A label to give the DataNode
            func (callable): A callable function associated with the DataNode operation
            args (tuple): Arguments to the function given by 'func'
        """
        # Check func parameter
        if callable(func):
            if hasattr(func, '__call__') and isfunction(func.__call__):
                argspec = getargspec(func.__call__)
            else:
                argspec = getargspec(func)
        else:
            raise TypeError('Function argument to DataNode {} is not callable'.format(label))

        # Check the function arguments
        max_len = len(argspec.args)
        if argspec.defaults is None:
            min_len = max_len
        else:
            min_len = max_len - len(argspec.defaults)
        if len(args) < min_len:
            raise ValueError(('Too few arguments supplied for DataNode function. '
                              '({} needed, {} supplied)').format(min_len, len(args)))
        if len(args) > max_len:
            raise ValueError(('Too many arguments supplied for DataNode function. '
                              '({} needed, {} supplied)').format(max_len, len(args)))

        # Save the function reference
        self._function = func
        
        # Call the base class initialization
        super(EvalDataNode, self).__init__(label, *args)

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """
        if len(self._inputs) == 0:
            data = self._function()
            return data[index] if isinstance(data, DataArray) else data
        else:
            args = tuple(d[index] if isinstance(d, (DataArray, DataNode)) else d
                         for d in self._inputs)
            return self._function(*args)
        

#===================================================================================================
# ReadDataNode
#===================================================================================================
class ReadDataNode(DataNode):
    """
    DataNode class for reading data from a NetCDF file
    """

    def __init__(self, filepath, variable, index=slice(None)):
        """
        Initializer
        
        Parameters:
            filepath (str): A string filepath to a NetCDF file 
            variable (str): A string variable name to read
            index (tuple, slice, int): A tuple of slices or ints, or a slice or int,
                specifying the range of data to read from the file (in file-local indices)
        """

        # Parse File Path
        if not isinstance(filepath, basestring):
            raise TypeError('Unrecognized file path object of type '
                            '{!r}: {!r}'.format(type(filepath), filepath))
        if not exists(filepath):
            raise OSError('File path not found: {!r}'.format(filepath))
        self._filepath = filepath

        # Attempt to open the NetCDF file to parse the variable name
        with Dataset(self._filepath, 'r') as ncfile:
            if not isinstance(variable, basestring):
                raise TypeError('Unrecognized variable name object of type '
                                '{!r}: {!r}'.format(type(variable), variable))
            if variable not in ncfile.variables:
                raise OSError('Variable {!r} not found in NetCDF file: '
                              '{!r}'.format(variable, self._filepath))
        self._variable = variable
    
        # Parse the reading index
        self._index = numpy.index_exp[index]

        # Call the base class initializer
        super(ReadDataNode, self).__init__('{0}{1}'.format(variable, index_str(index)))

    @property
    def variable(self):
        return self._variable

    def __getitem__(self, index):
        """
        Read DataArray from file
        """
        with Dataset(self._filepath, 'r') as ncfile:

            # Get a reference to the variable
            ncvar = ncfile.variables[self.variable]
    
            # Read the variable units
            attrs = ncvar.ncattrs()
            units_attr = ncvar.getncattr('units') if 'units' in attrs else 1
            calendar_attr = ncvar.getncattr('calendar') if 'calendar' in attrs else None
            try:
                units = Unit(units_attr, calendar=calendar_attr)
            except:
                units = Unit(1)
    
            # Read the raw variable dimensions
            dimensions = ncvar.dimensions

            # Get the shape of the variable
            shape0 = ncvar.shape
            
            # Compute the joined index object
            rindex = join(shape0, self._index, index)
            
            # Gather the return dimensions
            rdimensions = tuple(d for d,i in zip(dimensions, rindex) if isinstance(i, slice))            
    
            data = DataArray(ncvar[rindex], units=units, dimensions=rdimensions)

        return data


#===================================================================================================
# ValidateDataNode
#===================================================================================================
class ValidateDataNode(DataNode):
    """
    DataNode class to validate data from a neighboring DataNode
    """
    
    def __init__(self, label, dnode, minimum=None, maximum=None,
                 min_mean_abs=None, max_mean_abs=None):
        """
        Initializer
        
        Parameters:
            label: A label to give the DataNode
            dnode (DataNode): DataNode that provides input into this DataNode
            minimum: The minimum value the data should have, if valid
            maximum: The maximum value the data should have, if valid
            min_mean_abs: The minimum acceptable value of the mean of the 
                absolute value of the data
            max_mean_abs: The maximum acceptable value of the mean of the 
                absolute value of the data
        """
        # Check DataNode type
        if not isinstance(dnode, DataNode):
            raise TypeError('ValidatorNode can only validate output from a DataNode')
        
        # Store min/max
        self._min = minimum
        self._max = maximum

        # Stoe mean_abs min/max
        self._min_mean_abs = min_mean_abs
        self._max_mean_abs = max_mean_abs

        # Call base class initializer
        super(ValidateDataNode, self).__init__(label, dnode)

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """
        data = self._inputs[0][index]
        
        if self._min is not None:
            dmin = numpy.min(data)
            if dmin < self._min:
                warning(('Data from operator {!r} has minimum value '
                         '{} but requires data greater than or equal to '
                         '{}').format(self.name, dmin, self._min))

        if self._max is not None:
            dmax = numpy.max(data)
            if dmax > self._max:
                warning(('Data from operator {!r} has maximum value '
                         '{} but requires data less than or equal to '
                         '{}').format(self.name, dmax, self._max))

        if self._min_mean_abs is not None or self._max_mean_abs is not None:
            mean_abs = numpy.mean(numpy.abs(data))

        if self._min_mean_abs is not None:
            if mean_abs < self._min_mean_abs:
                warning(('Data from operator {!r} has minimum mean_abs value '
                         '{} but requires data greater than or equal to '
                         '{}').format(self.name, mean_abs, self._min_mean_abs))

        if self._max_mean_abs is not None:
            if mean_abs > self._max:
                warning(('Data from operator {!r} has maximum mean_abs value '
                         '{} but requires data less than or equal to '
                         '{}').format(self.name, mean_abs, self._max_mean_abs))

        return data


#===================================================================================================
# SetDataNode
#===================================================================================================
class SetDataNode(DataNode):
    """
    DataNode class to set data in memory
    """
    
    def __init__(self, label, data, units=None, dimensions=None):
        """
        Initializer
        
        Parameters:
            label: A label to give the DataNode
            data (array): Data to store in this DataNode
            units: Units to associate with the data
            dimensions: Dimensions to associate with the data 
        """
        # Store data
        self._data = DataArray(data, units=units, dimensions=dimensions)

        # Call base class initializer
        super(SetDataNode, self).__init__(label)

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """
        return self._data[index]
