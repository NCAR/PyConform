"""
Physical Array Class

This module contains the PhysArray class, which is the primary object passed along
edges of a Data Flow graph.  It is a subclass of the Numpy MaskedArray, and carries with
its data the units associated with the data, the dimensions associated with each axis of
the data.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

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

    def __new__(cls, inarray, name=None, units=None, dimensions=None, _shape=None):
        obj = numpy.ma.asarray(inarray).view(cls)

        # Store a name associated with the object
        if name is None:
            if 'name' not in obj._optinfo:
                obj.name = str(obj.__class__.__name__)
        else:
            obj.name = name

        # Store units of the data
        if units is None:
            if 'units' not in obj._optinfo:
                obj.units = Unit(1)
        elif isinstance(units, Unit):
            obj.units = units
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
            if len(_shape) != len(dimensions):
                raise ValueError('Initial shape must match dimension length')
            obj._optinfo['_shape'] = _shape

        return obj

    def __repr__(self):
        return ('{!s}(data={!s}, mask={!s}, fill_value={!s}, units={!r}, name={!r}, dimensions='
                '{!s})').format(self.__class__.__name__, self.data, self.mask, self.fill_value,
                                str(self.units), self.name, self.dimensions)

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

    def __getitem__(self, index):
        idx = align_index(index, self.dimensions)
        if len(idx) == 0:
            return self
        else:
            dimensions = tuple(d for i, d in zip(idx, self.dimensions) if isinstance(i, slice))
            if dimensions != self.dimensions:
                shape0 = tuple(s for i, s in zip(idx, self._shape) if isinstance(i, slice))
                return PhysArray(super(PhysArray, self).__getitem__(idx),
                                 dimensions=dimensions, _shape=shape0)
            else:
                return super(PhysArray, self).__getitem__(idx)

    @staticmethod
    def interpret_name(obj):
        """Return an object's assumed string name"""
        return obj.name if isinstance(obj, PhysArray) else str(obj)

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
    def _match_right_(left, right):
        rname = PhysArray.interpret_name(right)
        lunits = PhysArray.interpret_units(left)
        runits = PhysArray.interpret_units(right)
        if lunits != runits:
            if runits.is_convertible(lunits):
                right = runits.convert(right, lunits)
                rname = 'convert({}, to={})'.format(rname, lunits)
            else:
                raise UnitsError('Nonconvertible units: {}, {}'.format(lunits, runits))
        ldims = PhysArray.interpret_dimensions(left)
        rdims = PhysArray.interpret_dimensions(right)
        if ldims == () or rdims == ():
            return right, rname
        elif ldims != rdims:
            if set(ldims) == set(rdims):
                right = numpy.transpose(right, axes=tuple(rdims.index(d) for d in ldims))
                rname = 'transpose({}, to={})'.format(rname, ldims)
            else:
                raise DimensionsError('Nontransposable dimensions: {}, {}'.format(ldims, rdims))
        return right, rname

    def __add__(self, other):
        other, rname = PhysArray._match_right_(self, other)
        return PhysArray(super(PhysArray, self).__add__(other),
                         name='({}+{})'.format(self.name, rname))

    def __radd__(self, other):
        other, rname = PhysArray._match_right_(self, other)
        return PhysArray(super(PhysArray, self).__radd__(other),
                         name='({}+{})'.format(rname, self.name))

    def __iadd__(self, other):
        other, rname = PhysArray._match_right_(self, other)
        self.name = '({}+{})'.format(self.name, rname)
        return super(PhysArray, self).__iadd__(other)

    def __sub__(self, other):
        other, rname = PhysArray._match_right_(self, other)
        return PhysArray(super(PhysArray, self).__sub__(other),
                         name='({}-{})'.format(self.name, rname))

    def __rsub__(self, other):
        other, rname = PhysArray._match_right_(self, other)
        return PhysArray(super(PhysArray, self).__rsub__(other),
                         name='({}-{})'.format(rname, self.name))

    def __isub__(self, other):
        other, rname = PhysArray._match_right_(self, other)
        self.name = '({}-{})'.format(self.name, rname)
        return super(PhysArray, self).__isub__(other)

    @staticmethod
    def _mul_div_units_(op, left, right):
        lunits = PhysArray.interpret_units(left)
        runits = PhysArray.interpret_units(right)
        try:
            munits = op(lunits, runits)
        except:
            nm = 'multiply' if op == mul else 'divide'
            raise UnitsError('Cannot {} with units: {}, {}'.format(nm, lunits, runits))
        return munits

    @staticmethod
    def _mul_div_dimensions_(op, self, other):
        oname = PhysArray.interpret_name(other)
        sdims = PhysArray.interpret_dimensions(self)
        odims = PhysArray.interpret_dimensions(other)
        if sdims == ():
            mdims = odims
        elif sdims == odims or odims == ():
            mdims = sdims
        elif set(sdims) == set(odims):
            other = numpy.transpose(other, axes=tuple(odims.index(d) for d in sdims))
            oname = 'transpose({}, to={})'.format(oname, sdims)
            mdims = sdims
        else:
            nm = 'multiply' if op == mul else 'divide'
            raise DimensionsError(('Cannot {} with dimensions: {}, {}').format(nm, sdims, odims))
        return other, mdims, oname

    def __mul__(self, other):
        units = PhysArray._mul_div_units_(mul, self, other)
        other, dims, oname = PhysArray._mul_div_dimensions_(mul, self, other)
        return PhysArray(super(PhysArray, self).__mul__(other), units=units, dimensions=dims,
                         name='({}*{})'.format(self.name, oname))

    def __rmul__(self, other):
        units = PhysArray._mul_div_units_(mul, other, self)
        other, dims, oname = PhysArray._mul_div_dimensions_(mul, self, other)
        return PhysArray(super(PhysArray, self).__rmul__(other), units=units, dimensions=dims,
                         name='({}*{})'.format(oname, self.name))

    def __imul__(self, other):
        self.units = PhysArray._mul_div_units_(mul, self, other)
        other, dims, oname = PhysArray._mul_div_dimensions_(mul, self, other)
        self.dimensions = dims
        self.name = '({}*{})'.format(self.name, oname)
        return super(PhysArray, self).__imul__(other)

    def __div__(self, other):
        units = PhysArray._mul_div_units_(div, self, other)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__div__(other), units=units, dimensions=dims,
                         name='({}/{})'.format(self.name, oname))

    def __rdiv__(self, other):
        units = PhysArray._mul_div_units_(div, other, self)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__rdiv__(other), units=units, dimensions=dims,
                         name='({}/{})'.format(oname, self.name))

    def __idiv__(self, other):
        self.units = PhysArray._mul_div_units_(div, self, other)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        self.dimensions = dims
        self.name = '({}/{})'.format(self.name, oname)
        return super(PhysArray, self).__idiv__(other)

    def __floordiv__(self, other):
        units = PhysArray._mul_div_units_(div, self, other)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__floordiv__(other), units=units, dimensions=dims,
                         name='({}//{})'.format(self.name, oname))

    def __rfloordiv__(self, other):
        units = PhysArray._mul_div_units_(div, other, self)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__rfloordiv__(other), units=units, dimensions=dims,
                         name='({}//{})'.format(oname, self.name))

    def __ifloordiv__(self, other):
        self.units = PhysArray._mul_div_units_(div, self, other)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        self.dimensions = dims
        self.name = '({}//{})'.format(self.name, oname)
        return super(PhysArray, self).__ifloordiv__(other)

    def __truediv__(self, other):
        units = PhysArray._mul_div_units_(div, self, other)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__truediv__(other), units=units, dimensions=dims,
                         name='({}/{})'.format(self.name, oname))

    def __rtruediv__(self, other):
        units = PhysArray._mul_div_units_(div, other, self)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__rtruediv__(other), units=units, dimensions=dims,
                         name='({}/{})'.format(oname, self.name))

    def __itruediv__(self, other):
        self.units = PhysArray._mul_div_units_(div, self, other)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        self.dimensions = dims
        self.name = '({}/{})'.format(self.name, oname)
        return super(PhysArray, self).__itruediv__(other)

    def __mod__(self, other):
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__mod__(other), dimensions=dims,
                         name='({}%{})'.format(self.name, oname))

    def __rmod__(self, other):
        units = PhysArray.interpret_units(other)
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        return PhysArray(super(PhysArray, self).__rmod__(other), units=units, dimensions=dims,
                         name='({}%{})'.format(oname, self.name))

    def __imod__(self, other):
        other, dims, oname = PhysArray._mul_div_dimensions_(div, self, other)
        self.dimensions = dims
        self.name = '({}%{})'.format(self.name, oname)
        return super(PhysArray, self).__imod__(other)

    def __divmod__(self, other):
        return (self.__floordiv__(other), self.__mod__(other))

    def __rdivmod__(self, other):
        return (self.__rfloordiv__(other), self.__rmod__(other))

    @staticmethod
    def _pow_units_(left, right):
        rname = PhysArray.interpret_name(right)
        lunits = PhysArray.interpret_units(left)
        runits = PhysArray.interpret_units(right)
        if runits != Unit(1):
            if runits.is_convertible(Unit(1)):
                right = runits.convert(right, Unit(1))
                rname = 'convert({}, to={})'.format(rname, Unit(1))
            else:
                raise UnitsError('Exponents must be scalar: {}'.format(right))
        try:
            punits = lunits ** right
        except:
            raise UnitsError('Cannot exponentiate with units: {!r}, {}'.format(lunits, right))
        return punits, rname, right

    @staticmethod
    def _pow_dimensions_(left, right):
        ldims = PhysArray.interpret_dimensions(left)
        rdims = PhysArray.interpret_dimensions(right)
        if rdims != ():
            raise DimensionsError('Exponents must be scalar: {}'.format(right))
        return ldims

    def __pow__(self, other):
        units, oname, other = PhysArray._pow_units_(self, other)
        dimensions = PhysArray._pow_dimensions_(self, other)
        return PhysArray(super(PhysArray, self).__pow__(other), units=units, dimensions=dimensions,
                         name='({}**{})'.format(self.name, oname))

    def __rpow__(self, other):
        right = self.copy()
        units, sname, right = PhysArray._pow_units_(other, right)
        dimensions = PhysArray._pow_dimensions_(other, right)
        return PhysArray(super(PhysArray, right).__rpow__(other), units=units, dimensions=dimensions,
                         name='({}**{})'.format(PhysArray.interpret_name(other), sname))

    def __ipow__(self, other):
        units, oname, other = PhysArray._pow_units_(self, other)
        self.units = units
        self.dimensions = PhysArray._pow_dimensions_(self, other)
        self.name = '({}**{})'.format(self.name, oname)
        return super(PhysArray, self).__ipow__(other)

    def convert(self, units):
        """
        Return a new PhysArray with new units
        
        Parameters:
            units (Unit): The new units to which to convert the PhysArray
        """
        if self.units.is_convertible(units):
            print '1111: {!r}'.format(units)
            data = PhysArray(self.units.convert(self, units), units=units,
                             name='convert({}, to={})'.format(self.name, units))
            print '2222: {!r}'.format(data.units)
            return data
        else:
            print 'FAIL!!!'
            raise UnitsError('Cannot convert units from {!r} to {!r}'.format(self.units, units))

    def transpose(self, *dims):
        """
        Return a new PhysArray with dimensions transposed in the order given
        
        Parameters:
            dims (tuple): Tuple of dimension names in the new order
        """
        if len(dims) == 1 and isinstance(dims[0], tuple):
            dims = dims[0]
        if set(dims) == set(self.dimensions):
            new_dims = dims
            new_shp0 = tuple(self._shape[self.dimensions.index(d)] for d in dims)
            axes = tuple(self.dimensions.index(d) for d in dims)
        elif set(dims) == set(range(self.ndim)):
            new_dims = tuple(self.dimensions[i] for i in dims)
            new_shp0 = tuple(self._shape[i] for i in dims)
            axes = dims
        else:
            raise DimensionsError('Cannot transpose to dimensions/axes {}'.format(dims))
        return PhysArray(super(PhysArray, self).transpose(*axes), dimensions=new_dims,
                         name='transpose({}, to={})'.format(self.name, new_dims),
                         _shape=new_shp0)
