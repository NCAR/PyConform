"""
Basic Parser Tokenizers

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import Word, Combine, oneOf, Optional, CaselessLiteral, QuotedString
from pyparsing import nums, alphas, alphanums

# Unsigned Integers - convert to int
_numbers = Word(nums)
unsigned_integer = _numbers
unsigned_integer.setParseAction(lambda t: int(t[0]))

# Unsigned Floats - convert to float
_decimal_1 = Combine(_numbers + '.' + _numbers)
_decimal_2 = Combine(_numbers + '.')
_decimal_3 = Combine('.' + _numbers)
_decimal = Combine(_decimal_1 | _decimal_2 | _decimal_3)
_exponent = Combine(CaselessLiteral('e') + Optional(oneOf('+ -')) + _numbers)
_float_1 = Combine(_numbers + _exponent)
_float_2 = Combine(_decimal + Optional(_exponent))
_float = Combine(_float_1 | _float_2)
unsigned_float = _float
unsigned_float.setParseAction(lambda t: float(t[0]))

# Quoted Strings with single or double quotes
_quote_1 = QuotedString("'", escChar='\\')
_quote_2 = QuotedString('"', escChar='\\')
quoted_string = Combine(_quote_1 | _quote_2)

# Variable or Function Names
name = Word(alphas + '_', alphanums + '_')
