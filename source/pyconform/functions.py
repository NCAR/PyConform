"""
Functions for FunctionEvaluator Actions

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from abc import ABCMeta, abstractmethod
from cf_units import Unit
from operator import pow, neg, add, sub, mul, truediv
from numpy import sqrt


class UnitsError(ValueError):
    pass

#===============================================================================
# List all available functions or operators
#===============================================================================
def available():
    return available_operators().union(available_functions())

#===============================================================================
# Find a function or operator based on key and number of arguments
#===============================================================================
def find(key, numargs=2):
    if (key, numargs) in available_operators():
        return find_operator(key, numargs)
    elif (key, numargs) in available_functions():
        return find_function(key, numargs)
    else:
        raise KeyError(('{0}-arg operator/function with key {1!r} not '
                        'found').format(numargs, key))

#===============================================================================
# FunctionalAbstract - base class for Function and Operator Classes
#===============================================================================
class FunctionAbstract(object):
    __metaclass__ = ABCMeta
    
    key = 'function'
    numargs = 2
    function = lambda x, y: 1
    
    @abstractmethod
    def units(self, *arg_units):
        uret = arg_units[0] if isinstance(arg_units[0], Unit) else Unit(1)
        uarg = (None,) * len(self.numargs)
        return uret, uarg
    
################################################################################
##### OPERATORS ################################################################
################################################################################

#===============================================================================
# Get a list of the available functions by function key and number of arguments
#===============================================================================
def available_operators():
    return set(__OPERATORS__.keys())

#===============================================================================
# Get the function associated with the given key-symbol
#===============================================================================
def find_operator(key, numargs=2):
    if (key, numargs) not in __OPERATORS__:
        raise KeyError(('{0}-arg operator with key {1!r} not '
                        'found').format(numargs, key))
    return __OPERATORS__[(key, numargs)]

#===============================================================================
# Operator - From which all 'X op Y'-pattern operators derive
#===============================================================================
class Operator(FunctionAbstract):
    key = '?'
    numargs = 2
    function = lambda x, y: 1

#===============================================================================
# NegationOperator
#===============================================================================
class NegationOperator(Operator):
    key = '-'
    numargs = 1
    function = neg

    @staticmethod
    def units(arg_unit):
        uret = arg_unit if isinstance(arg_unit, Unit) else Unit(1)
        return uret, (None,)

#===============================================================================
# AdditionOperator
#===============================================================================
class AdditionOperator(Operator):
    key = '+'
    numargs = 2
    function = add

    @staticmethod
    def units(*arg_units):
        u = tuple(a if isinstance(a, Unit) else Unit(1) for a in arg_units)
        if u[0] == u[1]:
            return u[0], (None, None)
        elif u[1].is_convertible(u[0]):
            return u[0], (None, u[0])
        else:
            raise UnitsError(('Data with units {0[0]!s} and {0[1]!s} cannot be '
                              'added or subtracted').format(u))

#===============================================================================
# SubtractionOperator
#===============================================================================
class SubtractionOperator(Operator):
    key = '-'
    numargs = 2
    function = sub

    @staticmethod
    def units(*arg_units):
        return AdditionOperator.units(*arg_units)

#===============================================================================
# PowerOperator
#===============================================================================
class PowerOperator(Operator):
    key = '^'
    numargs = 2
    function = pow

    @staticmethod
    def units(*arg_units):
        u = tuple(a if isinstance(a, Unit) else Unit(1) for a in arg_units)
        if not u[1].is_dimensionless():
            raise UnitsError('Exponent in power function must be dimensionless')
        try:
            uret = pow(*u)
        except:
            raise UnitsError(('Cannot exponentiate units to power '
                              '{0}').format(arg_units[1]))
        return uret, (None, None)

#===============================================================================
# MultiplicationOperator
#===============================================================================
class MultiplicationOperator(Operator):
    key = '*'
    numargs = 2
    function = mul

    @staticmethod
    def units(*arg_units):
        u = tuple(a if isinstance(a, Unit) else Unit(1) for a in arg_units)
        try:
            uret = mul(*u)
        except:
            raise UnitsError(('Cannot multiply or divide units {0[0]} and '
                              '{0[1]}').format(u))
        return uret, (None, None)

#===============================================================================
# DivisionOperator
#===============================================================================
class DivisionOperator(Operator):
    key = '-'
    numargs = 2
    function = sub

    @staticmethod
    def units(*arg_units):
        u = tuple(a if isinstance(a, Unit) else Unit(1) for a in arg_units)
        try:
            uret = truediv(*u)
        except:
            raise UnitsError(('Cannot multiply or divide units {0[0]} and '
                              '{0[1]}').format(u))
        return uret, (None, None)

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
# Recursively return all subclasses of a given class
#===============================================================================
def _all_subclasses_(cls):
    return cls.__subclasses__() + [c for s in cls.__subclasses__()
                                   for c in _all_subclasses_(s)]

#===============================================================================
# Check that all functions patterns are unique - Needed for User-Defined Funcs
#===============================================================================
def check_functions():
    func_dict = {}
    func_map = [((c.key, c.numargs), c)
                for c in _all_subclasses_(Function)]
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
    return set((c.key, c.numargs)
               for c in _all_subclasses_(Function))

#===============================================================================
# Get the function associated with the given key-symbol
#===============================================================================
def find_function(key, numargs=2):
    func_map = dict(((c.key, c.numargs), c)
                    for c in _all_subclasses_(Function))
    if (key, numargs) not in func_map:
        raise KeyError(('{0}-arg function with key {1!r} not '
                        'found').format(numargs, key))
    return func_map[(key, numargs)]

#===============================================================================
# Function - From which all 'func(...)'-pattern functions derive
#===============================================================================
class Function(FunctionAbstract):
    key = 'f'
    numargs = 1
    function = lambda x: x

#===============================================================================
# SquareRoot
#===============================================================================
class SquareRootFunction(Function):
    key = 'sqrt'
    numargs = 1
    function = sqrt

    @staticmethod
    def units(arg_unit):
        u = arg_unit if isinstance(arg_unit, Unit) else Unit(1)
        try:
            uret = u.root(2)
        except:
            raise UnitsError(('Cannot take square-root of units {0}').format(u))
        return uret, (None,)

#===============================================================================
# ConvertFunction
#===============================================================================
class ConvertFunction(Function):
    key = 'convert'
    numargs = 3
    function = lambda data, uFrom, uTo: uFrom.convert(data, uTo)

    @staticmethod
    def units(*arg_units):
        u = [a if isinstance(a, Unit) else Unit(1) for a in arg_units]
        if u[0] != u[1]:
            raise UnitsError(('Input units {0[0]} different from expected '
                              'units {0[1]}').format(u))
        if not u[1].is_convertible(u[2]):
            raise UnitsError(('Ill-formed convert function.  Cannot convert '
                              'units {0[1]} to {0[2]}').format(u))
        uret = u[2]
        return uret, (None, None, None)
