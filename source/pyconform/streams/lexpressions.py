"""
Definiton Parser Expressions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import ply.lex as lex
import ply.yacc as yacc


tokens = ('INT', 'FLOAT', 'STRING', 'NAME',
          'LBRACKET', 'RBRACKET', 'COLON',
          'LPAREN', 'RPAREN')

t_ignore = ' \t\n'

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_COLON = r'\:'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_FLOAT(t):
    r'[-+]?(([0-9]*\.[0-9]+|[0-9]+\.[0-9]*)([eE][-+]?[0-9]+)?|[0-9]+([eE][-+]?[0-9]+))'
    t.value = float(t.value)
    return t


def t_INT(t):
    r'[-+]?[0-9]+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'\"(?:[^\"\\]|\\.)*\"|\'(?:[^\'\\]|\\.)*\''
    t.value = t.value[1:-1]
    return t


def t_error(t):
    raise TypeError('Failed to parse {!r}'.format(t.value))


lex.lex()


def lex_input(s):
    lex.input(s)  # @UndefinedVariable


def lex_next_token():
    return iter(lex.token, None).next()  # @UndefinedVariable


def p_float(p):
    """expression : FLOAT"""
    p[0] = p[1]


def p_int(p):
    """expression : INT"""
    p[0] = p[1]


yacc.yacc()


def yacc_parse(s):
    return yacc.parse(s)  # @UndefinedVariable
