"""
PLY - Lex Tokenizer

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from ply import lex

tokens = ('INT', 'FLOAT', 'NAME', 'LBRACKET', 'RBRACKET', 'LPAREN', 'RPAREN',
          'MINUS', 'PLUS', 'COLON', 'COMMA', 'EQUALS', 'STRING')

t_ignore = r' \t'

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_MINUS = r'\-'
t_PLUS = r'\+'
t_COLON = r'\:'
t_COMMA = r'\,'
t_EQUALS = r'='


def t_FLOAT(t):
    r'[-+]?(([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([eE][+-]?[0-9]+)?|[0-9]+[eE][+-]?[0-9]+)'
    t.value = float(t.value)
    return t


def t_INT(t):
    r'[-+]?[0-9]+'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'(\"([^\\\"]|\\.)*\"|\'([^\\\']|\\.)*\')'
    t.value = t.value[1:-1]
    return t


def t_error(t):
    raise TypeError('Unexpected string: {!r}'.format(t.value))


lex.lex()
