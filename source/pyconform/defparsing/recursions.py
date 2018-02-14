"""
Definiton Parser Recusive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from patterns import uint, ufloat, string, variable
from pyparsing import Forward, Group, Suppress, Optional, delimitedList

# Starting point for all expressions
expression = Forward()

# List Expressions
__items = delimitedList(expression)
lists = Group(Suppress('[') + Optional(__items) + Suppress(']'))
lists.setParseAction(lambda t: t.asList())

# Tuple Expressions
tuples = Group(Suppress('(') + __items + Suppress(')'))
tuples.setParseAction(lambda t: tuple(*t.asList()))

# Combine to allow nested parsing
expression << (string | variable | ufloat | uint | lists | tuples)
