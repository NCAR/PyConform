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
                 fileattribs=[OrderedDict([('a1', 'file 1 attrib 1'),
                                           ('a2', 'file 1 attrib 2')]),
                              OrderedDict([('a1', 'file 2 attrib 1'),
                                           ('a2', 'file 2 attrib 2')]),
                              OrderedDict([('a1', 'file 3 attrib 1'),
                                           ('a2', 'file 3 attrib 2')]),],
                 dimensions=OrderedDict([('time', [3,4,5]),
                                         ('space', 2)]),
                 variables=OrderedDict([('T1', ('time', 'space')),
                                        ('T2', ('space', 'time'))]),
                 varattribs=OrderedDict([('space', {'units': 'm'}),
                                         ('time', {'units': 'days since 1979-01-01 00:00:00',
                                                   'calendar': 'noleap'}),
                                         ('T1', {'units': 'K'}),
                                         ('T2', {'units': 'C'})]),
                 data=OrderedDict()):
        self.filenames = filenames
        self.clear()
        
        self.fileattribs = fileattribs
        self.dimensions = dimensions
        self.vardims = variables
        self.varattribs = varattribs
        
        self.variables = {}
        for filenum, filename in enumerate(self.filenames):
            self.variables[filename] = {}
            filevars = self.variables[filename]
            for coordname, dimsize in self.dimensions.iteritems():
                if coordname in data:
                    vdat = data[coordname][filenum]
                elif isinstance(dimsize, (list, tuple)):
                    start = filenum * dimsize[filenum]
                    end = (filenum + 1) * dimsize[filenum]
                    vdat = np.arange(start, end, dtype=np.float64)
                else:
                    vdat = np.arange(-(dimsize/2), dimsize/2, dtype=np.float64)
                filevars[coordname] = vdat

            for varname, vardims in self.vardims.iteritems():
                if varname in data:
                    vdat = data[varname][filenum]
                else:
                    vshape = []
                    for dim in vardims:
                        if isinstance(self.dimensions[dim], (list, tuple)):
                            vshape.append(self.dimensions[dim][filenum])
                        else:
                            vshape.append(self.dimensions[dim])
                    vdat = np.ones(tuple(vshape), dtype=np.float64)
                filevars[varname] = vdat
            
            print 'file: {}'.format(filename)
            for varname, vardata in filevars.iteritems():
                print '   {}: {}'.format(varname, vardata).replace('\n', '')
            print
        
        
    def write(self,
              ncformat='NETCDF4'):
        
        for filenum, filename in enumerate(self.filenames):
            ncfile = netCDF4.Dataset(filename, 'w', format=ncformat)
            
            for attrname, attrval in self.fileattribs[filenum].iteritems():
                setattr(ncfile, attrname, attrval)
                
            for dimname, dimsize in self.dimensions.iteritems():
                if isinstance(dimsize, (list, tuple)):
                    ncfile.createDimension(dimname)
                else:
                    ncfile.createDimension(dimname, dimsize)
            
            for coordname in self.dimensions.iterkeys():
                ncfile.createVariable(coordname, 'd', (coordname,))
                
            for varname, vardims in self.vardims.iteritems():
                ncfile.createVariable(varname, 'd', vardims)
            
            for coordname, dimsize in self.dimensions.iteritems():
                coordvar = ncfile.variables[coordname]
                for attrname, attrval in self.varattribs[coordname].iteritems():
                    setattr(coordvar, attrname, attrval)
                coordvar[:] = self.variables[filename][coordname]

            for varname, vardims in self.vardims.iteritems():
                var = ncfile.variables[varname]
                for attrname, attrval in self.varattribs[varname].iteritems():
                    setattr(var, attrname, attrval)
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
