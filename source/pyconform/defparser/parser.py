"""
Lex/Yacc-based Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from ply import yacc
from tokenizer import Tokenizer
from collections import namedtuple

OpType = namedtuple('OpType', ['name', 'arguments'])
VarType = namedtuple('VarType', ['name', 'indices'])
FuncType = namedtuple('FuncType', ['name', 'arguments', 'keywords'])


class Parser(Tokenizer):
    """
    Yacc-based Definition Parser
    """

    def __init__(self, **kwds):
        super(Parser, self).__init__(**kwds)
        yacc.yacc(module=self, debug=self.debug)

    precedence = (('left', 'EQ'),
                  ('left', '<', '>', 'LEQ', 'GEQ'),
                  ('left', '+', '-'),
                  ('left', '*', '/'),
                  ('right', 'NEG', 'POS'),
                  ('left', 'POW'))

    def p_array_like(self, p):
        """
        array_like : FLOAT
        array_like : INT
        array_like : variable
        array_like : function
        """
        p[0] = p[1]

    def p_array_like_group(self, p):
        """
        array_like : '(' array_like ')'
        """
        p[0] = p[2]

    def p_function_with_arguments_and_keywords(self, p):
        """
        function : NAME '(' argument_list ',' keyword_dict ')'
        """
        p[0] = FuncType(p[1], p[3], p[5])

    def p_function_with_arguments_only(self, p):
        """
        function : NAME '(' argument_list ')'
        """
        p[0] = FuncType(p[1], p[3], {})

    def p_function_with_keywords_only(self, p):
        """
        function : NAME '(' keyword_dict ')'
        """
        p[0] = FuncType(p[1], [], p[3])

    def p_argument_list_append(self, p):
        """
        argument_list : argument_list ',' argument
        """
        p[0] = p[1] + [p[3]]

    def p_single_item_argument_list(self, p):
        """
        argument_list : argument
        argument_list : 
        """
        p[0] = [p[1]] if len(p) > 1 else []

    def p_argument(self, p):
        """
        argument : array_like
        argument : STRING
        """
        p[0] = p[1]

    def p_keyword_dict_setitem(self, p):
        """
        keyword_dict : keyword_dict ',' NAME '=' argument
        """
        p[1][p[3]] = p[5]
        p[0] = p[1]

    def p_single_item_keyword_dict(self, p):
        """
        keyword_dict : NAME '=' argument
        """
        p[0] = {p[1]: p[3]}

    def p_variable(self, p):
        """
        variable : NAME '[' index_list ']'
        variable : NAME
        """
        indices = p[3] if len(p) > 3 else []
        p[0] = VarType(p[1], indices)

    def p_index_list_append(self, p):
        """
        index_list : index_list ',' index
        """
        p[0] = p[1] + [p[3]]

    def p_single_item_index_list(self, p):
        """
        index_list : index
        """
        p[0] = [p[1]]

    def p_index(self, p):
        """
        index : slice
        index : INT
        """
        p[0] = p[1]

    def p_slice(self, p):
        """
        slice : slice_argument ':' slice_argument ':' slice_argument
        slice : slice_argument ':' slice_argument
        """
        p[0] = slice(*p[1::2])

    def p_slice_argument(self, p):
        """
        slice_argument : INT
        slice_argument : 
        """
        p[0] = p[1] if len(p) > 1 else None

    def p_expression_unary(self, p):
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

    def p_expression_binary(self, p):
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

    def p_error(self, p):
        raise TypeError('Parsing error at {!r}'.format(p.value))

    def parse_definition(self, defstr):
        """
        Parse a string definiton

        Parameters:
            defstr (str): The string definition to parse
        """
        return yacc.parse(defstr)  # @UndefinedVariable
