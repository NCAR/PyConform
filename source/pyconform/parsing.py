"""
Parsing Module

This module defines the necessary elements to parse a string variable definition
into the recognized elements that are used to construct an Operation Graph.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import (nums, alphas, alphanums, oneOf, delimitedList,
                       operatorPrecedence, opAssoc, Word, Combine, Literal,
                       Forward, Suppress, Group, CaselessLiteral, Optional)
from operator import neg, pow, add, sub, truediv, mul

#===============================================================================
# ParsedStringType
#===============================================================================
class ParsedStringType(object):
    """
    A string-type object parsed from a variable definition
    """

    def __init__(self, tokens):
        token = tokens[0]
        self.name = token[0]
        self.args = tuple(token[1:])
    def __repr__(self):
        return "<{0} {1}{2} at {3!s}>".format(self.__class__.__name__,
                                              self.name,
                                              self.args,
                                              hex(id(self)))
    def __eq__(self, other):
        return (type(self) == type(other)) and (self.name == other.name) and (self.args == other.args)


#===============================================================================
# VariablePST - Variable ParsedStringType
#===============================================================================
class VariablePST(ParsedStringType):
    """
    A parsed variable string-type
    """
    pass


#===============================================================================
# FunctionPST - Function ParsedStringType
#===============================================================================
class FunctionPST(ParsedStringType):
    """
    A parsed function string-type
    """
    pass


#===============================================================================
# DefinitionParser
#===============================================================================
class DefinitionParser(object):
    """
    String variable-definition parser
    """

    def __init__(self):
        # INTEGERS: Just any word consisting only of numbers
        integer = Word(nums)
        integer.setParseAction(lambda t: int(t[0]))
        
        # FLOATS: More complicated... can be decimal format or exponential
        #         format or a combination of the two
        dec_flt = ( Combine( Word(nums) + '.' + Word(nums) ) |
                    Combine( Word(nums) + '.' ) |
                    Combine( '.' + Word(nums) ) )
        flt_exp = ( Combine( CaselessLiteral('e') +
                             Optional( oneOf('+ -') ) +
                             Word(nums) ) )
        floats = ( Combine( Word(nums) + flt_exp ) |
                   Combine( dec_flt + Optional(flt_exp) ) )
        floats.setParseAction(lambda t: float(t[0]))
    
        # String names ...identifiers for function or variable names
        name = Word( alphas+"_", alphanums+"_" )
        
        # FUNCTIONS: Function arguments can be empty or any combination of
        #            ints, floats, variables, and even other functions.  Hence,
        #            we need a Forward place-holder to start...
        expr = Forward()
        func = Group(name + (Suppress('(') + 
                             Optional(delimitedList(expr)) +
                             Suppress(')')))
        func.setParseAction(FunctionPST)
    
        # VARIABLE NAMES: Can be just string names or names with blocks
        #                 of indices (e.g., [1,2,-4])    
        index = Combine( Optional('-') + Word(nums) )
        index.setParseAction(lambda t: int(t[0]))
        islice = index + Optional(Suppress(':') + index +
                                  Optional(Suppress(':') + index))
        islice.setParseAction(lambda t: slice(*t) if len(t) > 1 else t[0])
        variable = Group(name + Optional(Suppress('[') +
                                         delimitedList(islice | expr) +
                                         Suppress(']')))
        variable.setParseAction(VariablePST)
    
        # Binary Operators
        self._binops = {'^': pow, '*': mul, '/': truediv, '+': add, '-': sub}
    
        # Expression parser
        expr << operatorPrecedence(floats | integer | func | variable,
                                   [(Literal('^'), 2, opAssoc.RIGHT, self._binop_),
                                    (oneOf('+ -'), 1, opAssoc.RIGHT, self._negop_),
                                    (oneOf('* /'), 2, opAssoc.RIGHT, self._binop_),
                                    (oneOf('+ -'), 2, opAssoc.RIGHT, self._binop_)])
        
        self._expr = expr
    
    def _negop_(self, tokens):
        op, val = tokens[0]
        if op == '+':
            return val
        else:
            return neg, val
        
    def _binop_(self, tokens):
        left, op, right = tokens[0]
        return self._binops[op], left, right
    
    def parse(self, strexpr):
        return self._expr.parseString(strexpr)[0]
