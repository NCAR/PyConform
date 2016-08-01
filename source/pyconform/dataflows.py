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

    def _align_indices_(self, index, dimensions):
        """
        Compute an index tuple with indices aligned according to dimension name
        
        Parameters:
            index: An index or a dictionary of indices keyed by dimension name
            dimensions (tuple): A tuple of named dimensions for each axis of the data
        """
        if index is None:
            return tuple(slice(0, 0) for d in dimensions)
        elif isinstance(index, dict):
            return tuple(index.get(d, slice(None)) for d in dimensions)
        else:
            return index

    @property
    def label(self):
        """
        The DataNode's label
        """
        return self._label


#===================================================================================================
# CreateDataNode
#===================================================================================================
class CreateDataNode(DataNode):
    """
    DataNode class to create data in memory
    
    This is a "source" DataNode.
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
        super(CreateDataNode, self).__init__(label)

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """
        return self._data[self._align_indices_(index, self._data.dimensions)]


#===================================================================================================
# ReadDataNode
#===================================================================================================
class ReadDataNode(DataNode):
    """
    DataNode class for reading data from a NetCDF file
    
    This is a "source" DataNode.
    """

    def __init__(self, filepath, variable, index=slice(None)):
        """
        Initializer
        
        Parameters:
            filepath (str): A string filepath to a NetCDF file 
            variable (str): A string variable name to read
            index (tuple, slice, int, dict): A tuple of slices or ints, or a slice or int,
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
        if isinstance(index, dict):
            self._index = index
        else:
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

            # Read the original variable dimensions
            dimensions0 = ncvar.dimensions

            # Align the read-indices on dimensions
            index1 = self._align_indices_(self._index, dimensions0)

            # Get the dimensions after application of the first index
            dimensions1 = tuple(d for d, i in zip(dimensions0, index1) if isinstance(i, slice))

            # Align the second index on the intermediate dimensions
            index2 = self._align_indices_(index, dimensions1)

            # Get the dimensions after application of the second index
            dimensions2 = tuple(d for d, i in zip(dimensions1, index2) if isinstance(i, slice))

            # Get the shape of the original variable
            shape0 = ncvar.shape

            # Compute the joined index object
            index12 = join(shape0, index1, index2)

            data = DataArray(ncvar[index12], units=units, dimensions=dimensions2)

        return data


#===================================================================================================
# EvalDataNode
#===================================================================================================
class EvalDataNode(DataNode):
    """
    DataNode class for evaluating a function on input from neighboring DataNodes
    
    The EvalDataNode is constructed with a function reference and any number of arguments to
    that function.  The number of arguments supplied must match the number of arguments accepted
    by the function.  The arguments can be any type, and the order of the arguments will be
    preserved in the call signature of the function.  If the arguments are of type DataNode,
    then a reference to the DataNode will be stored.  If the arguments are of any other type, the
    argument will be stored by the EvalDataNode.

    This is a "non-source"/"non-sink" DataNode.
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
            if isinstance(data, DataArray):
                return data[self._align_indices_(index, data.dimensions)]
            else:
                return data
        else:
            args = []
            for d in self._inputs:
                if isinstance(d, DataNode):
                    args.append(d[index])
                elif isinstance(d, DataArray):
                    args.append(d[self._align_indices_(index, d.dimensions)])
                else:
                    args.append(d)
            return self._function(*args)


#===================================================================================================
# MapDataNode
#===================================================================================================
class MapDataNode(DataNode):
    """
    DataNode class to map data from a neighboring DataNode to a new variable
    
    The MapDataNode takes additional attributes in its initializer that can effect the 
    behavior of this DataNode's __getitem__ method.  The special attributes are:
    
        'valid_min': The minimum value the data should have, if valid
        'valid_max': The maximum value the data should have, if valid
        'min_mean_abs': The minimum acceptable value of the mean of the absolute value of the data
        'max_mean_abs': The maximum acceptable value of the mean of the absolute value of the data
    
    If these attributes are supplied to the MapDataNode at construction time, then the
    associated validation checks will be made on the data when __getitem__ is called.
    
    Some additional special attributes are:
    
        'units': The name of the units to assign to this data
        'calendar': The name of the calendar to use if the units are time-like
        'dimensions': A tuple of dimension names to associate with the axes of the data
    
    This is a "non-source"/"non-sink" DataNode.
    """

    def __init__(self, label, dnode, dmap={}, dimensions=None, **attributes):
        """
        Initializer
        
        Parameters:
            label: A label to give the DataNode
            dnode (DataNode): DataNode that provides input into this DataNode
            dmap (dict): A dictionary mapping dimension names of the input data to
                new dimensions names for the output variable
            dimensions (tuple): The output dimensions for the mapped variable
            attributes: Additional named arguments corresponding to additional attributes
                to which to associate with the new variable
        """
        # Check DataNode type
        if not isinstance(dnode, DataNode):
            raise TypeError('MapDataNode can only act on output from another DataNode')

        # Store the dimension map
        self._dmap = dmap

        # Store the attributes given to the
        self._attributes = attributes

        # Check for dimensions (necessary)
        if dimensions is None:
            raise DimensionsError('Must supply dimensions to MapDataNode')
        elif not isinstance(dimensions, tuple):
            raise TypeError('Dimensions must be a tuple')
        self._dimensions = dimensions

        # Call base class initializer
        super(MapDataNode, self).__init__(label, dnode)

    @property
    def attributes(self):
        """
        Attributes dictionary
        """
        return self._attributes

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """

        # Compute the output units from internal attributes
        out_units = Unit(self.attributes.get('units', 1),
                         calendar=self.attributes.get('calendar', None))

        # Compute the output dimensions from internal attributes
        out_dims = self._dimensions

        # Compute the input index in terms of input dimensions
        if index is None:
            in_index = dict((self._dmap.get(d, d), slice(0, 0)) for d in out_dims)
        elif isinstance(index, dict):
            in_index = dict((self._dmap.get(k, k), v) for k, v in index.iteritems())
        else:
            in_index = dict((self._dmap.get(k, k), v) for k, v in zip(out_dims, numpy.index_exp[index]))

        # Get the data to assign
        in_data = self._inputs[0][in_index]

        # Validate minimum
        if 'valid_min' in self.attributes:
            dmin = numpy.min(in_data)
            if dmin < self.attributes['valid_min']:
                warning(('Data from operator {!r} has minimum value '
                         '{} but requires data greater than or equal to '
                         '{}').format(self.name, dmin, self._min))

        # Validate maximum
        if 'valid_max' in self.attributes:
            dmax = numpy.max(in_data)
            if dmax > self.attributes['valid_max']:
                warning(('Data from operator {!r} has maximum value '
                         '{} but requires data less than or equal to '
                         '{}').format(self.name, dmax, self._max))

        # Compute mean of the absolute value, if necessary
        if 'ok_min_mean_abs' in self.attributes or 'ok_max_mean_abs' in self.attributes:
            mean_abs = numpy.mean(numpy.abs(in_data))

        # Validate minimum mean abs
        if 'ok_min_mean_abs' in self.attributes:
            if mean_abs < self.attributes['ok_min_mean_abs']:
                warning(('Data from operator {!r} has minimum mean_abs value '
                         '{} but requires data greater than or equal to '
                         '{}').format(self.name, mean_abs, self._min_mean_abs))

        # Validate maximum mean abs
        if 'ok_max_mean_abs' in self.attributes:
            if mean_abs > self.attributes['ok_max_mean_abs']:
                warning(('Data from operator {!r} has maximum mean_abs value '
                         '{} but requires data less than or equal to '
                         '{}').format(self.name, mean_abs, self._max_mean_abs))

        return DataArray(in_data, units=out_units, dimensions=out_dims)
