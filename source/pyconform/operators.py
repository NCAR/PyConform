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
from cf_units import Unit

import numpy

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
    def __init__(self, name, units=Unit(None)):
        """
        Initializer
        
        Parameters:
            name (str): A string name/identifier for the operator
            units (Unit): A cf_units.Unit object declaring units of data returned
        """
        self._id = Operator._id_
        Operator._id_ += 1
        self._name = str(name)
        if not isinstance(units, Unit):
            raise TypeError('Units must be specified with cf_units.Unit type')
        self._units = units
    
    def id(self):
        """
        Return the internal ID of the Operator
        """
        return self._id

    def name(self):
        """
        Return the internal name of the Operator
        """
        return self._name
    
    def units(self):
        """
        Return the cf_units object for the data returned by the Operator
        """
        return self._units

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
        uname = None
        if hasattr(ncfile.variables[variable], 'units'):
            uname = ncfile.variables[variable].units
        ucal = None
        if hasattr(ncfile.variables[variable], 'calendar'):
            ucal = ncfile.variables[variable].calendar
        units = Unit(uname, calendar=ucal)

        # Close the NetCDF file
        ncfile.close()

        # Call base class initializer - sets self._name
        super(VariableSliceReader, self).__init__(variable, units)

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
    
    def __init__(self, name, func, args=[], units=Unit(None)):
        """
        Initializer
        
        Parameters:
            name (str): A string name/identifier for the operator
            func (Function): A function with arguments taken from other operators
            args (list): Arguments to the function, in order, where 'None'
                indicates an argument passed in at runtime
            units (Unit): A cf_units.Unit object declaring units of data returned
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
        super(FunctionEvaluator, self).__init__(name, units)
        
        
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
# SendOperator
#===============================================================================
class SendOperator(Operator):
    """
    Send data to a specified remote rank in COMM_WORLD
    """
    
    def __init__(self, dest, units=Unit(None)):
        """
        Initializer
        
        Parameters:
            dest (int): The destination rank in COMM_WORLD to send the data
            units (Unit): A cf_units.Unit object declaring units of data returned
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
        super(SendOperator, self).__init__(opname, units)
        
        # Store the destination rank
        self._dest = dest
        
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
    
    def __init__(self, source, units=Unit(None)):
        """
        Initializer
        
        Parameters:
            source (int): The source rank in COMM_WORLD to send the data
            units (Unit): A cf_units.Unit object declaring units of data returned
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
        super(RecvOperator, self).__init__(opname, units)
        
        # Store the source rank
        self._source = source
        
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
