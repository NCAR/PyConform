"""
Dataset Interface Class

This file contains the interface classes to the input and output multi-file
datasets.

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import OrderedDict
from copy import deepcopy
from numpy import dtype

import netCDF4


#===============================================================================
# DimensionInfo
#===============================================================================
class DimensionInfo(object):
    
    def __init__(self, name, size, unlimited=False):
        """
        Initializer
        
        Parameters:
            name (str): Dimension name
            size (int): Dimension size
            unlimited (bool): Whether the dimension is unlimited or not
        """
        self.name = str(name)
        self.size = int(size)
        self.unlimited = bool(unlimited)

        
#=========================================================================
# VariableInfo
#=========================================================================
class VariableInfo(object):

    def __init__(self, name, 
                 datatype='float64', 
                 dimensions=(), 
                 attributes={},
                 definition=None,
                 filename=None):
        """
        Initializer

        Parameters:
            name (str): Name of the variable
            datatype (str): Numpy datatype of the variable data
            dimensions (tuple): Tuple of dimension names in variable
            attributes (dict): Dictionary of variable attributes
            definition (str): Optional string definition of variable
            filename (str): Filename for read/write of variable
        """
        self.name = str(name)
        self.datatype = '{!s}'.format(dtype(datatype))
        self.dimensions = dimensions
        self.attributes = attributes
        self.definition = str(definition)
        self.filename = str(filename)

    def __eq__(self, other):
        if self.name != other.name:
            print 'Names: {} != {}'.format(self.name, other.name)
            return False
        if self.datatype != other.datatype:
            print 'Data Type: {} != {}'.format(self.datatype, other.datatype)
            return False
        if self.dimensions != other.dimensions:
            print 'Dimensions: {} != {}'.format(self.dimensions, other.dimensions)
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def units(self):
        return self.attributes.get('units')

    def standard_name(self):
        return self.attributes.get('standard_name')


#=========================================================================
# Dataset
#=========================================================================
class Dataset(object):

    def __init__(self, name='', dimensions={}, variables={}):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            dimensions (dict): Dictionary of dimension sizes
            variables (dict): Dictionary of VariableInfo objects defining
                the dataset
        """
        self.name = str(name)
        
        if not isinstance(variables, dict):
            err_msg = ('Dataset {!r} variables must be given in a '
                       'dict').format(self.name)
            raise TypeError(err_msg)
        for vinfo in variables.itervalues():
            if not isinstance(vinfo, VariableInfo):
                err_msg = ('Dataset {!r} variables must be of VariableInfo '
                           'type').format(self.name)
                raise TypeError(err_msg)            
            if not vinfo.units():
                err_msg = ('Variable {!r} has no units in Dataset '
                           '{!r}').format(vinfo.name, self.name)
                raise ValueError(err_msg)
            if not vinfo.standard_name():
                err_msg = ('Variable {!r} has no standard_name in Dataset '
                           '{!r}').format(vinfo.name, self.name)
                raise ValueError(err_msg)
        self.variables = variables

        if not isinstance(dimensions, dict):
            err_msg = ('Dataset {!r} dimensions must be given in a '
                       'dict').format(self.name)
            raise TypeError(err_msg)
        for dinfo in dimensions.itervalues():
            if not isinstance(dinfo, DimensionInfo):
                err_msg = ('Dataset {!r} dimensions must be DimensionInfo '
                           'type').format(self.name)
                raise TypeError(err_msg)
        self.dimensions = dimensions
                
    def get_dict(self):
        """
        Return the dictionary form of the Dataset definition
        
        Returns:
            OrderedDict: The ordered dictionary describing the dataset
        """
        dsdict = OrderedDict()
        for vinfo in self.variables.itervalues():
            vdict = OrderedDict()
            vdict['datatype'] = vinfo.datatype
            vdict['dimensions'] = vinfo.dimensions
            if vinfo.attributes:
                vdict['attributes'] = vinfo.attributes
            if vinfo.definition:
                vdict['definition'] = vinfo.definition
            if vinfo.filename:
                vdict['filename'] = vinfo.filename
            dsdict[vinfo.name] = vdict
        return dsdict
    
    def get_shape(self, name):
        """
        Get the shape of a variable in the dataset
        
        Parameters:
            name (str): name of the variable
        """
        if name not in self.variables:
            err_msg = 'Variable {!r} not in Dataset {!r}'.format(name, self.name)
            raise KeyError(err_msg)
        shape = [self.dimensions[d].size for d in self.variables[name].dimensions]
        return tuple(shape)
    
    def get_size(self, name):
        """
        Get the size of a variable in the dataset
        
        This is based on dimensions, so a variable that has no dimensions
        returns a size of 0.
        
        Parameters:
            name (str): name of the variable
        """
        return sum(self.get_size(name))
    
    def get_bytesize(self, name):
        """
        Get the size in bytes of a variable in the dataset
        
        If the size of the variable returns 0, then it assumes it is a
        single-value (non-array) variable.
        
        Parameters:
            name (str): name of the variable
        """
        size = self.get_size(name)
        itembytes = dtype(self.variables[name].datatype).itemsize
        if size == 0:
            return itembytes
        else:
            return itembytes * size
    

#=========================================================================
# InputDataset
#=========================================================================
class InputDataset(Dataset):

    def __init__(self, name='input', filenames=[]):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            filenames (list): List of filenames in the dataset
        """
        variables = []
        dimensions = {}
        for fname in filenames:
            try:
                ncfile = Dataset(fname)
                for dname, dobj in ncfile.dimensions.iteritems():
                    if dname not in dimensions:
                        if dobj.isunlimited():
                            dimensions[dname] = [dobj.size]
                        else:
                            dimensions[dname] = dobj.size
                    else:
                        err_msg = ('Dimension {!r} in input file {!r} '
                                   'does not match expected dimension '
                                   '{!r}').format(dname, fname,
                                                  dimensions[dname])
                        if dobj.isunlimited():
                            if dimensions[dname] != [dobj.size]:
                                raise ValueError(err_msg)
                        else:
                            if dimensions[dname] != dobj.size:
                                raise ValueError(err_msg)
                for vname, vobj in ncfile.variables.iteritems():
                    datatype = '{!s}'.format(vobj.dtype)
                    dimensions = vobj.dimensions
                    attributes = OrderedDict()
                    for attr in vobj.ncattrs:
                        attributes[attr] = vobj.getncattr(attr)
                    variables.append(VariableInfo(name=vname,
                                                  datatype=datatype,
                                                  dimensions=dimensions,
                                                  attributes=attributes,
                                                  filename=fname))
                ncfile.close()
            except:
                err_msg = 'Could not open or read input file {!r}'.format(fname)
                raise RuntimeError(err_msg)
        super(InputDataset, self).__init__(name, dimensions, variables)
        
        
#=========================================================================
# OutputDataset
#=========================================================================
class OutputDataset(Dataset):

    def __init__(self, name='output', dsdict=OrderedDict(),
                 prefix='conform.', suffix='.nc'):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            dsdict (dict): Dictionary describing the dataset variables
            prefix (str): String prefix to output filenames
            suffic (str): String suffix to output filenames 
        """
        variables = []
        for vname, vdict in dsdict:
            kwargs = {'dimensions': vdict['dimensions'],
                      'definition': vdict['definition']}
            if 'attributes' in vdict:
                kwargs['attributes'] = vdict['attributes']
            if 'datatype' in vdict:
                kwargs['datatype'] = vdict['datatype']
            filename = '{}{}{}'.format(prefix, vname, suffix)            
            variables.append(VariableInfo(vname, vdict['datatype'],
                                          vdict['dimensions'], 
                                          vdict['attributes'],
                                          vdict['definition'],
                                          filename))

