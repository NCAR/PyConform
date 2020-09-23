"""
DynVarMIP Diagnostics Functions Unit Tests

Copyright 2017-2020, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

import numpy as np

import pyconform.modules.dynvarmipdiags as dvmd


class Test(unittest.TestCase):

    def setUp(self):
        self.ntime = 5
        self.nlevi = 4
        self.nlat = 3
        self.nlon = 2

        self.shape = (self.ntime, self.nlevi, self.nlat, self.nlon)
        self.size = np.prod(self.shape)

        self.time = np.arange(self.ntime) * 30.0
        self.levi = np.arange(self.nlevi) * 100.0 + 1.0
        self.lat = (2.0 * np.arange(self.nlat) / (self.nlat - 1) - 1.0) * 80.0

        self.uzm = np.random.rand(*self.shape)
        self.vzm = np.random.rand(*self.shape)
        self.wzm = np.random.rand(*self.shape)
        self.uvzm = np.random.rand(*self.shape)
        self.uwzm = np.random.rand(*self.shape)
        self.thzm = np.random.rand(*self.shape)
        self.vthzm = np.random.rand(*self.shape)

    def test_vtem(self):
        dvmd.vtem(self.time, self.levi, self.lat, self.vzm, self.vthzm, self.thzm)

    def test_wtem(self):
        dvmd.wtem(self.time, self.levi, self.lat, self.wzm, self.vthzm, self.thzm)

    def test_utendvtem(self):
        dvmd.utendvtem(self.time, self.levi, self.lat, self.uzm, self.vzm, self.vthzm, self.thzm)

    def test_utendwtem(self):
        dvmd.utendwtem(self.time, self.levi, self.lat, self.uzm, self.wzm, self.vthzm, self.thzm)

    def test_epfy(self):
        dvmd.epfy(self.time, self.levi, self.lat, self.uzm, self.uvzm, self.vthzm, self.thzm)

    def test_epfz(self):
        dvmd.epfz(self.time, self.levi, self.lat, self.uzm, self.uwzm, self.vthzm, self.thzm)

    def test_utendepfd(self):
        dvmd.utendepfd(self.time, self.levi, self.lat, self.uzm, self.uvzm, self.uwzm, self.vthzm, self.thzm)

    def test_psitem(self):
        dvmd.psitem(self.time, self.levi, self.lat, self.vzm, self.vthzm, self.thzm)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
