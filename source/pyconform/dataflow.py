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

from pyconform.datasets import InputDatasetDesc, OutputDatasetDesc
from pyconform.parsing import parse_definition, ParsedVariable, ParsedFunction
from pyconform.functions import find
from pyconform.physarray import PhysArray
from pyconform.flownodes import DataNode, ReadNode, EvalNode, MapNode, ValidateNode, WriteNode
from asaptools.simplecomm import create_comm
from asaptools.partition import WeightBalanced
from collections import OrderedDict

import numpy


#===================================================================================================
# DataFlow
#===================================================================================================
class DataFlow(object):
    """
    An object describing the flow of data from input to output
    """

    def __init__(self, inpds, outds):
        """
        Initializer
        
        Parameters:
            inpds (InputDatasetDesc): The input dataset to use as reference when
                parsing variable definitions
            outds (OutputDatasetDesc): The output dataset defining the output variables and
                their definitions or data
        """
        # Input dataset
        if not isinstance(inpds, InputDatasetDesc):
            raise TypeError('Input dataset must be of InputDatasetDesc type')
        self._ids = inpds

        # Output dataset
        if not isinstance(outds, OutputDatasetDesc):
            raise TypeError('Output dataset must be of OutputDatasetDesc type')
        self._ods = outds

        # Separate output variables into variables with data or string 'definitions'
        datvars = {}
        defvars = {}
        for vname, vdesc in self._ods.variables.iteritems():
            if isinstance(vdesc.definition, basestring):
                defvars[vname] = vdesc
            else:
                datvars[vname] = vdesc

        # Create a dictionary to store DataNodes from variables with data 'definitions'
        self._datnodes = {}
        for vname, vdesc in datvars.iteritems():
            vdata = numpy.array(vdesc.definition, dtype=vdesc.datatype)
            vunits = vdesc.cfunits()
            vdims = vdesc.dimensions.keys()
            varray = PhysArray(vdata, name=vname, units=vunits, dimensions=vdims)
            self._datnodes[vname] = DataNode(varray)

        # Create a dictionary to store FlowNodes for variables with string 'definitions'
        self._defnodes = {}
        for vname, vdesc in defvars.iteritems():
            self._defnodes[vname] = self._construct_flow_(parse_definition(vdesc.definition))

        # Gather information about each FlowNode's metadata (via empty PhysArrays)
        definfos = dict((vname, vnode[None]) for vname, vnode in self._defnodes.iteritems())

        # Each output variable FlowNode must be mapped to its output dimensions.
        # To aid with this, we sort by number of dimensions:
        nodeorder = zip(*sorted((len(self._ods.variables[vname].dimensions), vname)
                                for vname in self._defnodes))[1]

        # Now, we construct the dimension maps
        self._i2omap = {}
        self._o2imap = {}
        for vname in nodeorder:
            out_dims = self._ods.variables[vname].dimensions.keys()
            inp_dims = definfos[vname].dimensions

            unmapped_out = tuple(d for d in out_dims if d not in self._o2imap)
            mapped_inp = tuple(self._o2imap[d] for d in out_dims if d in self._o2imap)
            unmapped_inp = tuple(d for d in inp_dims if d not in mapped_inp)

            if len(unmapped_out) != len(unmapped_inp):
                err_msg = 'Cannot map dimensions {} to dimensions {}'.format(inp_dims, out_dims)
                raise ValueError(err_msg)
            if len(unmapped_out) == 0:
                continue
            for out_dim, inp_dim in zip(unmapped_out, unmapped_inp):
                self._o2imap[out_dim] = inp_dim
                self._i2omap[inp_dim] = out_dim

        # Now that we know how dimensions are mapped, construct the output dimension sizes
        for dname, ddesc in self._ods.dimensions.iteritems():
            if not ddesc.is_set():
                ddesc.set(self._ids.dimensions[self._o2imap[dname]])

        # Append a MapNode to all string-defined nodes (map dimension names)
        for vname in self._defnodes:
            dnode = self._defnodes[vname]
            dinfo = definfos[vname]
            map_dims = tuple(self._i2omap[d] for d in dinfo.dimensions)
            name = 'map({!s}, to={})'.format(vname, map_dims)
            self._defnodes[vname] = MapNode(name, dnode, self._i2omap)

        # Now loop through ALL of the variables and create ValidateNodes for validation
        self._varnodes = {}
        for vname, vdesc in self._ods.variables.iteritems():
            if vname in self._datnodes:
                vnode = self._datnodes[vname]
            elif vname in self._defnodes:
                vnode = self._defnodes[vname]

            self._varnodes[vname] = ValidateNode(vname, vnode, units=vdesc.cfunits(),
                                                 dimensions=vdesc.dimensions.keys(),
                                                 attributes=vdesc.attributes,
                                                 dtype=vdesc.datatype)

        # Create the WriteNodes for each time-series output file
        writenodes = {}
        for fname, fdesc in self._ods.files.iteritems():
            vnodes = tuple(self._varnodes[n] for n in fdesc.variables.keys())
            writenodes[fname] = WriteNode(fdesc, inputs=vnodes)
        self._writenodes = writenodes

        # Compute the bytesizes of each output variable
        bytesizes = {}
        for vname, vdesc in self._ods.variables.iteritems():
            vsize = sum(ddesc.size for ddesc in vdesc.dimensions.itervalues())
            vsize = 1 if vsize == 0 else vsize
            bytesizes[vname] = vsize * numpy.dtype(vdesc.datatype).itemsize

        # Compute the file sizes for each output file
        self._filesizes = {}
        for fname, wnode in self._writenodes.iteritems():
            self._filesizes[fname] = sum(bytesizes[vnode.label] for vnode in wnode.inputs)

    def _construct_flow_(self, obj):
        if isinstance(obj, ParsedVariable):
            vname = obj.key
            if vname in self._ids.variables:
                return ReadNode(self._ids.variables[vname], index=obj.args)

            elif vname in self._datnodes:
                return self._datnodes[vname]

            else:
                raise KeyError('Variable {!r} not found or cannot be used as input'.format(vname))

        elif isinstance(obj, ParsedFunction):
            name = obj.key
            nargs = len(obj.args)
            func = find(name, numargs=nargs)
            args = [self._construct_flow_(arg) for arg in obj.args]
            if all(isinstance(o, (int, float)) for o in args):
                return func(*args)
            return EvalNode(name, func, *args)

        else:
            return obj

    @property
    def dimension_map(self):
        """The internally generated input-to-output dimension name map"""
        return self._i2omap

    def execute(self, chunks={}, serial=False, provenance=False, bounds={}):
        """
        Execute the Data Flow
        
        Parameters:
            chunks (dict): A dictionary of output dimension names and chunk sizes for each
                dimension given.  Output dimensions not included in the dictionary will not be
                chunked.  (Use OrderedDict to preserve order of dimensions, where the first
                dimension will be assumed to correspond to the fastest-varying index and the last
                dimension will be assumed to correspond to the slowest-varying index.)
            serial (bool): Whether to run in serial (True) or parallel (False)
            provenance (bool): Whether to write a provenance attribute generated during execution
                for each variable in the file
            bounds (dict):  Bounds on named variables specified in the output specification
                file.  Data will be written for values within these bounds inclusively.
        """
        # Check the bounds type
        if not isinstance(bounds, dict):
            raise TypeError('Bounds must be specified with a dictionary')

        # Make sure that the specified dimensions are valid
        for oname, (lbound, ubound) in bounds.iteritems():
            if oname not in self._ods.variables:
                raise ValueError('Cannot bound on unknown output variable {!r}'.format(oname))
            if not isinstance(lbound, int):
                raise TypeError(('Lower bound invalid for output variable {!r}: '
                                 '{}').format(oname, lbound))
            if not isinstance(ubound, int):
                raise TypeError(('Upper bound invalid for output variable {!r}: '
                                 '{}').format(oname, ubound))

        # Check chunks type
        if not isinstance(chunks, dict):
            raise TypeError('Chunks must be specified with a dictionary')

        # Make sure that the specified dimensions are valid
        for odname, odsize in chunks.iteritems():
            if odname not in self._o2imap:
                raise ValueError('Cannot chunk over unknown output dimension {!r}'.format(odname))
            if not isinstance(odsize, int):
                raise TypeError(('Chunk size invalid for output dimension {!r}: '
                                 '{}').format(odname, odsize))

        # Create the simple communicator
        scomm = create_comm(serial=bool(serial))
        prefix = '[{}/{}]'.format(scomm.get_rank(), scomm.get_size())
        if scomm.is_manager():
            print 'Beginning execution of data flow...'

        # Partition the output files/variables over available parallel (MPI) ranks
        fnames = scomm.partition(self._filesizes.items(), func=WeightBalanced(), involved=True)
        print '{}: Writing files: {}'.format(prefix, ', '.join(fnames))

        # Loop over output files and write using given chunking
        for fname in fnames:
            print '{}: Writing file: {}'.format(prefix, fname)
            self._writenodes[fname].execute(chunks=chunks, provenance=provenance, bounds=bounds)

        scomm.sync()
        if scomm.is_manager():
            print 'All output variables written.'
            print
