"""
Parsing Module

This module defines the necessary elements to parse a string variable definition
into the recognized elements that are used to construct an Operation Graph.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from numpy import index_exp
from pyparsing import nums, alphas, alphanums, oneOf, delimitedList, opAssoc, operatorPrecedence,\
    ParseException
from pyparsing import Word, Combine, Forward, Suppress, Group, Optional, ParserElement
from pyparsing import Literal, CaselessLiteral, QuotedString, ParseException

# To improve performance
ParserElement.enablePackrat()

#===================================================================================================
# ParsedFunction
#===================================================================================================
class ParsedFunction(object):
    """
    A parsed function string-type
    """

    def __init__(self, tokens):
        token = tokens[0]
        self.key = token[0]
        self.args = tuple(token[1:])
    def __repr__(self):
        return ("<{0} {1}{2!r} ('{3}') at {4}>"
                ).format(self.__class__.__name__, self.key, self.args, str(self), hex(id(self)))
    def __str__(self):
        strargs = '({0})'.format(','.join(str(arg) for arg in self.args))
        return "{0}{1!s}".format(self.key, strargs)
    def __eq__(self, other):
        return ((type(self) == type(other)) and
                (self.key == other.key) and
                (self.args == other.args))
        
        
#===================================================================================================
# ParsedUniOp
#===================================================================================================
class ParsedUniOp(ParsedFunction):
    """
    A parsed unary-operator string-type
    """
    def __str__(self):
        return "({0}{1!s})".format(self.key, self.args[0])


#===================================================================================================
# ParsedBinOp
#===================================================================================================
class ParsedBinOp(ParsedFunction):
    """
    A parsed binary-operator string-type
    """
    def __str__(self):
        return "({0!s}{1}{2!s})".format(self.args[0], self.key, self.args[1])


#===================================================================================================
# ParsedVariable
#===================================================================================================
class ParsedVariable(ParsedFunction):
    """
    A parsed variable string-type
    """
    def __init__(self, tokens):
        super(ParsedVariable, self).__init__(tokens)
        self.args = index_exp[self.args] if len(self.args) > 0 else ()
    def __repr__(self):
        return "<{0} '{1}' at {2}>".format(self.__class__.__name__, str(self), hex(id(self)))
    def __str__(self):
        if len(self.args) == 0:
            strargs = ''
        else:
            strargs = str(list(self.args))
        return "{0}{1}".format(self.key, strargs)


#===================================================================================================
# Operator Parser Functions
#===================================================================================================

# Negation operator
def _negop_(tokens):
    op, val = tokens[0]
    if op == '+':
        return val
    else:
        return ParsedUniOp([[op, val]])

# Binary Operators
def _binop_(tokens):
    left, op, right = tokens[0]
    return ParsedBinOp([[op, left, right]])

#===================================================================================================
# MAIN PARSER (DEFINED AT MODULE LEVEL TO MAKE A SINGLETON)
#===================================================================================================

# INTEGERS: Just any word consisting only of numbers
_INT_ = Word(nums)
_INT_.setParseAction(lambda t: int(t[0]))

# FLOATS: More complicated... can be decimal format or exponential
#         format or a combination of the two
_DEC_FLT_ = (Combine(Word(nums) + '.' + Word(nums)) |
             Combine(Word(nums) + '.') |
             Combine('.' + Word(nums)))
_EXP_FLT_ = (Combine(CaselessLiteral('e') + Optional(oneOf('+ -')) + Word(nums)))
_FLOAT_ = (Combine(Word(nums) + _EXP_FLT_) | Combine(_DEC_FLT_ + Optional(_EXP_FLT_)))
_FLOAT_.setParseAction(lambda t: float(t[0]))

# QUOTED STRINGS: Any words between quotations
_QSTR_ = QuotedString('"', escChar='\\')

# String _NAME_s ...identifiers for function or variable _NAME_s
_NAME_ = Word(alphas + "_", alphanums + "_")

# FUNCTIONS: Function arguments can be empty or any combination of
#            ints, _FLOAT_, variables, and even other functions.  Hence,
#            we need a Forward place-holder to start...
_EXPR_PARSER_ = Forward()
_FUNC_ = Group(_NAME_ + (Suppress('(') + Optional(delimitedList(_QSTR_ | _EXPR_PARSER_)) + Suppress(')')))
_FUNC_.setParseAction(ParsedFunction)

# VARIABLE NAMES: Can be just string _NAME_s or _NAME_s with blocks
#                 of indices (e.g., [1,2,-4])
_INDEX_ = Combine(Optional('-') + Word(nums))
_INDEX_.setParseAction(lambda t: int(t[0]))

_IDX_OR_NONE_ = Optional(_INDEX_)
_IDX_OR_NONE_.setParseAction(lambda t: t[0] if len(t) > 0 else [None])

# _ISLICE_ = _IDX_OR_NONE_ + Optional(Suppress(':') + _IDX_OR_NONE_ + Optional(Suppress(':') + _IDX_OR_NONE_))
# _ISLICE_.setParseAction(lambda t: slice(*t) if len(t) > 1 else t[0])
_ISLICE_ = delimitedList(_IDX_OR_NONE_, delim=':')
_ISLICE_.setParseAction(lambda t: slice(*t) if len(t) > 1 else t[0])

_VARIABLE_ = Group(_NAME_ + Optional(Suppress('[') + delimitedList(_ISLICE_ | _INDEX_) + Suppress(']')))
_VARIABLE_.setParseAction(ParsedVariable)

# Expression parser
_EXPR_PARSER_ << operatorPrecedence(_FLOAT_ | _INT_ | _FUNC_ | _VARIABLE_,
                                    [(Literal('^'), 2, opAssoc.RIGHT, _binop_),
                                     (oneOf('+ -'), 1, opAssoc.RIGHT, _negop_),
                                    (Literal('/'), 2, opAssoc.RIGHT, _binop_),
                                    (Literal('*'), 2, opAssoc.RIGHT, _binop_),
                                    (Literal('-'), 2, opAssoc.RIGHT, _binop_),
                                    (Literal('+'), 2, opAssoc.RIGHT, _binop_)])

#===================================================================================================
# Function to parse a string definition
#===================================================================================================

def parse_definition(strexpr):
    return _EXPR_PARSER_.parseString(strexpr)[0]
