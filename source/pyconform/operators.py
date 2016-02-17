"""
Fundamental Operators for the Operation Graphs

This module contains the Operator objects to be used in the DiGraph-based
Operation Graphs that implement the data transformation operations.

Some functions of the Operator objects are specifically designed to work
on the output from other Operators, from within a OperationGraph object.
This is precisely what the Operators are designed to do.  Some data of
the Operators pertain to the instance of the Operator itself, and this data
is stored with the instance.  Some data is determined entirely by the input
into the Operator at runtime, which occurs within the OperationGraph data
structure.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from __future__ import print_function
from abc import ABCMeta, abstractmethod
from netCDF4 import Dataset
from os.path import exists
from mpi4py import MPI
from cf_units import Unit
from sys import stderr

import numpy


#===============================================================================
# warning - Helper function
#===============================================================================
def warning(*objs):
    print("WARNING:", *objs, file=stderr)


#===============================================================================
# Operator
#===============================================================================
class Operator(object):
    """
    The abstract base class for the Operator objects used in OperationGraphs
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, name, units=Unit(1), dimensions=()):
        """
        Initializer
        
        Parameters:
            name (str): A string name/identifier for the operator
            units (Unit): The units of the data returned by the function
            dimensions (tuple): Dimensions of the returned data
        """
        if not isinstance(name, (str, unicode)):
            raise TypeError('Operator names must be strings')
        self._name = name

        if not isinstance(units, Unit):
            raise TypeError('Operator units must be of Unit type')
        self._units = units
        
        if not isinstance(dimensions, tuple):
            raise TypeError('Operator dimensions must be tuples')
        self._dimensions = dimensions
    
    @property
    def name(self):
        """
        Return the internal name of the Operator
        """
        return self._name

    @property
    def units(self):
        """
        Return the Unit object for the data returned by the Operator
        """
        return self._units

    @property
    def dimensions(self):
        """
        Return the dimensions of the data returned by the Operator
        """
        return self._dimensions
            
    def __str__(self):
        """
        String representation of the operator (its name)
        """
        return str(self._name)
    
    @abstractmethod
    def __eq__(self, other):
        """
        Check if two Operators are equal
        """
        if not isinstance(other, Operator):
            return False
        elif self._name != other._name:
            return False
        elif self._units != other._units:
            return False
        elif self._dimensions != other._dimensions:
            return False
        else:
            return True

    @abstractmethod
    def __call__(self):
        """
        Make callable like a function
        """
        pass
    

#===============================================================================
# InputSliceReader
#===============================================================================
class InputSliceReader(Operator):
    """
    Operator that reads an input variable slice upon calling
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
        
        # Determine units
        uname = getattr(ncfile.variables[variable], 'units', '1')
        ucal = getattr(ncfile.variables[variable], 'calendar', None)
        units = Unit(uname, calendar=ucal)
        
        # Determine dimensions
        dims = ncfile.variables[variable].dimensions

        # Close the NetCDF file
        ncfile.close()

        # Call base class initializer - sets self._name
        super(InputSliceReader, self).__init__(variable, units=units,
                                               dimensions=dims)

    def __eq__(self, other):
        """
        Check if two Operators are equal
        """
        if not isinstance(other, InputSliceReader):
            return False
        elif self._filepath != other._filepath:
            return False
        elif self._slice != other._slice:
            return False
        else:
            return super(InputSliceReader, self).__eq__(other)
    
    def __call__(self):
        """
        Make callable like a function
        """
        ncfile = Dataset(self._filepath, 'r')
        data = ncfile.variables[self._name][self._slice]
        ncfile.close()
        return data


#===============================================================================
# FunctionEvaluator
#===============================================================================
class FunctionEvaluator(Operator):
    """
    Generic function operator that acts on two operands
    """
    
    def __init__(self, name, func, args=[], units=Unit(1), dimensions=()):
        """
        Initializer
        
        Parameters:
            name (str): A string name/identifier for the operator
            func (Function): A function with arguments taken from other operators
            args (list): Arguments to the function, in order, where 'None'
                indicates an argument passed in at runtime
            units (Unit): The units of the data returned by the function
            dimensions (tuple): Dimensions of the returned data
        """
        # Check function
        if not callable(func):
            raise TypeError('Function object not callable: {!r}'.format(func))
        self._function = func
        
        # Check arguments
        if not isinstance(args, (tuple, list)):
            raise TypeError('Arguments not contained in list')
        self._arguments = args
        
        # Count the number of runtime arguments needed
        self._nargs = sum(arg is None for arg in args)

        # Call base class initializer
        super(FunctionEvaluator, self).__init__(name, units=units,
                                                dimensions=dimensions)

    def __eq__(self, other):
        """
        Check if two Operators are equal
        """
        if not isinstance(other, FunctionEvaluator):
            return False
        elif self._function != other._function:
            return False
        elif self._arguments != other._arguments:
            return False
        elif self._nargs != other._nargs:
            return False
        else:
            return super(FunctionEvaluator, self).__eq__(other)
        
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


#===============================================================================
# OutputSliceHandle
#===============================================================================
class OutputSliceHandle(Operator):
    """
    Operator that acts as a "handle" for output data streams
    """
    
    def __init__(self, name, slicetuple=(slice(None),),
                 units=Unit(1), dimensions=(), minimum=None, maximum=None):
        """
        Initializer
        
        Parameters:
            name (str): A string name/identifier for the operator
            slicetuple (tuple): The slice of the output variable into which
                the data is to be written
            units (Unit): The units returns by this Operator
            dimensions (tuple): Output data dimensions
            minimum: The minimum value the data should have, if valid
            maximum: The maximum value the data should have, if valid
        """
        # Call base class initializer
        super(OutputSliceHandle, self).__init__(name, units=units,
                                                dimensions=dimensions)

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
        
        # Store min/max
        self._min = minimum
        self._max = maximum
        
    @property
    def slicetuple(self):
        return self._slice

    def __eq__(self, other):
        """
        Check if two Operators are equal
        """
        if not isinstance(other, OutputSliceHandle):
            return False
        elif self._slice != other._slice:
            return False
        else:
            return super(OutputSliceHandle, self).__eq__(other)
        
    def __call__(self, data):
        """
        Make callable like a function
        
        Parameters:
            data: The data passed to the mapper
        """
        if self._min is not None:
            dmin = numpy.min(data)
            if dmin < self._min:
                warning(('Data from operator {!r} has minimum value '
                         '{} but requires data greater than or equal to '
                         '{}').format(self.name, dmin, self._min))

        if self._max is not None:
            dmax= numpy.max(data)
            if dmax > self._max:
                warning(('Data from operator {!r} has maximum value '
                         '{} but requires data less than or equal to '
                         '{}').format(self.name, dmax, self._max))
            
        return data
    

#===============================================================================
# SendOperator
#===============================================================================
class SendOperator(Operator):
    """
    Send data to a specified remote rank in COMM_WORLD
    """
    
    def __init__(self, dest, units=Unit(1), dimensions=()):
        """
        Initializer
        
        Parameters:
            dest (int): The destination rank in COMM_WORLD to send the data
            units (Unit): The units of the data returned by the function
            dimensions (tuple): Dimensions of the returned data
        """
        # Check if the function is callable
        if not isinstance(dest, int):
            raise TypeError('Destination rank must be an integer')
        size = MPI.COMM_WORLD.Get_size()
        if dest < 0 or dest >= size:
            raise ValueError(('Destination rank must be between 0 and '
                              '{}').format(size))
        
        # Call base class initializer
        opname = 'send(to={},from={})'.format(dest, MPI.COMM_WORLD.Get_rank())
        super(SendOperator, self).__init__(opname, units=units,
                                           dimensions=dimensions)
        
        # Store the destination rank
        self._dest = dest

    def __eq__(self, other):
        """
        Check if two Operators are equal
        """
        if not isinstance(other, SendOperator):
            return False
        elif self._dest != other._dest:
            return False
        else:
            return super(SendOperator, self).__eq__(other)
        
    def __call__(self, data):
        """
        Make callable like a function
        
        Parameters:
            data: The data to send
        """
        # Check data type
        if not isinstance(data, numpy.ndarray):
            raise TypeError('SendOperator only works with NDArrays')

        # Create the handshake message - Assumes data is an NDArray
        msg = {}
        msg['shape'] = data.shape
        msg['dtype'] = data.dtype

        # Send the handshake message to the RecvOperator
        tag = MPI.COMM_WORLD.Get_rank()
        MPI.COMM_WORLD.send(msg, dest=self._dest, tag=tag)

        # Receive the acknowledgement from the RecvOperator
        tag += MPI.COMM_WORLD.Get_size()
        ack = MPI.COMM_WORLD.recv(source=self._dest, tag=tag)

        # Check the acknowledgement, if not OK error
        if not ack:
            raise RuntimeError(('SendOperator on rank {} failed to '
                                'receive acknowledgement from rank '
                                '{}').format(MPI.COMM_WORLD.Get_rank(),
                                             self._dest))

        # If OK, send the data to the RecvOperator
        tag += MPI.COMM_WORLD.Get_size()
        MPI.COMM_WORLD.Send(data, dest=self._dest, tag=tag)
        return None


#===============================================================================
# RecvOperator
#===============================================================================
class RecvOperator(Operator):
    """
    Receive data from a specified remote rank in COMM_WORLD
    """
    
    def __init__(self, source, units=Unit(1), dimensions=()):
        """
        Initializer
        
        Parameters:
            source (int): The source rank in COMM_WORLD to send the data
            units (Unit): The units of the data returned by the function
            dimensions (tuple): Dimensions of the returned data
        """
        # Check if the function is callable
        if not isinstance(source, int):
            raise TypeError('Source rank must be an integer')
        size = MPI.COMM_WORLD.Get_size()
        if source < 0 or source >= size:
            raise ValueError(('Source rank must be between 0 and '
                              '{}').format(size))
        
        # Call base class initializer
        opname = 'recv(to={},from={})'.format(MPI.COMM_WORLD.Get_rank(), source)
        super(RecvOperator, self).__init__(opname, units=units,
                                           dimensions=dimensions)
        
        # Store the source rank
        self._source = source

    def __eq__(self, other):
        """
        Check if two Operators are equal
        """
        if not isinstance(other, RecvOperator):
            return False
        elif self._source != other._source:
            return False
        else:
            return super(RecvOperator, self).__eq__(other)
        
    def __call__(self):
        """
        Make callable like a function
        """

        # Receive the handshake message from the SendOperator
        tag = self._source
        msg = MPI.COMM_WORLD.recv(source=self._source, tag=tag)

        # Check the message content
        ack = (type(msg) is dict and
               all([key in msg for key in ['shape', 'dtype']]))

        # Send acknowledgement back to the SendOperator
        tag += MPI.COMM_WORLD.Get_size()
        MPI.COMM_WORLD.send(ack, dest=self._source, tag=tag)

        # If acknowledgement is bad, don't receive
        if not ack:
            raise RuntimeError(('RecvOperator on rank {} failed to '
                                'receive acknowledgement from rank '
                                '{}').format(MPI.COMM_WORLD.Get_rank(),
                                             self._dest))

        # Receive the data from the SendOperator
        tag += MPI.COMM_WORLD.Get_size()
        recvd = numpy.empty(msg['shape'], dtype=msg['dtype'])
        MPI.COMM_WORLD.Recv(recvd, source=self._source, tag=tag)        
        return recvd
