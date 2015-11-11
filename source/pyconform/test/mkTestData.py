"""
Make Testing Data

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import OrderedDict
from os import remove
from os.path import exists
import netCDF4
import numpy as np


#===============================================================================
# DataMaker
#===============================================================================
class DataMaker(object):
    """
    Simple tool to write a "fake" dataset for testing purposes
    """
    
    def __init__(self,
                 filenames=['test1.nc', 'test2.nc', 'test3.nc'],
                 attributes=OrderedDict([('a1', 'attrib 1'),
                                         ('a2', 'attrib 2')]),
                 dimensions=OrderedDict([('time', 4),
                                         ('lat', 3),
                                         ('lon', 2)]),
                 unlimited='time',
                 variables=OrderedDict([('T1', ('time','lat', 'lon')),
                                        ('T2', ('lat', 'lon', 'time'))]),
                 units={'lat': 'degrees_north',
                        'lon': 'degrees_east',
                        'time': 'days since 01-01-0001',
                        'T1': 'K', 'T2': 'C'}):
        self.filenames = filenames
        self.attributes = attributes
        self.dimensions = dimensions
        self.unlimited = unlimited
        self.var_dims = variables
        self.var_units = units
        
        self.variables = {}
        for filenum, filename in enumerate(self.filenames):
            self.variables[filename] = {}
            filevars = self.variables[filename]
            for coordname, dimsize in self.dimensions.iteritems():
                if coordname == self.unlimited:
                    start = filenum * dimsize
                    end = (filenum + 1) * dimsize
                    filevars[coordname] = np.linspace(start, end, dimsize, 
                                                      endpoint=False, 
                                                      dtype=np.float64)
                else:
                    filevars[coordname] = np.linspace(-(dimsize/2), dimsize/2, 
                                                      dimsize, endpoint=True,
                                                      dtype=np.float64)

            for varname, vardims in self.var_dims.iteritems():
                vshape = tuple([self.dimensions[d] for d in vardims])
                filevars[varname] = np.ones(vshape, dtype=np.float64)
        
        
    def write(self,
              ncformat='NETCDF4'):
        
        for filename in self.filenames:
            ncfile = netCDF4.Dataset(filename, 'w', format=ncformat)
            
            for attrname, attrval in self.attributes.iteritems():
                setattr(ncfile, attrname, attrval)
                
            for dimname, dimsize in self.dimensions.iteritems():
                if dimname == self.unlimited:
                    ncfile.createDimension(dimname)
                else:
                    ncfile.createDimension(dimname, dimsize)
            
            for coordname in self.dimensions.iterkeys():
                ncfile.createVariable(coordname, 'd', (coordname,))
                
            for varname, vardims in self.var_dims.iteritems():
                ncfile.createVariable(varname, 'd', vardims)
            
            for coordname, dimsize in self.dimensions.iteritems():
                coordvar = ncfile.variables[coordname]
                setattr(coordvar, 'units', self.var_units[coordname])
                coordvar[:] = self.variables[filename][coordname]

            for varname, vardims in self.var_dims.iteritems():
                var = ncfile.variables[varname]
                setattr(var, 'units', self.var_units[varname])
                var[:] = self.variables[filename][varname]
            
            ncfile.close()
            
    def clear(self):
        for filename in self.filenames:
            if exists(filename):
                remove(filename)
        
        
#===============================================================================
# Command-Line Operation
#===============================================================================
if __name__ == '__main__':
    pass