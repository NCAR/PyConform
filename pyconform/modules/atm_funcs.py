"""
Copyright 2017-2020, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import numpy as np

from pyconform.functions import Function
from pyconform.physarray import PhysArray


class delpFunction(Function):
    key = "delp"

    def __init__(self, p_PO, p_PS, p_hyai, p_hybi):
        super(delpFunction, self).__init__(p_PO, p_PS, p_hyai, p_hybi)

    def __getitem__(self, index):
        p_PO = self.arguments[0][index]
        p_PS = self.arguments[1][index]
        p_hyai = self.arguments[2][index]
        p_hybi = self.arguments[3][index]

        if index is None:
            return PhysArray(
                np.zeros((0, 0, 0, 0)),
                dimensions=[
                    p_PS.dimensions[0],
                    p_hybi.dimensions[0],
                    p_PS.dimensions[1],
                    p_PS.dimensions[2],
                ],
            )

        PO = p_PO.data
        PS = p_PS.data
        hyai = p_hyai.data
        hybi = p_hybi.data

        p = (hyai * PO) + (hybi * PS)
        j = len(hybi)
        delp = np.ma.zeros(
            (
                p_PS.dimensions[0],
                p_hybi.dimensions[0],
                p_PS.dimensions[1],
                p_PS.dimensions[2],
            )
        )
        for i in range(0, j - 1):
            delp[:, i, :, :] = p[:, i + 1, :, :] - p[:, i, :, :]

        new_name = "delp({}{}{}{})".format(
            p_PO.name, p_PS.name, p_hyai.name, p_hybi.name
        )

        return PhysArray(delp, name=new_name, units="Pa")


class rhoFunction(Function):
    key = "rho"

    def __init__(self, p_PO, p_PS, p_hyam, p_hybm, p_T):
        super(rhoFunction, self).__init__(p_PO, p_PS, p_hyam, p_hybm, p_T)

    def __getitem__(self, index):
        p_PO = self.arguments[0][index]
        p_PS = self.arguments[1][index]
        p_hyam = self.arguments[2][index]
        p_hybm = self.arguments[3][index]
        p_T = self.arguments[4][index]

        if index is None:
            return PhysArray(
                np.zeros((0, 0, 0, 0)),
                dimensions=[
                    p_T.dimensions[0],
                    p_T.dimensions[1],
                    p_T.dimensions[2],
                    p_T.dimensions[3],
                ],
            )

        PO = p_PO.data
        PS = p_PS.data
        hyam = p_hyam.data
        hybm = p_hybm.data
        T = p_T.data

        p = (hyam * PO) + (hybm * PS)
        rho = p / (287.04 * T)

        new_name = "rho({}{}{}{}{})".format(
            p_PO.name, p_PS.name, p_hyam.name, p_hybm.name, p_T.name
        )

        return PhysArray(rho, name=new_name, units="cm-3")


class pm25Function(Function):
    key = "pm25"

    def __init__(self, p_PO, p_PS, p_hyam, p_hybm, p_T, p_PM25_o):
        super(pm25Function, self).__init__(p_PO, p_PS, p_hyam, p_hybm, p_T, p_PM25_o)

    def __getitem__(self, index):
        p_PO = self.arguments[0][index]
        p_PS = self.arguments[1][index]
        p_hyam = self.arguments[2][index]
        p_hybm = self.arguments[3][index]
        p_T = self.arguments[4][index]
        p_PM25_o = self.arguments[5][index]

        if index is None:
            return PhysArray(
                np.zeros((0, 0, 0, 0)),
                dimensions=[
                    p_T.dimensions[0],
                    p_T.dimensions[1],
                    p_T.dimensions[2],
                    p_T.dimensions[3],
                ],
            )

        PO = p_PO.data
        PS = p_PS.data
        hyam = p_hyam.data
        hybm = p_hybm.data
        T = p_T.data
        PM25_o = p_PM25_o.data

        p = (hyam * PO) + (hybm * PS)
        pm25 = PM25_o * 287.0 * T / p

        new_name = "pm25({}{}{}{}{}{})".format(
            p_PO.name, p_PS.name, p_hyam.name, p_hybm.name, p_T.name, p_PM25_o.name
        )

        return PhysArray(pm25, name=new_name, units="kg/kg")


# class tozFunction(Function):
#     key = 'toz'

#     def __init__(self, p_PO, p_PS, p_hyam, p_hybm, p_indat3a):
#         super(tozFunction, self).__init__(p_PO, p_PS, p_hyam, p_hybm, p_indat3a)

#     def __getitem__(self, index):
#         p_PO = self.arguments[0][index]
#         p_PS = self.arguments[1][index]
#         p_hyam = self.arguments[2][index]
#         p_hybm = self.arguments[3][index]
#         p_indat3a = self.arguments[4][index]

#         if index is None:
#             return PhysArray(np.zeros((0, 0, 0)), dimensions=[p_indat3a.dimensions[0], p_indat3a.dimensions[1], p_indat3a.dimensions[2]])

#         PO = p_PO.data
#         PS = p_PS.data
#         hyam = p_hyam.data
#         hybm = p_hybm.data
#         T = p_T.data
#         j = len(hybm)

#         p = (hyam * PO) + (hybm * PS)
#         delp = np.ma.zeros((p_indat3a.dimensions[0], p_indat3a.dimensions[1], p_indat3a.dimensions[2]))
#         for i in range(0, j - 1):
#             delp[:, i, :, :] = p[:, i + 1, :, :] - p[:, u, :, :]
#         work3da = p_indat3a * delp * 1.e-02
#         cmordat2d = sum(work3da, dim=3)
#         cmordat2d = cmordat2d * 2.1e+22 / 2.69e16

#         new_name = 'toz({}{}{}{}{})'.format(
#             p_PO.name, p_PS.name, p_hyam.name, p_hybm.name, p_T.name)

#         return PhysArray(cmordat2d, name=new_name, units='m')
