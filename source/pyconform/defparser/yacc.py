"""
PLY - Yacc Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from lex import *  # @UnusedWildImport
from ply import yacc
from collections import namedtuple

VarType = namedtuple('VarType', ['name', 'indices'])
FuncType = namedtuple('FuncType', ['name', 'arguments', 'keywords'])

precedence = (('right', 'NEGATIVE', 'POSITIVE'),)


def p_expression(p):
    """
    expression : FLOAT
    expression : INT
    expression : variable
    expression : function
    """
    p[0] = p[1]


def p_expression_variable(p):
    """
    variable : NAME LBRACKET indices RBRACKET
    variable : NAME
    """
    indices = p[3] if len(p) > 3 else []
    p[0] = VarType(p[1], indices)


def p_indices(p):
    """
    indices : indices COMMA slice
    indices : indices COMMA INT
    """
    p[0] = p[1] + [p[3]]


def p_index(p):
    """
    indices : slice
    indices : INT
    """
    p[0] = [p[1]]


def p_slice(p):
    """
    slice : slice_argument COLON slice_argument COLON slice_argument
    slice : slice_argument COLON slice_argument
    """
    p[0] = p[1] if len(p) == 2 else slice(*p[1::2])


def p_slice_argument(p):
    """
    slice_argument : INT
    slice_argument : 
    """
    p[0] = p[1] if len(p) > 1 else None


def p_expression_function(p):
    """
    function : NAME LPAREN arguments COMMA keywords RPAREN
    """
    p[0] = FuncType(p[1], p[3], p[5])


def p_expression_function_args_only(p):
    """
    function : NAME LPAREN arguments RPAREN
    """
    p[0] = FuncType(p[1], p[3], {})


def p_expression_function_kwds_only(p):
    """
    function : NAME LPAREN keywords RPAREN
    """
    p[0] = FuncType(p[1], [], p[3])


def p_arguments(p):
    """
    arguments : arguments COMMA expression
    """
    p[0] = p[1] + [p[3]]


def p_argument(p):
    """
    arguments : expression
    arguments : 
    """
    p[0] = [p[1]] if len(p) > 1 else []


def p_keywords(p):
    """
    keywords : keywords COMMA NAME EQUALS expression
    """
    p[1][p[3]] = p[5]
    p[0] = p[1]


def p_keyword(p):
    """
    keywords : NAME EQUALS expression
    keywords : 
    """
    p[0] = {p[1]: p[3]} if len(p) > 1 else {}


def p_expression_unary(p):
    """
    expression : MINUS expression %prec NEGATIVE
    expression : PLUS expression %prec POSITIVE
    """
    if p[1] == '+':
        p[0] = p[2]
    elif p[1] == '-':
        p[0] = -p[2]


def p_error(p):
    raise TypeError('Parsing error at {!r}'.format(p.value))


yacc.yacc()
