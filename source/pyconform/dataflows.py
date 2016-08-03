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
from pyconform.indexing import index_str, join, align_index
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
    about the array data, including cfunits and dimensions.
    """

    def __new__(cls, inarray, cfunits=None, dimensions=None, dshape=None):
        obj = numpy.ma.asarray(inarray).view(cls)

        if cfunits is None:
            if 'cfunits' not in obj._optinfo:
                obj._optinfo['cfunits'] = Unit(1)
        elif isinstance(cfunits, Unit):
            obj._optinfo['cfunits'] = cfunits
        else:
            obj._optinfo['cfunits'] = Unit(cfunits)

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
        
        if dshape is None:
            if 'dshape' not in obj._optinfo:
                obj._optinfo['dshape'] = obj.shape
        elif isinstance(dshape, tuple):
            if len(dshape) != len(obj.shape):
                raise ValueError(('Dimension shape {} length does not match DataArray with {} '
                                  'axes').format(dshape, len(obj.shape)))
            obj._optinfo['dshape'] = dshape
        else:
            raise TypeError(('Cannot set DataArray object with dimension shape of type '
                             '{}').format(type(dshape)))

        return obj

    def __repr__(self):
        return ('{!s}(data = {!s}, mask = {!s}, fill_value = {!s}, cfunits = {!r}, '
                'dimensions = {!s})').format(self.__class__.__name__, self.data, self.mask,
                                             self.fill_value, str(self.cfunits), self.dimensions)

    @property
    def cfunits(self):
        return self._optinfo['cfunits']

    @property
    def dimensions(self):
        return self._optinfo['dimensions']

    @property
    def dshape(self):
        return self._optinfo['dshape']


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

    def __init__(self, label, data, cfunits=None, dimensions=None):
        """
        Initializer
        
        Parameters:
            label: A label to give the DataNode
            data (array): Data to store in this DataNode
            cfunits: Units to associate with the data
            dimensions: Dimensions to associate with the data 
        """
        # Store data
        self._data = DataArray(data, cfunits=cfunits, dimensions=dimensions)

        # Call base class initializer
        super(CreateDataNode, self).__init__(label)

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """
        return self._data[align_index(index, self._data.dimensions)]


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

            # Read the variable cfunits
            attrs = ncvar.ncattrs()
            units_attr = ncvar.getncattr('units') if 'units' in attrs else 1
            calendar_attr = ncvar.getncattr('calendar') if 'calendar' in attrs else None
            try:
                cfunits = Unit(units_attr, calendar=calendar_attr)
            except:
                cfunits = Unit(1)

            # Read the original variable dimensions
            dimensions0 = ncvar.dimensions

            # Align the read-indices on dimensions
            index1 = align_index(self._index, dimensions0)

            # Get the dimensions after application of the first index
            dimensions1 = tuple(d for d, i in zip(dimensions0, index1) if isinstance(i, slice))

            # Align the second index on the intermediate dimensions
            index2 = align_index(index, dimensions1)

            # Get the dimensions after application of the second index
            dimensions2 = tuple(d for d, i in zip(dimensions1, index2) if isinstance(i, slice))

            # Get the shape of the original variable
            shape0 = ncvar.shape

            # Compute the joined index object
            index12 = join(shape0, index1, index2)

            data = DataArray(ncvar[index12], cfunits=cfunits, dimensions=dimensions2, dshape=shape0)

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
                return data[align_index(index, data.dimensions)]
            else:
                return data
        else:
            args = []
            for d in self._inputs:
                if isinstance(d, DataNode):
                    args.append(d[index])
                elif isinstance(d, DataArray):
                    args.append(d[align_index(index, d.dimensions)])
                else:
                    args.append(d)
            return self._function(*args)


#===================================================================================================
# MapDataNode
#===================================================================================================
class MapDataNode(DataNode):
    """
    DataNode class to map input data from a neighboring DataNode to new dimension names and cfunits
    
    The MapDataNode can rename the dimensions of a DataNode's output data.  It does not change the
    data itself, however.  If the input dimensions cannot be mapped to the specified output
    dimensions in the order they are specified, then a DimensionsError will be raised.  A
    transposition should be done to change the order of the data dimensions in such a case.
    
    This is a "non-source"/"non-sink" DataNode.
    """

    def __init__(self, label, indata, dmap={}, dimensions=None):
        """
        Initializer
        
        Parameters:
            label: The label given to the DataNode
            indata (DataNode): DataNode that provides input into this DataNode
            dmap (dict): A dictionary mapping dimension names of the input data to
                new dimensions names for the output variable
            dimensions (tuple): The output dimensions for the mapped variable
        """
        # Check DataNode type
        if not isinstance(indata, DataNode):
            raise TypeError('MapDataNode can only act on output from another DataNode')

        # Store the dimension map
        self._dmap = dmap

        # Check for dimensions (necessary)
        if dimensions is None:
            raise DimensionsError('Must supply dimensions to MapDataNode')
        elif not isinstance(dimensions, tuple):
            raise TypeError('Dimensions must be a tuple')
        self._dimensions = dimensions

        # Call base class initializer
        super(MapDataNode, self).__init__(label, indata)

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """

        # Request the input information without pulling data
        in_info = self._inputs[0][None]

        # Get the input data dimensions
        in_dims = in_info.dimensions

        # Compute the output dimensions from internal attributes
        out_dims = self._dimensions

        # The input/output dimensions should be the same
        # OR should be contained in the dimension map
        for od in out_dims:
            d = self._dmap.get(od, od)
            if d not in in_dims:
                raise DimensionsError(('Output dimension {!r} cannot be mapped to any input '
                                       'dimension: {}').format(od, in_dims))

        # Compute the input index in terms of input dimensions
        if index is None:
            in_index = dict((self._dmap.get(d, d), slice(0, 0)) for d in out_dims)
        elif isinstance(index, dict):
            in_index = dict((self._dmap.get(k, k), v) for k, v in index.iteritems())
        else:
            in_index = dict((self._dmap.get(k, k), v)
                            for k, v in zip(out_dims, numpy.index_exp[index]))

        # Return the mapped data
        return DataArray(self._inputs[0][in_index], dimensions=out_dims)


#===================================================================================================
# PassDataNode
#===================================================================================================
class PassDataNode(DataNode):
    """
    DataNode class to validate input data from a neighboring DataNode
    
    The PassDataNode takes additional attributes in its initializer that can effect the 
    behavior of its __getitem__ method.  The special attributes are:
    
        'valid_min': The minimum value the data should have, if valid
        'valid_max': The maximum value the data should have, if valid
        'min_mean_abs': The minimum acceptable value of the mean of the absolute value of the data
        'max_mean_abs': The maximum acceptable value of the mean of the absolute value of the data
    
    If these attributes are supplied to the PassDataNode at construction time, then the
    associated validation checks will be made on the data when __getitem__ is called.
    
    Additional attributes may be added to the PassDataNode that do not affect functionality.
    These attributes may be named however the user wishes and can be retrieved from the DataNode
    as a dictionary with the 'attributes' property.

    This is a "non-source"/"non-sink" DataNode.
    """

    def __init__(self, label, indata, cfunits=None, dimensions=None, error=False, attributes={}):
        """
        Initializer
        
        Parameters:
            label: The label associated with this DataNode
            indata (DataNode): DataNode that provides input into this DataNode
            cfunits (Unit): CF units to validate against
            dimensions (tuple): The output dimensions to validate against
            error (bool): If True, raise exceptions instead of warnings
            attributes: Additional named arguments corresponding to additional attributes
                to which to associate with the new variable
        """
        # Check DataNode type
        if not isinstance(indata, DataNode):
            raise TypeError('MapDataNode can only act on output from another DataNode')

        # Call base class initializer
        super(PassDataNode, self).__init__(label, indata)

        # Save error flag
        self._error = bool(error)

        # Check for dimensions (necessary)
        if dimensions is not None and not isinstance(dimensions, tuple):
            raise TypeError('Dimensions must be a tuple')
        self._dimensions = dimensions

        # Make attributes consistent with cfunits and store cfunits
        if cfunits is None:
            if 'units' in attributes:
                self._cfunits = Unit(attributes['units'], calendar=attributes.get('calendar', None))
            else:
                self._cfunits = None
        else:
            self._cfunits = Unit(cfunits)
            attributes['units'] = str(cfunits)
            if self._cfunits.calendar is not None:
                attributes['calendar'] = str(self._cfunits.calendar)

        # Store the attributes given to the DataNode
        self._attributes = attributes

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """

        # Request the input information without pulling data
        in_info = self._inputs[0][None]

        # Check that units match as expected
        if self._cfunits is not None and self._cfunits != in_info.cfunits:
            msg = ('Units {!s} do not match expected units {!r} in PassDataNode '
                   '{!r}').format(self._cfunits, in_info.cfunits, self.label)
            if self._error:
                raise UnitsError(msg)
            else:
                warning(msg)

        # Check that the dimensions match as expected
        if self._dimensions is not None and self._dimensions != in_info.dimensions:
            msg = ('Dimensions {!s} do not match expected units {!r} in PassDataNode '
                   '{!r}').format(self._dimensions, in_info.dimensions, self.label)
            if self._error:
                raise DimensionsError(msg)
            else:
                warning(msg)

        # Get the data to validate
        in_data = self._inputs[0][index]

        # Testing parameters
        valid_min = self._attributes.get('valid_min', None)
        valid_max = self._attributes.get('valid_max', None)
        ok_min_mean_abs = self._attributes.get('ok_min_mean_abs', None)
        ok_max_mean_abs = self._attributes.get('ok_max_mean_abs', None)

        # Validate minimum
        if valid_min:
            dmin = numpy.min(in_data)
            if dmin < valid_min:
                warning(('Data from operator {!r} has minimum value '
                         '{} but requires data greater than or equal to '
                         '{}').format(self.label, dmin, valid_min))

        # Validate maximum
        if valid_max:
            dmax = numpy.max(in_data)
            if dmax > valid_max:
                warning(('Data from operator {!r} has maximum value '
                         '{} but requires data less than or equal to '
                         '{}').format(self.label, dmax, valid_max))

        # Compute mean of the absolute value, if necessary
        if ok_min_mean_abs or ok_max_mean_abs:
            mean_abs = numpy.mean(numpy.abs(in_data))

        # Validate minimum mean abs
        if ok_min_mean_abs:
            if mean_abs < ok_min_mean_abs:
                warning(('Data from operator {!r} has minimum mean_abs value '
                         '{} but requires data greater than or equal to '
                         '{}').format(self.label, mean_abs, ok_min_mean_abs))

        # Validate maximum mean abs
        if ok_max_mean_abs:
            if mean_abs > ok_max_mean_abs:
                warning(('Data from operator {!r} has maximum mean_abs value '
                         '{} but requires data less than or equal to '
                         '{}').format(self.label, mean_abs, ok_max_mean_abs))

        return in_data


#===================================================================================================
# WriteDataNode
#===================================================================================================
class WriteDataNode(DataNode):
    """
    DataNode that writes input data to a file
    """

    def __init__(self, filename, *inputs, **kwds):
        """
        Initializer
        
        Parameters:
            filename (str): Name of the file to write
            inputs (PassDataNode): A tuple of PassDataNodes providing input into the file
            unlimited (tuple): A tuple of dimensions that should be written as unlimited dimensions
                (This parameter is pulled from the kwds argument to the initializer, if given.)
            attributes (dict): Dictionary of global attributes to write to the file
                (This parameter is pulled from the kwds argument to the initializer, if given.)
        """
        # Check filename
        if not isinstance(filename, basestring):
            raise TypeError('Filename must be of string type')
        
        # Check and store input variables
        for inp in inputs:
            if not isinstance(inp, PassDataNode):
                raise TypeError(('WriteDataNode {!r} cannot accept input from type '
                                 '{}').format(filename, type(inp)))

        # Call base class (label is filename)
        super(WriteDataNode, self).__init__(filename, *inputs)
        
        # Grab the unlimited dimensions parameter and check type
        unlimited = kwds.pop('unlimited', ())
        if not isinstance(unlimited, tuple):
            raise TypeError('Unlimited dimensions must be given as a tuple')
        self._unlimited = unlimited
        
        # Save the global attributes
        self._attributes = kwds
        
        # Set the filehandle
        self._file = None

    def close(self):
        """
        Close the file associated with the WriteDataNode
        """
        if self._file is not None:
            self._file.close()
        
    def __getitem__(self, index):

        if self._file is None:
            
            # Open the output file
            self._file = Dataset(self.label, 'w')
        
            # Write the global attributes
            self._file.setncatts(self._attributes)
            
            # Get info for each input node by name
            varinfos = dict((node.label, node[None]) for node in self._inputs)
    
            # Determine the required dimensions from the input variables
            req_dims = dict()
            for vinfo in varinfos.itervalues():
                for dname, dsize in zip(vinfo.dimensions, vinfo.dshape):
                    if dname in req_dims and dsize != req_dims[dname]:
                        raise DimensionsError(('Dimension {!r} has incompatable sizes {} and '
                                               '{}').format(dname, dsize, req_dims[dname]))
                    else:
                        req_dims[dname] = dsize
                
            # Create the required dimensions
            for dname, dsize in req_dims.iteritems():
                if dname in self._unlimited:
                    self._file.createDimension(dname)
                else:
                    self._file.createDimension(dname, dsize)
    
            # Create the variables and write their attributes
            ncvars = {}
            for vnode in self._inputs:
                vname = vnode.label
                vinfo = varinfos[vname]
                ncvar = self._file.createVariable(vname, str(vinfo.dtype), vinfo.dimensions)
                for aname, avalue in vnode._attributes.iteritems():
                    ncvar.setncattr(aname, avalue)
                ncvars[vname] = ncvar

        # Now perform use the data flows to stream data into the file
        for vnode in self._inputs:
            ncvar[vnode.label][index] = vnode[index]
