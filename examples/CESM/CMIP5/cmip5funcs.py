#!/usr/bin/env python

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


#===============================================================================
# VertInterpFunction
#===============================================================================
class VertInterpFunction(Function):
    key = 'vinth2p'
    # datai, hbcofa, hbcofb, plevo, psfc, p0


    def __call__(self, datai, ha, hb, polevs, ps, p0):
        
        ishape = datai.shape
        levidx = len(ishape) - 3
        nolevs = polevs.size
        oshape = tuple(nolevs if i == levidx else n for i,n in enumerate(ishape))
        
        return resize(datai, oshape)
    
    @staticmethod
    def units(diunits, haunits, hbunits, pounits, psunits, p0units):
        umb = Unit('mb')
        upa = Unit('Pa')
        
        diu = diunits if isinstance(diunits, Unit) else Unit(1)
        
        pou = pounits if isinstance(pounits, Unit) else Unit(1)
        pouret = None
        if pou != umb:
            if pou.is_convertible(umb):
                pouret = umb
            else:
                raise UnitsError('Cannot convert units')
        
        psu = psunits if isinstance(psunits, Unit) else Unit(1)
        psuret = None
        if psu != upa:
            if psu.is_convertible(upa):
                psuret = upa
            else:
                raise UnitsError('Cannot convert units')

        p0u = opunits if isinstance(p0units, Unit) else Unit(1)
        p0uret = None
        if p0u != umb:
            if p0u.is_convertible(umb):
                p0uret = umb
            else:
                raise UnitsError('Cannot convert units')

        return diu, (None, None, None, pouret, psuret, p0uret)

    @staticmethod
    def dimensions(didims, hadims, hbdims, podims, psdims, p0dims):
        did = didims if isinstance(didims, tuple) else ()
        if len(did) != 3 and len(did) != 4:
            raise DimensionsError('vinth2p only accepts 3 or 4 dimensional data')
        
        had = hadims if isinstance(hadims, tuple) else ()
        if len(had) != 1:
            raise DimensionsError('Hybrid coefficient a not 1D')
        ilevd = had[0]
        hbd = hbdims if isinstance(hbdims, tuple) else ()
        if len(hbd) != 1:
            raise DimensionsError('Hybrid coefficient b not 1D')
        if hbd[0] != ilevd:
            raise DimensionsError('Hybrid coefficients a and b '
                                  'have different dimensions')

        p0d = p0dims if isinstance(p0dims, tuple) else ()
        if len(p0d) != 0:
            raise DimensionsError('Reference pressure a not scalar')

        pod = podims if isinstance(podims, tuple) else ()
        if len(pod) != 1:
            raise DimensionsError('Output pressure levels not 1D')
        olevd = pod[0]
        
        psd = psdims if isinstance(psdims, tuple) else ()
        for d in psd:
            if d not in did:
                raise DimensionsError(('Surface pressure dimension {0} not '
                                       'found in input data '
                                       'dimensions').format(d))
        did_not_in_psd = tuple(d for d in did if d not in psd)
        if did_not_in_psd != had:
            print did_not_in_psd
            raise DimensionsError('Input data dimensions do not match hybrid '
                                  'coefficients in vertical interpolation')
        
        levidx = did.index(ilevd)
        if levidx != len(did) - 3:
            raise DimensionsError('Input data level dimension must be second')
        
        didret = [d for d in did]
        didret[levidx] = olevd
        didret = tuple(didret)

        return didret, (None, None, None, None, None, None)
    
