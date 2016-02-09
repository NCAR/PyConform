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


#===============================================================================
# DefitionParser
#===============================================================================
class DefitionParser(object):
    """
    Variable Definition Parser
    """
    
    def __init__(self, inpdataset=InputDataset()):
        """
        Initializer
        
        Parameters:
            inpdataset (InputDataset): The input dataset containing the variable
                information referenced by the output dataset definitions
        """
        # Type Checking
        if not isinstance(inpdataset, InputDataset):
            raise TypeError('Input dataset must be of InputDataset type')
        self._ids = inpdataset
                
        # Cyclic iterator over available input filenames
        fnames = [v.filename for v in self._ids.variables.itervalues()]
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
        if varname not in self._ids.variables:
            err_msg = ('Definition {!r} references variable {!r} that is not '
                       'is not found in the reference dataset '
                       '{!r}').format(s, varname, self._ids.name)
            raise KeyError(err_msg)
        if self._ids.variables[varname].filename:
            fname = self._ids.variables[varname].filename
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
            raise ValueError('Power exponents must be dimensionless')
        
        # If the base is int/float, then exponent must be an Operator
        if isinstance(base, (int, float)) and isinstance(exp, Operator):
            fargs = [base, None]
            fops = [exp]
            funits = Unit(1)
        
        # If the base is an Operator, then the exponent can be anything
        elif isinstance(base, Operator):
            fops = [base]
            
            # If the exponent is an int, then base units can be anything
            if isinstance(exp, int):
                fargs = [None, exp]
                funits = base.units() ** exp
            
            # If the exponent is a float, then base must be dimensionless
            elif isinstance(exp, float):
                if not base.units().is_dimensionless():
                    raise ValueError('Floating-point exponents can only be '
                                     'applied to dimensionless bases')
                fargs = [None, exp]
                funits = Unit(1)   
            
            # If exponent is an operator, then base must be dimensionless
            elif isinstance(exp, Operator):
                if not base.units().is_dimensionless():
                    raise ValueError('Element-wise power operations can only '
                                     'be applied to dimensionless bases')
                fargs = []
                fops.append(exp)
                funits = Unit(1)    
            
            else:
                raise ValueError('Unrecognized exponent datatype')                
        else:
            raise ValueError('Unrecognized base datatype')                

        fname = '({!s}^{!s})'.format(base, exp)
        op = FunctionEvaluator(fname, pow, args=fargs, units=funits)
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
            op = FunctionEvaluator(fname, neg, units=val.units())
            self._opgraph.connect(val, op)
            return op
        else:
            raise ValueError('Unrecognized operand datatype')                

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
        
        elif isinstance(left, Operator) and isinstance(right, (int, float)):
            funits = left.units()
            fargs = [None, right]
            fops = [left]

        elif isinstance(left, Operator) and isinstance(right, Operator):
            funits = left.units() * right.units()
            fargs = [None, None]
            fops = [left, right]
        
        else:
            raise ValueError('Unrecognized operand datatype')
        
        fname = '({!s}{!s}{!s})'.format(left, opstr, right)
        op = FunctionEvaluator(fname, fptr, args=fargs, units=funits)
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
                raise ValueError('Cannot add/subtract with incompatible units')
            funits = Unit(1)
            fargs = [left, None]
            fops = [right]
        
        elif isinstance(left, Operator) and isinstance(right, (int, float)):
            if not left.units().is_dimensionless():
                raise ValueError('Cannot add/subtract with incompatible units')
            funits = Unit(1)
            fargs = [None, right]
            fops = [left]

        elif isinstance(left, Operator) and isinstance(right, Operator):
            if not right.units().is_convertible(left.units()):
                raise ValueError('Cannot add/subtract with incompatible units')
            elif right.units() != left.units():
                cunits1 = left.units()
                cunits2 = right.units()
                cname = 'convert({!s},to={!s})'.format(right, cunits1)
                cfunc = cunits2.convert
                cargs = [None, cunits1]
                cright = FunctionEvaluator(cname, cfunc, args=cargs, units=cunits1)
                self._opgraph.connect(right, cright)
                funits = cunits1
                fargs = [None, None]
                fops = [left, cright]
            else:
                funits = left.units()
                fargs = [None, None]
                fops = [left, right]

        else:
            raise ValueError('Unrecognized operand datatype')
        
        fname = '({!s}{!s}{!s})'.format(left, opstr, right)
        op = FunctionEvaluator(fname, fptr, args=fargs, units=funits)
        for op1 in fops:
            self._opgraph.connect(op1, op)
        return op
    
    def parse_definition(self, definition):
        """
        Parse a variable definition string
        
        Parameters:
            definition (str): The string definition of the variable
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
