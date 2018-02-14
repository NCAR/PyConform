"""
Simple Parser Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import Word, Combine, oneOf, Optional, CaselessLiteral, QuotedString
from pyparsing import nums, alphas, alphanums

# Unsigned Integers - convert to int
__numbers = Word(nums)
integers = __numbers
integers.setParseAction(lambda t: int(t[0]))

# Unsigned Floats - convert to float
__decimal_1 = Combine(__numbers + '.' + __numbers)
__decimal_2 = Combine(__numbers + '.')
__decimal_3 = Combine('.' + __numbers)
__decimal = Combine(__decimal_1 | __decimal_2 | __decimal_3)
__exponent = Combine(CaselessLiteral('e') + Optional(oneOf('+ -')) + __numbers)
__float_1 = Combine(__numbers + __exponent)
__float_2 = Combine(__decimal + Optional(__exponent))
floats = Combine(__float_1 | __float_2)
floats.setParseAction(lambda t: float(t[0]))

# Quoted Strings with single or double quotes
__string_1 = QuotedString("'", escChar='\\')
__string_2 = QuotedString('"', escChar='\\')
strings = Combine(__string_1 | __string_2)

# Variable or Function Names
names = Word(alphas + '_', alphanums + '_')
