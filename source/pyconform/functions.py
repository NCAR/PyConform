"""
Functions for FunctionEvaluator Actions

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from abc import ABCMeta, abstractmethod
from pyconform.dataflows import DataArray
from cf_units import Unit
from numpy import sqrt, transpose


#===================================================================================================
# UnitsError
#===================================================================================================
class UnitsError(ValueError):
    """Exception for when DataArray Units are invalid"""
    def __init__(self, name, iarg, units):
        message = 'In {}, argument {} requires conversion to {!s}'.format(name, iarg, units)
        super(UnitsError, self).__init__(message)
        self.name = name
        self.iarg = iarg
        self.units = units


#===================================================================================================
# DimensionsError
#===================================================================================================
class DimensionsError(ValueError):
    """Exception for when DataArray Dimensions are invalid"""
    def __init__(self, name, iarg, dims):
        message = 'In {}, argument {} requires dimensions {!s}'.format(name, iarg, dims)
        super(DimensionsError, self).__init__(message)
        self.name = name
        self.iarg = iarg
        self.dimensions = dims

#===================================================================================================
# List all available functions or operators
#===================================================================================================
def available():
    return available_operators().union(available_functions())


#===================================================================================================
# Find a function or operator based on key and number of arguments
#===================================================================================================
def find(key, numargs=2):
    if (key, numargs) in available_operators():
        return find_operator(key, numargs)
    elif (key, numargs) in available_functions():
        return find_function(key, numargs)
    else:
        raise KeyError(('{0}-arg operator/function with key {1!r} not '
                        'found').format(numargs, key))


#===================================================================================================
# FunctionBase - base class for Function and Operator Classes
#===================================================================================================
class FunctionBase(object):
    __metaclass__ = ABCMeta
    key = 'function'
    numargs = 2

    def get_units(self, *args):
        return tuple(arg.cfunits if isinstance(arg, DataArray) else Unit(1) for arg in args)

    def get_dimensions(self, *args):
        return tuple(arg.dimensions if isinstance(arg, DataArray) else () for arg in args)

    @abstractmethod
    def __call__(self, *args):
        return 1


####################################################################################################
##### OPERATORS ####################################################################################
####################################################################################################

#===================================================================================================
# Get a list of the available functions by function key and number of arguments
#===================================================================================================
def available_operators():
    return set(__OPERATORS__.keys())


#===================================================================================================
# Get the function associated with the given key-symbol
#===================================================================================================
def find_operator(key, numargs=2):
    if (key, numargs) not in __OPERATORS__:
        raise KeyError(('{0}-arg operator with key {1!r} not '
                        'found').format(numargs, key))
    return __OPERATORS__[(key, numargs)]


#===================================================================================================
# Operator - From which all 'X op Y'-pattern operators derive
#===================================================================================================
class Operator(FunctionBase):
    key = '?'
    numargs = 2


#===================================================================================================
# NegationOperator
#===================================================================================================
class NegationOperator(Operator):
    key = '-'
    numargs = 1

    def __call__(self, arg):
        return -arg


#===================================================================================================
# AdditionOperator
#===================================================================================================
class AdditionOperator(Operator):
    key = '+'
    numargs = 2

    def __call__(self, left, right):
        lunits, runits = self.get_units(left, right)
        if lunits != runits:
            raise UnitsError(self.__class__.__name__, 1, lunits)

        ldims, rdims = self.get_dimensions(left, right)
        if ldims != rdims:
            raise DimensionsError(self.__class__.__name__, 1, ldims)

        return left + right

#===================================================================================================
# SubtractionOperator
#===================================================================================================
class SubtractionOperator(Operator):
    key = '-'
    numargs = 2

    def __call__(self, left, right):
        lunits, runits = self.get_units(left, right)
        if lunits != runits:
            raise UnitsError(self.__class__.__name__, 1, lunits)

        ldims, rdims = self.get_dimensions(left, right)
        if ldims != rdims:
            raise DimensionsError(self.__class__.__name__, 1, ldims)

        return left - right

#===================================================================================================
# PowerOperator
#===================================================================================================
class PowerOperator(Operator):
    key = '^'
    numargs = 2

    def __call__(self, left, right):
        lunits, runits = self.get_units(left, right)
        ldims, rdims = self.get_dimensions(left, right)

        if runits != Unit(1):
            raise UnitsError(self.__class__.__name__, 1, Unit(1))
        if rdims != ():
            raise DimensionsError(self.__class__.__name__, 1, ())

        try:
            punits = lunits ** right
        except:
            raise ValueError('Cannot exponentiate units ({!r} ** {})'.format(lunits, right))

        return DataArray(left ** right, cfunits=punits, dimensions=ldims)


#===================================================================================================
# MultiplicationOperator
#===================================================================================================
class MultiplicationOperator(Operator):
    key = '*'
    numargs = 2

    def __call__(self, left, right):
        lunits, runits = self.get_units(left, right)
        ldims, rdims = self.get_dimensions(left, right)

        try:
            munits = lunits * runits
        except:
            raise ValueError('Cannot multiply units ({!r} * {!r})'.format(lunits, runits))

        if ldims == ():
            mdims = rdims
        elif ldims == rdims or rdims == ():
            mdims = ldims
        else:
            raise ValueError(('Cannot multiply mismatched dimensions '
                              '({!r} * {!r})').format(ldims, rdims))

        return DataArray(left * right, cfunits=munits, dimensions=mdims)


#===================================================================================================
# DivisionOperator
#===================================================================================================
class DivisionOperator(Operator):
    key = '-'
    numargs = 2

    def __call__(self, left, right):
        lunits, runits = self.get_units(left, right)
        ldims, rdims = self.get_dimensions(left, right)

        try:
            munits = lunits / runits
        except:
            raise ValueError('Cannot divide units ({!r} * {!r})'.format(lunits, runits))

        if ldims == ():
            mdims = rdims
        elif ldims == rdims or rdims == ():
            mdims = ldims
        else:
            raise ValueError(('Cannot divide mismatched dimensions '
                              '({!r} * {!r})').format(ldims, rdims))

        return DataArray(left / right, cfunits=munits, dimensions=mdims)


#===================================================================================================
# Operator map - Fixed to prevent user-redefinition!
#===================================================================================================

__OPERATORS__ = {('-', 1): NegationOperator(),
                 ('^', 2): PowerOperator(),
                 ('+', 2): AdditionOperator(),
                 ('-', 2): SubtractionOperator(),
                 ('*', 2): MultiplicationOperator(),
                 ('/', 2): DivisionOperator()}

####################################################################################################
##### FUNCTIONS ####################################################################################
####################################################################################################

#===================================================================================================
# Recursively return all subclasses of a given class
#===================================================================================================
def _all_subclasses_(cls):
    return cls.__subclasses__() + [c for s in cls.__subclasses__()
                                   for c in _all_subclasses_(s)]

#===================================================================================================
# Check that all functions patterns are unique - Needed for User-Defined Funcs
#===================================================================================================
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

#===================================================================================================
# Get a list of the available functions by function key and number of arguments
#===================================================================================================
def available_functions():
    return set((c.key, c.numargs)
               for c in _all_subclasses_(Function))

#===================================================================================================
# Get the function associated with the given key-symbol
#===================================================================================================
def find_function(key, numargs=2):
    func_map = dict(((c.key, c.numargs), c())
                    for c in _all_subclasses_(Function))
    if (key, numargs) not in func_map:
        raise KeyError(('{0}-arg function with key {1!r} not '
                        'found').format(numargs, key))
    return func_map[(key, numargs)]

#===================================================================================================
# Function - From which all 'func(...)'-pattern functions derive
#===================================================================================================
class Function(FunctionBase):
    key = 'function'
    numargs = 1

#===================================================================================================
# SquareRoot
#===================================================================================================
class SquareRootFunction(Function):
    key = 'sqrt'
    numargs = 1

    def __call__(self, data):
        dunits = self.get_units(data)
        ddims = self.get_dimensions(data)

        try:
            sunits = dunits.root(2)
        except:
            raise ValueError('Cannot take square-root of units ({!r})'.format(dunits))

        return DataArray(sqrt(data), cfunits=sunits, dimensions=ddims)

#===================================================================================================
# ConvertFunction
#===================================================================================================
class ConvertFunction(Function):
    key = 'C'
    numargs = 2

    def __call__(self, data, to_units):
        units1 = self.get_units(data)
        units2 = Unit(to_units)

        if not units1.is_convertible(units2):
            raise ValueError('Cannot convert units ({!r} --> {!r})'.format(units1, units2))

        return DataArray(units1.convert(data, units2, inplace=True),
                         cfunits=units2, dimensions=self.get_dimensions(data))

#===================================================================================================
# TransposeFunction
#===================================================================================================
class TransposeFunction(Function):
    key = 'T'
    numargs = 2

    def __call__(self, data, new_dims):
        dunits = self.get_units(data)

        old_dims = self.get_dimensions(data)
        if set(old_dims) != set(new_dims):
            raise ValueError(('Cannot transpose dimensions '
                              '({!r} --> {!r})').format(old_dims, new_dims))

        order = tuple(old_dims.index(d) for d in new_dims)

        return DataArray(transpose(data, order), cfunits=dunits, dimensions=new_dims)
