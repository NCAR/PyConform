"""
Simple Parser Patterns/Expressions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import ParseExpression, Word, nums, alphas, alphanums, oneOf
from pyparsing import Combine as Comb, Optional as Opt, CaselessLiteral as Caseless
from pyparsing import QuotedString as QStr

ParseExpression.enablePackrat()

# Integers - convert to int
uint_expr = Word(nums)
uint_expr.setParseAction(lambda t: int(t[0]))

int_expr = Comb(Opt('-') + Word(nums))
int_expr.setParseAction(lambda t: int(t[0]))

# Floats - convert to float
_dec1_ = Comb(Word(nums) + '.' + Word(nums))
_dec2_ = Comb(Word(nums) + '.')
_dec3_ = Comb('.' + Word(nums))
_dec_ = Comb(_dec1_ | _dec2_ | _dec3_)
_exp_ = Comb(Caseless('e') + Opt(oneOf('+ -')) + Word(nums))
_flt1_ = Comb(Word(nums) + _exp_)
_flt2_ = Comb(_dec_ + Opt(_exp_))
ufloat_expr = Comb(_flt1_ | _flt2_)
ufloat_expr.setParseAction(lambda t: float(t[0]))

# Signed Floats
float_expr = Comb(Opt('-') + (_flt1_ | _flt2_))
float_expr.setParseAction(lambda t: float(t[0]))

# Variable Slices
_s_ = Word(': ')
slice_expr = Comb(Opt(int_expr) + _s_ + Opt(int_expr) + Opt(_s_ + int_expr))
slice_expr.setParseAction(lambda t: slice(*[int(i) if i else None
                                            for i in t[0].split(':')]))

# Quoted Strings with single or double quotes
_str1_ = QStr("'", escChar='\\')
_str2_ = QStr('"', escChar='\\')
str_expr = Comb(_str1_ | _str2_)

# Variable or Function Names
name_expr = Word(alphas + '_', alphanums + '_')
