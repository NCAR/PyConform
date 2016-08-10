"""
Data Array Class

This module contains the DataArray class, which is the primary object passed along
edges of a Data Flow graph.  It is a subclass of the Numpy MaskedArray, and carries with
its data the units associated with the data, the dimensions associated with each axis of
the data.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from __future__ import print_function
from pyconform.indexing import align_index
from cf_units import Unit

import numpy


#===================================================================================================
# DataArray
#===================================================================================================
class DataArray(numpy.ma.MaskedArray):
    """
    A DataArray is the basic object passed along the edges of a Data Flow graph
    
    Derived from Numpy MaskedArray, the DataArray contains additional information
    about the array data, including cfunits and dimensions.
    """

    def __new__(cls, inarray, cfunits=None, dimensions=None):
        obj = numpy.ma.asarray(inarray).view(cls)

        if cfunits is None:
            if 'cfunits' not in obj._optinfo:
                obj._optinfo['cfunits'] = Unit(1)
        elif isinstance(cfunits, Unit):
            obj._optinfo['cfunits'] = cfunits
        else:
            obj._optinfo['cfunits'] = Unit(cfunits)

        if dimensions is None:
            if 'dimensions' not in obj._optinfo:
                obj._optinfo['dimensions'] = tuple([None] * len(obj.shape))
        elif isinstance(dimensions, tuple):
            if len(dimensions) != len(obj.shape):
                raise ValueError(('Dimensions {} length does not match DataArray with {} '
                                  'axes').format(dimensions, len(obj.shape)))
            obj._optinfo['dimensions'] = dimensions
        else:
            raise TypeError(('Cannot set DataArray object with dimensions of type '
                             '{}').format(type(dimensions)))

        return obj

    def __repr__(self):
        return ('{!s}(data = {!s}, mask = {!s}, fill_value = {!s}, cfunits = {!r}, '
                'dimensions = {!s})').format(self.__class__.__name__, self.data, self.mask,
                                             self.fill_value, str(self.cfunits), self.dimensions)

    @property
    def cfunits(self):
        return self._optinfo['cfunits']

    @property
    def dimensions(self):
        return self._optinfo['dimensions']

    def __getitem__(self, index):
        if index == () and self.dimensions == ():
            return self
        else:
            return super(DataArray, self).__getitem__(align_index(index, self.dimensions))
