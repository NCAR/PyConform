"""
Physical Array Class

This module contains the PhysArray class, which is the primary object passed along
edges of a Data Flow graph.  It is a subclass of the Numpy MaskedArray, and carries with
its data the units associated with the data, the dimensions associated with each axis of
the data.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from __future__ import print_function
from pyconform.indexing import align_index
from cf_units import Unit
from operator import mul, div

import numpy


#===================================================================================================
# UnitsError
#===================================================================================================
class UnitsError(ValueError):
    """Exception indicating an error involving units of a PhysArray object"""


#===================================================================================================
# DimensionsError
#===================================================================================================
class DimensionsError(ValueError):
    """Exception indicating an error involving dimensions of a PhysArray object"""


#===================================================================================================
# PhysArray
#===================================================================================================
class PhysArray(numpy.ma.MaskedArray):
    """
    A PhysArray is an array of data with both units and dimensions

    The PhysArray is deried from the Numpy MaskedArray and is the basic object
    along the edges of a Data Flow graph.
    """

    def __new__(cls, inarray, name='', units=None, dimensions=None, _shape=None, _dimensions=None):
        obj = numpy.ma.asarray(inarray).view(cls)

        # Store a name associated with the object
        obj.name = name

        # Store units of the data
        if units is None:
            if 'units' not in obj._optinfo:
                obj.units = Unit(1)
        else:
            obj.units = Unit(units)

        # Store dimension names associated with each axis
        if dimensions is None:
            if 'dimensions' not in obj._optinfo:
                obj.dimensions = tuple(i for i in xrange(obj.ndim))
        else:
            obj.dimensions = dimensions

        # Initial shape
        if _shape is None:
            if '_shape' not in obj._optinfo:
                obj._optinfo['_shape'] = obj.shape
        else:
            if not isinstance(_shape, tuple):
                raise TypeError('Initial shape must be a tuple')
            obj._optinfo['_shape'] = _shape

        # Initial dimensions
        if _dimensions is None:
            if '_dimensions' not in obj._optinfo:
                obj._optinfo['_dimensions'] = obj.dimensions
        else:
            if not isinstance(_dimensions, tuple):
                raise TypeError('Initial dimensions must be a tuple')
            obj._optinfo['_dimensions'] = _dimensions
            
        return obj

    def __repr__(self):
        return ('{!s}(name={!r}, data={!s}, mask={!s}, fill_value={!s}, units={!r}, '
                'dimensions={!s})').format(self.__class__.__name__, self.name, self.data, self.mask,
                                           self.fill_value, str(self.units), self.dimensions)

    @property
    def name(self):
        """String name for the data"""
        return self._optinfo['name']

    @name.setter
    def name(self, nm):
        """String name for the data"""
        if not isinstance(nm, basestring):
            raise TypeError('PhysArray name must be string')
        self._optinfo['name'] = nm
        
    @property
    def units(self):
        """Units of the data"""
        return self._optinfo['units']

    @units.setter
    def units(self, units):
        """Units of the data"""
        if not isinstance(units, Unit):
            raise TypeError('Units must be of Unit type')
        self._optinfo['units'] = units

    @property
    def dimensions(self):
        """Named dimensions of the data"""
        return self._optinfo['dimensions']

    @dimensions.setter
    def dimensions(self, dims):
        """Named dimensions of the data"""
        if not isinstance(dims, tuple):
            raise TypeError('Dimensions must be a tuple')
        if len(dims) != len(self.shape):
            raise ValueError('Dimensions must have same length as shape')
        self._optinfo['dimensions'] = dims

    @property
    def _shape(self):
        """Initial size of each dimension of the data"""
        return self._optinfo['_shape']

    @property
    def _dimensions(self):
        """Initial dimensions names"""
        return self._optinfo['_dimensions']

    def __getitem__(self, index):
        idx = align_index(index, self.dimensions)
        if len(idx) == 0:
            return self
        else:
            dimensions = tuple(d for i, d in zip(idx, self.dimensions) if isinstance(i, slice))
            if dimensions != self.dimensions:
                return PhysArray(super(PhysArray, self).__getitem__(idx), dimensions=dimensions)
            else:
                return super(PhysArray, self).__getitem__(idx)

    @staticmethod
    def interpret_units(obj):
        """Return an object's assumed units"""
        return obj.units if isinstance(obj, PhysArray) else Unit(1)

    @staticmethod
    def interpret_dimensions(obj):
        """Return an object's assumed dimensions"""
        if isinstance(obj, PhysArray):
            return obj.dimensions
        else:
            return tuple(i for i in xrange(len(numpy.shape(obj))))

    @staticmethod
    def _match_units_(left, right):
        lunits = PhysArray.interpret_units(left)
        runits = PhysArray.interpret_units(right)
        if lunits == runits:
            return lunits
        else: 
            raise UnitsError('Units mismatch: {}, {}'.format(lunits, runits))

    @staticmethod
    def _match_dimensions_(left, right):
        ldims = PhysArray.interpret_dimensions(left)
        rdims = PhysArray.interpret_dimensions(right)
        if ldims == rdims:
            return ldims
        else:
            raise DimensionsError('Dimensions mismatch: {}, {}'.format(ldims, rdims))

    def __add__(self, other):
        units = PhysArray._match_units_(self, other)
        dimensions = PhysArray._match_dimensions_(self, other)
        return PhysArray(super(PhysArray, self).__add__(other), units=units, dimensions=dimensions)

    def __radd__(self, other):
        units = PhysArray._match_units_(self, other)
        dimensions = PhysArray._match_dimensions_(self, other)
        return PhysArray(super(PhysArray, self).__radd__(other), units=units, dimensions=dimensions)

    def __iadd__(self, other):
        self.units = PhysArray._match_units_(self, other)
        self.dimensions = PhysArray._match_dimensions_(self, other)
        return super(PhysArray, self).__iadd__(other)

    def __sub__(self, other):
        units = PhysArray._match_units_(self, other)
        dimensions = PhysArray._match_dimensions_(self, other)
        return PhysArray(super(PhysArray, self).__sub__(other), units=units, dimensions=dimensions)

    def __rsub__(self, other):
        units = PhysArray._match_units_(self, other)
        dimensions = PhysArray._match_dimensions_(self, other)
        return PhysArray(super(PhysArray, self).__rsub__(other), units=units, dimensions=dimensions)

    def __isub__(self, other):
        self.units = PhysArray._match_units_(self, other)
        self.dimensions = PhysArray._match_dimensions_(self, other)
        return super(PhysArray, self).__isub__(other)

    @staticmethod
    def _binop_units_(op, left, right):
        lunits = PhysArray.interpret_units(left)
        runits = PhysArray.interpret_units(right)
        try:
            munits = op(lunits, runits)
        except:
            nm = 'multiply' if op == mul else 'divide'
            raise UnitsError('Cannot {} with units: {}, {}'.format(nm, lunits, runits))
        return munits

    @staticmethod
    def _binop_dimensions_(op, left, right):
        ldims = PhysArray.interpret_dimensions(left)
        rdims = PhysArray.interpret_dimensions(right)
        if ldims == ():
            mdims = rdims
        elif ldims == rdims or rdims == ():
            mdims = ldims
        else:
            nm = 'multiply' if op == mul else 'divide'
            raise DimensionsError(('Cannot {} with dimensions: {}, {}').format(nm, ldims, rdims))
        return mdims

    def __div__(self, other):
        units = PhysArray._binop_units_(div, self, other)
        dimensions = PhysArray._binop_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__div__(other), units=units, dimensions=dimensions)

    def __rdiv__(self, other):
        units = PhysArray._binop_units_(div, other, self)
        dimensions = PhysArray._binop_dimensions_(div, other, self)
        return PhysArray(super(PhysArray, self).__rdiv__(other), units=units, dimensions=dimensions)

    def __idiv__(self, other):
        self.units = PhysArray._binop_units_(div, self, other)
        self.dimensions = PhysArray._binop_dimensions_(div, self, other)
        return super(PhysArray, self).__idiv__(other)

    def __floordiv__(self, other):
        units = PhysArray._binop_units_(div, self, other)
        dimensions = PhysArray._binop_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__floordiv__(other), units=units, dimensions=dimensions)

    def __rfloordiv__(self, other):
        units = PhysArray._binop_units_(div, other, self)
        dimensions = PhysArray._binop_dimensions_(div, other, self)
        return PhysArray(super(PhysArray, self).__rfloordiv__(other), units=units, dimensions=dimensions)

    def __ifloordiv__(self, other):
        self.units = PhysArray._binop_units_(div, self, other)
        self.dimensions = PhysArray._binop_dimensions_(div, self, other)
        return super(PhysArray, self).__ifloordiv__(other)

    def __truediv__(self, other):
        units = PhysArray._binop_units_(div, self, other)
        dimensions = PhysArray._binop_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__truediv__(other), units=units, dimensions=dimensions)

    def __rtruediv__(self, other):
        units = PhysArray._binop_units_(div, other, self)
        dimensions = PhysArray._binop_dimensions_(div, other, self)
        return PhysArray(super(PhysArray, self).__rtruediv__(other), units=units, dimensions=dimensions)

    def __itruediv__(self, other):
        self.units = PhysArray._binop_units_(div, self, other)
        self.dimensions = PhysArray._binop_dimensions_(div, self, other)
        return super(PhysArray, self).__itruediv__(other)

    def __mod__(self, other):
        dimensions = PhysArray._binop_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__mod__(other), units=self.units, dimensions=dimensions)

    def __rmod__(self, other):
        dimensions = PhysArray._binop_dimensions_(div, other, self)
        return PhysArray(super(PhysArray, self).__rmod__(other), units=self.units, dimensions=dimensions)

    def __imod__(self, other):
        self.dimensions = PhysArray._binop_dimensions_(div, self, other)
        return super(PhysArray, self).__imod__(other)

    def __divmod__(self, other):
        return (self.__floordiv__(other), self.__mod__(other))

    def __rdivmod__(self, other):
        return (self.__rfloordiv__(other), self.__rmod__(other))

    def __mul__(self, other):
        units = PhysArray._binop_units_(mul, self, other)
        dimensions = PhysArray._binop_dimensions_(mul, self, other)
        return PhysArray(super(PhysArray, self).__mul__(other), units=units, dimensions=dimensions)

    def __rmul__(self, other):
        units = PhysArray._binop_units_(mul, other, self)
        dimensions = PhysArray._binop_dimensions_(mul, other, self)
        return PhysArray(super(PhysArray, self).__rmul__(other), units=units, dimensions=dimensions)

    def __imul__(self, other):
        self.units = PhysArray._binop_units_(mul, self, other)
        self.dimensions = PhysArray._binop_dimensions_(mul, self, other)
        return super(PhysArray, self).__imul__(other)

    @staticmethod
    def _pow_units_(left, right):
        lunits = PhysArray.interpret_units(left)
        runits = PhysArray.interpret_units(right)
        if runits != Unit(1):
            raise UnitsError('Exponents must be scalar: {}'.format(right))
        try:
            punits = lunits ** right
        except:
            raise UnitsError('Cannot exponentiate with units: {!r}, {}'.format(lunits, right))
        return punits

    @staticmethod
    def _pow_dimensions_(left, right):
        ldims = PhysArray.interpret_dimensions(left)
        rdims = PhysArray.interpret_dimensions(right)
        if rdims != ():
            raise DimensionsError('Exponents must be scalar: {}'.format(right))
        return ldims

    def __pow__(self, other):
        units = PhysArray._pow_units_(self, other)
        dimensions = PhysArray._pow_dimensions_(self, other)
        return PhysArray(super(PhysArray, self).__pow__(other),  units=units, dimensions=dimensions)

    def __rpow__(self, other):
        units = PhysArray._pow_units_(self, other)
        dimensions = PhysArray._pow_dimensions_(self, other)
        return PhysArray(super(PhysArray, self).__rpow__(other), units=units, dimensions=dimensions)

    def __ipow__(self, other):
        self.units = PhysArray._pow_units_(self, other)
        self.dimensions = PhysArray._pow_dimensions_(self, other)
        return super(PhysArray, self).__ipow__(other)

