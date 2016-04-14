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
        self.obj = token[0]
        self.args = tuple(token[1:])
    def __repr__(self):
        return "<{0} {1}{2} at {3!s}>".format(self.__class__.__name__,
                                              self.obj,
                                              self.args,
                                              hex(id(self)))
    def __eq__(self, other):
        return ((type(self) == type(other)) and
                (self.obj == other.obj) and
                (self.args == other.args))


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
# OperatorPST - Operator ParsedStringType
#===============================================================================
class OperatorPST(ParsedStringType):
    """
    A parsed function string-type
    """
    pass


#===============================================================================
# DefinitionParser
#===============================================================================

# Negation operator
def _negop_(tokens):
    op, val = tokens[0]
    if op == '+':
        return val
    else:
        return OperatorPST([[neg, val]])

# Binary Operators
_BIN_OPS_ = {'^': pow, '*': mul, '/': truediv, '+': add, '-': sub}
def _binop_(tokens):
    left, op, right = tokens[0]
    return OperatorPST([[_BIN_OPS_[op], left, right]])

# INTEGERS: Just any word consisting only of numbers
_INT_ = Word(nums)
_INT_.setParseAction(lambda t: int(t[0]))

# FLOATS: More complicated... can be decimal format or exponential
#         format or a combination of the two
_DEC_FLT_ = ( Combine( Word(nums) + '.' + Word(nums) ) |
              Combine( Word(nums) + '.' ) |
              Combine( '.' + Word(nums) ) )
_EXP_FLT_ = ( Combine( CaselessLiteral('e') +
                       Optional( oneOf('+ -') ) +
                       Word(nums) ) )
_FLOAT_ = ( Combine( Word(nums) + _EXP_FLT_ ) |
            Combine( _DEC_FLT_ + Optional(_EXP_FLT_) ) )
_FLOAT_.setParseAction(lambda t: float(t[0]))

# String _NAME_s ...identifiers for function or variable _NAME_s
_NAME_ = Word( alphas+"_", alphanums+"_" )

# FUNCTIONS: Function arguments can be empty or any combination of
#            ints, _FLOAT_, variables, and even other functions.  Hence,
#            we need a Forward place-holder to start...
_EXPR_PARSER_ = Forward()
_FUNC_ = Group(_NAME_ + (Suppress('(') + 
                         Optional(delimitedList(_EXPR_PARSER_)) +
                         Suppress(')')))
_FUNC_.setParseAction(FunctionPST)

# VARIABLE NAMES: Can be just string _NAME_s or _NAME_s with blocks
#                 of indices (e.g., [1,2,-4])    
_INDEX_ = Combine( Optional('-') + Word(nums) )
_INDEX_.setParseAction(lambda t: int(t[0]))
_ISLICE_ = _INDEX_ + Optional(Suppress(':') + _INDEX_ +
                              Optional(Suppress(':') + _INDEX_))
_ISLICE_.setParseAction(lambda t: slice(*t) if len(t) > 1 else t[0])
#         variable = Group(_NAME_ + Optional(Suppress('[') +
#                                            delimitedList(_ISLICE_ | 
#                                                          _EXPR_PARSER_) +
#                                          Suppress(']')))
_VARIABLE_ = Group(_NAME_ + Optional(Suppress('[') +
                                     delimitedList(_ISLICE_) +
                                     Suppress(']')))
_VARIABLE_.setParseAction(VariablePST)

# Expression parser
_EXPR_PARSER_ << operatorPrecedence(_FLOAT_ | _INT_ | _FUNC_ | _VARIABLE_,
                                    [(Literal('^'), 2, opAssoc.RIGHT, _binop_),
                                     (oneOf('+ -'), 1, opAssoc.RIGHT, _negop_),
                                     (oneOf('* /'), 2, opAssoc.RIGHT, _binop_),
                                     (oneOf('+ -'), 2, opAssoc.RIGHT, _binop_)])

# Parse a string variable definition
def parse_definition(strexpr):
    return _EXPR_PARSER_.parseString(strexpr)[0]


#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == "__main__":
    pass
