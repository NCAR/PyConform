"""
DynVarMIP Diagnostic Function Classes

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.physarray import PhysArray
from pyconform.functions import Function

import pyconform.modules.dynvarmipdiags as dvmd


#=========================================================================
# DynVarMIPFunction
#=========================================================================
class DynVarMIPFunction(Function):
    key = 'dynvarmipfunc'

    def __init__(self, *args):
        super(DynVarMIPFunction, self).__init__(*args)
        self._dynvarmip_func = None

    def __getitem__(self, index):
        args = [self.arguments[i][index] for i in len(self.arguments)]
        arg_names = ','.join([arg.name for arg in args])
        data = self._dynvarmip_func(*args)
        name = '{}({})'.format(self.key, arg_names)
        return PhysArray(data, name=name)


#=========================================================================
# wtemDynVarMIPFunction
#=========================================================================
class wtemDynVarMIPFunction(Function):
    key = 'dynvarmip_wtem'

    def __init__(self, time, levi, lat, wzm, vthzm, thzm):
        super(wtemDynVarMIPFunction, self).__init__(
            time, levi, lat, wzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.wtem


#=========================================================================
# utendwtemDynVarMIPFunction
#=========================================================================
class utendwtemDynVarMIPFunction(Function):
    key = 'dynvarmip_utendwtem'

    def __init__(self, time, levi, lat, uzm, wzm, vthzm, thzm):
        super(utendwtemDynVarMIPFunction, self).__init__(
            time, levi, lat, uzm, wzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.utendwtem


#=========================================================================
# vtemDynVarMIPFunction
#=========================================================================
class vtemDynVarMIPFunction(Function):
    key = 'dynvarmip_vtem'

    def __init__(self, time, levi, lat, vzm, vthzm, thzm):
        super(vtemDynVarMIPFunction, self).__init__(
            time, levi, lat, vzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.vtem


#=========================================================================
# utendvtemDynVarMIPFunction
#=========================================================================
class utendvtemDynVarMIPFunction(Function):
    key = 'dynvarmip_utendvtem'

    def __init__(self, time, levi, lat, uzm, vzm, vthzm, thzm):
        super(utendvtemDynVarMIPFunction, self).__init__(
            time, levi, lat, uzm, vzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.utendvtem


#=========================================================================
# epfyDynVarMIPFunction
#=========================================================================
class epfyDynVarMIPFunction(Function):
    key = 'dynvarmip_epfy'

    def __init__(self, time, levi, lat, uzm, uvzm, vthzm, thzm):
        super(epfyDynVarMIPFunction, self).__init__(
            time, levi, lat, uzm, uvzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.epfy


#=========================================================================
# epfzDynVarMIPFunction
#=========================================================================
class epfzDynVarMIPFunction(Function):
    key = 'dynvarmip_epfz'

    def __init__(self, time, levi, lat, uzm, uwzm, vthzm, thzm):
        super(epfzDynVarMIPFunction, self).__init__(
            time, levi, lat, uzm, uwzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.epfz


#=========================================================================
# utendepfdDynVarMIPFunction
#=========================================================================
class utendepfdDynVarMIPFunction(Function):
    key = 'dynvarmip_utendepfd'

    def __init__(self, time, levi, lat, uzm, uvzm, uwzm, vthzm, thzm):
        super(utendepfdDynVarMIPFunction, self).__init__(
            time, levi, lat, uzm, uvzm, uwzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.utendepfd


#=========================================================================
# psitemDynVarMIPFunction
#=========================================================================
class psitemDynVarMIPFunction(Function):
    key = 'dynvarmip_psitem'

    def __init__(self, time, levi, lat, vzm, vthzm, thzm):
        super(psitemDynVarMIPFunction, self).__init__(
            time, levi, lat, vzm, vthzm, thzm)
        self._dynvarmip_func = dvmd.psitem
