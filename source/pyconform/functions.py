"""
Functions for FunctionEvaluator Actions

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from abc import ABCMeta, abstractmethod
from pyconform.physarray import PhysArray, UnitsError
from numpy import sqrt, mean
from cf_units import Unit


#===================================================================================================
# Find a function or operator based on key and number of arguments
#===================================================================================================
def find(key, numargs=None):
    try:
        fop = find_operator(key, numargs=numargs)
    except:
        pass
    else:
        return fop
    
    if numargs is not None:
        raise KeyError('No operator {!r} with {} arguments found'.format(key, numargs))

    try:
        fop = find_function(key)
    except:
        raise KeyError('No operator or function {!r} found'.format(key))
    else:
        return fop


#===================================================================================================
# FunctionBase - base class for Function and Operator Classes
#===================================================================================================
class FunctionBase(object):
    __metaclass__ = ABCMeta
    key = 'function'

    @abstractmethod
    def __call__(self, *args, **kwds):
        return 1


####################################################################################################
##### OPERATORS ####################################################################################
####################################################################################################


#===================================================================================================
# Get the function associated with the given key-symbol
#===================================================================================================
def find_operator(key, numargs=None):
    if key not in __OPERATORS__:
        raise KeyError('Operator {!r} not found'.format(key))
    ops = __OPERATORS__[key]
    if numargs is None:
        if len(ops) == 0:
            raise KeyError('Operator {!r} found but not defined'.format(key))
        elif len(ops) == 1:
            return ops.values()[0]
        else:
            raise KeyError(('Operator {!r} has multiple definitions, '
                            'number of arguments required').format(key))
    elif numargs not in ops:
        raise KeyError('Operator {!r} with {} arguments not found'.format(key, numargs))
    else:
        return ops[numargs]


#===================================================================================================
# operators
#===================================================================================================
def list_operators():
    return list(__OPERATORS__.keys())


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
        return left + right


#===================================================================================================
# SubtractionOperator
#===================================================================================================
class SubtractionOperator(Operator):
    key = '-'
    numargs = 2

    def __call__(self, left, right):
        return left - right


#===================================================================================================
# PowerOperator
#===================================================================================================
class PowerOperator(Operator):
    key = '**'
    numargs = 2

    def __call__(self, left, right):
        return left ** right


#===================================================================================================
# MultiplicationOperator
#===================================================================================================
class MultiplicationOperator(Operator):
    key = '*'
    numargs = 2

    def __call__(self, left, right):
        return left * right


#===================================================================================================
# DivisionOperator
#===================================================================================================
class DivisionOperator(Operator):
    key = '-'
    numargs = 2

    def __call__(self, left, right):
        return left / right


#===================================================================================================
# Operator map - Fixed to prevent user-redefinition!
#===================================================================================================

__OPERATORS__ = {'-': {1: NegationOperator(), 2: SubtractionOperator()},
                 '**': {2: PowerOperator()},
                 '+': {2: AdditionOperator()},
                 '*': {2: MultiplicationOperator()},
                 '/': {2: DivisionOperator()}}

####################################################################################################
##### FUNCTIONS ####################################################################################
####################################################################################################

#===================================================================================================
# Recursively return all subclasses of a given class
#===================================================================================================
def _all_subclasses_(cls):
    return cls.__subclasses__() + [c for s in cls.__subclasses__() for c in _all_subclasses_(s)]


#===================================================================================================
# Get the function associated with the given key-symbol
#===================================================================================================
def find_function(key):
    func = None
    for c in _all_subclasses_(Function):
        if c.key == key:
            if func is None:
                func = c
            else:
                raise RuntimeError('Function {!r} is multiply defined'.format(key))
    if func is None:
        raise KeyError('Function {!r} not found'.format(key))
    else:
        return func()
    

#===================================================================================================
# list_functions
#===================================================================================================
def list_functions():
    return [c.key for c in _all_subclasses_(Function)]


#===================================================================================================
# Function - From which all 'func(...)'-pattern functions derive
#===================================================================================================
class Function(FunctionBase):
    key = 'func'
    
    def __init__(self):
        self._sumlike_dimensions = set()
    
    @property
    def sumlike_dimensions(self):
        return self._sumlike_dimensions
    
    def add_sumlike_dimensions(self, *dims):
        self._sumlike_dimensions.update(set(dims))


#===================================================================================================
# SquareRoot
#===================================================================================================
class SquareRootFunction(Function):
    key = 'sqrt'

    def __call__(self, data):
        if isinstance(data, PhysArray):
            try:
                units = data.units.root(2)
            except:
                raise UnitsError('sqrt: Cannot take square-root of units {!r}'.format(data.units))
            return PhysArray(sqrt(data.data), units=units, name='sqrt({})'.format(data.name),
                             dimensions=data.dimensions, positive=data.positive)
        else:
            return sqrt(data)


#===================================================================================================
# MeanFunction
#===================================================================================================
class MeanFunction(Function):
    key = 'mean'
    
    def __call__(self, data, *dimensions):
        if not isinstance(data, PhysArray):
            raise TypeError('mean: Data must be a PhysArray')
        if not all(isinstance(d, basestring) for d in dimensions):
            raise TypeError('mean: Dimensions must be strings')
        indims = [d for d in dimensions if d in data.dimensions]
        self.add_sumlike_dimensions(*indims)
        axes = tuple(data.dimensions.index(d) for d in indims)
        new_dims = tuple(d for d in data.dimensions if d not in indims)
        dim_str = ','.join(str(d) for d in indims)
        return PhysArray(mean(data.data, axis=axes),
                         units=data.units, dimensions=new_dims, positive=data.positive,
                         name='mean({}, dims=[{}])'.format(data.name, dim_str))


#===================================================================================================
# PositiveUpFunction
#===================================================================================================
class PositiveUpFunction(Function):
    key = 'up'
    
    def __call__(self, data):
        return PhysArray(data).up()


#===================================================================================================
# PositiveDownFunction
#===================================================================================================
class PositiveDownFunction(Function):
    key = 'down'
    
    def __call__(self, data):
        return PhysArray(data).down()


#===================================================================================================
# ChangeUnitsFunction
#===================================================================================================
class ChangeUnitsFunction(Function):
    key = 'chunits'
    
    def __call__(self, data, units=1):
        uobj = units.units if isinstance(units, PhysArray) else Unit(units)
        unit_str = '{}{}'.format(uobj, '' if uobj.calendar is None else '|{}'.format(uobj.calendar))
        new_name = 'chunits({}, units={})'.format(data.name, unit_str)
        return PhysArray(data, name=new_name, units=uobj)
