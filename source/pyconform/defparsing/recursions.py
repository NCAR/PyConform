"""
Definiton Parser Recusive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import Forward, Group, Suppress, Optional, Literal, ParseExpression
from pyparsing import delimitedList, infixNotation, oneOf, opAssoc, nestedExpr

from patterns import uinteger, ufloat, string, variable, name
from actions import keyword_action, function_action
from actions import unary_op_action, binary_op_action

ParseExpression.enablePackrat()

# Starting point for all expressions
expression = Forward()

# Keyword Arguments
_keyword_ = Group(name + Suppress('=') + (string | expression))
_keyword_.setParseAction(keyword_action)

# Function Expressions
_arguments_ = Optional(delimitedList(_keyword_ | string | expression))
function = Group(name + Suppress('(') + _arguments_ + Suppress(')'))
function.setParseAction(function_action)
function.setDebug(True)

# Mathematical Parsing
mathematics = infixNotation(function | variable | ufloat | uinteger,
                            [(Literal('**'), 2, opAssoc.RIGHT, binary_op_action),
                             (oneOf('+ -'), 1, opAssoc.RIGHT, unary_op_action),
                             (oneOf('/ *'), 2, opAssoc.RIGHT, binary_op_action),
                             (oneOf('- +'), 2, opAssoc.RIGHT, binary_op_action),
                             (oneOf('< >'), 2, opAssoc.RIGHT, binary_op_action),
                             (Literal('=='), 2, opAssoc.RIGHT, binary_op_action)])

# Combine to allow nested parsing
expression << mathematics
