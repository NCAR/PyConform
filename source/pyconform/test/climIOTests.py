"""
Tests for the climIO class

Copyright 2015, University Corporation for Atmospheric Research
See the LICENSE.rst file for details
"""

import unittest

import sys
from glob import glob
from cStringIO import StringIO
from os import linesep as eol
from os import remove
from os.path import exists

import Nio
import netCDF4
import numpy as np

import climIO


class climIOTests(unittest.TestCase):

    def setUp(self):

        # Init the I/O ports
        self.io_ports = {'Nio':climIO.init_climIO(override='Nio'),'netCDF4':climIO.init_climIO(override='netCDF4')}

        # Test Data Generation
        self._clean_directory()
        #self.nlat = 19
        #self.nlon = 36
        #self.ntime = 10
        self.nlat = 4
        self.nlon = 8
        self.ntime = 1
        self.slices = 'input.nc'
        self.scalars = ['scalar{}'.format(i) for i in xrange(2)]
        self.timvars = ['tim{}'.format(i) for i in xrange(2)]
        self.tvmvars = ['tvm{}'.format(i) for i in xrange(2)]
        self.tsvar = 'tsvar'
        self.fattrs = {'attr1': 'attribute one',
                       'attr2': 'attribute two'}
  

        # Open the file for writing
        fname = self.slices
        self.fobj = Nio.open_file(fname, 'w')

        # Write attributes to file
        for name, value in self.fattrs.iteritems():
            setattr(self.fobj, name, value)

        # Create the dimensions in the file
        self.fobj.create_dimension('lat', self.nlat)
        self.fobj.create_dimension('lon', self.nlon)
        self.fobj.create_dimension('time', None)

        # Create the coordinate variables & add attributes
        lat = self.fobj.create_variable('lat', 'f', ('lat',))
        lon = self.fobj.create_variable('lon', 'f', ('lon',))
        time = self.fobj.create_variable('time', 'f', ('time',))

        # Set the coordinate variable attributes
        setattr(lat, 'long_name', 'latitude')
        setattr(lon, 'long_name', 'longitude')
        setattr(time, 'long_name', 'time')
        setattr(lat, 'units', 'degrees north')
        setattr(lon, 'units', 'degrees east')
        setattr(time, 'units', 'days from 01-01-0001')

        # Set the values of the coordinate variables
        lat[:] = np.linspace(-90, 90, self.nlat).astype(np.float32)#, dtype=np.float32)
        lon[:] = np.linspace(-180, 180, self.nlon, endpoint=False).astype(np.float32)#, dtype=np.float32)
        time[:] = np.arange(i * self.ntime, (i + 1) * self.ntime, dtype=np.float32)

        # Create the scalar variables
        for n in xrange(len(self.scalars)):
            vname = self.scalars[n]
            v = self.fobj.create_variable(vname, 'd', ())
            setattr(v, 'long_name', 'scalar{}'.format(n))
            setattr(v, 'units', '[{}]'.format(vname))
            v.assign_value(np.float64(n * 10))

        # Create the time-invariant metadata variables
        for n in xrange(len(self.timvars)):
            vname = self.timvars[n]
            v = self.fobj.create_variable(vname, 'd', ('lat', 'lon'))
            setattr(v, 'long_name', 'time-invariant metadata {}'.format(n))
            setattr(v, 'units', '[{}]'.format(vname))
            v[:] = np.ones((self.nlat, self.nlon), dtype=np.float64) * n

        # Create the time-variant metadata variables
        for n in xrange(len(self.tvmvars)):
            vname = self.tvmvars[n]
            v = self.fobj.create_variable(vname, 'd', ('time', 'lat', 'lon'))
            setattr(v, 'long_name', 'time-variant metadata {}'.format(n))
            setattr(v, 'units', '[{}]'.format(vname))
            v[:] = np.ones((self.ntime, self.nlat, self.nlon), dtype=np.float64) * n

        # Create the time-series variable
        vname = self.tsvar
        self.var = self.fobj.create_variable(vname, 'd', ('time', 'lat', 'lon'))
        setattr(self.var, 'long_name', 'time-series variable {}'.format(n))
        setattr(self.var, 'units', '[{}]'.format(vname))
        self.tsvalues = np.ones((self.ntime, self.nlat, self.nlon), dtype=np.float64) 
        self.var[:] = self.tsvalues

    def tearDown(self):
        self._clean_directory()

    def _clean_directory(self):
        for ncfile in glob('*.nc'):
            remove(ncfile)

    def _assertion(self, name, actual, expected,
                   data=None, show=True, assertion=None):
        msg = eol 
        if data:
            msg += ' - Input:    {}'.format(data) + eol 
        msg += ' - Actual:   {}'.format(actual) + eol 
        msg += ' - Expected: {}'.format(expected)
        if show:
            print msg
        if assertion:
            assertion(actual, expected, msg)
        else:
            self.assertEqual(actual, expected, msg)

    def test_file_operations(self):
        # Loop over each IO port and test all function calls (all ports have the same functions/arguments)
        for n,p in self.io_ports.items():

            # Test open_file
            f = p.open_file(self.slices)  
            if (n == 'Nio'):
                #self.assertIsInstance(f, nio._NioFile)              
                self.assertNotEqual(f, None,"{0}: open_file".format(n))
            elif (n == 'netCDF4'):
                self.assertIsInstance(f, netCDF4.Dataset, "{0}: open_file".format(n))
  
            # Test read_slice
            test_vals = p.read_slice(f, self.tsvar, index=0, all_values=False)
            self.assertTrue((test_vals==self.tsvalues[0]).all(), "{0}: read_slice,index".format(n))
            test_vals = p.read_slice(f, self.tsvar, index=-99, all_values=True)
            self.assertTrue((test_vals==self.tsvalues[:]).all(), "{0}: read_slice,all".format(n))   

            # Test create_file
            new_f = p.create_file('new.nc', 'netcdf4c')
            self.assertNotEqual(type(new_f), None, "{0}: create_file,netcdf4c".format(n))
            remove('new.nc')
            new_f = p.create_file('new.nc', 'netcdf4')
            self.assertNotEqual(type(new_f), None, "{0}: create_file,netcdf4".format(n))
            remove('new.nc')
            new_f = p.create_file('new.nc', 'netcdf')
            self.assertNotEqual(type(new_f), None, "{0}: create_file,netcdf".format(n))
            remove('new.nc')
            new_f = p.create_file('new.nc', 'netcdfLarge')
            self.assertNotEqual(type(new_f), None, "{0}: create_file,netcdfLarge".format(n)) 

            # Test get_var_info
            typeCode,dimnames,attr = p.get_var_info(f, self.tsvar)
            if (isinstance(attr,dict)):
                att_k = attr.keys()
            else:
                att_k = attr
            self.assertEqual(typeCode, 'd', "{0}: get_var_info,typecode".format(n))
            self.assertEqual(dimnames, ['time', 'lat', 'lon'], "{0}: get_var_info,dimensions".format(n))
            for k in att_k:
              self.assertIn(k, ['units', 'long_name'],"{0}: get_var_info,attributes".format(n))

            # Test define_file
            all_vars,new_f = p.define_file(new_f, self.tsvar, self.timvars, self.slices, self.tsvar)
            if (n == 'Nio'):
                self.assertNotEqual(new_f, None, "{0}: define_file,file".format(n))
            elif (n == 'netCDF4'):
                self.assertIsInstance(new_f, netCDF4.Dataset, "{0}: define_file,file".format(n))
            for k in all_vars.keys():
                self.assertIn(k, ['tsvar','tim0','tim1'], "{0}: define_file,varibales,{1}".format(n,k))

            # Test create_var
            new_v = p.create_var(new_f, self.tsvar+'2', typeCode, dimnames, attr)
            if (n == 'Nio'):
                #self.assertIsInstance(f, nio._NioVariable)              
                self.assertNotEqual(new_v, None,"{0}: create_var".format(n))
            elif (n == 'netCDF4'):
                self.assertIsInstance(new_v, netCDF4.Variable, "{0}: create_var".format(n)) 

            # Test write_var
            p.write_var(all_vars, self.tsvalues[:], self.tsvar)
            self.assertTrue((all_vars[self.tsvar]==self.tsvalues[0]).all(), "{0}: write_var,index 0".format(n))
            p.write_var(all_vars, self.tsvalues[:], self.tsvar, index=1)
            self.assertTrue((all_vars[self.tsvar][1]==self.tsvalues[0]).all(), "{0}: write_var,index 1".format(n))
 

    def test_close(self):
   
        for n,p in self.io_ports.items():
            f = p.open_file(self.slices)
            f = p.close_file(f)

if __name__ == "__main__":
    hline = '=' * 70
    print hline
    print 'STANDARD OUTPUT FROM ALL TESTS:'
    print hline

    mystream = StringIO()
    tests = unittest.TestLoader().loadTestsFromTestCase(climIOTests)
    unittest.TextTestRunner(stream=mystream).run(tests)

    print hline
    print 'TESTS RESULTS:'
    print hline
    print str(mystream.getvalue())
