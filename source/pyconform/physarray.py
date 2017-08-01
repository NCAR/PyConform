"""
Physical Array Class

This module contains the PhysArray class, which is the primary object passed along
edges of a Data Flow graph.  It is a subclass of the Numpy MaskedArray, and carries with
its data the units associated with the data, the dimensions associated with each axis of
the data.

Copyright 2017, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.indexing import align_index
from cf_units import Unit
from os import linesep
from operator import mul, div

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


#=======================================================================================================================
# getdata
#=======================================================================================================================
def getdata(obj):
    """
    Retrieve the ndarray data associated with an object
    """
    return numpy.ma.getdata(obj)


#=======================================================================================================================
# getmask
#=======================================================================================================================
def getmask(obj):
    """
    Retrieve the mask associated with an object
    """
    return numpy.ma.getmask(obj)


#=======================================================================================================================
# getname
#=======================================================================================================================
def getname(obj):
    """
    Retrieve the string name associated with an object
    """
    if isinstance(obj, PhysArray):
        return obj.name
    else:
        return str(obj).replace(linesep, ' ')


#=======================================================================================================================
# getunits
#=======================================================================================================================
def getunits(obj):
    """
    Retrieve the Unit associated with the object
    """
    if isinstance(obj, PhysArray):
        return obj.units
    else:
        return Unit(1)


#=======================================================================================================================
# getdimensions
#=======================================================================================================================
def getdimensions(obj):
    """
    Retrieve the dimensions-tuple associated with the object
    """
    if isinstance(obj, PhysArray):
        return obj.dimensions
    else:
        return tuple(reversed(range(len(numpy.shape(obj)))))


#=======================================================================================================================
# getpositive
#=======================================================================================================================
def getpositive(obj):
    """
    Retrieve the positive attribute associated with the object
    """
    if isinstance(obj, PhysArray):
        return obj.positive
    else:
        return None


#===================================================================================================
# PhysArray
#===================================================================================================
class PhysArray(numpy.ma.MaskedArray):
    """
    A PhysArray is an array of data with both units and dimensions

    The PhysArray is deried from the Numpy MaskedArray and is the basic object
    along the edges of a Data Flow graph.
    """

    def __new__(cls, indata, mask=None, name=None, units=None, dimensions=None, positive=''):
        obj = numpy.ma.asarray(indata).view(cls)
        if obj.dtype.char in ('S', 'U'):
            return CharArray(indata, name=name, dimensions=dimensions)
        
        # Add the mask if specified
        if mask is not None:
            obj.mask = mask

        # Store a name associated with the object
        if name is None:
            obj.name = getname(indata)
        else:
            obj.name = name

        # Store units of the data
        if units is None:
            obj.units = getunits(indata)
        else:
            obj.units = units

        # Store dimension names associated with each axis
        if dimensions is None:
            obj.dimensions = getdimensions(indata)
        else:
            obj.dimensions = dimensions

        # Set the positive direction for the data
        if positive == '':
            obj.positive = getpositive(indata)
        else:
            obj.positive = positive

        return obj

    def __repr__(self):
        datstr = super(PhysArray, self).__str__().replace(linesep, ' ')
        posstr = '' if self.positive is None else ', positive={!r}'.format(self.positive)
        return ('{!s}(data={!s}, fill_value={!s}, units={!r}, name={!r}, dimensions='
                '{!s}{})').format(self.__class__.__name__, datstr, self.fill_value,
                                  str(self.units), self.name, self.dimensions, posstr)

    @property
    def name(self):
        """String name for the data"""
        return self._optinfo['name']

    @name.setter
    def name(self, nm):
        """String name for the data"""
        self._optinfo['name'] = nm

    def __str__(self):
        return '{}'.format(self.name)

    @property
    def units(self):
        """Units of the data"""
        return self._optinfo['units']

    @units.setter
    def units(self, units):
        """Units of the data"""
        self._optinfo['units'] = units if isinstance(units, Unit) else Unit(units)
    
    @staticmethod
    def _safe_convert_(obj, units1, units2):
        # Because netcdftime datetime conversion always returns an NDArray, even if the
        # original object is a subclass of NDArray, we have to wrap the convert function
        # to safely preserve the object type...  sigh.
        u1 = units1 if isinstance(units1, Unit) else Unit(units1)
        u2 = units2 if isinstance(units2, Unit) else Unit(units2)
        if isinstance(obj, PhysArray):
            new_array = numpy.ma.MaskedArray(units1.convert(obj.data, units2), mask=obj.mask, dtype=obj.dtype)
            u1_str = '{}'.format(u1) + ('|{}'.format(u1.calendar) if u1.calendar else '')
            u2_str = '{}'.format(u2) + ('|{}'.format(u2.calendar) if u2.calendar else '')
            new_name = "convert({}, from={}, to={})".format(obj.name, u1_str, u2_str)
            return PhysArray(new_array, name=new_name, units=u2, dimensions=obj.dimensions)
        elif isinstance(obj, numpy.ma.MaskedArray):
            return numpy.ma.MaskedArray(u1.convert(obj.data, u2), mask=obj.mask, dtype=obj.dtype)
        else:
            return u1.convert(obj, u2)

    def convert(self, units):
        """
        Return a new PhysArray with new units
        
        Parameters:
            units (Unit): The new units to which to convert the PhysArray
        """
        uunit = units if isinstance(units, Unit) else Unit(units)
        if self.units == uunit:
            return self
        elif self.units.is_convertible(uunit):
            return PhysArray._safe_convert_(self, self.units, uunit)
        else:
            raise UnitsError('Cannot convert units {!r} to {!r}'.format(self.units, uunit))

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
    
    def transpose(self, *dims):
        """
        Return a new PhysArray with dimensions transposed in the order given
        
        Does nothing if no transpose is necesary
        
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
        if new_dims == self.dimensions:
            return self
        else:
            old_dims_str = ','.join(self.dimensions)
            new_dims_str = ','.join(new_dims)
            new_name = 'transpose({}, from=[{}], to=[{}])'.format(self.name, old_dims_str, new_dims_str)
            return PhysArray(super(PhysArray, self).transpose(*axes), dimensions=new_dims, name=new_name)

    @property
    def positive(self):
        """Positive direction (up or down) for the data"""
        return self._optinfo['positive']

    @positive.setter
    def positive(self, pos):
        """Positive direction (up or down) for the data"""
        if isinstance(pos, basestring):
            strpos = str(pos).lower()
            if strpos not in ['up', 'down']:
                raise ValueError('Positive attribute must be up/down or None, not {!r}'.format(pos))
            pos = strpos
        elif pos is not None:
            raise ValueError('Positive attribute must be up/down or None, not {!r}'.format(pos))
        self._optinfo['positive'] = pos

    def flip(self):
        """
        Flip the direction of the positive attribute, if set, and correspondingly multiply by -1
        
        Does nothing if the positive attribute is not set (i.e., equals None)
        """
        if self.positive is not None:
            nm = self.name
            self *= -1
            self.positive = 'up' if self.positive == 'down' else 'down'
            self.name = '{}({})'.format(self.positive, nm)
        return self

    def up(self):
        """
        Set the direction of the positive attribute to 'up' and multiply by -1, if necessary
        
        Only multiplies by -1 if the positive attribute is already set to 'down'.
        """
        if self.positive is None:
            self.positive = 'up'
            self.name = 'up({})'.format(self.name)
        elif self.positive == 'down':
            self.flip()
        return self

    def down(self):
        """
        Set the direction of the positive attribute to 'down' and multiply by -1, if necessary
        
        Only multiplies by -1 if the positive attribute is already set to 'up'.
        """
        if self.positive is None:
            self.positive = 'down'
            self.name = 'down({})'.format(self.name)
        elif self.positive == 'up':
            self.flip()
        return self

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
    
    def _broadcast_(self, other):
        for d in set(self.dimensions).intersection(set(other.dimensions)):
            if self.shape[self.dimensions.index(d)] != other.shape[other.dimensions.index(d)]:
                raise DimensionsError('Cannot broadcast arrays with dimensions {} and '
                                      '{}'.format(self.dimensions, other.dimensions))
        self_dims = self.dimensions + tuple(d for d in other.dimensions if d not in self.dimensions)
        self.shape = tuple(self.shape[self.dimensions.index(d)] if d in self.dimensions else 1 for d in self_dims)
        other_dims = other.dimensions + tuple(d for d in self.dimensions if d not in other.dimensions)
        other.shape = tuple(other.shape[other.dimensions.index(d)] if d in other.dimensions else 1 for d in other_dims)
        if len(self.dimensions) > 0 and self_dims != self.dimensions:
            fromdims = ','.join(self.dimensions)
            todims = ','.join(self_dims)
            self.name = 'broadcast({}, from=[{}], to=[{}])'.format(self.name, fromdims, todims)
        self.dimensions = self_dims
        if len(other.dimensions) > 0 and other_dims != other.dimensions:
            fromdims = ','.join(other.dimensions)
            todims = ','.join(other_dims)
            other.name = 'broadcast({}, from=[{}], to=[{}])'.format(other.name, fromdims, todims)
        other.dimensions = other_dims
        return other.transpose(self_dims)

    def _match_positive_(self, other):
        if self.positive == other.positive:
            pass
        elif self.positive is None:
            if other.positive == 'up':
                self.up()
            elif other.positive == 'down':
                self.down()
        elif other.positive is None:
            if self.positive == 'up':
                other.up()
            elif self.positive == 'down':
                other.down()
        else:
            other.flip()
    
    def _check_inplace_(self, other):
        other = PhysArray(other)
        sdims = set(self.dimensions)
        odims = set(other.dimensions)
        if not odims.issubset(sdims):
            for d in odims - sdims:
                if other.shape[other.dimensions.index(d)] > 1:
                    raise DimensionsError(('Cannot broadcast dimensions {} to {} in inplace operation'
                                           '').format(other.dimensions, self.dimensions))

    def _add_sub_init_(self, other):
        other = self._broadcast_(PhysArray(other)).convert(self.units)
        self._match_positive_(other)
        return other
        
    def __add__(self, other):
        result = PhysArray(self)
        other = result._add_sub_init_(other)
        return PhysArray(super(PhysArray, result).__add__(other), name='({}+{})'.format(result.name, other.name),
                         units=result.units, positive=result.positive)

    def __radd__(self, other):
        return PhysArray(other).__add__(self)
    
    def __iadd__(self, other):
        self._check_inplace_(other)
        other = self._add_sub_init_(other)
        super(PhysArray, self).__iadd__(other)
        self.name = '({}+{})'.format(self.name, other.name)
        return self

    def __sub__(self, other):
        result = PhysArray(self)
        other = result._add_sub_init_(other)
        return PhysArray(super(PhysArray, result).__sub__(other), name='({}-{})'.format(result.name, other.name),
                         units=result.units, positive=result.positive)

    def __rsub__(self, other):
        return PhysArray(other).__sub__(self)

    def __isub__(self, other):
        self._check_inplace_(other)
        other = self._add_sub_init_(other)
        super(PhysArray, self).__isub__(other)
        self.name = '({}-{})'.format(self.name, other.name)
        return self

    def _units_op_(self, val, op):
        sunits = self.units
        try:
            units = op(sunits, val)
        except:
            opnm = str(op.__name__)
            raise UnitsError('Operator {!r} failed with units: {}, {}'.format(opnm, sunits, val))
        return units

    def _mul_div_init_(self, other):
        other = self._broadcast_(PhysArray(other))
        self._match_positive_(other)
        return other

    def __mul__(self, other):
        result = PhysArray(self)
        other = result._mul_div_init_(other)
        return PhysArray(super(PhysArray, result).__mul__(other), name='({}*{})'.format(result.name, other.name),
                         units=self._units_op_(other.units, mul), positive=result.positive)

    def __rmul__(self, other):
        return PhysArray(other).__mul__(self)

    def __imul__(self, other):
        self._check_inplace_(other)
        other = self._mul_div_init_(other)
        super(PhysArray, self).__imul__(other)
        self.name = '({}*{})'.format(self.name, other.name)
        self.units = self._units_op_(other.units, mul)
        return self

    def invert(self):
        """Return a new PhysArray with the value of the array inverted (1/value)"""
        return PhysArray(1.0 / self.data, dimensions=self.dimensions, units=self.units.invert(),
                         name='(1/{!s})'.format(self), positive=self.positive)

    def __div__(self, other):
        result = PhysArray(self)
        other = result._mul_div_init_(other)
        return PhysArray(super(PhysArray, result).__div__(other), name='({}/{})'.format(result.name, other.name),
                         units=self._units_op_(other.units, div), positive=result.positive)

    def __rdiv__(self, other):
        return PhysArray(other).__div__(self)

    def __idiv__(self, other):
        self._check_inplace_(other)
        other = self._mul_div_init_(other)
        super(PhysArray, self).__idiv__(other)
        self.name = '({}/{})'.format(self.name, other.name)
        self.units = self._units_op_(other.units, div)
        return self

    def __floordiv__(self, other):
        result = PhysArray(self)
        other = result._mul_div_init_(other)
        return PhysArray(super(PhysArray, result).__floordiv__(other), name='({}//{})'.format(result.name, other.name),
                         units=self._units_op_(other.units, div), positive=result.positive)

    def __rfloordiv__(self, other):
        return PhysArray(other).__floordiv__(self)

    def __ifloordiv__(self, other):
        self._check_inplace_(other)
        other = self._mul_div_init_(other)
        super(PhysArray, self).__ifloordiv__(other)
        self.name = '({}//{})'.format(self.name, other.name)
        self.units = self._units_op_(other.units, div)
        return self

    def __truediv__(self, other):
        return self.__div__(other)

    def __rtruediv__(self, other):
        return PhysArray(other).__truediv__(self)

    def __itruediv__(self, other):
        return self.__idiv__(other)

    def __mod__(self, other):
        raise NotImplementedError('Modulus of a PhysArray is not defined.')

    def __rmod__(self, other):
        return PhysArray(other).__mod__(self)

    def __imod__(self, other):
        raise NotImplementedError('Modulus of a PhysArray is not defined.')

    def _check_exponent_(self, exp):
        if exp.dimensions != ():
            raise DimensionsError('Exponents must be scalar: {}'.format(exp))
        if exp.positive is not None:
            raise ValueError('Exponents cannot have positive attribute: {}'.format(exp))
        if not exp.units.is_convertible(Unit(1)):
            raise UnitsError('Exponents cannot have physical units')
        return exp.convert(Unit(1))

    def __pow__(self, other):
        other = self._check_exponent_(PhysArray(other))
        positive = None if other.data % 2 == 0 else self.positive
        return PhysArray(super(PhysArray, self).__pow__(other), units=self.units**other,
                         name='({!s}**{!s})'.format(self, other), positive=positive)

    def __rpow__(self, other):
        return PhysArray(other).__pow__(self)

    def __ipow__(self, other):
        other = self._check_exponent_(PhysArray(other))
        super(PhysArray, self).__ipow__(other)
        self.name='({!s}**{!s})'.format(self, other)
        self.units **= other
        self.positive = None if other.data % 2 == 0 else self.positive
        return self


#=======================================================================================================================
# CharArray
#=======================================================================================================================
class CharArray(PhysArray):
    """
    Special kind of PhysArray to deal with string arrays
    """
    
    def __new__(cls, indata, name=None, dimensions=None):
        arr = numpy.asarray(indata, dtype='U')
        if len(arr.shape) == 0:
            arr = arr.reshape(1).view('U1')
        else:
            strlen = arr.dtype.itemsize / 4
            shape = arr.shape + (strlen,)
            arr = arr.view('U1').reshape(shape)
        obj = numpy.ma.masked_where(arr == '', arr).view(cls)
        obj.fill_value = ''
        
        # Store a name associated with the object
        if name is None:
            ndat = arr.view('U{}'.format(arr.shape[-1])).reshape(arr.shape[:-1])
            obj.name = getname(ndat)
        else:
            obj.name = name

        # Store units of the data
        obj.units = Unit('no unit')

        # Store dimension names associated with each axis
        if dimensions is None:
            obj.dimensions = getdimensions(arr)
        else:
            obj.dimensions = dimensions

        # Set the positive direction for the data
        obj.positive = None

        return obj

    def __repr__(self):
        prndat = self.data.view('U{}'.format(self.shape[-1])).reshape(self.shape[:-1])
        datstr = str(prndat).replace(linesep, ' ')
        posstr = '' if self.positive is None else ', positive={!r}'.format(self.positive)
        return ('{!s}(data={!s}, name={!r}, dimensions='
                '{!s}{})').format(self.__class__.__name__, datstr, self.name, self.dimensions, posstr)
    @property
    def units(self):
        """Units of the data"""
        return self._optinfo['units']
        
    @units.setter
    def units(self, units):
        new_units = units if isinstance(units, Unit) else Unit(units)
        if not new_units.is_no_unit():
            raise UnitsError('CharArrays cannot have units.')
        self._optinfo['units'] = new_units

    @property
    def positive(self):
        """Positive direction (up or down) for the data"""
        return self._optinfo['positive']

    @positive.setter
    def positive(self, pos):
        if pos is not None:
            raise ValueError('CharArrays cannot be assigned a positive attribute')
        self._optinfo['positive'] = pos

    def convert(self, units):
        try:
            new_self = PhysArray.convert(self, units)
        except UnitsError:
            raise UnitsError('CharArrays do not have units and cannot be converted to units {}'.format(units))
        return new_self

    def transpose(self, *dims):
        if dims[-1] != self.dimensions[-1]:
            raise DimensionsError('The last dimension of a CharArray must always be the string length.  '
                                  'Cannot be transposed.')
        return PhysArray.transpose(self, *dims)

    def invert(self):
        raise NotImplementedError('CharArrays cannot be inverted')
