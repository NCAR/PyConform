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
from operator import mul, div, pow

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

    def __new__(cls, inarray, name=None, units=None, dimensions=None, initshape=None):
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

        # Initial shape
        if initshape is None:
            if 'initshape' not in obj._optinfo:
                obj._optinfo['initshape'] = numpy.shape(inarray)
        else:
            obj.initshape = initshape

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
    def initshape(self):
        """Initial size of each dimension of the data"""
        return self._optinfo['initshape']

    @initshape.setter
    def initshape(self, shape):
        """Initial size of each dimension of the data"""
        if not isinstance(shape, tuple):
            raise TypeError('Initial shape must be a tuple')
        if len(shape) != len(self.shape):
            raise ValueError('Initial shape must have same length as shape')
        self._optinfo['initshape'] = shape

    def __getitem__(self, index):
        idx = align_index(index, self.dimensions)
        if len(idx) == 0:
            return self
        else:
            dimensions = tuple(d for i, d in zip(idx, self.dimensions) if isinstance(i, slice))
            if dimensions != self.dimensions:
                shape0 = tuple(s for i, s in zip(idx, self.initshape) if isinstance(i, slice))
                return PhysArray(super(PhysArray, self).__getitem__(idx),
                                 dimensions=dimensions, initshape=shape0)
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
    def _transpose_name_(name, idims, odims):
        idim_str = ','.join(idims)
        odim_str = ','.join(odims)
        return 'transpose({}, from=[{}], to=[{}])'.format(name, idim_str, odim_str)

    @staticmethod
    def _safe_convert_(obj, units1, units2):
        # Because netcdftime datetime conversion always returns an NDArray, even if the
        # original object is a subclass of NDArray, we have to wrap the convert function
        # to safely preserve the object type...  sigh.
        if isinstance(obj, PhysArray):
            new_array = numpy.ma.MaskedArray(units1.convert(obj.data, units2),
                                             mask=obj.mask, dtype=obj.dtype)
            new_name = PhysArray._convert_name_(obj.name, units1, units2)
            return PhysArray(new_array, name=new_name, units=units2,
                             dimensions=obj.dimensions, initshape=obj.initshape)
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

    def transpose(self, *dims):
        """
        Return a new PhysArray with dimensions transposed in the order given
        
        Parameters:
            dims (tuple): Tuple of dimension names in the new order
        """
        if len(dims) == 1 and isinstance(dims[0], tuple):
            dims = dims[0]
        if set(dims) == set(self.dimensions):
            new_dims = tuple(dims)
            new_shp0 = tuple(self.initshape[self.dimensions.index(d)] for d in dims)
            axes = tuple(self.dimensions.index(d) for d in dims)
        elif set(dims) == set(range(self.ndim)):
            new_dims = tuple(self.dimensions[i] for i in dims)
            new_shp0 = tuple(self.initshape[i] for i in dims)
            axes = dims
        else:
            raise DimensionsError(('Cannot transpose dimensions/axes {} to '
                                   '{}').format(self.dimensions, dims))
        return PhysArray(super(PhysArray, self).transpose(*axes), dimensions=new_dims,
                         name=PhysArray._transpose_name_(self.name, self.dimensions, new_dims),
                         initshape=new_shp0)

    def _transpose_scalar_check_(self, obj):
        if self.dimensions == () or obj.dimensions == ():
            return self
        else:
            return self.transpose(obj.dimensions)

    def _return_dim_shape_(self, other):
        if self.dimensions == ():
            return other.dimensions, other.initshape
        else:
            return self.dimensions, self.initshape

    def __add__(self, other):
        other = PhysArray(other)._convert_scalar_check_(self.units)._transpose_scalar_check_(self)
        dims, initshape = self._return_dim_shape_(other)
        return PhysArray(super(PhysArray, self).__add__(other), dimensions=dims, initshape=initshape,
                         units=self.units, name='({}+{})'.format(self.name, other.name))

    def __radd__(self, other):
        return PhysArray(other).__add__(self)

    def __iadd__(self, other):
        other = PhysArray(other)._convert_scalar_check_(self.units)._transpose_scalar_check_(self)
        super(PhysArray, self).__iadd__(other)
        self.name = '({}+{})'.format(self.name, other.name)
        self.dimensions, self.initshape = self._return_dim_shape_(other)
        return self

    def __sub__(self, other):
        other = PhysArray(other)._convert_scalar_check_(self.units)._transpose_scalar_check_(self)
        dims, initshape = self._return_dim_shape_(other)
        return PhysArray(super(PhysArray, self).__sub__(other), dimensions=dims, initshape=initshape,
                         units=self.units, name='({}-{})'.format(self.name, other.name))

    def __rsub__(self, other):
        return PhysArray(other).__sub__(self)

    def __isub__(self, other):
        other = PhysArray(other)._convert_scalar_check_(self.units)._transpose_scalar_check_(self)
        super(PhysArray, self).__isub__(other)
        self.name = '({}-{})'.format(self.name, other.name)
        self.dimensions, self.initshape = self._return_dim_shape_(other)
        return self

    def _op_units_(self, val, op):
        sunits = self.units
        try:
            units = op(sunits, val)
        except:
            opnm = str(op.__name__)
            raise UnitsError('Operator {!r} failed with units: {}, {}'.format(opnm, sunits, val))
        return units

    def __mul__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        units = self._op_units_(other.units, mul)
        dims, initshape = self._return_dim_shape_(other)
        return PhysArray(super(PhysArray, self).__mul__(other), dimensions=dims, initshape=initshape,
                         units=units, name='({}*{})'.format(self.name, other.name))

    def __rmul__(self, other):
        return PhysArray(other).__mul__(self)

    def __imul__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        super(PhysArray, self).__imul__(other)
        self.name = '({}*{})'.format(self.name, other.name)
        self.units = self._op_units_(other.units, mul)
        self.dimensions, self.initshape = self._return_dim_shape_(other)
        return self

    def __div__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        units = self._op_units_(other.units, div)
        dims, initshape = self._return_dim_shape_(other)
        return PhysArray(super(PhysArray, self).__div__(other), dimensions=dims, initshape=initshape,
                         units=units, name='({}/{})'.format(self.name, other.name))

    def __rdiv__(self, other):
        return PhysArray(other).__div__(self)

    def __idiv__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        super(PhysArray, self).__idiv__(other)
        self.name = '({}/{})'.format(self.name, other.name)
        self.units = self._op_units_(other.units, div)
        self.dimensions, self.initshape = self._return_dim_shape_(other)
        return self

    def __floordiv__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        units = self._op_units_(other.units, div)
        dims, initshape = self._return_dim_shape_(other)
        return PhysArray(super(PhysArray, self).__floordiv__(other), dimensions=dims, initshape=initshape,
                         units=units, name='({}//{})'.format(self.name, other.name))

    def __rfloordiv__(self, other):
        return PhysArray(other).__floordiv__(self)

    def __ifloordiv__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        super(PhysArray, self).__ifloordiv__(other)
        self.name = '({}//{})'.format(self.name, other.name)
        self.units = self._op_units_(other.units, div)
        self.dimensions, self.initshape = self._return_dim_shape_(other)
        return self

    def __truediv__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        units = self._op_units_(other.units, div)
        dims, initshape = self._return_dim_shape_(other)
        return PhysArray(super(PhysArray, self).__truediv__(other), dimensions=dims, initshape=initshape,
                         units=units, name='({}/{})'.format(self.name, other.name))

    def __rtruediv__(self, other):
        return PhysArray(other).__truediv__(self)

    def __itruediv__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        super(PhysArray, self).__itruediv__(other)
        self.name = '({}/{})'.format(self.name, other.name)
        self.units = self._op_units_(other.units, div)
        self.dimensions, self.initshape = self._return_dim_shape_(other)
        return self

    def __mod__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        dims, initshape = self._return_dim_shape_(other)
        return PhysArray(super(PhysArray, self).__mod__(other), dimensions=dims, initshape=initshape,
                         name='({}%{})'.format(self.name, other.name))

    def __rmod__(self, other):
        return PhysArray(other).__mod__(self)

    def __imod__(self, other):
        other = PhysArray(other)._transpose_scalar_check_(self)
        super(PhysArray, self).__imod__(other)
        self.name = '({}%{})'.format(self.name, other.name)
        self.dimensions, self.initshape = self._return_dim_shape_(other)
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
                         name='({}**{})'.format(self.name, other.name))

    def __rpow__(self, other):
        return PhysArray(other).__pow__(self)

    def __ipow__(self, other):
        other = PhysArray(other)._convert_scalar_check_(Unit(1))
        if other.dimensions != ():
            raise DimensionsError('Exponents must be scalar: {}'.format(other))
        super(PhysArray, self).__ipow__(other)
        self.units = self._op_units_(other, pow)
        self.name = '({}**{})'.format(self.name, other.name)
        return self
