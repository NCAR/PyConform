"""
Operation Graph Parsing - Output Variable Definitions

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyparsing import nums, alphas, alphanums, operatorPrecedence, oneOf
from pyparsing import Word, Literal, Optional, Combine, opAssoc


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
        # Integer operands
        integers = Word(nums)
        integers.setParseAction(self._int_operand_parser_)
        
        # Floating-point operands
        floats = Combine(Word(nums) + '.' + Optional(Word(nums)))
        floats.setParseAction(self._float_operand_parser_)

        # String variable name operands    
        varname = Word(alphas + "_", alphanums + "_" )
        varname.setParseAction(self._variable_operand_parser_)
        
        # Define the basic operand
        operand = floats | integers | varname
    
        # Define each operator symbol and how it is parsed
        pow_op = (Literal('^'), 2, opAssoc.RIGHT, self._pow_operator_parser_)
        sgn_op = (oneOf('+ -'), 1, opAssoc.RIGHT, self._sgn_operator_parser_)
        mul_op = (oneOf('* /'), 2, opAssoc.RIGHT, self._mul_operator_parser_)
        add_op = (oneOf('+ -'), 2, opAssoc.RIGHT, self._add_operator_parser_)
        
        # Define the operator precedence list/order
        op_order = [pow_op, sgn_op, mul_op, add_op]
    
        # Define the expression parser using operator precedence
        self._parser = operatorPrecedence(operand, op_order)
                