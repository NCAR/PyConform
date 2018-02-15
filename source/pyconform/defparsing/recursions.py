"""
Definiton Parser Recusive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import Forward, Group, Suppress, Optional, delimitedList

from patterns import uinteger, ufloat, string, variable, name
from actions import list_action, function_action

# Starting point for all expressions
expression = Forward()

# List Expressions
__items = delimitedList(expression)
lists = Group(Suppress('[') + Optional(__items) + Suppress(']'))
lists.setParseAction(list_action)

# Keyword Arguments
_keyword_ = Group(name + Suppress('=') + (string | expression))
_keyword_.setParseAction(lambda t: tuple(*t))

# Function Expressions
_arguments_ = Optional(delimitedList(string | _keyword_ | expression))
function = Group(name + (Suppress('(') + _arguments_ + Suppress(')')))
function.setParseAction(function_action)

# Combine to allow nested parsing
expression << (string | ufloat | uinteger | function | variable | lists)
