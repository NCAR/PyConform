"""
Parse Actions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import namedtuple

VariableType = namedtuple('variable', ['name', 'indices'])
VariableType.__new__.__defaults__ = (None, None)

FunctionType = namedtuple('function', ['name', 'arguments', 'keywords'])
FunctionType.__new__.__defaults__ = (None, tuple(), {})


def integer_action(tokens):
    return int(tokens[0])


def float_action(tokens):
    return float(tokens[0])


def variable_action(tokens):
    token = tokens[0]
    name = token[0]
    indices = None if len(token) == 1 else token[1]
    return VariableType(name, indices)


def list_action(tokens):
    return tokens.asList()
