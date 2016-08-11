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
from pyconform.indexing import index_str, join, align_index, index_tuple
from pyconform.datasets import InputDataset, OutputDataset
from pyconform.parsing import parse_definition, ParsedVariable, ParsedFunction
from pyconform.physicalarrays import PhysicalArray, UnitsError, DimensionsError
from pyconform.functions import find, ConvertFunction, TransposeFunction
from cf_units import Unit
from inspect import getargspec, isfunction
from os.path import exists
from netCDF4 import Dataset
from sys import stderr
from itertools import cycle as itercycle

import numpy


#===============================================================================
# warning - Helper function
#===============================================================================
def warning(*objs):
    print("WARNING:", *objs, file=stderr)


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
    PhysicalArray.
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
        self._inputs = list(inputs)

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

    @property
    def inputs(self):
        """
        Inputs into this DataNode
        """
        return self._inputs


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
        self._data = PhysicalArray(data, cfunits=cfunits, dimensions=dimensions)

        # Call base class initializer
        super(CreateDataNode, self).__init__(label)

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """
        return self._data[index]


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

        # Check variable name type and existence in the file
        if not isinstance(variable, basestring):
            raise TypeError('Unrecognized variable name object of type '
                            '{!r}: {!r}'.format(type(variable), variable))
        with Dataset(self._filepath, 'r') as ncfile:
            if variable not in ncfile.variables:
                raise OSError('Variable {!r} not found in NetCDF file: '
                              '{!r}'.format(variable, self._filepath))
        self._variable = variable

        # Store the reading index
        self._index = index

        # Call the base class initializer
        super(ReadDataNode, self).__init__('{0}{1}'.format(variable, index_str(index)))

    @property
    def variable(self):
        return self._variable

    def __getitem__(self, index):
        """
        Read PhysicalArray from file
        """
        with Dataset(self._filepath, 'r') as ncfile:

            # Get a reference to the variable
            ncvar = ncfile.variables[self.variable]

            # Read the variable cfunits
            attrs = ncvar.ncattrs()
            units_attr = ncvar.getncattr('units') if 'units' in attrs else 1
            calendar_attr = ncvar.getncattr('calendar') if 'calendar' in attrs else None
            cfunits = Unit(units_attr, calendar=calendar_attr)

            # Read the original variable dimensions
            dimensions0 = ncvar.dimensions

            # Read the original variable shape
            shape0 = ncvar.shape

            # Align the read-indices on dimensions
            index1 = align_index(self._index, dimensions0)

            # Get the dimensions after application of the first index
            dimensions1 = tuple(d for d, i in zip(dimensions0, index1) if isinstance(i, slice))

            # Compute the original shape after potential dimension reduction
            shape1 = tuple(s for s, i in zip(shape0, index1) if isinstance(i, slice))

            # Align the second index on the intermediate dimensions
            index2 = align_index(index, dimensions1)

            # Get the dimensions after application of the second index
            dimensions2 = tuple(d for d, i in zip(dimensions1, index2) if isinstance(i, slice))

            # Compute the original shape after potential dimension reduction
            shape2 = tuple(s for s, i in zip(shape1, index2) if isinstance(i, slice))

            # Compute the joined index object
            index12 = join(shape0, index1, index2)

            data = PhysicalArray(ncvar[index12], cfunits=cfunits, dimensions=dimensions2,
                                 initialshape=shape2)

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
            if isinstance(data, PhysicalArray):
                return data[index]
            else:
                return data
        else:
            args = [d[index] if isinstance(d, (PhysicalArray, DataNode)) else d for d in self._inputs]
            return self._function(*args)


#===================================================================================================
# MapDataNode
#===================================================================================================
class MapDataNode(DataNode):
    """
    DataNode class to map input data from a neighboring DataNode to new dimension names and cfunits
    
    The MapDataNode can rename the dimensions of a DataNode's output data.  It does not change the
    data itself, however.  The input dimension names will be changed according to the dimension
    map given.  If an input dimension name is not referenced by the map, then the input dimension
    name does not change.
    
    This is a "non-source"/"non-sink" DataNode.
    """

    def __init__(self, label, dnode, dmap={}):
        """
        Initializer
        
        Parameters:
            label: The label given to the DataNode
            dnode (DataNode): DataNode that provides input into this DataNode
            dmap (dict): A dictionary mapping dimension names of the input data to
                new dimensions names for the output variable
            dimensions (tuple): The output dimensions for the mapped variable
        """
        # Check DataNode type
        if not isinstance(dnode, DataNode):
            raise TypeError('MapDataNode can only act on output from another DataNode')

        # Check dimension map type
        if not isinstance(dmap, dict):
            raise TypeError('Dimension map must be a dictionary')

        # Store the dimension input-to-output map
        self._i2omap = dmap

        # Construct the reverse mapping
        self._o2imap = dict((v, k) for k, v in dmap.iteritems())

        # Call base class initializer
        super(MapDataNode, self).__init__(label, dnode)

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """

        # Request the input information without pulling data
        inp_info = self._inputs[0][None]

        # Get the input data dimensions
        inp_dims = inp_info.dimensions

        # The input/output dimensions will be the same
        # OR should be contained in the input-to-output dimension map
        out_dims = tuple(self._i2omap.get(d, d) for d in inp_dims)

        # Compute the input index in terms of input dimensions
        if index is None:
            inp_index = dict((d, slice(0, 0)) for d in inp_dims)

        elif isinstance(index, dict):
            inp_index = dict((self._o2imap.get(d, d), i) for d, i in index.iteritems())

        else:
            out_index = index_tuple(index, len(inp_dims))
            inp_index = dict((self._o2imap.get(d, d), i) for d, i in zip(out_dims, out_index))

        # Return the mapped data
        return PhysicalArray(self._inputs[0][inp_index], dimensions=out_dims)


#===================================================================================================
# ValidateDataNode
#===================================================================================================
class ValidateDataNode(DataNode):
    """
    DataNode class to validate input data from a neighboring DataNode
    
    The ValidateDataNode takes additional attributes in its initializer that can effect the 
    behavior of its __getitem__ method.  The special attributes are:
    
        'valid_min': The minimum value the data should have, if valid
        'valid_max': The maximum value the data should have, if valid
        'min_mean_abs': The minimum acceptable value of the mean of the absolute value of the data
        'max_mean_abs': The maximum acceptable value of the mean of the absolute value of the data
    
    If these attributes are supplied to the ValidateDataNode at construction time, then the
    associated validation checks will be made on the data when __getitem__ is called.
    
    Additional attributes may be added to the ValidateDataNode that do not affect functionality.
    These attributes may be named however the user wishes and can be retrieved from the DataNode
    as a dictionary with the 'attributes' property.

    This is a "non-source"/"non-sink" DataNode.
    """

    def __init__(self, label, dnode, **attribs):
        """
        Initializer
        
        Parameters:
            label: The label associated with this DataNode
            dnode (DataNode): DataNode that provides input into this DataNode
            cfunits (Unit): CF units to validate against
            dimensions (tuple): The output dimensions to validate against
            error (bool): If True, raise exceptions instead of warnings
            attribs: Additional named arguments corresponding to additional attributes
                to which to associate with the new variable
        """
        # Check DataNode type
        if not isinstance(dnode, DataNode):
            raise TypeError('ValidateDataNode can only act on output from another DataNode')

        # Call base class initializer
        super(ValidateDataNode, self).__init__(label, dnode)

        # Save error flag
        self._error = bool(attribs.pop('error', False))

        # Check for dimensions
        dimensions = attribs.pop('dimensions', None)
        if dimensions is not None and not isinstance(dimensions, tuple):
            raise TypeError('Dimensions must be a tuple')
        self._dimensions = dimensions

        # Make attributes consistent with cfunits and store cfunits
        cfunits = attribs.pop('cfunits', None)
        if cfunits is None:
            if 'units' in attribs:
                self._cfunits = Unit(attribs['units'], calendar=attribs.get('calendar', None))
            else:
                self._cfunits = None
        else:
            self._cfunits = Unit(cfunits)
            attribs['units'] = str(cfunits)
            if self._cfunits.calendar is not None:
                attribs['calendar'] = str(self._cfunits.calendar)

        # Store the attributes given to the DataNode
        self._attributes = {str(a): str(v) for a, v in attribs.iteritems()}

    def __getitem__(self, index):
        """
        Compute and retrieve the data associated with this DataNode operation
        """

        # Get the data to validate
        indata = self._inputs[0][index]

        # Check that units match as expected
        if self._cfunits is not None and self._cfunits != indata.cfunits:
            msg = ('Units {!r} do not match expected units {!r} in ValidateDataNode '
                   '{!r}').format(str(self._cfunits), str(indata.cfunits), self.label)
            if self._error:
                raise UnitsError(msg)
            else:
                warning(msg)

        # Check that the dimensions match as expected
        if self._dimensions is not None and self._dimensions != indata.dimensions:
            msg = ('Dimensions {!s} do not match expected dimensions {!s} in ValidateDataNode '
                   '{!r}').format(self._dimensions, str(indata.dimensions), self.label)
            if self._error:
                raise DimensionsError(msg)
            else:
                warning(msg)

        # Testing parameters
        valid_min = self._attributes.get('valid_min', None)
        valid_max = self._attributes.get('valid_max', None)
        ok_min_mean_abs = self._attributes.get('ok_min_mean_abs', None)
        ok_max_mean_abs = self._attributes.get('ok_max_mean_abs', None)

        # Validate minimum
        if valid_min:
            dmin = numpy.min(indata)
            if dmin < valid_min:
                warning(('Data from operator {!r} has minimum value '
                         '{} but requires data greater than or equal to '
                         '{}').format(self.label, dmin, valid_min))

        # Validate maximum
        if valid_max:
            dmax = numpy.max(indata)
            if dmax > valid_max:
                warning(('Data from operator {!r} has maximum value '
                         '{} but requires data less than or equal to '
                         '{}').format(self.label, dmax, valid_max))

        # Compute mean of the absolute value, if necessary
        if ok_min_mean_abs or ok_max_mean_abs:
            mean_abs = numpy.mean(numpy.abs(indata))

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

        return indata


#===================================================================================================
# WriteDataNode
#===================================================================================================
class WriteDataNode(DataNode):
    """
    DataNode that writes validated data to a file
    """

    def __init__(self, filename, *inputs, **kwds):
        """
        Initializer
        
        Parameters:
            filename (str): Name of the file to write
            inputs (ValidateDataNode): A tuple of ValidateDataNodes providing input into the file
            unlimited (tuple): A tuple of dimensions that should be written as unlimited dimensions
                (This parameter is pulled from the 'kwds' argument, if given.)
            attributes (dict): Dictionary of global attributes to write to the file
                (This parameter is pulled from the 'kwds' argument, if given.)
        """
        # Check filename
        if not isinstance(filename, basestring):
            raise TypeError('Filename must be of string type')

        # Check and store input variables
        for inp in inputs:
            if not isinstance(inp, ValidateDataNode):
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
        self._attributes = {str(a): str(v) for a, v in kwds.iteritems()}

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

            # Generate and collect information for each input data object
            vinfos = {i.label: i[None] for i in self.inputs}

            # Collect the dimension sizes from the initialshape parameter of the input data
            req_dims = {}
            for vinfo in vinfos.itervalues():
                for dname, dsize in zip(vinfo.dimensions, vinfo.initialshape):
                    if dname not in req_dims:
                        req_dims[dname] = dsize
                    elif req_dims[dname] != dsize:
                        raise RuntimeError(('Dimension {!r} has inconsistent size: '
                                            '{}, {}').format(dname, req_dims[dname], dsize))

            # Create the required dimensions for the variable
            for dname, dsize in req_dims.iteritems():
                if dname in self._unlimited:
                    self._file.createDimension(dname)
                else:
                    self._file.createDimension(dname, dsize)

            # Create the variables and write their attributes
            for vnode in self._inputs:
                vname = vnode.label
                vinfo = vinfos[vname]
                ncvar = self._file.createVariable(vname, str(vinfo.dtype), vinfo.dimensions)
                for aname, avalue in vnode._attributes.iteritems():
                    ncvar.setncattr(aname, avalue)

        # Now perform the data flows to stream data into the file
        for vnode in self._inputs:
            ncvar = self._file.variables[vnode.label]
            ncvar[align_index(index, ncvar.dimensions)] = vnode[index]


#===============================================================================
# FlowFactory
#===============================================================================
class FlowFactory(object):
    """
    Object that constructs a data flow
    """

    def __init__(self, inpds, cycle=True):
        """
        Initializer
        
        Parameters:
            inpds (InputDataset): The input dataset to use as reference when
                parsing variable definitions
            cyc (bool): If True, cycles which file to read metadata variables
                from (i.e., variables that exist in all input files).  If False,
                always reads metadata variables from the first input file.
        """
        # Input dataset
        if not isinstance(inpds, InputDataset):
            raise TypeError('Input dataset must be of InputDataset type')
        self._inputds = inpds

        # Cyclic iterator over available input filenames
        fnames = [v.filename for v in self._inputds.variables.itervalues()]
        if cycle:
            self._infile_cycle = itercycle(filter(None, fnames))
        else:
            self._infile_cycle = itercycle([filter(None, fnames)[0]])

        # Initialize the dimension map and the inverse dimension map
        self._i2omap = {}
        self._o2imap = {}

    def from_definitions(self, outds, error=False):
        """
        Construct a data flow from definitions in an output dataset
        
        Parameters:
            outds (OutputDataset): The output dataset defining the output variables and
                their definitions or data
            error (bool): Whether to throw exceptions if validation checks do not pass,
                otherwise just show warnings.
        """
        # Output dataset
        if not isinstance(outds, OutputDataset):
            raise TypeError('Output dataset must be of OutputDataset type')

        # Separate output variables into variables with 'data' or 'definitions'
        withdata = {}
        withdefn = {}
        for vname, vinfo in outds.variables.iteritems():
            if vinfo.data is not None:
                withdata[vname] = vinfo
            elif vinfo.definition is not None:
                withdefn[vname] = vinfo
            else:
                raise ValueError(('Output variable {0} does not have withdata '
                                  'data nor a definition').format(vname))

        # Create a dictionary to store "source" DataNodes from 'data' attributes
        srcnodes = {}

        # First, parse output variables with 'data'
        for vname, vinfo in withdata.iteritems():
            vdata = numpy.array(vinfo.data, dtype=vinfo.datatype)
            vshape = tuple(outds.dimensions[d].size for d in vinfo.dimensions)
            cdnode = CreateDataNode(vname, vdata, cfunits=vinfo.cfunits(),
                                    dimensions=vinfo.dimensions, dshape=vshape)
            srcnodes[vname] = cdnode

        # Create a dictionary to store "output variable" DataNodes from 'definition' attributes
        outnodes = {}

        # Parse the output variable with definitions
        for vname, vinfo in withdefn.iteritems():
            obj = parse_definition(vinfo.definition)
            outnodes[vname] = self._construct_flow_(obj, srcnodes=srcnodes)

        # By now, everything should work with the given units and dimensions!
        # So, let's get the informat for each output variable DataNode's data
        dinfos = dict((vname, vnode[None]) for vname, vnode in outnodes.iteritems())

        # Each output variable DataNode must be mapped to its output dimensions.
        # To aid with this, we sort by number of dimensions:
        nodeorder = zip(*sorted((len(vinfo.dimensions), vname)
                                for vname, vinfo in outds.variables.iteritems()))[1]
        for vname in nodeorder:
            out_dims = outds.variables[vname].dimensions
            inp_dims = dinfos[vname].dimensions

            unmapped_out = tuple(d for d in out_dims if d not in self._o2imap)
            mapped_inp = tuple(self._o2imap[d] for d in out_dims if d in self._o2imap)
            unmapped_inp = tuple(d for d in inp_dims if d not in mapped_inp)

            if len(unmapped_out) != len(unmapped_inp):
                raise ValueError(('Cannot map dimensions {} to dimensions '
                                  '{}').format(inp_dims, out_dims))
            if len(unmapped_out) == 0:
                continue
            for out_dim, inp_dim in zip(unmapped_out, unmapped_inp):
                self._o2imap[out_dim] = inp_dim
                self._i2omap[inp_dim] = out_dim

        # Now append the necessary dimension renaming, unit conversion, transposing, validating
        for vname in outnodes:
            dnode = outnodes[vname]
            dinfo = dinfos[vname]

            # Check and convert units, if necessary
            out_units = outds.variables[vname].cfunits()
            if out_units != dinfo.cfunits:
                if dinfo.cfunits.is_convertible(out_units):
                    name = 'C({!s}, to={!r})'.format(dnode, str(out_units))
                    outnodes[vname] = EvalDataNode(name, ConvertFunction, dnode, out_units)
                else:
                    raise ValueError('Cannot convert units {} to {}'.format(dinfo.cfunits, out_units))

            # Map dimensions from input namespace to output namespace
            dnode = outnodes[vname]
            map_dims = tuple(self._i2omap[d] for d in dinfo[vname].dimensions)
            name = 'map({!s}, to={})'.format(vname, map_dims)
            outnodes[vname] = MapDataNode(name, dnode, self._i2omap)

            # Transpose dimensions, if necessary
            dnode = outnodes[vname]
            out_dims = outds.variables[vname].dimensions
            if out_dims != map_dims:
                if set(out_dims) == set(map_dims):
                    name = 'T({!s}, to={!r})'.format(dnode, out_dims)
                    outnodes[vname] = EvalDataNode(name, TransposeFunction, dnode, out_dims)

            # Validate the result
            dnode = outnodes[vname]

        # Now loop through all of the variables and create PassNodes for validation
        varnodes = {}
        for vname, vinfo in outds.variables.iteritems():
            if vname in srcnodes:
                vnode = srcnodes[vname]
            elif vname in outnodes:
                vnode = outnodes[vname]

            vunits = vinfo.cfunits()
            vdims = vinfo.dimensions
            vattrs = vinfo.attributes
            varnodes[vname] = ValidateDataNode(vname, vnode, cfunits=vunits, dimensions=vdims,
                                           error=error, attributes=vattrs)

        # Now determine which output variables have their own output file
        tsvnames = tuple(vname for vname, vinfo in outds.variables.iteritems()
                         if vinfo.filename is not None)
        mvnames = tuple(vname for vname, vinfo in outds.variables.iteritems()
                        if vinfo.filename is None)

        # Create the WriteDataNodes for each time-series output file
        writenodes = {}
        for tsvname in tsvnames:
            tsvinfo = outds.variables[tsvname]
            filename = tsvinfo.filename
            vnodes = tuple(varnodes[n] for n in mvnames) + (varnodes[tsvname],)
            unlimited = tuple(dname for dname, dinfo in outds.dimensions.iteritems()
                              if dinfo.unlimited)
            attribs = dict((k, v) for k, v in outds.attributes.iteritems())
            attribs['unlimited'] = unlimited
            writenodes[tsvname] = WriteDataNode(filename, *vnodes, **attribs)

        return writenodes

    def _construct_flow_(self, obj, srcnodes={}):
        if isinstance(obj, ParsedVariable):
            vname = obj.key
            if vname in self._inputds.variables:
                vinfo = self._inputds.variables[vname]
                if vinfo.filename:
                    fname = vinfo.filename
                else:
                    fname = self._infile_cycle.next()
                return ReadDataNode(fname, vname, index=obj.args)

            elif vname in srcnodes:
                return srcnodes[vname]

            else:
                raise KeyError('Variable {0!r} not found or cannot be used as input'.format(vname))

        elif isinstance(obj, ParsedFunction):
            name = obj.key
            nargs = len(obj.args)
            func = find(name, numargs=nargs)
            args = [self._construct_flow_(arg, srcnodes) for arg in obj.args]
            if all(isinstance(o, (int, float)) for o in args):
                return func(*args)
            return self._try_fix_(EvalDataNode(name, func, *args))

        else:
            return obj

    def _try_fix_(self, dnode):
        """
        Try to fix a DataNode's units and dimensions
        """
        try:
            dnode[None]

        except UnitsError as e:
            if not e.hints:
                raise ValueError('UnitsError without hints')

            iarg, req_units = e.hints.popitem()
            arg = dnode.inputs[iarg]
            name = 'C({!s}, to={!r})'.format(arg, str(req_units))
            dnode.inputs[iarg] = EvalDataNode(name, ConvertFunction, arg, req_units)
            self._try_fix_(dnode)

        except DimensionsError as e:
            for iarg, req_dims in e.hints.iteritems():
                if not all(d in self._inputds.dimensions for d in req_dims):
                    continue
                arg = dnode.inputs[iarg]

                if isinstance(arg, CreateDataNode):
                    arg_dims = arg._data.dimensions
                    if len(arg_dims) != len(req_dims):
                        raise ValueError(('Dimensions {} cannot be mapped to '
                                          '{}').format(req_dims, arg_dims))
                    rdmap = {}
                    for out_dim, inp_dim in zip(arg_dims, req_dims):
                        if out_dim not in self._dmap:
                            rdmap[inp_dim] = out_dim
                            self._dmap[out_dim] = inp_dim
                        elif self._dmap[out_dim] != inp_dim:
                            raise ValueError(('Output dimension {!r} appears to '
                                              'map to input dimensions {!r} and '
                                              '{!r}').format(out_dim, inp_dim, self._dmap[out_dim]))
                    name = 'map({!s}, to={})'.format(arg, req_dims)
                    dnode.inputs[iarg] = MapDataNode(name, arg, rdmap, req_dims)
                    self._try_fix_(dnode)

                else:
                    name = 'T({!s}, to={!r})'.format(arg, req_dims)
                    dnode.inputs[iarg] = EvalDataNode(name, TransposeFunction, arg, req_dims)
                    self._try_fix_(dnode)

            raise ValueError('Dimensions cannot be mapped or transposed')

        except:
            raise
