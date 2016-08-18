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

from pyconform.datasets import InputDataset, OutputDataset
from pyconform.parsing import parse_definition, ParsedVariable, ParsedFunction
from pyconform.functions import find
from pyconform.flownodes import DataNode, ReadNode, EvalNode, MapNode, ValidateNode, WriteNode
from itertools import cycle as itercycle
from collections import OrderedDict

import numpy


#===================================================================================================
# DataFlow
#===================================================================================================
class DataFlow(object):
    """
    An object describing the flow of data from input to output
    """

    def __init__(self, inpds, outds, cycle=True, error=False):
        """
        Initializer
        
        Parameters:
            inpds (InputDataset): The input dataset to use as reference when
                parsing variable definitions
            outds (OutputDataset): The output dataset defining the output variables and
                their definitions or data
            cyc (bool): If True, cycles which file to read metadata variables
                from (i.e., variables that exist in all input files).  If False,
                always reads metadata variables from the first input file.
        """
        # Input dataset
        if not isinstance(inpds, InputDataset):
            raise TypeError('Input dataset must be of InputDataset type')
        self._ids = inpds

        # Output dataset
        if not isinstance(outds, OutputDataset):
            raise TypeError('Output dataset must be of OutputDataset type')
        self._ods = outds

        # Cyclic iterator over available input filenames
        fnames = [v.filename for v in self._ids.variables.itervalues()]
        if cycle:
            self._infile_cycle = itercycle(filter(None, fnames))
        else:
            self._infile_cycle = itercycle([filter(None, fnames)[0]])

        # Initialize the dimension map and the inverse dimension map
        self._i2omap = {}
        self._o2imap = {}

        # Separate output variables into variables with 'data' or 'definitions'
        datavars = {}
        defnvars = {}
        for vname, vinfo in self._ods.variables.iteritems():
            if vinfo.data is not None:
                datavars[vname] = vinfo
            elif vinfo.definition is not None:
                defnvars[vname] = vinfo
            else:
                raise ValueError(('Output variable {0} does not have a data parameter '
                                  'nor a definition parameter').format(vname))

        # Create a dictionary to store "source" DataNodes from 'data' attributes
        self._datnodes = {}

        # First, parse output variables with 'data'
        for vname, vinfo in datavars.iteritems():
            vdata = numpy.array(vinfo.data, dtype=vinfo.datatype)
            cdnode = DataNode(vname, vdata, units=vinfo.cfunits(), dimensions=vinfo.dimensions)
            self._datnodes[vname] = cdnode

        # Create a dictionary to store "output variable" DataNodes from 'definition' attributes
        self._defnodes = {}

        # Parse the output variable definitions
        for vname, vinfo in defnvars.iteritems():
            self._defnodes[vname] = self._construct_flow_(parse_definition(vinfo.definition))

        # Gather information about each FlowNode's data
        definfos = dict((vname, vnode[None]) for vname, vnode in self._defnodes.iteritems())

        # Each output variable FlowNode must be mapped to its output dimensions.
        # To aid with this, we sort by number of dimensions:
        nodeorder = zip(*sorted((len(self._ods.variables[vname].dimensions), vname)
                                for vname in self._defnodes))[1]
        for vname in nodeorder:
            out_dims = self._ods.variables[vname].dimensions
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

        # Append the necessary dimension mapping
        for vname in self._defnodes:
            dnode = self._defnodes[vname]
            dinfo = definfos[vname]

            # Map dimensions from input namespace to output namespace
            map_dims = tuple(self._i2omap[d] for d in dinfo.dimensions)
            name = 'map({!s}, to={})'.format(vname, map_dims)
            self._defnodes[vname] = MapNode(name, dnode, self._i2omap)

        # Now loop through ALL of the variables and create ValidateNodes for validation
        self._varnodes = {}
        for vname, vinfo in self._ods.variables.iteritems():
            if vname in self._datnodes:
                vnode = self._datnodes[vname]
            elif vname in self._defnodes:
                vnode = self._defnodes[vname]

            self._varnodes[vname] = ValidateNode(vname, vnode, units=vinfo.cfunits(),
                                                 dimensions=vinfo.dimensions,
                                                 attributes=vinfo.attributes,
                                                 error=error)

        # Now determine which output variables have no output file (metadata variables)
        tsvnames = tuple(vname for vname, vinfo in self._ods.variables.iteritems()
                         if vinfo.filename is not None)
        mvnames = tuple(vname for vname, vinfo in self._ods.variables.iteritems()
                        if vinfo.filename is None)

        # Create the WriteDataNodes for each time-series output file
        writenodes = {}
        for tsvname in tsvnames:
            tsvinfo = self._ods.variables[tsvname]
            filename = tsvinfo.filename
            vnodes = tuple(self._varnodes[n] for n in mvnames) + (self._varnodes[tsvname],)
            unlimited = tuple(self._i2omap[d] for d in self._ids.dimensions
                              if self._ids.dimensions[d].unlimited)
            attribs = OrderedDict((k, v) for k, v in self._ods.attributes.iteritems())
            attribs['unlimited'] = unlimited
            writenodes[tsvname] = WriteNode(filename, *vnodes, **attribs)

        self._writenodes = writenodes

    def _construct_flow_(self, obj):
        if isinstance(obj, ParsedVariable):
            vname = obj.key
            if vname in self._ids.variables:
                vinfo = self._ids.variables[vname]
                fname = vinfo.filename if vinfo.filename else self._infile_cycle.next()
                return ReadNode(fname, vname, index=obj.args)

            elif vname in self._datnodes:
                return self._datnodes[vname]

            else:
                raise KeyError('Variable {0!r} not found or cannot be used as input'.format(vname))

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

    def execute(self, chunks={}):
        """
        Execute the Data Flow
        
        Parameters:
            chunks (dict): A dictionary of output dimension names and chunk sizes for each
                dimension given.  Output dimensions not included in the dictionary will not be
                chunked.  (Use OrderedDict to preserve order of dimensions, where the first
                dimension will be assumed to correspond to the fastest-varying index and the last
                dimension will be assumed to correspond to the slowest-varying index.)
        """
        # Check chunks type
        if not isinstance(chunks, dict):
            raise TypeError('Chunks must be specified with a dictionary')

        # Make sure that the specified dimensions are valid
        for odname, odsize in chunks.iteritems():
            if odname not in self._o2imap:
                raise ValueError('Cannot chunk over unknown output dimension {!r}'.format(odname))
            if not isinstance(odsize, int):
                raise TypeError('Chunk size invalid: {}'.format(odsize))

        # Loop over output files and write using given chunking
        for vname, wnode in self._writenodes.iteritems():
            print 'Writing output variable {!r} to file'.format(vname)
            wnode.execute(chunks=chunks)

        print 'All output variables written.'
        print
