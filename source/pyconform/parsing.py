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

import operator


#===============================================================================
# DefitionParser
#===============================================================================
class DefitionParser(object):
    """
    Variable Definition Parser
    """
    
    def __init__(self):
        """
        Initializer
        """

        # Integer operands
        integers = Word(nums)
        integers.setParseAction(lambda s,l,t: int(t[0]))
        
        # Floating-point operands
        floats = Combine(Word(nums) + '.' + Optional(Word(nums)))
        floats.setParseAction(lambda s,l,t: float(t[0]))

        # String variable name operands    
        varname = Word(alphas + "_", alphanums + "_" )
        
        # Define the basic operand
        operand = floats | integers | varname
    
        # Define how to parse exponent operator and arguments
        expop = Literal('^')
        def exp_func(tokens):
            base, _, exp = tokens[0]
            return operator.pow, base, exp
    
        # Define how to parse +/- sign operators and arguments
        signops = oneOf('+ -')
        def sign_func(tokens):
            sgn, val = tokens[0]
            if sgn == '+':
                return val
            else:
                return operator.neg, val
    
        # Define how to parse multiplication/division operators and arguments
        multops = oneOf('* /')
        def mult_func(tokens):
            left, op, right = tokens[0]
            if op == '*':
                return operator.mul, left, right
            else:
                return operator.div, left, right
    
        # Define how to parse addition/subtraction operators and arguments
        plusops = oneOf('+ -')
        def plus_func(tokens):
            left, op, right = tokens[0]
            if op == '+':
                return operator.add, left, right
            else:
                return operator.sub, left, right
    
        # Define the expression parser using operator precedence
        self._expr = operatorPrecedence(operand,
                                        [(expop, 2, opAssoc.RIGHT, exp_func),
                                         (signops, 1, opAssoc.RIGHT, sign_func),
                                         (multops, 2, opAssoc.RIGHT, mult_func),
                                         (plusops, 2, opAssoc.RIGHT, plus_func)])
        
    def parse_definition(self, definition):
        """
        Parse a variable definition string
        
        Parameters:
            definition (str): The string definition of the variable
        """
        return self._expr.parseString(definition)[0]
    
    def name_definition(self, deftree):
        """
        Compute a string from a definition tuple
        
        Parameters:
            definition (tuple): An definition tuple
        """
        strval = ''
        if isinstance(deftree, tuple):
            strval += deftree[0].__name__ + '('
            strval += ','.join(self.name_definition(dt) for dt in deftree[1:])
            strval += ')'
        else:
            strval += str(deftree)
        return strval
