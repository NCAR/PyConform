#!/usr/bin/env python

from Ngl import vinth2p
from pyconform.physarray import PhysArray
from pyconform.functions import Function, UnitsError, DimensionsError
from cf_units import Unit
from numpy import resize

#===================================================================================================
# PositiveUpFunction
#===================================================================================================
class PositiveUpFunction(Function):
    key = 'up'
    
    def __call__(self, data):
        if isinstance(data, PhysArray):
            return data.up()
        else:
            return PhysArray(data).up()


#===================================================================================================
# PositiveDownFunction
#===================================================================================================
class PositiveDownFunction(Function):
    key = 'down'
    
    def __call__(self, data):
        if isinstance(data, PhysArray):
            return data.down()
        else:
            return PhysArray(data).down()


#===================================================================================================
# ChangeUnitsFunction
#===================================================================================================
class ChangeUnitsFunction(Function):
    key = 'chunits'
    
    def __call__(self, data, units):
        if isinstance(data, PhysArray):
            data.units = units
            return data
        else:
            return PhysArray(data, units=units)


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
        
        if len(datai.dimensions) != 3 or len(datai.dimensions) != 4:
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
                
        _plevo = plevo.convert('mb')
        _p0 = p0.convert('mb')
        _psfc = psfc.convert('Pa')
        
        ilev = datai.dimensions.index(dlevi)

        new_dims = [d for d in datai.dimensions]
        new_dims[ilev] = dlevo
        new_dims = tuple(new_dims)
        
        new_name = 'vinth2p({}, plevs={})'.format(datai.name, plevo.name)

        return PhysArray(vinth2p(datai.data, hbcofa.data, hbcofb.data, plevo.data,
                                 psfc.data, intyp, p0.data, 1, bool(ixtrp)), name=new_name,
                         dimensions=new_dims, units=datai.units, positive=datai.positive)
