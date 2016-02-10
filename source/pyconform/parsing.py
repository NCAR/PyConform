"""
Variable Definition Parsing Utility

This module contains the DefinitionParser class that is used to parse the
variable definitions, check that they are valid, and provide the necessary
data needed to generate the operation graphs.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import nums, alphas, alphanums, operatorPrecedence, oneOf
from pyparsing import Word, Literal, Optional, Combine, opAssoc
from dataset import InputDataset
from opgraph import OperationGraph
from itertools import cycle
from operator import pow, neg, add, sub, mul, div
from cf_units import Unit
from operators import Operator, VariableSliceReader, FunctionEvaluator
from copy import deepcopy
from numpy import transpose


#===============================================================================
# UnitsError
#===============================================================================
class UnitsError(ValueError):
    """
    Exception raised when units do not match
    """
    pass


#===============================================================================
# DimensionsError
#===============================================================================
class DimensionsError(ValueError):
    """
    Exception raised when dimensions do not match
    """
    pass


#===============================================================================
# DefitionParser
#===============================================================================
class DefitionParser(object):
    """
    Variable Definition Parser
    """
    
    def __init__(self, refs=InputDataset()):
        """
        Initializer
        
        Parameters:
            refs (InputDataset): The input dataset containing the variable
                information referenced by the output dataset definitions
        """
        # Type Checking
        if not isinstance(refs, InputDataset):
            raise TypeError('Input dataset must be of InputDataset type')
        self._refs = refs
                
        # Cyclic iterator over available input filenames
        fnames = [v.filename for v in self._refs.variables.itervalues()]
        self._ifncycle = cycle(filter(None, fnames))
        
        # Initialize the internal operation graph for parser storage
        self._opgraph = OperationGraph()

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
        self._expr = operatorPrecedence(operand, op_order)
    
    def _int_operand_parser_(self, s, l, t):
        return int(t[0])

    def _float_operand_parser_(self, s, l, t):
        return float(t[0])

    def _variable_operand_parser_(self, s, l, t):
        varname = str(t[0])
        if varname not in self._refs.variables:
            err_msg = ('Definition {!r} references variable {!r} that is not '
                       'is not found in the reference dataset '
                       '{!r}').format(s, varname, self._refs.name)
            raise KeyError(err_msg)
        if self._refs.variables[varname].filename:
            fname = self._refs.variables[varname].filename
        else:
            fname = self._ifncycle.next()
        op = VariableSliceReader(fname, varname)
        self._opgraph.add(op)
        return op
    
    def _pow_operator_parser_(self, tokens):
        base, _, exp = tokens[0]
        
        # If both int/float, then just return the result
        if isinstance(base, (int, float)) and isinstance(exp, (int, float)):
            return base ** exp

        # If the exponent is an Operator, then it must be dimensionless
        if isinstance(exp, Operator) and not exp.units().is_dimensionless():
            raise UnitsError('Power exponents must be dimensionless')
        
        # If the base is int/float, then exponent must be an Operator
        if isinstance(base, (int, float)) and isinstance(exp, Operator):
            fargs = [base, None]
            fops = [exp]
            funits = Unit(1)
            fdims = exp.dimensions()
        
        # If the base is an Operator, then the exponent can be anything
        elif isinstance(base, Operator):
            fops = [base]
            
            # If the exponent is an int, then base units can be anything
            if isinstance(exp, int):
                fargs = [None, exp]
                funits = base.units() ** exp
                fdims = base.dimensions()
            
            # If the exponent is a float, then base must be dimensionless
            elif isinstance(exp, float):
                if not base.units().is_dimensionless():
                    raise UnitsError('Floating-point exponents can only be '
                                     'applied to dimensionless bases')
                fargs = [None, exp]
                funits = Unit(1)   
                fdims = base.dimensions()
            
            # If exponent is an operator, then base must be dimensionless
            elif isinstance(exp, Operator):
                if not base.units().is_dimensionless():
                    raise UnitsError('Element-wise power operations can only '
                                     'be applied to dimensionless bases')
                fargs = []
                funits = Unit(1)
                fdims = base.dimensions()
                
                # Check if the same dimensions exist (i.e., can be matched)
                if set(base.dimensions()) != set(exp.dimensions()):
                    raise DimensionsError(('Dimensions of {!r} and {!r} cannot be '
                                           'matched').format(base.name(), exp.name()))
                
                # Otherwise, only the order is off, so just reorder/transpose
                elif base.dimensions() != exp.dimensions():
                    xdims = exp.dimensions()
                    neworder = [xdims.index(d) for d in base.dimensions()]
                    tname = 'transpose({},order={})'.format(exp.name(), neworder)
                    texp = FunctionEvaluator(tname, transpose, args=[None, neworder], 
                                             units=exp.units(), 
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
            op = FunctionEvaluator(fname, neg, units=val.units(),
                                   dimensions=val.dimensions())
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
            funits = right.units()
            fargs = [left, None]
            fops = [right]
            fdims = right.dimensions()
        
        elif isinstance(left, Operator) and isinstance(right, (int, float)):
            funits = left.units()
            fargs = [None, right]
            fops = [left]
            fdims = left.dimensions()

        elif isinstance(left, Operator) and isinstance(right, Operator):
            funits = left.units() * right.units()
            fargs = [None, None]
            fops = [left]
            fdims = left.dimensions()

            # Check if the same dimensions exist (i.e., can be matched)
            if set(left.dimensions()) != set(right.dimensions()):
                raise DimensionsError(('Dimensions of {!r} and {!r} cannot be '
                                       'matched').format(left.name(), right.name()))
            
            # Otherwise, only the order is off, so just reorder/transpose
            elif left.dimensions() != right.dimensions():
                rdims = right.dimensions()
                neworder = [rdims.index(d) for d in left.dimensions()]
                tname = 'transpose({},order={})'.format(right.name(), neworder)
                tright = FunctionEvaluator(tname, transpose, args=[None, neworder], 
                                           units=right.units(),
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
            if not right.units().is_dimensionless():
                raise UnitsError('Cannot add/subtract with incompatible units')
            funits = Unit(1)
            fargs = [left, None]
            fops = [right]
            fdims = right.dimensions()
        
        elif isinstance(left, Operator) and isinstance(right, (int, float)):
            if not left.units().is_dimensionless():
                raise UnitsError('Cannot add/subtract with incompatible units')
            funits = Unit(1)
            fargs = [None, right]
            fops = [left]
            fdims = left.dimensions()

        elif isinstance(left, Operator) and isinstance(right, Operator):
            funits = left.units()
            fargs = [None, None]
            fops = [left]
            fdims = left.dimensions()

            # Check units
            if not right.units().is_convertible(left.units()):
                raise UnitsError('Cannot add/subtract with incompatible units')
            elif right.units() != left.units():
                cunits1 = left.units()
                cunits2 = right.units()
                cname = 'convert({!s},to={!s})'.format(right, cunits1)
                cfunc = cunits2.convert
                cargs = [None, cunits1]
                cright = FunctionEvaluator(cname, cfunc, args=cargs, units=cunits1,
                                           dimensions=right.dimensions())
                self._opgraph.connect(right, cright)
                newr = cright
            else:
                newr = right

            # Check if the same dimensions exist (i.e., can be matched)
            if set(left.dimensions()) != set(newr.dimensions()):
                print left.dimensions(), newr.di
                raise DimensionsError(('Dimensions of {!r} and {!r} cannot be '
                                       'matched').format(left.name(), newr.name()))
            
            # Otherwise, only the order is off, so just reorder/transpose
            elif left.dimensions() != newr.dimensions():
                rdims = newr.dimensions()
                neworder = [rdims.index(d) for d in left.dimensions()]
                tname = 'transpose({},order={})'.format(right.name(), neworder)
                tright = FunctionEvaluator(tname, transpose, args=[None, neworder], 
                                           units=newr.units(),
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
    
    def parse_definition(self, definition):
        """
        Parse a variable definition string
        
        Parameters:
            definition (str): The string definition of the variable
            
        Returns:
            Operator: The root of the definition's OperationGraph
        """
        return self._expr.parseString(definition)[0]
    
    def get_graph(self):
        """
        Retrieve a copy of the internal OperationGraph
        """
        return deepcopy(self._opgraph)
    
    def reset(self):
        """
        Reset the internal OperationGraph
        """
        self._opgraph.clear()
