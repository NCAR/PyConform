"""
Definiton Parser Recusive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import namedtuple
from pyparsing import delimitedList, infixNotation, oneOf, opAssoc
from pyparsing import Forward as Fwd, Group as Grp, Suppress as Sup
from pyparsing import Optional as Opt, Literal as Lit
from simple import uint_expr, int_expr, ufloat_expr, str_expr, name_expr, slice_expr

from pyparsing import ParseExpression
ParseExpression.enablePackrat()

KwdType = namedtuple('KwdType', ['name', 'value'])
VarType = namedtuple('VarType', ['name', 'indices'])
FuncType = namedtuple('FuncType', ['name', 'arguments'])
OpType = namedtuple('OpType', ['symbol', 'arguments'])


def var_action(tokens):
    token = tokens[0]
    name = token[0]
    inds = token[1:]
    return VarType(name, inds)


def kwd_action(tokens):
    token = tokens[0]
    name = token[0]
    value = token[1]
    return KwdType(name, value)


def func_action(tokens):
    token = tokens[0]
    name = token[0]
    args = token[1:]
    return FuncType(name, args)


def neg_op_action(tokens):
    op, val = tokens[0]
    return val if op == '+' else OpType(op, [val])


def bin_op_action(tokens):
    left, op, right = tokens[0]
    return OpType(op, [left, right])


# Starting point for all recursive expressions
expr = Fwd()

keyval_expr = Grp(name_expr + Sup(':') + expr)
keyval_expr.setParseAction(lambda t: tuple(*t))

dict_expr = Grp(Sup('{') + delimitedList(keyval_expr) + Sup('}'))
dict_expr.setParseAction(lambda t: dict(*t.asList()))

list_expr = Grp(Sup('[') + Opt(delimitedList(expr)) + Sup(']'))
list_expr.setParseAction(lambda t: t.asList())

tupl_expr = Grp(Sup('(') + delimitedList(expr) + Sup(')'))
tupl_expr.setParseAction(lambda t: tuple(*t))

var_expr = Grp(name_expr +
               Opt(Sup('[') + delimitedList(slice_expr | int_expr | expr) + Sup(']')))
var_expr.setParseAction(var_action)

kwd_expr = Grp(name_expr + Sup('=') + expr)
kwd_expr.setParseAction(kwd_action)

func_expr = Grp(name_expr +
                Sup('(') + Opt(delimitedList(kwd_expr | expr)) + Sup(')'))
func_expr.setParseAction(func_action)

math_expr = infixNotation(func_expr | var_expr | ufloat_expr | uint_expr,
                          [(Lit('**'), 2, opAssoc.RIGHT, bin_op_action),
                           (oneOf('+ -'), 1, opAssoc.RIGHT, neg_op_action),
                           (oneOf('/ *'), 2, opAssoc.RIGHT, bin_op_action),
                           (oneOf('- +'), 2, opAssoc.RIGHT, bin_op_action),
                           (oneOf('< >'), 2, opAssoc.RIGHT, bin_op_action),
                           (Lit('=='), 2, opAssoc.RIGHT, bin_op_action)])

expr << (math_expr | str_expr | ufloat_expr | uint_expr | func_expr |
         var_expr | tupl_expr | dict_expr | list_expr)
