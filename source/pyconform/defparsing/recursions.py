"""
Definiton Parser Recusive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import Forward, Group, Suppress, Optional, delimitedList

from patterns import uinteger, ufloat, string, variable
from actions import list_action

# Starting point for all expressions
expression = Forward()

# List Expressions
__items = delimitedList(expression)
lists = Group(Suppress('[') + Optional(__items) + Suppress(']'))
lists.setParseAction(list_action)

# Combine to allow nested parsing
expression << (string | ufloat | uinteger | variable | lists)
