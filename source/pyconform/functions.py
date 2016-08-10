"""
Functions for FunctionEvaluator Actions

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from abc import ABCMeta, abstractmethod
from pyconform.dataarrays import DataArray
from cf_units import Unit
from numpy import sqrt, transpose


#===================================================================================================
# UnitsError
#===================================================================================================
class UnitsError(ValueError):
    """Exception for when DataArray Units are invalid"""
    def __init__(self, name, hints={}):
        msgs = []
        for iarg, units in hints.iteritems():
            msgs.append('argument {} requires conversion to {!s}'.format(iarg, str(units)))
        message = 'In {}: '.format(name) + ', or '.join(msgs)
        super(UnitsError, self).__init__(message)
        self.name = name
        self.hints = hints


#===================================================================================================
# DimensionsError
#===================================================================================================
class DimensionsError(ValueError):
    """Exception for when DataArray Dimensions are invalid"""
    def __init__(self, name, hints={}):
        msgs = []
        for iarg, dimensions in hints.iteritems():
            msgs.append('argument {} requires dimensions {!s}'.format(iarg, dimensions))
        message = 'In {}: '.format(name) + ', or '.join(msgs)
        super(DimensionsError, self).__init__(message)
        self.name = name
        self.hints = hints


#===================================================================================================
# Find a function or operator based on key and number of arguments
#===================================================================================================
def find(key, numargs=None):
    try:
        fop = find_operator(key, numargs)
    except:
        pass
    else:
        return fop

    try:
        fop = find_function(key, numargs)
    except:
        if numargs is not None:
            raise KeyError(('No operator or function {!r} with {} '
                            'arguments found').format(key, numargs))
        else:
            raise KeyError('No operator or function {!r} found'.format(key))
    else:
        return fop


#===================================================================================================
# FunctionBase - base class for Function and Operator Classes
#===================================================================================================
class FunctionBase(object):
    __metaclass__ = ABCMeta
    key = 'function'
    numargs = 2

    def get_units(self, *args):
        if len(args) == 0:
            return None
        elif len(args) == 1:
            return args[0].cfunits if isinstance(args[0], DataArray) else Unit(1)
        else:
            return tuple(arg.cfunits if isinstance(arg, DataArray) else Unit(1) for arg in args)

    def get_dimensions(self, *args):
        if len(args) == 0:
            return None
        elif len(args) == 1:
            return args[0].dimensions if isinstance(args[0], DataArray) else ()
        else:
            return tuple(arg.dimensions if isinstance(arg, DataArray) else () for arg in args)

    @abstractmethod
    def __call__(self, *args):
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
        units = self.get_units(arg)
        dims = self.get_dimensions(arg)
        return DataArray(-arg, cfunits=units, dimensions=dims)


#===================================================================================================
# AdditionOperator
#===================================================================================================
class AdditionOperator(Operator):
    key = '+'
    numargs = 2

    def __call__(self, left, right):
        lunits, runits = self.get_units(left, right)
        if lunits != runits:
            raise UnitsError(self.__class__.__name__, hints={1: lunits})

        ldims, rdims = self.get_dimensions(left, right)
        if ldims != rdims:
            raise DimensionsError(self.__class__.__name__, hints={0: rdims, 1: ldims})

        return DataArray(left + right, cfunits=lunits, dimensions=ldims)

#===================================================================================================
# SubtractionOperator
#===================================================================================================
class SubtractionOperator(Operator):
    key = '-'
    numargs = 2

    def __call__(self, left, right):
        lunits, runits = self.get_units(left, right)
        if lunits != runits:
            raise UnitsError(self.__class__.__name__, hints={1: lunits})

        ldims, rdims = self.get_dimensions(left, right)
        if ldims != rdims:
            raise DimensionsError(self.__class__.__name__, hints={0: rdims, 1: ldims})

        return DataArray(left - right, cfunits=lunits, dimensions=ldims)

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
            raise UnitsError(self.__class__.__name__, hints={1: Unit(1)})
        if rdims != ():
            raise DimensionsError(self.__class__.__name__, hints={1: ()})

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

__OPERATORS__ = {'-': {1: NegationOperator(), 2: SubtractionOperator()},
                 '^': {2: PowerOperator()},
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
def find_function(key, numargs=None):
    funcs = {}
    for c in _all_subclasses_(Function):
        if c.key != key:
            continue
        if c.numargs not in funcs:
            funcs[c.numargs] = c
        else:
            raise RuntimeError(('Function {!r} with {} arguments is '
                                'multiply defined').format(c.key, c.numargs))
    if numargs is None:
        if len(funcs) == 0:
            raise KeyError('Function {!r} not found'.format(key))
        elif len(funcs) == 1:
            return funcs.values()[0]()
        else:
            raise KeyError(('Function {!r} has multiple definitions, '
                            'number of arguments required').format(key))
    elif numargs not in funcs:
        raise KeyError('Function {!r} with {} arguments not found'.format(c.key, c.numargs))
    else:
        return funcs[numargs]()


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
            print dunits
            raise ValueError('Cannot take square-root of {!r}'.format(dunits))

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
