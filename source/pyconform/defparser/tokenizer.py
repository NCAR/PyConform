"""
Lex-based Tokenizer

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from ply import lex


class Tokenizer(object):
    """
    Lex-based Tokenizer
    """

    def __init__(self, **kwds):
        self.debug = kwds.get('debug', 0)
        lex.lex(module=self, debug=self.debug)

    tokens = ('FLOAT', 'INT', 'STRING', 'NAME', 'POW', 'EQ', 'LEQ', 'GEQ')
    literals = ('*', '/', '+', '-', '<', '>',
                '=', ',', ':', '(', ')', '[', ']')

    t_ignore = ' \t'

    t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_POW = r'\*\*'
    t_LEQ = r'<='
    t_GEQ = r'>='
    t_EQ = r'=='

    def t_FLOAT(self, t):
        r'[-+]?(([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([eE][+-]?[0-9]+)?|[0-9]+[eE][+-]?[0-9]+)'
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r'[-+]?[0-9]+'
        t.value = int(t.value)
        return t

    def t_STRING(self, t):
        r'(\"([^\\\"]|\\.)*\"|\'([^\\\']|\\.)*\')'
        t.value = t.value[1:-1]
        return t

    def t_error(self, t):
        raise TypeError('Failed to tokenize string: {!r}'.format(t.value))

    def tokenize(self, s):
        """
        Tokenize a given string

        Parameters:
            s (str): The string to tokenize
        """
        lex.input(s)  # @UndefinedVariable
        return iter(lex.token, None).next()  # @UndefinedVariable
