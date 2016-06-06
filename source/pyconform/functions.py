"""
Functions for FunctionEvaluator Actions

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from abc import ABCMeta, abstractmethod
from cf_units import Unit
from numpy import sqrt, transpose


class UnitsError(ValueError):
    pass


class DimensionsError(ValueError):
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

    @abstractmethod
    def units(self, *arg_units):
        uret = arg_units[0] if isinstance(arg_units[0], Unit) else Unit(1)
        uarg = (None,) * len(self.numargs)
        return uret, uarg

    @abstractmethod
    def dimensions(self, *arg_dims):
        dret = arg_dims[0] if isinstance(arg_dims[0], tuple) else tuple()
        darg = (None,) * len(self.numargs)
        return dret, darg
    
    def __call__(self, *args):
        return 1
    

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


#===============================================================================
# NegationOperator
#===============================================================================
class NegationOperator(Operator):
    key = '-'
    numargs = 1

    @staticmethod
    def units(unit):
        uret = unit if isinstance(unit, Unit) else Unit(1)
        return uret, (None,)

    @staticmethod
    def dimensions(dims):
        dret = dims if isinstance(dims, tuple) else ()
        return dret, (None,)
    
    def __call__(self, arg):
        return -arg
    

#===============================================================================
# AdditionOperator
#===============================================================================
class AdditionOperator(Operator):
    key = '+'
    numargs = 2

    @staticmethod
    def units(lunit, runit):
        ul = lunit if isinstance(lunit, Unit) else Unit(1)
        ur = runit if isinstance(runit, Unit) else Unit(1)
        if ul == ur:
            return ul, (None, None)
        elif ur.is_convertible(ul):
            return ul, (None, ul)
        else:
            raise UnitsError(('Data with units {0!s} and {1!s} cannot be '
                              'added or subtracted').format(ul, ur))

    @staticmethod
    def dimensions(ldims, rdims):
        dl = ldims if isinstance(ldims, tuple) else ()
        dr = rdims if isinstance(rdims, tuple) else ()
        if dl == ():
            return dr, (None, None)
        elif dl == dr or dr == ():
            return dl, (None, None)
        elif set(dl) == set(dr):
            return dl, (None, dl)
        else:
            raise DimensionsError(('Data with dimensions {0} and {1} cannot '
                                   'be added or subtracted').format(dl, dr))
    
    def __call__(self, left, right):
        return left + right

#===============================================================================
# SubtractionOperator
#===============================================================================
class SubtractionOperator(Operator):
    key = '-'
    numargs = 2

    @staticmethod
    def units(lunit, runit):
        return AdditionOperator.units(lunit, runit)
    
    @staticmethod
    def dimensions(ldims, rdims):
        return AdditionOperator.dimensions(ldims, rdims)
    
    def __call__(self, left, right):
        return left - right

#===============================================================================
# PowerOperator
#===============================================================================
class PowerOperator(Operator):
    key = '^'
    numargs = 2

    @staticmethod
    def units(lunit, runit):
        if not isinstance(runit, (int, float)):
            raise UnitsError('Exponent in power function must be a '
                             'unitless scalar')
        try:
            upow = lunit ** runit
        except:
            raise UnitsError(('Cannot exponentiate units to power '
                              '{0}').format(runit))
        uret = upow if isinstance(upow, Unit) else Unit(1)
        return uret, (None, None)

    @staticmethod
    def dimensions(ldims, rdims):
        if not isinstance(rdims, (int, float)):
            raise DimensionsError('Exponent in power function must be a '
                                  'dimensionless scalar')
        dret = ldims if isinstance(ldims, tuple) else () 
        return dret, (None, None)
    
    def __call__(self, left, right):
        return left ** right


#===============================================================================
# MultiplicationOperator
#===============================================================================
class MultiplicationOperator(Operator):
    key = '*'
    numargs = 2

    @staticmethod
    def units(lunit, runit):
        ul = lunit if isinstance(lunit, Unit) else Unit(1)
        ur = runit if isinstance(runit, Unit) else Unit(1)
        try:
            uret = ul * ur
        except:
            raise UnitsError(('Cannot multiply or divide units {0} and '
                              '{1}').format(ul, ur))
        return uret, (None, None)

    @staticmethod
    def dimensions(ldims, rdims):
        dl = ldims if isinstance(ldims, tuple) else ()
        dr = rdims if isinstance(rdims, tuple) else ()
        if dl == ():
            return dr, (None, None)
        elif dl == dr or dr == ():
            return dl, (None, None)
        elif set(dl) == set(dr):
            return dl, (None, dl)
        else:
            raise DimensionsError(('Data with dimensions {0} and {1} cannot '
                                   'be multiplied or divided').format(dl, dr))
    
    def __call__(self, left, right):
        return left * right


#===============================================================================
# DivisionOperator
#===============================================================================
class DivisionOperator(Operator):
    key = '-'
    numargs = 2

    @staticmethod
    def units(lunit, runit):
        ul = lunit if isinstance(lunit, Unit) else Unit(1)
        ur = runit if isinstance(runit, Unit) else Unit(1)
        try:
            uret = ul / ur
        except:
            raise UnitsError(('Cannot multiply or divide units {0} and '
                              '{1}').format(ul, ur))
        return uret, (None, None)

    @staticmethod
    def dimensions(ldims, rdims):
        return MultiplicationOperator.dimensions(ldims, rdims)
    
    def __call__(self, left, right):
        return left / right


#===============================================================================
# Operator map - Fixed to prevent user-redefinition!
#===============================================================================

__OPERATORS__ = {('-', 1): NegationOperator(),
                 ('^', 2): PowerOperator(),
                 ('+', 2): AdditionOperator(),
                 ('-', 2): SubtractionOperator(),
                 ('*', 2): MultiplicationOperator(),
                 ('/', 2): DivisionOperator()}

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
    func_map = dict(((c.key, c.numargs), c())
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

#===============================================================================
# SquareRoot
#===============================================================================
class SquareRootFunction(Function):
    key = 'sqrt'
    numargs = 1

    @staticmethod
    def units(unit):
        u = unit if isinstance(unit, Unit) else Unit(1)
        try:
            uret = u.root(2)
        except:
            raise UnitsError(('Cannot take square-root of units {0}').format(u))
        return uret, (None,)

    @staticmethod
    def dimensions(dims):
        dret = dims if isinstance(dims, tuple) else ()
        return dret, (None,)
    
    def __call__(self, data):
        return sqrt(data)

#===============================================================================
# ConvertFunction
#===============================================================================
class ConvertFunction(Function):
    key = 'convert'
    numargs = 3

    @staticmethod
    def units(data_units, from_units, to_units):
        ud = data_units if isinstance(data_units, Unit) else Unit(1)
        uf = from_units if isinstance(from_units, Unit) else Unit(1)
        ut = to_units if isinstance(to_units, Unit) else Unit(1)
        if ud != uf:
            raise UnitsError(('Input units {0} different from expected '
                              'units {1}').format(ud, uf))
        if not uf.is_convertible(ut):
            raise UnitsError(('Ill-formed convert function.  Cannot convert '
                              'units {0} to {1}').format(uf, ut))
        uret = ut
        return uret, (None, None, None)

    @staticmethod
    def dimensions(data_dims, from_units, to_units):
        dret = data_dims if isinstance(data_dims, tuple) else ()
        return dret, (None, None, None)
    
    def __call__(self, data, from_units, to_units):
        return from_units.convert(data, to_units)

#===============================================================================
# TransposeFunction
#===============================================================================
class TransposeFunction(Function):
    key = 'transpose'
    numargs = 2

    @staticmethod
    def units(data_units, order):
        uret = data_units if isinstance(data_units, Unit) else Unit(1)
        return uret, (None, None)

    @staticmethod
    def dimensions(data_dims, order):
        d = data_dims if isinstance(data_dims, tuple) else ()
        dret = tuple(d[i] for i in order)
        return dret, (None, None)
    
    def __call__(self, data, order):
        return transpose(data, order)
