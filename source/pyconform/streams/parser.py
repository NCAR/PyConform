"""
Definiton Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import namedtuple
from pyparsing import nums, alphas, alphanums, oneOf, delimitedList, infixNotation, opAssoc
from pyparsing import Word, Combine as Comb, Optional as Opt, CaselessLiteral as Caseless
from pyparsing import QuotedString as QStr, Forward as Fwd, Group as Grp, Suppress as Sup
from pyparsing import Literal as Lit

from pyparsing import ParseExpression
ParseExpression.enablePackrat()

KwdType = namedtuple('KwdType', ['name', 'value'])
VarType = namedtuple('VarType', ['name', 'indices'])
FuncType = namedtuple('FuncType', ['name', 'arguments'])
OpType = namedtuple('OpType', ['symbol', 'arguments'])

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

# Starting point for all recursive expressions
expr = Fwd()

_key_words_ = (name_expr | str_expr | int_expr | float_expr)
_key_vals_ = Grp(_key_words_ + Sup(':') + expr)
_key_vals_.setParseAction(lambda t: tuple(*t))
dict_expr = Grp(Sup('{') + delimitedList(_key_vals_) + Sup('}'))
dict_expr.setParseAction(lambda t: dict(*t.asList()))

list_expr = Grp(Sup('[') + Opt(delimitedList(expr)) + Sup(']'))
list_expr.setParseAction(lambda t: t.asList())

tupl_expr = Grp(Sup('(') + delimitedList(expr) + Sup(')'))
tupl_expr.setParseAction(lambda t: tuple(*t))

_indices_ = delimitedList(slice_expr | int_expr | expr)
var_expr = Grp(name_expr + Opt(Sup('[') + _indices_ + Sup(']')))
var_expr.setParseAction(lambda t: VarType(t[0][0], t[0][1:]))

_kwd_arg_ = Grp(name_expr + Sup('=') + expr)
_kwd_arg_.setParseAction(lambda t: KwdType(t[0][0], t[0][1]))
_args_ = delimitedList(_kwd_arg_ | expr)
func_expr = Grp(name_expr + Sup('(') + Opt(_args_) + Sup(')'))
func_expr.setParseAction(lambda t: FuncType(t[0][0], t[0][1:]))


def neg_op_action(tokens):
    op, val = tokens[0]
    return val if op == '+' else OpType(op, [val])


def bin_op_action(tokens):
    left, op, right = tokens[0]
    return OpType(op, [left, right])


math_expr = infixNotation(func_expr | var_expr | ufloat_expr | uint_expr,
                          [(Lit('**'), 2, opAssoc.RIGHT, bin_op_action),
                           (oneOf('+ -'), 1, opAssoc.RIGHT, neg_op_action),
                           (oneOf('/ *'), 2, opAssoc.RIGHT, bin_op_action),
                           (oneOf('- +'), 2, opAssoc.RIGHT, bin_op_action),
                           (oneOf('< >'), 2, opAssoc.RIGHT, bin_op_action),
                           (Lit('=='), 2, opAssoc.RIGHT, bin_op_action)])

expr << (math_expr | str_expr | ufloat_expr | uint_expr | func_expr |
         var_expr | tupl_expr | dict_expr | list_expr)


def parse_definition(string):
    return expr.parseString(string)[0]
