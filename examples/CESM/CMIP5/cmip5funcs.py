#!/usr/bin/env python

from Ngl import vinth2p
from pyconform.physarray import PhysArray, UnitsError, DimensionsError
from pyconform.functions import Function
from cf_units import Unit
from numpy import diff
        
        
#===================================================================================================
# BoundsFunction
#===================================================================================================
class BoundsFunction(Function):
    key = 'bounds'
    
    def __call__(self, data, bdim='bnds', location=1, endpoints=1):
        if not isinstance(data, PhysArray):
            raise TypeError('bounds: data must be a PhysArray')
        if not isinstance(bdim, basestring):
            raise TypeError('bounds: bounds dimension name must be a string')
        if location not in [0,1,2]:
            raise ValueError('bounds: location must be 0, 1, or 2')
        if len(data.dimensions) != 1:
            raise DimensionsError('bounds: data can only be 1D')
        mod_end = bool(endpoints)

        bnds = PhysArray([1, 1], dimensions=(bdim,))
        new_data = PhysArray(data * bnds, name='bounds({})'.format(data.name))
        if len(new_data) == 0:
            return new_data
        dx = diff(data.data)
        if location == 0:
            new_data[:-1,1] = data.data[:-1] + dx
            if mod_end:
                new_data[-1,1] = data.data[-1] + dx[-1]
        elif location == 1:
            hdx = 0.5 * dx
            new_data[1:,0] = data.data[1:] - hdx
            new_data[:-1,1] = data.data[:-1] + hdx
            if mod_end:
                new_data[0,0] = data.data[0] - hdx[0]
                new_data[-1,1] = data.data[-1] + hdx[-1]
        elif location == 2:
            new_data[1:,0] = data.data[1:] - dx
            if mod_end:
                new_data[0,0] = data.data[0] - dx[0]
        return new_data


#===================================================================================================
# VertInterpFunction
#===================================================================================================
class VertInterpFunction(Function):
    key = 'vinth2p'

    def __call__(self, datai, hbcofa, hbcofb, plevo, psfc, p0, intyp=1, ixtrp=0):
        if (not isinstance(datai, PhysArray) or not isinstance(hbcofa, PhysArray) or
            not isinstance(hbcofb, PhysArray) or not isinstance(plevo, PhysArray) or
            not isinstance(psfc, PhysArray) or not isinstance(p0, PhysArray)):
            raise TypeError('vinth2p: arrays must be PhysArrays')
        
        if len(datai.dimensions) != 3 and len(datai.dimensions) != 4:
            raise DimensionsError('vinth2p: interpolated data must be 3D or 4D')
        if len(hbcofa.dimensions) != 1 or len(hbcofb.dimensions) != 1:
            raise DimensionsError('vinth2p: hybrid a/b coefficients must be 1D')
        if len(plevo.dimensions) != 1:
            raise DimensionsError('vinth2p: output pressure levels must be 1D')
        if len(p0.dimensions) != 0:
            raise DimensionsError('vinth2p: reference pressure must be scalar')

        dlevi = hbcofa.dimensions[0]
        if dlevi != hbcofb.dimensions[0]:
            raise DimensionsError('vinth2p: hybrid a/b coefficients do not have same dimensions')
        dlevo = plevo.dimensions[0]
        
        for d in psfc.dimensions:
            if d not in datai.dimensions:
                raise DimensionsError(('vinth2p: surface pressure dimension {!r} not found '
                                       'in input data dimensions').format(d))
        dlat, dlon = psfc.dimensions[-2:]

        if (dlevi, dlat, dlon) != datai.dimensions[-3:]:
            raise DimensionsError(('vinth2p: input data dimensions {} inconsistent with the '
                                   'dimensions of surface pressure {} and hybrid coefficients {}'
                                   '').format(datai.dimensions, psfc.dimensions, hbcofa.dimensions))
                
        _plevo = plevo.convert('mbar')
        _p0 = p0.convert('mbar')
        _psfc = psfc.convert('Pa')
        
        ilev = datai.dimensions.index(dlevi)

        new_dims = [d for d in datai.dimensions]
        new_dims[ilev] = dlevo
        new_dims = tuple(new_dims)
        
        new_name = 'vinth2p({}, plevs={})'.format(datai.name, plevo.name)

        return PhysArray(vinth2p(datai.data, hbcofa.data, hbcofb.data, plevo.data,
                                 psfc.data, intyp, p0.data, 1, bool(ixtrp)), name=new_name,
                         dimensions=new_dims, units=datai.units, positive=datai.positive)
