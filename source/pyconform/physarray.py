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
from operator import mul, pow

import numpy

_ALPHAS_ = 'abcdefghijklmnopqrstuvwxyz'

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

    def __new__(cls, inarray, name=None, units=None, dimensions=None, positive=None):
        obj = numpy.ma.asarray(inarray).view(cls)

        # Store a name associated with the object
        if name is None:
            if 'name' not in obj._optinfo:
                obj.name = str(inarray)
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
                obj.dimensions = tuple(range(len(numpy.shape(inarray))))
        else:
            obj.dimensions = dimensions

        # Set the positive direction for the data
        if positive is None:
            if 'positive' not in obj._optinfo:
                obj.positive = 'none'
        else:
            obj.positive = positive

        return obj

    def __str__(self):
        return '{}'.format(self.name)

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
        if not isinstance(dims, (list, tuple)):
            raise TypeError('Dimensions must be a tuple')
        if len(dims) != len(self.shape):
            raise ValueError('Dimensions must have same length as shape')
        self._optinfo['dimensions'] = tuple(dims)

    @property
    def positive(self):
        """Positive direction (up or down) for the data"""
        return self._optinfo['positive']

    @positive.setter
    def positive(self, pos):
        """Positive direction (up or down) for the data"""
        strpos = str(pos).lower()
        if strpos not in ['up', 'down', 'none']:
            raise ValueError('Positive attribute must be up, down, or none, not {!r}'.format(pos))
        self._optinfo['positive'] = strpos

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

    def __setitem__(self, index, values):
        idx = align_index(index, self.dimensions)
        if isinstance(values, PhysArray):
            values = values.convert(self.units).transpose(self.dimensions)
        super(PhysArray, self).__setitem__(idx, values)

    @staticmethod
    def _convert_name_(name, units1, units2):
        u1_str = '{}'.format(units1) + ('|{}'.format(units1.calendar) if units1.calendar else '')
        u2_str = '{}'.format(units2) + ('|{}'.format(units2.calendar) if units2.calendar else '')
        return "convert({}, from={}, to={})".format(name, u1_str, u2_str)

    @staticmethod
    def _safe_convert_(obj, units1, units2):
        # Because netcdftime datetime conversion always returns an NDArray, even if the
        # original object is a subclass of NDArray, we have to wrap the convert function
        # to safely preserve the object type...  sigh.
        if isinstance(obj, PhysArray):
            new_array = numpy.ma.MaskedArray(units1.convert(obj.data, units2),
                                             mask=obj.mask, dtype=obj.dtype)
            new_name = PhysArray._convert_name_(obj.name, units1, units2)
            return PhysArray(new_array, name=new_name, units=units2, dimensions=obj.dimensions)
        elif isinstance(obj, numpy.ma.MaskedArray):
            return numpy.ma.MaskedArray(units1.convert(obj.data, units2),
                                        mask=obj.mask, dtype=obj.dtype)
        else:
            return units1.convert(obj, units2)

    def convert(self, units):
        """
        Return a new PhysArray with new units
        
        Parameters:
            units (Unit): The new units to which to convert the PhysArray
        """
        if self.units.is_convertible(units):
            return PhysArray._safe_convert_(self, self.units, units)
        else:
            raise UnitsError('Cannot convert units {!r} to {!r}'.format(self.units, units))

    def _convert_scalar_check_(self, units):
        if self.units != units:
            return self.convert(units)
        else:
            return self

    @staticmethod
    def _transpose_name_(name, idims, odims):
        idim_str = ','.join(idims)
        odim_str = ','.join(odims)
        return 'transpose({}, from=[{}], to=[{}])'.format(name, idim_str, odim_str)

    def transpose(self, *dims):
        """
        Return a new PhysArray with dimensions transposed in the order given
        
        Parameters:
            dims (tuple): Tuple of dimension names in the new order
        """
        if len(dims) == 1 and isinstance(dims[0], (list, tuple)):
            dims = tuple(dims[0])
        if set(dims) == set(self.dimensions):
            new_dims = tuple(dims)
            axes = tuple(self.dimensions.index(d) for d in dims)
        elif set(dims) == set(range(self.ndim)):
            new_dims = tuple(self.dimensions[i] for i in dims)
            axes = dims
        else:
            raise DimensionsError(('Cannot transpose dimensions/axes {} to '
                                   '{}').format(self.dimensions, dims))
        return PhysArray(super(PhysArray, self).transpose(*axes), dimensions=new_dims,
                         name=PhysArray._transpose_name_(self.name, self.dimensions, new_dims))

    def _transpose_scalar_check_(self, obj):
        if self.dimensions == () or obj.dimensions == () or self.dimensions == obj.dimensions:
            return self
        else:
            return self.transpose(obj.dimensions)
    
    def up(self):
        nm = self.name
        if self.positive == 'down':
            self *= -1
        self.positive = 'up'
        self.name = 'up({})'.format(nm)
        return self

    def down(self):
        nm = self.name
        if self.positive == 'up':
            self *= -1
        self.positive = 'down'
        self.name = 'down({})'.format(nm)
        return self
    
    @staticmethod
    def _match_positive_(left, right):
        if left.positive == 'up':
            return left, PhysArray(right).up()
        elif left.positive == 'down':
            return left, PhysArray(right).down()
        else:
            if right.positive == 'up':
                return PhysArray(left).up(), right
            elif right.positive == 'down':
                return PhysArray(left).down(), right
            else:
                return left, right            
            
    def _return_dims_(self, other):
        if self.dimensions == ():
            return other.dimensions
        else:
            return self.dimensions
    
    def __add__(self, other):
        other = PhysArray(other)._convert_scalar_check_(self.units)._transpose_scalar_check_(self)
        dims = self._return_dims_(other)
        left, right = PhysArray._match_positive_(self, other)
        return PhysArray(super(PhysArray, left).__add__(right), dimensions=dims,
                         units=left.units, name='({}+{})'.format(left.name, right.name))

    def __radd__(self, other):
        return PhysArray(other).__add__(self)

    def __iadd__(self, other):
        self = self.__add__(other)
        return self

    def __sub__(self, other):
        other = PhysArray(other)._convert_scalar_check_(self.units)._transpose_scalar_check_(self)
        dims = self._return_dims_(other)
        left, right = PhysArray._match_positive_(self, other)
        return PhysArray(super(PhysArray, left).__sub__(right), dimensions=dims,
                         units=left.units, name='({}-{})'.format(left.name, right.name))

    def __rsub__(self, other):
        return PhysArray(other).__sub__(self)

    def __isub__(self, other):
        self = self.__sub__(other)
        return self

    def _op_units_(self, val, op):
        sunits = self.units
        try:
            units = op(sunits, val)
        except:
            opnm = str(op.__name__)
            raise UnitsError('Operator {!r} failed with units: {}, {}'.format(opnm, sunits, val))
        return units

    def _common_dim_multiply_(self, other):
        n = 0
        symbol_map = {}
        for d in self.dimensions + other.dimensions:
            if d not in symbol_map:
                symbol_map[d] = _ALPHAS_[n]
                n += 1
        lsyms = ''.join(symbol_map[d] for d in self.dimensions)
        rsyms = ''.join(symbol_map[d] for d in other.dimensions)
        visited = set()
        common_dims = ()
        for d in (self.dimensions + other.dimensions):
            if d in visited:
                continue
            visited.add(d)
            common_dims += (d,)
        osyms = ''.join(symbol_map[d] for d in common_dims)
        expr = '{},{}->{}'.format(lsyms, rsyms, osyms)
        ounits = self._op_units_(other.units, mul)
        return PhysArray(numpy.ma.MaskedArray(numpy.einsum(expr, self, other),
                                              mask=self.mask + other.mask),
                         dimensions=common_dims, units=ounits,
                         name='({}*{})'.format(self.name, other.name))

    def __mul__(self, other):
        return self._common_dim_multiply_(PhysArray(other))

    def __rmul__(self, other):
        return PhysArray(other).__mul__(self)

    def __imul__(self, other):
        self = self.__mul__(other)
        return self

    def invert(self):
        return PhysArray(1.0 / self.data, dimensions=self.dimensions, units=self.units.invert(),
                         name='(1/{!s})'.format(self))

    def __div__(self, other):
        data = self._common_dim_multiply_(PhysArray(other).invert())
        data.name = '({!s}/{!s})'.format(self, other)
        return data

    def __rdiv__(self, other):
        return PhysArray(other).__div__(self)

    def __idiv__(self, other):
        self = self.__div__(other)
        return self

    def __floordiv__(self, other):
        data = self._common_dim_multiply_(PhysArray(other).invert())
        return PhysArray(numpy.ma.floor(data.data), dimensions=data.dimensions, units=data.units,
                         name='({!s}//{!s})'.format(self, other))

    def __rfloordiv__(self, other):
        return PhysArray(other).__floordiv__(self)

    def __ifloordiv__(self, other):
        self = self.__floordiv__(PhysArray(other))
        return self

    def __truediv__(self, other):
        return self.__div__(other)

    def __rtruediv__(self, other):
        return PhysArray(other).__truediv__(self)

    def __itruediv__(self, other):
        self = self.__truediv__(other)
        return self

    def __mod__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        dims = self._return_dims_(other)
        return PhysArray(super(PhysArray, self).__mod__(other), dimensions=dims,
                         name='({!s}%{!s})'.format(self, other))

    def __rmod__(self, other):
        return PhysArray(other).__mod__(self)

    def __imod__(self, other):
        self = self.__mod__(other)
        return self

    def __divmod__(self, other):
        return self.__floordiv__(other), self.__mod__(other)

    def __rdivmod__(self, other):
        return self.__rfloordiv__(other), self.__rmod__(other)

    def _check_exponent_dims_(self, exp):
        if exp.dimensions != ():
            raise DimensionsError('Exponents must be scalar: {}'.format(exp))

    def __pow__(self, other):
        other = PhysArray(other)._convert_scalar_check_(Unit(1))
        units = self._op_units_(other, pow)
        if other.dimensions != ():
            raise DimensionsError('Exponents must be scalar: {}'.format(other))
        return PhysArray(super(PhysArray, self).__pow__(other), units=units,
                         name='({!s}**{!s})'.format(self, other))

    def __rpow__(self, other):
        return PhysArray(other).__pow__(self)

    def __ipow__(self, other):
        self = self.__pow__(other)
        return self

