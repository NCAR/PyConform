"""
Parse Actions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import namedtuple, OrderedDict

VariableType = namedtuple('VariableType', ['name', 'indices'])
KeywordType = namedtuple('KeywordType', ['key', 'value'])
FunctionType = namedtuple('FunctionType', ['name', 'arguments', 'keywords'])
UnaryOpType = namedtuple('UnaryOpType', ['operator', 'operand'])
BinaryOpType = namedtuple('BinaryOpType', ['operator', 'left', 'right'])


def integer_action(tokens):
    return int(tokens[0])


def float_action(tokens):
    return float(tokens[0])


def list_action(tokens):
    return tokens.asList()


def variable_action(tokens):
    token = tokens[0]
    name = token[0]
    indices = None if len(token) == 1 else token[1:]
    return VariableType(name, indices)


def keyword_action(tokens):
    token = tokens[0]
    return KeywordType(*token)


def function_action(tokens):
    token = tokens[0]
    name = token[0]
    arguments = []
    keywords = OrderedDict()
    for t in token[1:]:
        if isinstance(t, KeywordType):
            keywords[t.key] = t.value
        else:
            arguments.append(t)
    arguments = tuple(arguments)
    return FunctionType(name, arguments, keywords)


def unary_op_action(tokens):
    op, val = tokens[0]
    if op == '+':
        return val
    else:
        return UnaryOpType(operator=op, operand=val)


def binary_op_action(tokens):
    left, op, right = tokens[0]
    return BinaryOpType(operator=op, left=left, right=right)
