"""
Operation Graph Class

This module contains the OperationGraph class to be used with the Operator 
classes and the DiGraph class to build an "operator graph" or "operation graph."
This graph walks through the graph performing the Operator functions connected
by the DiGraph object.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from graph import DiGraph
from pyparsing import nums, alphas, alphanums, operatorPrecedence, oneOf
from pyparsing import Word, Literal, Optional, Combine, opAssoc
from dataset import InputDataset, OutputDataset
from itertools import cycle
from collections import OrderedDict
from operator import pow, neg, add, sub, mul, div
from cf_units import Unit
from operators import Operator, InputSliceReader, FunctionEvaluator, OutputSliceHandle
from numpy import transpose


#===============================================================================
# UnitsError
#===============================================================================
class UnitsError(ValueError):
    """
    Exception raised when units cannot be matched
    """
    pass


#===============================================================================
# DimensionsError
#===============================================================================
class DimensionsError(ValueError):
    """
    Exception raised when dimensions cannot be matched
    """
    pass


#===============================================================================
# OperationGraph
#===============================================================================
class OperationGraph(DiGraph):
    """
    Operation Graph
    
    A directed graph defining a connected set of operations whose results
    are used as input to adjacent operators.
    """

    def __init__(self):
        """
        Initialize
        """
        super(OperationGraph, self).__init__()

    def add(self, vertex):
        """
        Add a vertex to the graph
        
        Parameters:
            vertex (Operator): An Operator vertex to be added to the graph
        """
        if not isinstance(vertex, Operator):
            raise TypeError('OperationGraph must consist only of Operators')
        super(OperationGraph, self).add(vertex)

    def __call__(self, root):
        """
        Perform the OperationGraph operations
        
        Parameters:
            root (Operator): The root of the operation, from which data is
                requested from the operation graph
        """
        if root not in self:
            raise KeyError('Operator {!r} not in OperationGraph'.format(root))
        def evaluate_from(op):
            return op(*map(evaluate_from, self.neighbors_to(op)))
        return evaluate_from(root)
    
    def handles(self):
        """
        Return a dictionary of output variable handles in the graph
        """
        return dict((op.name, op) for op in self.vertices
                    if isinstance(op, OutputSliceHandle))


#===============================================================================
# GraphFiller
#===============================================================================
class GraphFiller(object):
    """
    Object that fills an OperationGraph
    """
    
    def __init__(self):
        """
        Initializer
        """
        # Integer operands
        integers = Word(nums)
        integers.setParseAction(self._int_operand_parser_)
        
        # Floating-point operands
        floats = Combine(Word(nums) + '.' + Optional(Word(nums)))
        floats.setParseAction(self._float_operand_parser_)

        # String variable name operands    
        varname = Word(alphas + "_", alphanums + "_" )
        varname.setParseAction(self._variable_operand_parser_)
        
        # Define the basic operand
        operand = floats | integers | varname
    
        # Define each operator symbol and how it is parsed
        pow_op = (Literal('^'), 2, opAssoc.RIGHT, self._pow_operator_parser_)
        sgn_op = (oneOf('+ -'), 1, opAssoc.RIGHT, self._sgn_operator_parser_)
        mul_op = (oneOf('* /'), 2, opAssoc.RIGHT, self._mul_operator_parser_)
        add_op = (oneOf('+ -'), 2, opAssoc.RIGHT, self._add_operator_parser_)
        
        # Define the operator precedence list/order
        op_order = [pow_op, sgn_op, mul_op, add_op]
    
        # Define the expression parser using operator precedence
        self._defparser = operatorPrecedence(operand, op_order)
        
        # Place-holders for future operations
        self._opgraph = None
        self._ids = None
        self._ods = None
        self._ifncycle = None
    
    def _int_operand_parser_(self, s, l, t):
        return int(t[0])

    def _float_operand_parser_(self, s, l, t):
        return float(t[0])

    def _variable_operand_parser_(self, s, l, t):
        varname = str(t[0])
        if varname not in self._ids.variables:
            err_msg = ('Definition {!r} references variable {!r} that is not '
                       'is not found in the reference dataset '
                       '{!r}').format(s, varname, self._ids.name)
            raise KeyError(err_msg)
        if self._ids.variables[varname].filename:
            fname = self._ids.variables[varname].filename
        else:
            fname = self._ifncycle.next()
        op = InputSliceReader(fname, varname)
        self._opgraph.add(op)
        return op
    
    def _pow_operator_parser_(self, tokens):
        base, _, exp = tokens[0]
        
        # If both int/float, then just return the result
        if isinstance(base, (int, float)) and isinstance(exp, (int, float)):
            return base ** exp

        # If the exponent is an Operator, then it must be dimensionless
        if isinstance(exp, Operator) and not exp.units.is_dimensionless():
            raise UnitsError('Power exponents must be dimensionless')
        
        # If the base is int/float, then exponent must be an Operator
        if isinstance(base, (int, float)) and isinstance(exp, Operator):
            fargs = [base, None]
            fops = [exp]
            funits = Unit(1)
            fdims = exp.dimensions
        
        # If the base is an Operator, then the exponent can be anything
        elif isinstance(base, Operator):
            fops = [base]
            
            # If the exponent is an int, then base units can be anything
            if isinstance(exp, int):
                fargs = [None, exp]
                funits = base.units ** exp
                fdims = base.dimensions
            
            # If the exponent is a float, then base must be dimensionless
            elif isinstance(exp, float):
                if not base.units.is_dimensionless():
                    raise UnitsError('Floating-point exponents can only be '
                                     'applied to dimensionless bases')
                fargs = [None, exp]
                funits = Unit(1)   
                fdims = base.dimensions
            
            # If exponent is an operator, then base must be dimensionless
            elif isinstance(exp, Operator):
                if not base.units.is_dimensionless():
                    raise UnitsError('Element-wise power operations can only '
                                     'be applied to dimensionless bases')
                fargs = []
                funits = Unit(1)
                fdims = base.dimensions
                
                # Check if the same dimensions exist (i.e., can be matched)
                if set(base.dimensions) != set(exp.dimensions):
                    raise DimensionsError(('Dimensions of {!r} and {!r} cannot be '
                                           'matched').format(base.name, exp.name))
                
                # Otherwise, only the order is off, so just reorder/transpose
                elif base.dimensions != exp.dimensions:
                    xdims = exp.dimensions
                    neworder = [xdims.index(d) for d in base.dimensions]
                    tname = 'transpose({},order={})'.format(exp.name, neworder)
                    texp = FunctionEvaluator(tname, transpose, args=[None, neworder], 
                                             units=exp.units, 
                                             dimensions=fdims)
                    self._opgraph.connect(exp, texp)
                    fops.append(texp)
                else:
                    fops.append(exp)
            else:
                raise TypeError('Unrecognized exponent datatype')                
        else:
            raise TypeError('Unrecognized base datatype')                

        fname = '({!s}^{!s})'.format(base, exp)
        op = FunctionEvaluator(fname, pow, args=fargs, units=funits, dimensions=fdims)
        for op1 in fops:
            self._opgraph.connect(op1, op)
        return op

    def _sgn_operator_parser_(self, tokens):
        opstr, val = tokens[0]
        
        if opstr == '+':
            return val
        
        elif isinstance(val, (int, float)):
            return neg(val)
        
        elif isinstance(val, Operator):
            fname = '(-{!s})'.format(val)
            op = FunctionEvaluator(fname, neg, units=val.units,
                                   dimensions=val.dimensions)
            self._opgraph.connect(val, op)
            return op
        else:
            raise TypeError('Unrecognized operand datatype')                

    def _mul_operator_parser_(self, tokens):
        left, opstr, right = tokens[0]
        
        if opstr == '*':
            fptr = mul
        else:
            fptr = div

        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return fptr(left, right)
                    
        elif isinstance(left, (int, float)) and isinstance(right, Operator):
            funits = right.units
            fargs = [left, None]
            fops = [right]
            fdims = right.dimensions
        
        elif isinstance(left, Operator) and isinstance(right, (int, float)):
            funits = left.units
            fargs = [None, right]
            fops = [left]
            fdims = left.dimensions

        elif isinstance(left, Operator) and isinstance(right, Operator):
            funits = left.units * right.units
            fargs = [None, None]
            fops = [left]
            fdims = left.dimensions

            # Check if the same dimensions exist (i.e., can be matched)
            if set(left.dimensions) != set(right.dimensions):
                raise DimensionsError(('Dimensions of {!r} and {!r} cannot be '
                                       'matched').format(left.name, right.name))
            
            # Otherwise, only the order is off, so just reorder/transpose
            elif left.dimensions != right.dimensions:
                rdims = right.dimensions
                neworder = [rdims.index(d) for d in left.dimensions]
                tname = 'transpose({},order={})'.format(right.name, neworder)
                tright = FunctionEvaluator(tname, transpose, args=[None, neworder], 
                                           units=right.units,
                                           dimensions=fdims)
                self._opgraph.connect(right, tright)
                fops.append(tright)
            else:
                fops.append(right)
        
        else:
            raise TypeError('Unrecognized operand datatype')
        
        fname = '({!s}{!s}{!s})'.format(left, opstr, right)
        op = FunctionEvaluator(fname, fptr, args=fargs, units=funits,
                               dimensions=fdims)
        for op1 in fops:
            self._opgraph.connect(op1, op)
        return op

    def _add_operator_parser_(self, tokens):
        left, opstr, right = tokens[0]
        
        if opstr == '+':
            fptr = add
        else:
            fptr = sub

        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return fptr(left, right)
                    
        elif isinstance(left, (int, float)) and isinstance(right, Operator):
            if not right.units.is_dimensionless():
                raise UnitsError('Cannot add/subtract with incompatible units')
            funits = Unit(1)
            fargs = [left, None]
            fops = [right]
            fdims = right.dimensions
        
        elif isinstance(left, Operator) and isinstance(right, (int, float)):
            if not left.units.is_dimensionless():
                raise UnitsError('Cannot add/subtract with incompatible units')
            funits = Unit(1)
            fargs = [None, right]
            fops = [left]
            fdims = left.dimensions

        elif isinstance(left, Operator) and isinstance(right, Operator):
            funits = left.units
            fargs = [None, None]
            fops = [left]
            fdims = left.dimensions

            # Check units
            if not right.units.is_convertible(left.units):
                raise UnitsError('Cannot add/subtract with incompatible units')
            elif right.units != left.units:
                cname = 'convert({!s},to={!s})'.format(right, left.units)
                cfunc = right.units.convert
                cargs = [None, left.units]
                cright = FunctionEvaluator(cname, cfunc, args=cargs,
                                           units=left.units,
                                           dimensions=right.dimensions)
                self._opgraph.connect(right, cright)
                newr = cright
            else:
                newr = right

            # Check if the same dimensions exist (i.e., can be matched)
            if set(left.dimensions) != set(newr.dimensions):
                print left.dimensions, newr.dimensions
                raise DimensionsError(('Dimensions of {!r} and {!r} cannot be '
                                       'matched').format(left.name, newr.name))
            
            # Otherwise, only the order is off, so just reorder/transpose
            elif left.dimensions != newr.dimensions:
                rdims = newr.dimensions
                neworder = [rdims.index(d) for d in left.dimensions]
                tname = 'transpose({},order={})'.format(right.name, neworder)
                tright = FunctionEvaluator(tname, transpose, args=[None, neworder], 
                                           units=newr.units,
                                           dimensions=fdims)
                self._opgraph.connect(newr, tright)
                fops.append(tright)
            else:
                fops.append(newr)
        
        else:
            raise TypeError('Unrecognized operand datatype')
        
        fname = '({!s}{!s}{!s})'.format(left, opstr, right)
        op = FunctionEvaluator(fname, fptr, args=fargs, units=funits,
                               dimensions=fdims)
        for op1 in fops:
            self._opgraph.connect(op1, op)
        return op
    
    def from_definitions(self, opgraph, inp, out):
        """
        Fill the OperationGraph with Operators from variable definitions
        
        Parameters:
            opgraph (OperationGraph): The operation graph to fill from the
                output variable definitions
            inp (InputDataset): The input dataset with variables referenced
                in the output variable definitions
            out (OutputDataset): The output dataset with variables defined
                in terms of input variable names
            
        Returns:
            OrderedDict: ordered dictionary mapping output variable names to
                root Operators in the OperationGraph
        """
        # OperationGraph
        if not isinstance(opgraph, OperationGraph):
            raise TypeError('Operation graph must be of OperationGraph type')
        self._opgraph = opgraph
        
        # Input/reference dataset
        if not isinstance(inp, InputDataset):
            raise TypeError('Input dataset must be of InputDataset type')
        self._ids = inp

        # Input/reference dataset
        if not isinstance(out, OutputDataset):
            raise TypeError('Output dataset must be of OutputDataset type')
        self._ods = out

        # Cyclic iterator over available input filenames
        fnames = [v.filename for v in self._ids.variables.itervalues()]
        self._ifncycle = cycle(filter(None, fnames))

        # Parse the output variable definitions
        groots = OrderedDict()
        for vname, vinfo in self._ods.variables.iteritems():
            definition = self._ods.variables[vname].definition
            groot = self._defparser.parseString(definition)[0]
            
            # Check if units match
            vunits = vinfo.cfunits()
            if groot.units != vunits:
                if groot.units.is_convertible(vunits):
                    cname = 'convert({!s},to={!s})'.format(groot.name, vunits)
                    cargs = [None, vunits]
                    cop = FunctionEvaluator(cname, groot.units.convert,
                                            args=cargs, units=vunits,
                                            dimensions=groot.dimensions)
                    self._opgraph.connect(groot, cop)
                    groot = cop
                else:
                    raise UnitsError(('Cannot convert units {!r} to '
                                      'output variable {!r} units '
                                      '{!r}').format(groot.units, 
                                                     vname, vunits))

            # Save the root operator
            groots[vname] = groot
            
        # Create the dimension name map
        dim_map = self._map_dimensions_(groots)

        # Map the dimensions
        for vname, vinfo in self._ods.variables.iteritems():
            groot = groots[vname]

            # Check if dimensions match
            vdims = tuple(dim_map[d] for d in vinfo.dimensions)
            if groot.dimensions != vdims:
                if set(groot.dimensions) == set(vdims):
                    neworder = [vdims.index(d) for d in groot.dimensions]
                    tname = 'transpose({},order={})'.format(groot.name, neworder)
                    top = FunctionEvaluator(tname, transpose,
                                            args=[None, neworder],
                                            units=groot.units,
                                            dimensions=vdims)
                    self._opgraph.connect(groot, top)
                    groot = top
                else:
                    raise DimensionsError(('Cannot transpose dimensions {!s} '
                                           'to output variable {!r} dimensions '
                                           '{!s}').format(groot.dimensions,
                                                          vname, vdims))
            
            # Create the final output variable handle
            vmin = vinfo.attributes.get('valid_min')
            vmax = vinfo.attributes.get('valid_max')
            outop = OutputSliceHandle(vname, units=vinfo.cfunits(),
                                      dimensions=vinfo.dimensions,
                                      minimum=vmin, maximum=vmax)
            self._opgraph.connect(groot, outop)
            groots[vname] = outop
        
        return groots
 
    def _map_dimensions_(self, groots):
        dim_map = {}
        
        # Sort output variables by dimension size
        vordered = OrderedDict(sorted(self._ods.variables.iteritems(),
                                      key=lambda item: len(item[1].dimensions)))

        # In dimension-length order, attempt to map input to ouput dimensions
        for vname, vinfo in vordered.iteritems():
            groot = groots[vname]
            odims = vinfo.dimensions
            idims = groot.dimensions
            if len(odims) != len(idims):
                err_msg = ('Output variable {!r} has dimensions {} that cannot '
                           'be mapped to its definition {!r} with dimensions '
                           '{}').format(vname, odims, groot.name, idims)
                raise ValueError(err_msg)

            # Find the unmapped dimensions
            xodims = []
            xidims = [idim for idim in idims]
            for odim in odims:
                if odim in dim_map:
                    idim = dim_map[odim]
                    if idim not in idims:
                        err_msg = ('Output variable {!r} has an output '
                                   'dimension {!r} that appears to map to '
                                   'input dimension {!r} which is not found '
                                   'in its definition '
                                   '{!r}').format(vname, odim, idim, groot.name)
                        raise ValueError(err_msg)
                    if idim in xidims:
                        xidims.remove(idim)
                else:
                    xodims.append(odim)

            if len(xodims) != len(xidims):
                err_msg = ('Unmapped output dimensions {!r} cannot be mapped '
                           'to input dimensions {!r} for output variable {!r} '
                           'with definition '
                           '{!r}').format(odim, idim, vname, groot.name)
                raise ValueError(err_msg)
            
            if len(xodims) == 1:
                xodim = xodims[0]
                xidim = xidims[0]
                dim_map[xodim] = xidim
                
            elif len(xodims) > 1:
                err_msg = ('Unmapped output dimensions {!r} cannot be mapped '
                           'safely to input dimensions {!r} for output '
                           'variable {!r} with definition '
                           '{!r}').format(xodims, xidims, vname, groot.name)
                raise ValueError(err_msg)

        return dim_map
