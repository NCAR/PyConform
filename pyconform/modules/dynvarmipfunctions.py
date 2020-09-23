"""
DynVarMIP Diagnostic Function Classes

Copyright 2017-2020, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import numpy as np

import pyconform.modules.dynvarmipdiags as dvmd
from pyconform.functions import Function
from pyconform.physarray import PhysArray


#=========================================================================
# DynVarMIPFunction
#=========================================================================
class DynVarMIPFunction(Function):
    key = 'dynvarmipfunc'

    def __init__(self, time, lev, lat, *args):
        super(DynVarMIPFunction, self).__init__(time, lev, lat, *args)
        self._dynvarmip_func = None
        self._units = None
        self._positive = None

    def __getitem__(self, index):
        args = [np.ma.asarray(arg[index]) for arg in self.arguments]
        arg_names = ','.join([arg.name for arg in args])
        data = self._dynvarmip_func(*args)
        name = '{}({})'.format(self.key, arg_names)
        return PhysArray(data, name=name, dimensions=args[-1].dimensions,
                         units=self._units, positive=self._positive)


#=========================================================================
# wtemDynVarMIPFunction
#=========================================================================
class wtemDynVarMIPFunction(DynVarMIPFunction):
    key = 'dynvarmip_wtem'

    def __init__(self, time, lev, lat, wzm, vthzm, thzm):
        super(wtemDynVarMIPFunction, self).__init__(
            time, lev, lat, wzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.wtem
        self._units = 'm s-1'
        self._positive = None


#=========================================================================
# utendwtemDynVarMIPFunction
#=========================================================================
class utendwtemDynVarMIPFunction(DynVarMIPFunction):
    key = 'dynvarmip_utendwtem'

    def __init__(self, time, lev, lat, uzm, wzm, vthzm, thzm):
        super(utendwtemDynVarMIPFunction, self).__init__(
            time, lev, lat, uzm, wzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.utendwtem
        self._units = 'm s-1 d-1'
        self._positive = None


#=========================================================================
# vtemDynVarMIPFunction
#=========================================================================
class vtemDynVarMIPFunction(DynVarMIPFunction):
    key = 'dynvarmip_vtem'

    def __init__(self, time, lev, lat, vzm, vthzm, thzm):
        super(vtemDynVarMIPFunction, self).__init__(
            time, lev, lat, vzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.vtem
        self._units = 'm s-1'
        self._positive = None


#=========================================================================
# utendvtemDynVarMIPFunction
#=========================================================================
class utendvtemDynVarMIPFunction(DynVarMIPFunction):
    key = 'dynvarmip_utendvtem'

    def __init__(self, time, lev, lat, uzm, vzm, vthzm, thzm):
        super(utendvtemDynVarMIPFunction, self).__init__(
            time, lev, lat, uzm, vzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.utendvtem
        self._units = 'm s-1 d-1'
        self._positive = None


#=========================================================================
# epfyDynVarMIPFunction
#=========================================================================
class epfyDynVarMIPFunction(DynVarMIPFunction):
    key = 'dynvarmip_epfy'

    def __init__(self, time, lev, lat, uzm, uvzm, vthzm, thzm):
        super(epfyDynVarMIPFunction, self).__init__(
            time, lev, lat, uzm, uvzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.epfy
        self._units = 'm3 s-2'
        self._positive = None


#=========================================================================
# epfzDynVarMIPFunction
#=========================================================================
class epfzDynVarMIPFunction(DynVarMIPFunction):
    key = 'dynvarmip_epfz'

    def __init__(self, time, lev, lat, uzm, uwzm, vthzm, thzm):
        super(epfzDynVarMIPFunction, self).__init__(
            time, lev, lat, uzm, uwzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.epfz
        self._units = 'm3 s-2'
        self._positive = 'up'


#=========================================================================
# utendepfdDynVarMIPFunction
#=========================================================================
class utendepfdDynVarMIPFunction(DynVarMIPFunction):
    key = 'dynvarmip_utendepfd'

    def __init__(self, time, lev, lat, uzm, uvzm, uwzm, vthzm, thzm):
        super(utendepfdDynVarMIPFunction, self).__init__(
            time, lev, lat, uzm, uvzm, uwzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.utendepfd
        self._units = 'm s-2'
        self._positive = None


#=========================================================================
# psitemDynVarMIPFunction
#=========================================================================
class psitemDynVarMIPFunction(DynVarMIPFunction):
    key = 'dynvarmip_psitem'

    def __init__(self, time, lev, lat, vzm, vthzm, thzm):
        super(psitemDynVarMIPFunction, self).__init__(
            time, lev, lat, vzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.psitem
        self._units = 'kg s-1'
        self._positive = None
