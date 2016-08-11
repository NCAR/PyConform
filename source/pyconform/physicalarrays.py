"""
Physical Array Class

This module contains the PhysicalArray class, which is the primary object passed along
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
    """Exception indicating an error involving units of a PhysicalArray object"""


#===================================================================================================
# DimensionsError
#===================================================================================================
class DimensionsError(ValueError):
    """Exception indicating an error involving dimensions of a PhysicalArray object"""


#===================================================================================================
# PhysicalArray
#===================================================================================================
class PhysicalArray(numpy.ma.MaskedArray):
    """
    A PhysicalArray is an array of data with both units and dimensions

    The PhysicalArray is deried from the Numpy MaskedArray and is the basic object
    along the edges of a Data Flow graph.
    """

    def __new__(cls, inarray, name=None, cfunits=None, dimensions=None, initialshape=None):
        obj = numpy.ma.asarray(inarray).view(cls)

        if name is None:
            if 'name' not in obj._optinfo:
                raise ValueError('PhysicalArray must have a name')
        else:
            obj.name = name

        if cfunits is None:
            if 'cfunits' not in obj._optinfo:
                obj.cfunits = Unit(1)
        else:
            obj.cfunits = Unit(cfunits)

        if dimensions is None:
            if 'dimensions' not in obj._optinfo:
                obj.dimensions = tuple([None] * len(obj.shape))
        else:
            obj.dimensions = dimensions

        if initialshape is None:
            if 'initialshape' not in obj._optinfo:
                obj.initialshape = obj.shape
        else:
            obj.initialshape = initialshape

        if 'provenance' not in obj._optinfo:
            obj._optinfo['provenance'] = []

        return obj

    def __repr__(self):
        return ('{!s}(name={!r}, data={!s}, mask={!s}, fill_value={!s}, cfunits={!r}, '
                'dimensions={!s})').format(self.__class__.__name__, self.data, self.mask,
                                           self.fill_value, str(self.cfunits), self.dimensions)

    @property
    def name(self):
        """String name for the data"""
        return self._optinfo['name']

    @name.setter
    def name(self, nm):
        """String name for the data"""
        if not isinstance(nm, basestring):
            raise TypeError('PhysicalArray name must be string')
        self._optinfo['name'] = nm
        
    @property
    def cfunits(self):
        """CF-Convention Units of the data"""
        return self._optinfo['cfunits']

    @cfunits.setter
    def cfunits(self, units):
        """CF-Convention Units of the data"""
        if not isinstance(units, Unit):
            raise TypeError('CF Units must be of Unit type')
        self._optinfo['cfunits'] = units

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
    def initialshape(self):
        """Initial size of each dimension of the data"""
        return self._optinfo['initialshape']

    @initialshape.setter
    def initialshape(self, ishape):
        """Initial size of each dimension of the data"""
        if not isinstance(ishape, tuple):
            raise TypeError('Initial shape must be a tuple')
        if len(ishape) != len(self.shape):
            raise ValueError('Initial shape must have same length as shape')
        self._optinfo['initialshape'] = ishape

    @property
    def provenance(self):
        """List of historical changes to the data"""
        return self._optinfo['provenance']
    
    def __getitem__(self, index):
        idx = align_index(index, self.dimensions)
        if len(idx) == 0:
            return self
        else:
            ishape = tuple(s for i, s in zip(idx, self.initialshape) if isinstance(i, slice))
            dimensions = tuple(d for i, d in zip(idx, self.dimensions) if isinstance(i, slice))
            if dimensions != self.dimensions:
                return PhysicalArray(super(PhysicalArray, self).__getitem__(idx),
                                     dimensions=dimensions, initialshape=ishape)
            else:
                return super(PhysicalArray, self).__getitem__(idx)

    @staticmethod
    def cfunitsof(obj):
        """Return an object's assumed units"""
        return obj.cfunits if isinstance(obj, PhysicalArray) else Unit(1)

    @staticmethod
    def dimensionsof(obj):
        """Return an object's assumed dimensions"""
        if isinstance(obj, PhysicalArray):
            return obj.dimensions
        else:
            return tuple([None] * len(numpy.shape(obj)))

    @staticmethod
    def _match_units_(left, right):
        lunits = PhysicalArray.cfunitsof(left)
        runits = PhysicalArray.cfunitsof(right)
        if lunits == runits:
            return lunits
        elif 
            raise UnitsError('Units mismatch: {}, {}'.format(lunits, runits))

        ldims = PhysicalArray.dimensionsof(left)
        rdims = PhysicalArray.dimensionsof(right)
        if ldims != rdims:
            raise DimensionsError('Dimensions mismatch: {}, {}'.format(ldims, rdims))

    def __add__(self, other):
        PhysicalArray._match_units_(self, other)
        return PhysicalArray(super(PhysicalArray, self).__add__(other),
                             cfunits=self.cfunits, dimensions=self.dimensions)

    def __radd__(self, other):
        PhysicalArray._match_units_(self, other)
        return PhysicalArray(super(PhysicalArray, self).__radd__(other),
                             cfunits=self.cfunits, dimensions=self.dimensions)

    def __iadd__(self, other):
        PhysicalArray._match_units_(self, other)
        return super(PhysicalArray, self).__iadd__(other)

    def __sub__(self, other):
        PhysicalArray._match_units_(self, other)
        return PhysicalArray(super(PhysicalArray, self).__sub__(other),
                             cfunits=self.cfunits, dimensions=self.dimensions)

    def __rsub__(self, other):
        PhysicalArray._match_units_(self, other)
        return PhysicalArray(super(PhysicalArray, self).__rsub__(other),
                             cfunits=self.cfunits, dimensions=self.dimensions)

    def __isub__(self, other):
        PhysicalArray._match_units_(self, other)
        return super(PhysicalArray, self).__isub__(other)

    @staticmethod
    def _binop_units_(op, left, right):
        lunits = PhysicalArray.cfunitsof(left)
        runits = PhysicalArray.cfunitsof(right)
        try:
            munits = op(lunits, runits)
        except:
            opname = 'multiply' if op == mul else 'divide'
            raise UnitsError('Cannot {} with units: {!r}, {!r}'.format(opname, lunits, runits))
        return munits

    @staticmethod
    def _binop_dimensions_(op, left, right):
        ldims = PhysicalArray.dimensionsof(left)
        rdims = PhysicalArray.dimensionsof(right)
        if ldims == ():
            mdims = rdims
        elif ldims == rdims or rdims == ():
            mdims = ldims
        else:
            opname = 'multiply' if op == mul else 'divide'
            raise DimensionsError(('Cannot {} with dimensions: '
                                        '{!r}, {!r}').format(opname, ldims, rdims))
        return mdims

    def __div__(self, other):
        cfunits = PhysicalArray._binop_units_(div, self, other)
        dimensions = PhysicalArray._binop_dimensions_(div, self, other)
        return PhysicalArray(super(PhysicalArray, self).__div__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __rdiv__(self, other):
        cfunits = PhysicalArray._binop_units_(div, other, self)
        dimensions = PhysicalArray._binop_dimensions_(div, other, self)
        return PhysicalArray(super(PhysicalArray, self).__rdiv__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __idiv__(self, other):
        self.cfunits = PhysicalArray._binop_units_(div, self, other)
        self.dimensions = PhysicalArray._binop_dimensions_(div, self, other)
        return super(PhysicalArray, self).__idiv__(other)

    def __floordiv__(self, other):
        cfunits = PhysicalArray._binop_units_(div, self, other)
        dimensions = PhysicalArray._binop_dimensions_(div, self, other)
        return PhysicalArray(super(PhysicalArray, self).__floordiv__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __rfloordiv__(self, other):
        cfunits = PhysicalArray._binop_units_(div, other, self)
        dimensions = PhysicalArray._binop_dimensions_(div, other, self)
        return PhysicalArray(super(PhysicalArray, self).__rfloordiv__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __ifloordiv__(self, other):
        self.cfunits = PhysicalArray._binop_units_(div, self, other)
        self.dimensions = PhysicalArray._binop_dimensions_(div, self, other)
        return super(PhysicalArray, self).__ifloordiv__(other)

    def __truediv__(self, other):
        cfunits = PhysicalArray._binop_units_(div, self, other)
        dimensions = PhysicalArray._binop_dimensions_(div, self, other)
        return PhysicalArray(super(PhysicalArray, self).__truediv__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __rtruediv__(self, other):
        cfunits = PhysicalArray._binop_units_(div, other, self)
        dimensions = PhysicalArray._binop_dimensions_(div, other, self)
        return PhysicalArray(super(PhysicalArray, self).__rtruediv__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __itruediv__(self, other):
        self.cfunits = PhysicalArray._binop_units_(div, self, other)
        self.dimensions = PhysicalArray._binop_dimensions_(div, self, other)
        return super(PhysicalArray, self).__itruediv__(other)

    def __mod__(self, other):
        dimensions = PhysicalArray._binop_dimensions_(div, self, other)
        return PhysicalArray(super(PhysicalArray, self).__mod__(other),
                             cfunits=self.cfunits, dimensions=dimensions)

    def __rmod__(self, other):
        dimensions = PhysicalArray._binop_dimensions_(div, other, self)
        return PhysicalArray(super(PhysicalArray, self).__rmod__(other),
                             cfunits=self.cfunits, dimensions=dimensions)

    def __imod__(self, other):
        self.dimensions = PhysicalArray._binop_dimensions_(div, self, other)
        return super(PhysicalArray, self).__imod__(other)

    def __divmod__(self, other):
        return (self.__floordiv__(other), self.__mod__(other))

    def __rdivmod__(self, other):
        return (self.__rfloordiv__(other), self.__rmod__(other))

    def __mul__(self, other):
        cfunits = PhysicalArray._binop_units_(mul, self, other)
        dimensions = PhysicalArray._binop_dimensions_(mul, self, other)
        return PhysicalArray(super(PhysicalArray, self).__mul__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __rmul__(self, other):
        cfunits = PhysicalArray._binop_units_(mul, other, self)
        dimensions = PhysicalArray._binop_dimensions_(mul, other, self)
        return PhysicalArray(super(PhysicalArray, self).__rmul__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __imul__(self, other):
        self.cfunits = PhysicalArray._binop_units_(mul, self, other)
        self.dimensions = PhysicalArray._binop_dimensions_(mul, self, other)
        return super(PhysicalArray, self).__imul__(other)

    @staticmethod
    def _pow_units_(left, right):
        lunits = PhysicalArray.cfunitsof(left)
        runits = PhysicalArray.cfunitsof(right)
        if runits != Unit(1):
            raise UnitsError('Exponents must be scalar: {}'.format(right))
        try:
            punits = lunits ** right
        except:
            raise UnitsError('Cannot exponentiate with units: {!r}, {}'.format(lunits, right))
        return punits

    @staticmethod
    def _pow_dimensions_(left, right):
        ldims = PhysicalArray.dimensionsof(left)
        rdims = PhysicalArray.dimensionsof(right)
        if rdims != ():
            raise DimensionsError('Exponents must be scalar: {}'.format(right))
        return ldims

    def __pow__(self, other):
        cfunits = PhysicalArray._pow_units_(self, other)
        dimensions = PhysicalArray._pow_dimensions_(self, other)
        return PhysicalArray(super(PhysicalArray, self).__pow__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __rpow__(self, other):
        cfunits = PhysicalArray._pow_units_(self, other)
        dimensions = PhysicalArray._pow_dimensions_(self, other)
        return PhysicalArray(super(PhysicalArray, self).__rpow__(other),
                             cfunits=cfunits, dimensions=dimensions)

    def __ipow__(self, other):
        self.cfunits = PhysicalArray._pow_units_(self, other)
        self.dimensions = PhysicalArray._pow_dimensions_(self, other)
        return super(PhysicalArray, self).__ipow__(other)

