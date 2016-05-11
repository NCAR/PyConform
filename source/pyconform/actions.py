"""
Fundamental actions for the Action Graphs

This module contains the Action objects to be used in the DiGraph-based
ActionGraphs that implement the data transformation operations.  Each vertex
in an ActionGraph must be an Action.

Some functions of the Action objects are specifically designed to work
on the output from other Actions, from within an ActionGraph object.
This is precisely what the Actions are designed to do.  Some data of
the Actions pertain to the instance of the Action itself, and this data
is stored with the instance.  Some data is determined entirely by the input
into the Action at runtime, which occurs within the ActionGraph data
structure.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from __future__ import print_function
from abc import ABCMeta, abstractmethod
from pyconform.slicetuple import SliceTuple
from netCDF4 import Dataset
from os.path import exists
from cf_units import Unit
from mpi4py import MPI
from sys import stderr

import numpy


#===============================================================================
# warning - Helper function
#===============================================================================
def warning(*objs):
    print("WARNING:", *objs, file=stderr)


#===============================================================================
# Action
#===============================================================================
class Action(object):
    """
    The abstract base class for the Action objects used in OperationGraphs
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, key, name):
        """
        Initializer
        
        Parameters:
            key (hashable): A hashable key to associate with this Action
            name (str): A string name/identifier for the operator
        """
        if not isinstance(name, (str, unicode)):
            raise TypeError('Action names must be strings')
        self._name = name
        
        # Key
        self._key = key
        
        # Default units
        self._units = None
        
        # Default dimensions
        self._dimensions = None
        
    @property
    def name(self):
        """
        Return the internal name of the Action
        """
        return self._name
    
    @property
    def key(self):
        """
        The hashable key associated with this Action
        """
        return self._key

    def __str__(self):
        """
        String representation of the operation (its name)
        """
        return str(self._name)

    @property
    def units(self):
        """
        The units of the data returned by the operation
        """
        return self._units
    
    @units.setter
    def units(self, u):
        """
        Set the units of the data to be returned by the operation
        """
        if isinstance(u, Unit):
            self._units = u
        elif isinstance(u, tuple):
            self._units = Unit(u[0], calendar=u[1])
        else:
            self._units = Unit(u)

    @property
    def dimensions(self):
        """
        The dimensions tuple of the data returned by the operation
        """
        return self._dimensions
    
    @dimensions.setter
    def dimensions(self, d):
        """
        Set the dimensions tuple of the data returned by the operation
        """
        self._dimensions = tuple(d)

    @abstractmethod
    def __eq__(self, other):
        """
        Check if two Actions are equal
        """
        if not isinstance(other, Action):
            return False
        elif self._key != other._key:
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
        Perform the operation and return the resulting data 
        """
        pass
    

#===============================================================================
# InputSliceReader
#===============================================================================
class InputSliceReader(Action):
    """
    Action that reads an input variable slice upon calling
    """
    
    def __init__(self, filepath, variable, slicetuple=None):
        """
        Initializer
        
        Parameters:
            filepath (str): A string filepath to a NetCDF file 
            variable (str): A string variable name to read
            slicetuple (SliceTuple): A tuple of slice objects specifying the
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
        self._slice = SliceTuple(slicetuple)
        
        # Call base class initializer - sets self._name
        name = '{0}[{1}]'.format(variable, str(self._slice))
        super(InputSliceReader, self).__init__(variable, name)

        # Read/set the units
        if 'units' in ncfile.variables[variable].ncattrs():
            units = ncfile.variables[variable].getncattr('units')
        else:
            units = Unit(1)
        if 'calendar' in ncfile.variables[variable].ncattrs():
            calendar = ncfile.variables[variable].getncattr('calendar')
        else:
            calendar = None
        self._units = Unit(units, calendar=calendar)
        
        # Read/set the dimensions
        self._dimensions = ncfile.variables[variable].dimensions
        
        # Close the NetCDF file
        ncfile.close()
    
    @Action.units.setter
    def units(self, u):
        pass # Prevent from changing units!
    
    @Action.dimensions.setter
    def dimensions(self, d):
        pass # Prevent from changing dimensions!

    @property
    def slicetuple(self):
        return self._slice
    
    def __eq__(self, other):
        """
        Check if two Actions are equal
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
        data = ncfile.variables[self._key][self._slice.index]
        ncfile.close()
        return data


#===============================================================================
# FunctionEvaluator
#===============================================================================
class FunctionEvaluator(Action):
    """
    Generic function operator that acts on two operands
    """
    
    def __init__(self, key, name, func, signature=[]):
        """
        Initializer
        
        Parameters:
            key (hashable): Hashable key associated with the function
            name (str): A string name/identifier for the operator
            func (Function): A function with arguments taken from other operators
            signature (list): Arguments to the function, in order, where 'None'
                indicates an argument passed in at runtime
        """
        # Check function
        if not callable(func):
            raise TypeError('Function object not callable: {!r}'.format(func))
        self._function = func
        
        # Check arguments
        if not isinstance(signature, (tuple, list)):
            raise TypeError('Signature not contained in list')
        self._signature = signature
        
        # Count the number of runtime arguments needed
        self._nargs = sum(arg is None for arg in signature)

        # Call base class initializer
        super(FunctionEvaluator, self).__init__(key, name)

    @property
    def signature(self):
        return self._signature
    
    def __eq__(self, other):
        """
        Check if two Actions are equal
        """
        if not isinstance(other, FunctionEvaluator):
            return False
        elif self._function != other._function:
            return False
        elif self._signature != other._signature:
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
        rtargs = [arg if arg else tmp_args.pop(0) for arg in self._signature]
        rtargs.extend(tmp_args)
        return self._function(*rtargs)


#===============================================================================
# OutputSliceHandle
#===============================================================================
class OutputSliceHandle(Action):
    """
    Action that acts as a "handle" for output data streams
    """
    
    def __init__(self, variable, slicetuple=None, minimum=None, maximum=None):
        """
        Initializer
        
        Parameters:
            variable (str): A string name/identifier for the variable
            slicetuple (tuple): The slice of the output variable into which
                the data is to be written
            minimum: The minimum value the data should have, if valid
            maximum: The maximum value the data should have, if valid
        """
        # Parse slice tuple
        self._slice = SliceTuple(slicetuple)
        
        # Call base class initializer
        name = '{0}[{1}]'.format(variable, str(self._slice))
        super(OutputSliceHandle, self).__init__(variable, name)

        # Store min/max
        self._min = minimum
        self._max = maximum
        
    @property
    def slicetuple(self):
        return self._slice.index

    def __eq__(self, other):
        """
        Check if two Actions are equal
        """
        if not isinstance(other, OutputSliceHandle):
            return False
        elif self._slice != other._slice:
            return False
        elif self._min != other._min:
            return False
        elif self._max != other._max:
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
# MPISender
#===============================================================================
class MPISender(Action):
    """
    Send data to a specified remote rank in COMM_WORLD
    """
    
    def __init__(self, dest):
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
        source = MPI.COMM_WORLD.Get_rank()
        opname = 'send(to={},from={})'.format(dest, source)
        super(MPISender, self).__init__((source, dest), opname)
        
        # Store the destination rank
        self._dest = dest
    
    @property
    def destination(self):
        return self._dest

    def __eq__(self, other):
        """
        Check if two Actions are equal
        """
        if not isinstance(other, MPISender):
            return False
        elif self._dest != other._dest:
            return False
        else:
            return super(MPISender, self).__eq__(other)
        
    def __call__(self, data):
        """
        Make callable like a function
        
        Parameters:
            data: The data to send
        """
        # Check data type
        if not isinstance(data, numpy.ndarray):
            raise TypeError('MPISender only works with NDArrays')

        # Create the handshake message - Assumes data is an NDArray
        msg = {}
        msg['shape'] = data.shape
        msg['dtype'] = data.dtype

        # Send the handshake message to the MPIReceiver
        tag = MPI.COMM_WORLD.Get_rank()
        MPI.COMM_WORLD.send(msg, dest=self._dest, tag=tag)

        # Receive the acknowledgement from the MPIReceiver
        tag += MPI.COMM_WORLD.Get_size()
        ack = MPI.COMM_WORLD.recv(source=self._dest, tag=tag)

        # Check the acknowledgement, if not OK error
        if not ack:
            raise RuntimeError(('MPISender on rank {} failed to '
                                'receive acknowledgement from rank '
                                '{}').format(MPI.COMM_WORLD.Get_rank(),
                                             self._dest))

        # If OK, send the data to the MPIReceiver
        tag += MPI.COMM_WORLD.Get_size()
        MPI.COMM_WORLD.Send(data, dest=self._dest, tag=tag)
        return None


#===============================================================================
# MPIReceiver
#===============================================================================
class MPIReceiver(Action):
    """
    Receive data from a specified remote rank in COMM_WORLD
    """
    
    def __init__(self, source):
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
        dest = MPI.COMM_WORLD.Get_rank()
        opname = 'recv(to={},from={})'.format(dest, source)
        super(MPIReceiver, self).__init__((source, dest), opname)
        
        # Store the source rank
        self._source = source

    @property
    def source(self):
        return self._source
    
    def __eq__(self, other):
        """
        Check if two Actions are equal
        """
        if not isinstance(other, MPIReceiver):
            return False
        elif self._source != other._source:
            return False
        else:
            return super(MPIReceiver, self).__eq__(other)
        
    def __call__(self):
        """
        Make callable like a function
        """

        # Receive the handshake message from the MPISender
        tag = self._source
        msg = MPI.COMM_WORLD.recv(source=self._source, tag=tag)

        # Check the message content
        ack = (type(msg) is dict and
               all([key in msg for key in ['shape', 'dtype']]))

        # Send acknowledgement back to the MPISender
        tag += MPI.COMM_WORLD.Get_size()
        MPI.COMM_WORLD.send(ack, dest=self._source, tag=tag)

        # If acknowledgement is bad, don't receive
        if not ack:
            raise RuntimeError(('MPIReceiver on rank {} failed to '
                                'receive acknowledgement from rank '
                                '{}').format(MPI.COMM_WORLD.Get_rank(),
                                             self._dest))

        # Receive the data from the MPISender
        tag += MPI.COMM_WORLD.Get_size()
        recvd = numpy.empty(msg['shape'], dtype=msg['dtype'])
        MPI.COMM_WORLD.Recv(recvd, source=self._source, tag=tag)        
        return recvd
