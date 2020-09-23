"""
IDL Functions Re-written in Python

These functions are modeled to mimic calculations of the IDL functions
'deriv', 'spl_init', 'spl_interp', and 'int_tabulated', which are used
to compute the DynVarMIP diagnostics.

IDL code for these functions can be found in the GDL, open-source version
of IDL, available at https://github.com/gnudatalanguage/gdl.  Obviously,
the code was not copied, but the Python code was based on the original IDL
code to determine operation order and bit-for-bit correctness.

NOTE: All of these functions return numpy arrays!

Copyright 2017-2020, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import numpy

_signature_letters = 'ijklmnabcdefgh'


def deriv(x, y=None, axis=0):
    """
    Python version of GDL deriv function
    """
    if y is None:
        y1 = numpy.array(x)
        x1 = numpy.arange(len(x), dtype=y1.dtype)
    else:
        y1 = numpy.array(y)
        x1 = numpy.array(x)

    x0 = numpy.roll(x1, 1)
    x2 = numpy.roll(x1, -1)
    y0 = numpy.roll(y1, 1, axis=axis)
    y2 = numpy.roll(y1, -1, axis=axis)

    x12 = x1 - x2
    x01 = x0 - x1
    x02 = x0 - x2

    a0 = x12 / (x01 * x02)
    a1 = 1.0 / x12 - 1.0 / x01
    a2 = -x01 / (x02 * x12)

    xsig = _signature_letters[axis]
    ysig = _signature_letters[:numpy.ndim(y1)]
    sig = '{},{}->{}'.format(ysig, xsig, ysig)
    d = (numpy.einsum(sig, y0, a0) +
         numpy.einsum(sig, y1, a1) +
         numpy.einsum(sig, y2, a2))

    i0 = tuple(0 if i == axis else slice(None) for i in range(numpy.ndim(y1)))
    i1 = tuple(1 if i == axis else slice(None) for i in range(numpy.ndim(y1)))
    i2 = tuple(2 if i == axis else slice(None) for i in range(numpy.ndim(y1)))
    a0 = (x01[1] + x02[1]) / (x01[1] * x02[1])
    a1 = -x02[1] / (x01[1] * x12[1])
    a2 = x01[1] / (x02[1] * x12[1])
    d[i0] = y1[i0] * a0 + y1[i1] * a1 + y1[i2] * a2

    i0 = tuple(-3 if i == axis else slice(None) for i in range(numpy.ndim(y1)))
    i1 = tuple(-2 if i == axis else slice(None) for i in range(numpy.ndim(y1)))
    i2 = tuple(-1 if i == axis else slice(None) for i in range(numpy.ndim(y1)))
    a0 = -x12[-2] / (x01[-2] * x02[-2])
    a1 = x02[-2] / (x01[-2] * x12[-2])
    a2 = -(x02[-2] + x12[-2]) / (x02[-2] * x12[-2])
    d[i2] = y1[i0] * a0 + y1[i1] * a1 + y1[i2] * a2
    return d


def spl_init(x1, y1, axis=0):
    """
    Python version of GDL spl_init function
    """
    n = len(x1)
    x0 = numpy.roll(x1, 1)
    x2 = numpy.roll(x1, -1)
    y0 = numpy.roll(y1, 1, axis=axis)
    y2 = numpy.roll(y1, -1, axis=axis)

    psig = (x1 - x0) / (x2 - x0)
    psig[0] = (x1[0] - x2[0]) / (x0[0] - x2[0])
    psig[-1] = (x1[-1] - x2[-1]) / (x0[-1] - x2[-1])

    xsig = _signature_letters[axis]
    ysig = _signature_letters[:numpy.ndim(y1)]
    sig = '{},{}->{}'.format(ysig, xsig, ysig)

    pu_a = numpy.einsum(sig, y2 - y1, 1.0 / ((x2 - x1) * (x2 - x0)))
    pu_b = numpy.einsum(sig, y1 - y0, 1.0 / ((x1 - x0) * (x2 - x0)))
    pu = pu_a - pu_b

    b = numpy.empty_like(y1)
    u = numpy.empty_like(y1)

    i0 = tuple(0 if i == axis else slice(None) for i in range(numpy.ndim(y1)))
    b[i0] = 0.0
    u[i0] = 0.0
    for i in range(1, n - 1):
        j = tuple(i if k == axis else slice(None)
                  for k in range(numpy.ndim(y1)))
        jm1 = tuple(i - 1 if k == axis else slice(None)
                    for k in range(numpy.ndim(y1)))
        p = psig[i] * b[jm1] + 2.0
        b[j] = (psig[i] - 1.0) / p
        u[j] = (6.0 * pu[j] - psig[i] * u[jm1]) / p
    i0 = tuple(-1 if i == axis else slice(None) for i in range(numpy.ndim(y1)))
    b[i0] = 0.0
    for i in range(n - 2, -1, -1):
        j = tuple(i if k == axis else slice(None)
                  for k in range(numpy.ndim(y1)))
        jp1 = tuple(i + 1 if k == axis else slice(None)
                    for k in range(numpy.ndim(y1)))
        b[j] = b[j] * b[jp1] + u[j]
    return b


def spl_interp(xa, ya, y2a, x, axis=0):
    """
    Python version of GDL spl_interp function
    """
    n = len(xa)
    valloc = numpy.digitize(x, xa) - 1
    klo = []
    for i in valloc:
        klo.append(min(max(i, 0), (n - 2)))
    klo = numpy.array(klo)
    khi = klo + 1
    xahi = xa[khi]
    xalo = xa[klo]

    h = xahi - xalo

    jhi = [khi if k == axis else slice(None) for k in range(numpy.ndim(ya))]
    jlo = [klo if k == axis else slice(None) for k in range(numpy.ndim(ya))]
    yahi = ya[tuple(jhi)]
    yalo = ya[tuple(jlo)]
    y2ahi = y2a[tuple(jhi)]
    y2alo = y2a[tuple(jlo)]

    a = (xahi - x) / h
    b = (x - xalo) / h
    c = (a ** 3 - a) * (h ** 2) / 6.0
    d = (b ** 3 - b) * (h ** 2) / 6.0

    xsig = _signature_letters[axis]
    ysig = _signature_letters[:numpy.ndim(ya)]
    sig = '{},{}->{}'.format(ysig, xsig, ysig)

    return (numpy.einsum(sig, yalo, a) + numpy.einsum(sig, yahi, b) +
            numpy.einsum(sig, y2alo, c) + numpy.einsum(sig, y2ahi, d))


def int_tabulated(x, y, axis=0):
    """
    Python version of GDL int_tabulated function
    """
    nx = len(x)
    nseg = nx - 1
    while nseg % 4 != 0:
        nseg += 1
    nint = nseg / 4
    xmin = numpy.min(x)
    xmax = numpy.max(x)
    h = (xmax - xmin) / float(nseg)
    x_unif = numpy.linspace(xmin, xmax, nseg + 1)
    z_spl = spl_init(x, y, axis=axis)
    z_unif = spl_interp(x, y, z_spl, x_unif, axis=axis)
    coef_l = [7] + [32, 12, 32, 14] * (nint - 1) + [32, 12, 32, 7]
    coeffs = 2.0 * h * numpy.array(coef_l, dtype='d') / 45.0
    xsig = _signature_letters[axis]
    ysig = _signature_letters[:numpy.ndim(y)]
    sig = '{},{}->{}'.format(ysig, xsig, ysig)
    return numpy.sum(numpy.einsum(sig, z_unif, coeffs), axis=axis)
