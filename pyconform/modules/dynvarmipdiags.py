"""
Basic functions for the DynVarMIP Diagnostics

NOTE:  All of these functions return numpy arrays!

Copyright 2017-2020, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import numpy

from pyconform.modules.idl import deriv, int_tabulated

# Constants
p0 = 101325.0
a = 6.37123e6
om = 7.29212e-5
H = 7000.0
g0 = 9.80665


def _init_wtem(time, levi, lat, wzm, vthzm, thzm):
    ntime = len(time)

    latrad = (lat / 180.0) * numpy.pi
    coslat = numpy.cos(latrad)
    levi100 = 100.0 * levi

    _wzm = -1.0 * numpy.einsum('ij...,j->ij...', wzm, levi100) / H

    wtem = numpy.zeros(wzm.shape, dtype='d')
    for itime in range(ntime):
        dthdp = deriv(levi100, thzm[itime, ...])
        psieddy = vthzm[itime, ...] / dthdp
        tmp = numpy.einsum('ij...,j->ij...', psieddy, coslat)
        dpsidy = numpy.einsum(
            'ij...,j->ij...', deriv(latrad, tmp, axis=1), 1.0 / (a * coslat)
        )
        wtem[itime, ...] = _wzm[itime, ...] + dpsidy
    return wtem


def wtem(time, levi, lat, wzm, vthzm, thzm):
    levi100 = 100.0 * levi
    wtem = _init_wtem(time, levi, lat, wzm, vthzm, thzm)
    wtem = -1.0 * numpy.einsum('ij...,j->ij...', wtem, H / levi100)
    return wtem


def vtem(time, levi, lat, vzm, vthzm, thzm):
    ntime = len(time)

    levi100 = 100.0 * levi

    vtem = numpy.zeros(vzm.shape, dtype='d')
    for itime in range(ntime):
        dthdp = deriv(levi100, thzm[itime, ...])
        psieddy = vthzm[itime, ...] / dthdp
        dpsidp = deriv(levi100, psieddy)
        vtem[itime, ...] = vzm[itime, ...] - dpsidp
    return vtem


def utendvtem(time, levi, lat, uzm, vzm, vthzm, thzm):
    ntime = len(time)

    latrad = (lat / 180.0) * numpy.pi
    coslat = numpy.cos(latrad)
    fshape = (1, len(lat)) + tuple([1] * (uzm.ndim - 3))
    f = 2 * om * numpy.sin(latrad).reshape(fshape)
    _vtem = vtem(time, levi, lat, vzm, vthzm, thzm)

    utendvtem = numpy.zeros(uzm.shape, dtype='d')
    for itime in range(ntime):
        ucos = numpy.einsum('ij...,j->ij...', uzm[itime, ...], coslat)
        dudphi = deriv(latrad, ucos, axis=1) / a
        utendvtem[itime, ...] = _vtem[itime, ...] * (f - dudphi)
    return utendvtem


def utendwtem(time, levi, lat, uzm, wzm, vthzm, thzm):
    ntime = len(time)

    levi100 = 100.0 * levi
    wtem = _init_wtem(time, levi, lat, wzm, vthzm, thzm)

    utendwtem = numpy.zeros(uzm.shape, dtype='d')
    for itime in range(ntime):
        dudp = deriv(levi100, uzm[itime, ...])
        utendwtem[itime, ...] = -1.0 * wtem[itime, ...] * dudp
    return utendwtem


def _init_epfy(time, levi, lat, uzm, uvzm, vthzm, thzm):
    ntime = len(time)

    latrad = (lat / 180.0) * numpy.pi
    coslat = numpy.cos(latrad)
    levi100 = 100.0 * levi

    epfy = numpy.zeros(uzm.shape, dtype='d')
    for itime in range(ntime):
        dthdp = deriv(levi100, thzm[itime, ...])
        dudp = deriv(levi100, uzm[itime, ...])
        psieddy = vthzm[itime, ...] / dthdp
        epfy[itime, ...] = a * numpy.einsum(
            'j,ij...->ij...', coslat, (dudp * psieddy - uvzm[itime, ...])
        )
    return epfy


def epfy(time, levi, lat, uzm, uvzm, vthzm, thzm):
    levi100 = 100.0 * levi
    epfy = _init_epfy(time, levi, lat, uzm, uvzm, vthzm, thzm)
    epfy = numpy.einsum('ij...,j->ij...', epfy, levi100) / p0
    return epfy


def _init_epfz(time, levi, lat, uzm, uwzm, vthzm, thzm):
    ntime = len(time)

    latrad = (lat / 180.0) * numpy.pi
    coslat = numpy.cos(latrad)
    fshape = (1, len(lat)) + tuple([1] * (uzm.ndim - 3))
    f = 2 * om * numpy.sin(latrad).reshape(fshape)
    levi100 = 100.0 * levi

    _uwzm = -1.0 * numpy.einsum('ij...,j->ij...', uwzm, levi100) / H

    epfz = numpy.zeros(uzm.shape, dtype='d')
    for itime in range(ntime):
        ucos = numpy.einsum('ij...,j->ij...', uzm[itime, ...], coslat)
        dudphi = deriv(latrad, ucos, axis=1) / a
        dthdp = deriv(levi100, thzm[itime, ...])
        psieddy = vthzm[itime, ...] / dthdp
        epfz[itime, ...] = a * numpy.einsum(
            'j,ij...->ij...', coslat, (f - dudphi) * psieddy - _uwzm[itime, ...]
        )
    return epfz


def epfz(time, levi, lat, uzm, uwzm, vthzm, thzm):
    epfz = _init_epfz(time, levi, lat, uzm, uwzm, vthzm, thzm)
    epfz = -1.0 * (H / p0) * epfz
    return epfz


def utendepfd(time, levi, lat, uzm, uvzm, uwzm, vthzm, thzm):
    ntime = len(time)

    latrad = (lat / 180.0) * numpy.pi
    coslat = numpy.cos(latrad)
    levi100 = 100.0 * levi
    iacoslat = 1.0 / (a * coslat)

    epfy = _init_epfy(time, levi, lat, uzm, uvzm, vthzm, thzm)
    epfz = _init_epfz(time, levi, lat, uzm, uwzm, vthzm, thzm)

    utendepfd = numpy.zeros(uzm.shape, dtype='d')
    for itime in range(ntime):
        tmp = numpy.einsum('ij...,j->ij...', epfy[itime, ...], coslat)
        depfydphi = numpy.einsum('ij...,j->ij...', deriv(latrad, tmp, axis=1), iacoslat)
        depfzdp = deriv(levi100, epfz[itime, ...])
        utendepfd[itime, ...] = numpy.einsum(
            'ij...,j->ij...', depfydphi + depfzdp, iacoslat
        )
    return utendepfd


def psitem(time, levi, lat, vzm, vthzm, thzm):
    ntime = len(time)
    nlevi = len(levi)

    latrad = (lat / 180.0) * numpy.pi
    coslat = numpy.cos(latrad)
    levi100 = levi * 100.0

    psitem = numpy.zeros(vzm.shape, dtype='d')
    vzm_shape_1 = list(vzm.shape[1:])
    vzm_shape_1[0] += 1
    vzmwithzero = numpy.zeros(vzm_shape_1, dtype='d')
    levi100withzero = numpy.zeros((nlevi + 1,), dtype='d')
    levi100withzero[1:] = levi100
    for itime in range(ntime):
        dthdp = deriv(levi100, thzm[itime, ...])
        psieddy = vthzm[itime, ...] / dthdp
        vzmwithzero[1:, ...] = vzm[itime, ...]
        for ilev in range(1, nlevi + 1):
            result = int_tabulated(
                levi100withzero[0 : ilev + 1], vzmwithzero[0 : ilev + 1, ...]
            )
            tmp1 = (2 * numpy.pi * a * coslat) / g0
            tmp2 = result - psieddy[ilev - 1, ...]
            psitem[itime, ilev - 1, ...] = numpy.einsum('i,i...->i...', tmp1, tmp2)

    return psitem
