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

from numpy.ma import MaskedArray, asarray
from cf_units import Unit
from inspect import getargspec, isfunction
from os.path import exists
from netCDF4 import Dataset


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
class DataArray(MaskedArray):
    """
    A DataArray is the basic object passed along the edges of a Data Flow graph
    
    Derived from Numpy MaskedArray, the DataArray contains additional information
    about the array data, including units and dimensions.
    """

    def __new__(cls, inarray, units=None, dimensions=None):
        obj = asarray(inarray).view(cls)

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
    The basic object that can appear in a Data Flow.
    
    The Node object represents a point in the directed acyclic graph where multiple
    edges meet.  It represents a functional operation on the DataArrays coming into it from
    its adjacent DataNodes.  The DataNode itself outputs the result of this operation
    through the __getitem__ interface (i.e., DataNode[item]), returning a slice of a
    DataArray.
    """

    def __init__(self, label, func, *args):
        """
        Initializer
        
        Parameters:
            label: A label to give the DataNode
            func (callable): A callable function associated with the DataNode operation
            args (tuple): Arguments to the function given by 'func'
        """
        self._label = label

        if callable(func):
            if hasattr(func, '__call__') and isfunction(func.__call__):
                argspec = getargspec(func.__call__)
            else:
                argspec = getargspec(func)
        else:
            raise TypeError('Function argument to DataNode {} is not callable'.format(label))

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
        self._function = func
        self._arguments = args

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """
        if len(self._arguments) == 0:
            data = self._function()
            return data[index] if isinstance(data, DataArray) else data
        else:
            args = tuple(d[index] if isinstance(d, (DataArray, DataNode)) else d
                         for d in self._arguments)
            return self._function(*args)

    @property
    def label(self):
        return self._label


#===================================================================================================
# DataNode
#===================================================================================================
class ReaderNode(DataNode):
    """
    Basic class for reading data from a NetCDF file
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

        # Attempt to open the NetCDF file
        try:
            ncfile = Dataset(self._filepath, 'r')
        except:
            raise OSError('Cannot open as a NetCDF file: {!r}'.format(self._filepath))

        # Parse variable name
        if not isinstance(variable, basestring):
            raise TypeError('Unrecognized variable name object of type '
                            '{!r}: {!r}'.format(type(variable), variable))
        if variable not in ncfile.variables:
            raise OSError('Variable {!r} not found in NetCDF file: '
                          '{!r}'.format(variable, self._filepath))
        self._variable = variable

        # Parse the reading index
        self._shape = ncfile.variables[variable].shape
        self._index = ReaderNode._index_to_tuple_(index, len(self._shape))

        # Set the node label
        self._label = '{0}{1}'.format(variable, ReaderNode._index_to_str_(index))

        # Close the NetCDF file
        ncfile.close()

    @staticmethod
    def _index_to_str_(index):
        idx_str = ''
        if isinstance(index, int):
            idx_str += str(index)
        elif isinstance(index, Ellipsis):
            idx_str += '...'
        elif isinstance(index, slice):
            if index.start is not None:
                idx_str += str(index.start)
            idx_str += ':'
            if index.stop is not None:
                idx_str += str(index.stop)
            if index.step is not None:
                idx_str += ':{!s}'.format(index.step)
        elif isinstance(index, tuple):
            idx_str += ', '.join(ReaderNode._index_to_str_(idx) for idx in index)
        else:
            raise TypeError('ReaderNode index contains bad type {}'.format(type(index)))
        return '[{}]'.format(idx_str)

    @staticmethod
    def _index_to_tuple_(index, ndim):
        if isinstance(index, (int, slice)):
            idx_list = [index] + [slice(None)] * (ndim - 1)
        elif isinstance(index, Ellipsis):
            idx_list = [slice(None)] * ndim
        elif isinstance(index, tuple):
            idx_list = sum(ReaderNode._index_to_tuple_(i, 1) for i in index)
        else:
            raise TypeError('ReaderNode index contains bad type {}'.format(type(index)))
        return tuple(idx_list)

    @property
    def variable(self):
        return self._variable

    def __getitem__(self, index):
        """
        Read DataArray from file
        """
        ncfile = Dataset(self._filepath, 'r')
        ncvar = ncfile.variables[self.variable]

        # Read the units
        attrs = ncvar.ncattrs()
        units_attr = ncvar.getncattr('units') if 'units' in attrs else 1
        calendar_attr = ncvar.getncattr('calendar') if 'calendar' in attrs else None
        try:
            units = Unit(units_attr, calendar=calendar_attr)
        except:
            units = Unit(1)

        # Read the shape of the variable
        shape = ncvar.shape

        # Read the dimensions
        dimensions = ncvar.dimensions

        data = [self._index]
        ncfile.close()
        return data
