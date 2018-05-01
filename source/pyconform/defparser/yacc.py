"""
PLY - Yacc Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from lex import *  # @UnusedWildImport
from ply import yacc
from collections import namedtuple

OpType = namedtuple('VarType', ['name', 'arguments'])
VarType = namedtuple('VarType', ['name', 'indices'])
FuncType = namedtuple('FuncType', ['name', 'arguments', 'keywords'])

precedence = (('left', 'EQ'),
              ('left', '<', '>', 'LEQ', 'GEQ'),
              ('left', '+', '-'),
              ('left', '*', '/'),
              ('right', 'NEG', 'POS'),
              ('left', 'POW'))


def p_array_like(p):
    """
    array_like : FLOAT
    array_like : INT
    array_like : function
    array_like : variable
    """
    p[0] = p[1]


def p_array_like_group(p):
    """
    array_like : '(' array_like ')'
    """
    p[0] = p[2]


def p_function_with_arguments_and_keywords(p):
    """
    function : NAME '(' argument_list ',' keyword_dict ')'
    """
    p[0] = FuncType(p[1], p[3], p[5])


def p_function_with_arguments_only(p):
    """
    function : NAME '(' argument_list ')'
    """
    p[0] = FuncType(p[1], p[3], {})


def p_function_with_keywords_only(p):
    """
    function : NAME '(' keyword_dict ')'
    """
    p[0] = FuncType(p[1], [], p[3])


def p_argument_list_append(p):
    """
    argument_list : argument_list ',' argument
    """
    p[0] = p[1] + [p[3]]


def p_single_item_argument_list(p):
    """
    argument_list : argument
    argument_list : 
    """
    p[0] = [p[1]] if len(p) > 1 else []


def p_argument(p):
    """
    argument : array_like
    argument : STRING
    """
    p[0] = p[1]


def p_keyword_dict_setitem(p):
    """
    keyword_dict : keyword_dict ',' NAME '=' argument
    """
    p[1][p[3]] = p[5]
    p[0] = p[1]


def p_single_item_keyword_dict(p):
    """
    keyword_dict : NAME '=' argument
    """
    p[0] = {p[1]: p[3]}


def p_variable(p):
    """
    variable : NAME '[' index_list ']'
    variable : NAME
    """
    indices = p[3] if len(p) > 3 else []
    p[0] = VarType(p[1], indices)


def p_index_list_append(p):
    """
    index_list : index_list ',' index
    """
    p[0] = p[1] + [p[3]]


def p_single_item_index_list(p):
    """
    index_list : index
    """
    p[0] = [p[1]]


def p_index(p):
    """
    index : slice
    index : INT
    """
    p[0] = p[1]


def p_slice(p):
    """
    slice : slice_argument ':' slice_argument ':' slice_argument
    slice : slice_argument ':' slice_argument
    """
    p[0] = slice(*p[1::2])


def p_slice_argument(p):
    """
    slice_argument : INT
    slice_argument : 
    """
    p[0] = p[1] if len(p) > 1 else None


def p_expression_unary(p):
    """
    array_like : '-' array_like %prec NEG
    array_like : '+' array_like %prec POS
    """
    if p[1] == '+':
        p[0] = p[2]
    elif p[1] == '-':
        if isinstance(p[2], (OpType, VarType, FuncType)):
            p[0] = OpType(p[1], [p[2]])
        else:
            p[0] = -p[2]


def p_expression_binary(p):
    """
    array_like : array_like POW array_like
    array_like : array_like '-' array_like
    array_like : array_like '+' array_like
    array_like : array_like '*' array_like
    array_like : array_like '/' array_like
    array_like : array_like '<' array_like
    array_like : array_like '>' array_like
    array_like : array_like LEQ array_like
    array_like : array_like GEQ array_like
    array_like : array_like EQ array_like
    """
    if (isinstance(p[1], (OpType, VarType, FuncType)) or
            isinstance(p[3], (OpType, VarType, FuncType))):
        p[0] = OpType(p[2], [p[1], p[3]])
    elif p[2] == '**':
        p[0] = p[1] ** p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]
    elif p[2] == '<':
        p[0] = p[1] < p[3]
    elif p[2] == '>':
        p[0] = p[1] > p[3]
    elif p[2] == '<=':
        p[0] = p[1] <= p[3]
    elif p[2] == '>=':
        p[0] = p[1] >= p[3]
    elif p[2] == '==':
        p[0] = p[1] == p[3]


def p_error(p):
    raise TypeError('Parsing error at {!r}'.format(p.value))


yacc.yacc()
