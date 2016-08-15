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
from pyconform.flownodes import CreateNode, ReadNode, EvalNode, MapNode, ValidateNode, WriteNode
from itertools import cycle as itercycle

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
        self._inputds = inpds

        # Output dataset
        if not isinstance(outds, OutputDataset):
            raise TypeError('Output dataset must be of OutputDataset type')
        self._outputds = outds

        # Cyclic iterator over available input filenames
        fnames = [v.filename for v in self._inputds.variables.itervalues()]
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
        for vname, vinfo in self._outputds.variables.iteritems():
            if vinfo.data is not None:
                datavars[vname] = vinfo
            elif vinfo.definition is not None:
                defnvars[vname] = vinfo
            else:
                raise ValueError(('Output variable {0} does not have a data parameter '
                                  'nor a definition parameter').format(vname))

        # Create a dictionary to store "source" DataNodes from 'data' attributes
        datanodes = {}

        # First, parse output variables with 'data'
        for vname, vinfo in datavars.iteritems():
            vdata = numpy.array(vinfo.data, dtype=vinfo.datatype)
            cdnode = CreateNode(vname, vdata, units=vinfo.cfunits(), dimensions=vinfo.dimensions)
            datanodes[vname] = cdnode

        # Create a dictionary to store "output variable" DataNodes from 'definition' attributes
        defnodes = {}

        # Parse the output variable definitions
        for vname, vinfo in defnvars.iteritems():
            obj = parse_definition(vinfo.definition)
            defnodes[vname] = self._construct_flow_(obj, datanodes=datanodes)

        # Gather information about each FlowNode's data
        definfos = dict((vname, vnode[None]) for vname, vnode in defnodes.iteritems())

        # Each output variable FlowNode must be mapped to its output dimensions.
        # To aid with this, we sort by number of dimensions:
        nodeorder = zip(*sorted((len(vinfo.dimensions), vname)
                                for vname, vinfo in self._outputds.variables.iteritems()))[1]
        for vname in nodeorder:
            if vname not in defnodes:
                continue

            out_dims = self._outputds.variables[vname].dimensions
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
        for vname in defnodes:
            dnode = defnodes[vname]
            dinfo = definfos[vname]

            # Map dimensions from input namespace to output namespace
            map_dims = tuple(self._i2omap[d] for d in dinfo.dimensions)
            name = 'map({!s}, to={})'.format(vname, map_dims)
            defnodes[vname] = MapNode(name, dnode, self._i2omap)

        # Now loop through ALL of the variables and create ValidateNodes for validation
        varnodes = {}
        for vname, vinfo in self._outputds.variables.iteritems():
            if vname in datanodes:
                vnode = datanodes[vname]
            elif vname in defnodes:
                vnode = defnodes[vname]

            vunits = vinfo.units()
            vdims = vinfo.dimensions
            vattrs = vinfo.attributes
            varnodes[vname] = ValidateNode(vname, vnode, units=vunits, dimensions=vdims,
                                           attributes=vattrs, error=error)

        # Now determine which output variables have no output file (metadata variables)
        tsvnames = tuple(vname for vname, vinfo in self._outputds.variables.iteritems()
                        if vinfo.filename is not None)
        mvnames = tuple(vname for vname, vinfo in self._outputds.variables.iteritems()
                        if vinfo.filename is None)

        # Create the WriteDataNodes for each time-series output file
        writenodes = {}
        for tsvname in tsvnames:
            tsvinfo = self._outputds.variables[tsvname]
            filename = tsvinfo.filename
            vnodes = tuple(varnodes[n] for n in mvnames) + (varnodes[tsvname],)
            unlimited = tuple(self._i2omap[d] for d in self._inputds.dimensions
                              if self._inputds.dimensions[d].unlimited)
            attribs = dict((k, v) for k, v in self._outputds.attributes.iteritems())
            attribs['unlimited'] = unlimited
            writenodes[tsvname] = WriteNode(filename, *vnodes, **attribs)

        self._writenodes = writenodes

    def _construct_flow_(self, obj, datanodes={}):
        if isinstance(obj, ParsedVariable):
            vname = obj.key
            if vname in self._inputds.variables:
                vinfo = self._inputds.variables[vname]
                fname = vinfo.filename if vinfo.filename else self._infile_cycle.next()
                return ReadNode(fname, vname, index=obj.args)

            elif vname in datanodes:
                return datanodes[vname]

            else:
                raise KeyError('Variable {0!r} not found or cannot be used as input'.format(vname))

        elif isinstance(obj, ParsedFunction):
            name = obj.key
            nargs = len(obj.args)
            func = find(name, numargs=nargs)
            args = [self._construct_flow_(arg, datanodes) for arg in obj.args]
            if all(isinstance(o, (int, float)) for o in args):
                return func(*args)
            return EvalNode(name, func, *args)

        else:
            return obj
