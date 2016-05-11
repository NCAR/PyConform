"""
Functions for FunctionEvaluator Actions

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from abc import ABCMeta, abstractproperty
from operator import pow, neg, add, sub, mul, truediv
from numpy import sqrt


#===============================================================================
# Recursively return all subclasses of a given class
#===============================================================================
def _all_subclasses_(cls):
    return cls.__subclasses__() + [c for s in cls.__subclasses__()
                                   for c in _all_subclasses_(s)]

################################################################################
##### OPERATORS ################################################################
################################################################################

#===============================================================================
# Get a list of the available functions by function key and number of arguments
#===============================================================================
def available_operators():
    return __OPERATORS__.items()

#===============================================================================
# Get the function associated with the given key-symbol
#===============================================================================
def get_operator(symbol, numargs=2):
    if (symbol, numargs) not in __OPERATORS__:
        raise KeyError(('{0}-arg operator with symbol {1!r} not '
                        'found').format(numargs, symbol))
    return __OPERATORS__[(symbol, numargs)]

#===============================================================================
# OperatorAbstract - From which all 'X op Y'-pattern operators derive
#===============================================================================
class OperatorAbstract(object):
    __metaclass__ = ABCMeta
    @abstractproperty
    def symbol(self):
        return 'function'
    @abstractproperty
    def function(self):
        return lambda x, y: 1
    @property
    def numargs(self):
        return 2

#===============================================================================
# NegationOperator
#===============================================================================
class NegationOperator(OperatorAbstract):
    @property
    def symbol(self):
        return '-'
    @property
    def function(self):
        return neg
    @property
    def numargs(self):
        return 1

#===============================================================================
# AdditionOperator
#===============================================================================
class AdditionOperator(OperatorAbstract):
    @property
    def symbol(self):
        return '+'
    @property
    def function(self):
        return add

#===============================================================================
# SubtractionOperator
#===============================================================================
class SubtractionOperator(OperatorAbstract):
    @property
    def symbol(self):
        return '-'
    @property
    def function(self):
        return sub

#===============================================================================
# PowerOperator
#===============================================================================
class PowerOperator(OperatorAbstract):
    @property
    def symbol(self):
        return '^'
    @property
    def function(self):
        return pow

#===============================================================================
# MultiplicationOperator
#===============================================================================
class MultiplicationOperator(OperatorAbstract):
    @property
    def symbol(self):
        return '*'
    @property
    def function(self):
        return mul

#===============================================================================
# DivisionOperator
#===============================================================================
class DivisionOperator(OperatorAbstract):
    @property
    def symbol(self):
        return '/'
    @property
    def function(self):
        return truediv

#===============================================================================
# Operator map - Fixed to prevent user-redefinition!
#===============================================================================

__OPERATORS__ = {('-', 1): NegationOperator,
                 ('^', 2): PowerOperator,
                 ('+', 2): AdditionOperator,
                 ('-', 2): SubtractionOperator,
                 ('*', 2): MultiplicationOperator,
                 ('/', 2): DivisionOperator}

################################################################################
##### FUNCTIONS ################################################################
################################################################################

#===============================================================================
# Check that all functions patterns are unique - Needed for User-Defined Funcs
#===============================================================================
def check_functions():
    func_dict = {}
    func_map = [((c().name, c().numargs), c.__name__)
                for c in _all_subclasses_(FunctionAbstract)]
    non_unique_patterns = []
    for func_pattern, class_name in func_map:
        if func_pattern in func_dict:
            func_dict[func_pattern].append(class_name)
            non_unique_patterns.append(func_pattern)
        else:
            func_dict[func_pattern] = [class_name]
    if len(non_unique_patterns) > 0:
        err_msg = ['Some function patterns are multiply defined:']
        for func_pattern in non_unique_patterns:
            func_descr = '{0[1]}-arg {0[0]!r}'.format(func_pattern)
            class_names = ', '.join(func_dict[func_pattern])
            err_msg += ['   {0} maps to {1}'.format(func_descr, class_names)]
        raise RuntimeError(linesep.join(err_msg))

#===============================================================================
# Get a list of the available functions by function key and number of arguments
#===============================================================================
def available_functions():
    return [(c().name, c().numargs)
            for c in _all_subclasses_(FunctionAbstract)]

#===============================================================================
# Get the function associated with the given key-symbol
#===============================================================================
def get_function(name, numargs=2):
    func_map = dict(((c().name, c().numargs), c().function)
                    for c in _all_subclasses_(FunctionAbstract))
    if (name, numargs) not in func_map:
        raise KeyError(('{0}-arg function with name {1!r} not '
                        'found').format(numargs, name))
    return func_map[(name, numargs)]

#===============================================================================
# FunctionAbstract - From which all 'func(...)'-pattern functions derive
#===============================================================================
class FunctionAbstract(object):
    __metaclass__ = ABCMeta
    @abstractproperty
    def name(self):
        return 'function'
    @abstractproperty
    def function(self):
        return lambda: 1
    @property
    def numargs(self):
        return 1

#===============================================================================
# SquareRoot
#===============================================================================
class SquareRootFunction(FunctionAbstract):
    @property
    def name(self):
        return 'sqrt'
    @property
    def function(self):
        return sqrt
