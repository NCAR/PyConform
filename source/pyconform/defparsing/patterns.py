"""
Simple Parser Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import Word, Combine, Optional, CaselessLiteral, QuotedString, Group, Suppress
from pyparsing import nums, alphas, alphanums, oneOf, delimitedList

from actions import integer_action, float_action, variable_action

# Unsigned Integers - convert to int
numw = Word(nums)
uint = numw
uint.setParseAction(integer_action)

# Signed Integers
integer = Combine(Optional('-') + numw)
integer.setParseAction(integer_action)

# Unsigned Floats - convert to float
_decimal1_ = Combine(numw + '.' + numw)
_decimal2_ = Combine(numw + '.')
_decimal3_ = Combine('.' + numw)
_decimal_ = Combine(_decimal1_ | _decimal2_ | _decimal3_)
_exponent_ = Combine(CaselessLiteral('e') + Optional(oneOf('+ -')) + numw)
_float1_ = Combine(numw + _exponent_)
_float2_ = Combine(_decimal_ + Optional(_exponent_))
ufloat = Combine(_float1_ | _float2_)
ufloat.setParseAction(float_action)

# Quoted Strings with single or double quotes
_string1_ = QuotedString("'", escChar='\\')
_string2_ = QuotedString('"', escChar='\\')
string = Combine(_string1_ | _string2_)

# Variable or Function Names
name = Word(alphas + '_', alphanums + '_')

# Variables with slice Indices
_index_or_none_ = Optional(integer)
_index_or_none_.setParseAction(lambda t: t[0] if len(t) > 0 else [None])
_slice_ = delimitedList(_index_or_none_, delim=':')
_slice_.setParseAction(lambda t: slice(*t) if len(t) > 1 else t[0])
_indices_ = (Suppress('[') + delimitedList(_slice_) + Suppress(']'))
_indices_.setParseAction(lambda t: t.asList())
variable = Group(name + Optional(_indices_))
variable.setParseAction(variable_action)
