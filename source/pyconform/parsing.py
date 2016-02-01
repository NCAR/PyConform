"""
Variable Definition Parsing Utility

This module contains the DefinitionParser class that is used to parse the
variable definitions, check that they are valid, and provide the necessary
data needed to generate the operation graphs.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from dataset import InputDataset, OutputDataset
from pyparsing import nums, alphas, alphanums, operatorPrecedence, oneOf
from pyparsing import Word, Literal, Optional, Combine, opAssoc
from collections import OrderedDict

import operator


#===============================================================================
# DefitionParser
#===============================================================================
class DefitionParser(object):
    """
    Variable Definition Parser
    """
    
    def __init__(self, inputds, outputds, definitions):
        """
        Initializer
        
        Parameters:
            inputds (InputDataset): InputDataset instance
            outputds (OutputDataset): OutputDataset instance
            definitions (dict): Dictionary of InputDataser to OutputDataset
                variable definitions
        """
        if not isinstance(inputds, InputDataset):
            err_msg = 'Input dataset must be of InputDataset type'
            raise TypeError(err_msg)
        if not isinstance(outputds, OutputDataset):
            err_msg = 'Output dataset must be of OutputDataset type'
            raise TypeError(err_msg)
        if not isinstance(definitions, dict):
            err_msg = 'Definitions must be contained in a dictionary'
            raise TypeError(err_msg)
    
        self._ids = inputds
        self._ods = outputds
        
        # Generate the map of definitions (as operation tuples)
        self._defmap = self._parse_definitions_(definitions)

        # Check that the variable names in the optuples are valid        
        self._check_variable_names_(self._defmap)
        
        # Determine the dimension map
        self._dimmap = self._compute_dimension_map_(self._defmap)
        
    def _parse_definitions_(self, definitions):
        """
        Parse the definitions dictionary
        
        Parameters:
            definitions (dict): Dictionary of InputDataset to OutputDataset
                variable definition strings
        """

        # Integer operands
        integers = Word(nums)
        integers.setParseAction(lambda s,l,t: int(t[0]))
        
        # Floating-point operands
        floats = Combine(Word(nums) + '.' + Optional(Word(nums)))
        floats.setParseAction(lambda s,l,t: float(t[0]))

        # String variable name operands    
        varname = Word(alphas + "_", alphanums + "_" )
        
        # Define the basic operand
        operand = floats | integers | varname
    
        # Define how to parse exponent operator and arguments
        expop = Literal('^')
        def exp_func(tokens):
            base, _, exp = tokens[0]
            return operator.pow, base, exp
    
        # Define how to parse +/- sign operators and arguments
        signops = oneOf('+ -')
        def sign_func(tokens):
            sgn, val = tokens[0]
            if sgn == '+':
                return val
            else:
                return operator.neg, val
    
        # Define how to parse multiplication/division operators and arguments
        multops = oneOf('* /')
        def mult_func(tokens):
            left, op, right = tokens[0]
            if op == '*':
                return operator.mul, left, right
            else:
                return operator.div, left, right
    
        # Define how to parse addition/subtraction operators and arguments
        plusops = oneOf('+ -')
        def plus_func(tokens):
            left, op, right = tokens[0]
            if op == '+':
                return operator.add, left, right
            else:
                return operator.sub, left, right
    
        # Define the expression parser using operator precedence
        expr = operatorPrecedence(operand,
                                  [(expop, 2, opAssoc.RIGHT, exp_func),
                                   (signops, 1, opAssoc.RIGHT, sign_func),
                                   (multops, 2, opAssoc.RIGHT, mult_func),
                                   (plusops, 2, opAssoc.RIGHT, plus_func)])

        defmap = OrderedDict()
        for ovar, defstr in definitions.iteritems():
            optuple = expr.parseString(defstr)[0]
            if not isinstance(optuple, tuple):
                optuple = (optuple,)
            defmap[ovar] = optuple

        return defmap
    
    @staticmethod
    def _optuple_to_str_(optuple):
        """
        Convert an operation tuple into a string
        
        Parameters:
            optuple (tuple): An operation tuple
        """
        strval = ''
        if len(optuple) > 0:
            if callable(optuple[0]):
                strval += optuple[0].__name__ + '('
                strval += DefitionParser._optuple_to_str_(optuple[1:])
                strval += ')'
            else:
                for arg in optuple:
                    if isinstance(arg, tuple):
                        strval += DefitionParser._optuple_to_str_(arg)
                    else:
                        strval += str(arg)
                        if arg != optuple[-1]:
                            strval += ','
        return strval

    def _check_variable_names_(self, defmap):
        """
        Check that output variables names are completely defined
        
        Checks that all input variable names referenced exist
        
        Parameters:
            defmap (dict): A dictionary of output variable names mapped to
                parsed definitions (nested tuples)
        """
        err_str = 'Variable {!r} not found in {!r} dataset'
        
        def check_deftuple_names(deftuple):
            if isinstance(deftuple, tuple):
                for arg in deftuple:
                    if isinstance(arg, (str, unicode)):
                        if arg not in self._ids.variables:
                            err_msg = err_str.format(arg, self._ids.name)
                            raise ValueError(err_msg)
                    elif isinstance(arg, tuple):
                        check_deftuple_names(arg)

        required_ovars = set(self._ods.variables.keys())
        for ovar, deftuple in defmap.iteritems():
            if ovar not in required_ovars:
                err_msg = err_str.format(ovar, self._ods.name)
                raise ValueError(err_msg)
            required_ovars.remove(ovar)
            check_deftuple_names(deftuple)
            
        if len(required_ovars) > 0:
            err_msg = ('Some variables in {!r} dataset not defined:{}'
                       '{}').format(self._ods.name, linesep, required_ovars)
            raise RuntimeError(err_msg)

    def _compute_dimension_map_(self, defmap):
        """
        Compute the mapping from input dataset dimensions to output dimensions
        
        Parameters:
            defmap (dict): A dictionary of output variable names mapped to
                parsed definitions (nested tuples)
        """
        
        def get_dimensions(deftuple):
            argdims = {}
            for arg in deftuple:
                if isinstance(arg, (str, unicode)):
                    key = arg
                    dims = tuple(self._ids.variables[arg].dimensions.keys())
                    argdims[key] = dims
                elif isinstance(arg, tuple):
                    key = DefitionParser._optuple_to_str_(arg)
                    dims = get_dimensions(arg)
                    argdims[key] = dims
            return argdims
        
        def reduce_dimensions(argdims):
            if isinstance(argdims, dict):
                if len(argdims) > 0:
                    key0, val0 = argdims.popitem()
                    dims0 = reduce_dimensions(val0)
                    for key, val in argdims.iteritems():
                        dims = reduce_dimensions(val)
                        if dims0 != dims:
                            err_msg = ('Argument {!r} has dimensions {!r} '
                                       'but argument {!r} has dimensions '
                                       '{!r}').format(key0, dims0, key, dims)
                            raise ValueError(err_msg)
                    return dims0
                else:
                    return tuple()
            else:
                return tuple(argdims)
                    
        dimmap = {}
        for ovar, deftuple in defmap.iteritems():
            odims = tuple(self._ods.variables[ovar].dimensions.keys())
            idims = reduce_dimensions(get_dimensions(deftuple))
            if len(odims) != len(idims):
                defstr = DefitionParser._optuple_to_str_(deftuple)
                err_msg = ('Output variable {!r} has {} dimensions while its '
                           'definition {!r} has {} '
                           'dimensions').format(ovar, len(odims), defstr, 
                                                len(idims))
                raise ValueError(err_msg)
            for odim, idim in zip(odims, idims):
                if odim not in dimmap:
                    dimmap[odim] = str(idim)
                elif idim != dimmap[odim]:
                    err_msg = ('Output dimension {!r} in output variable {!r} '
                               'appears to map to both {!r} and {!r} input '
                               'dimensions').format(odim, ovar, idim, 
                                                    dimmap[odim])
                    raise ValueError(err_msg)

        return dimmap
