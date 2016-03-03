"""
Operation Graph Parsing - Output Variable Definitions

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import (nums, alphas, alphanums, operatorPrecedence, oneOf,
                       Word, CaselessLiteral, Literal, Optional, Combine,
                       delimitedList, Group, Suppress, Forward)
from pyparsing.opAssoc import RIGHT
from operator import neg, pow, add, sub, mul, truediv


#===============================================================================
# DefinitionParser
#===============================================================================
class DefinitionParser(object):
    """
    Class to parse string variable definitions and generate OperationGraphs
    """
    
    def __init__(self):
        """
        Initializer
        """
        # INTEGERS: Just any word consisting only of numbers
        int_id = Word(nums)
        int_id.setParseAction(lambda t: int(t[0]))
        
        # FLOATS: More complicated... can be decimal format or 
        #         exponential format or combination of either
        dec_flt = ( Combine( Word(nums) + '.' + Word(nums) ) |
                    Combine( Word(nums) + '.' ) |
                    Combine( '.' + Word(nums) ) )
        flt_exp = ( Combine( CaselessLiteral('e') +
                             Optional( oneOf('+ -') ) +
                             Word(nums) ) )
        float_id = ( Combine( Word(nums) + flt_exp ) |
                     Combine( dec_flt + Optional( flt_exp ) ) )
        float_id.setParseAction(lambda t: float(t[0]))
    
        # String names ...identifiers for function or variable names
        name_id = Word( alphas+"_", alphanums+"_" )
        
        # VARIABLE NAMES: Can be just string names or names with indices
        #                 (e.g., [1,2,-4], [1:5, 2:10, 0:100:2])
        idx_id = Combine( Optional('-') + Word(nums) )
        idx_id.setParseAction(lambda t: int(t[0]))
        variable = Group(name_id + Optional(Suppress('[') +
                                            delimitedList(idx_id) +
                                            Suppress(']')))
        def var_parser(t):
            var_args = t[0]
            return '=={}{}=='.format(var_args[0], var_args[1:])
        variable.setParseAction(var_parser)
    
        # FUNCTIONS: Function arguments can be empty or any combination of ints, floats, variables,
        #            and even other functions.  Hence, we need a Forward place-holder to start...
        expr = Forward()
        func_id = Group(name_id +
                        Suppress('(') +
                        delimitedList(expr) +
                        Suppress(')'))
        def func_parser(t):
            func_args = t[0]
            func_args[0] = '**{}**'.format(func_args[0])
            return tuple(func_args)
        func_id.setParseAction(func_parser)
    
        # Negation Operator
        def neg_parser(tokens):
            op, val = tokens[0]
            if op == '+':
                return val
            else:
                return neg, val
    
        # Binary Operators
        binary_ops = {'^': pow,
                      '*': mul,
                      '/': truediv,
                      '+': add,
                      '-': sub}
        def binary_parser(tokens):
            left, op, right = tokens[0]
            return binary_ops[op], left, right
    
        expr << operatorPrecedence(float_id | int_id | func_id | variable,
                                   [(Literal('^'), 2, RIGHT, binary_parser),
                                    (oneOf('+ -'), 1, RIGHT, neg_parser),
                                    (oneOf('* /'), 2, RIGHT, binary_parser),
                                    (oneOf('+ -'), 2, RIGHT, binary_parser)])
        
        self._parser = expr
                