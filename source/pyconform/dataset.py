"""
Dataset Interface Class

This file contains the interface classes to the input and output multi-file
datasets.

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from collections import OrderedDict
from numpy import dtype
from netCDF4 import Dataset as NC4Dataset


#===============================================================================
# DimensionInfo
#===============================================================================
class DimensionInfo(object):
    
    def __init__(self, name, size=None, unlimited=False):
        """
        Initializer
        
        Parameters:
            name (str): Dimension name
            size (int): Dimension size
            unlimited (bool): Whether the dimension is unlimited or not
        """
        self.name = str(name)
        self.size = int(size) if size else None        
        self.unlimited = bool(unlimited)

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.size != other.size:
            return False
        if self.unlimited != other.unlimited:
            return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        unlim_str = ', unlimited' if self.unlimited else ''
        return '{!r} [{}{}]'.format(self.name, self.size, unlim_str)
        
#=========================================================================
# VariableInfo
#=========================================================================
class VariableInfo(object):

    def __init__(self, name, 
                 datatype='float32', 
                 dimensions=(), 
                 attributes=OrderedDict(),
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
        self.definition = definition
        self.filename = filename

    def __eq__(self, other):
        if self.name != other.name:
            print '**** name: {} != {}'.format(self.name, other.name)
            return False
        if self.datatype != other.datatype:
            print '**** dtype: {} != {}'.format(self.datatype, other.datatype)
            return False
        if self.dimensions != other.dimensions:
            print '**** dims: {} != {}'.format(self.dimensions, other.dimensions)
            return False
        if self.attributes != other.attributes:
            print '**** attrs: {} != {}'.format(self.attributes, other.attributes)
            return False
        if self.definition != other.definition:
            print '**** def: {} != {}'.format(self.definition, other.definition)
            return False
        if self.filename != other.filename:
            print '**** fname: {} != {}'.format(self.filename, other.filename)
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        strval = 'Variable: {!r}'.format(self.name) + linesep
        strval += '   datatype: {!r}'.format(self.datatype) + linesep
        strval += '   dimensions: {!s}'.format(self.dimensions) + linesep
        if self.definition:
            strval += '   definition: {!r}'.format(self.definition) + linesep
        if self.filename:
            strval += '   filename: {!r}'.format(self.filename) + linesep
        if self.attributes:
            strval += '   attributes:' + linesep
            for aname, avalue in self.attributes.iteritems():
                strval += '      {}: {!r}'.format(aname, avalue) + linesep
        return strval

    def units(self):
        return self.attributes.get('units')

    def standard_name(self):
        return self.attributes.get('standard_name')


#=========================================================================
# Dataset
#=========================================================================
class Dataset(object):

    def __init__(self, name='',
                 dimensions=OrderedDict(), 
                 variables=OrderedDict(),
                 gattribs=OrderedDict()):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            dimensions (dict): Dictionary of dimension sizes
            variables (dict): Dictionary of VariableInfo objects defining
                the dataset
            gattribs (dict): Dictionary of attributes common to all files
                in the dataset
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

        if not isinstance(gattribs, dict):
            err_msg = ('Dataset {!r} global attributes must be given in a '
                       'dict').format(self.name)
            raise TypeError(err_msg)
        self.attributes = gattribs
                
    def get_dict(self):
        """
        Return the dictionary form of the Dataset definition
        
        Returns:
            dict: The ordered dictionary describing the dataset
        """
        dsdict = OrderedDict()
        dsdict['attributes'] = self.attributes
        dsdict['variables'] = OrderedDict()
        for vinfo in self.variables.itervalues():
            vdict = OrderedDict()
            vdict['datatype'] = vinfo.datatype
            vdict['dimensions'] = vinfo.dimensions
            if vinfo.definition:
                vdict['definition'] = vinfo.definition
            if vinfo.filename:
                vdict['filename'] = vinfo.filename
            if vinfo.attributes:
                vdict['attributes'] = vinfo.attributes
            dsdict['variables'][vinfo.name] = vdict
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
        if self.dimensions:
            return tuple(self.dimensions[d].size 
                         for d in self.variables[name].dimensions)
        else:
            return None
    
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
        variables = {}
        varfiles = {}
        dimensions = {}
        attributes = OrderedDict()
        for fname in filenames:

            try:
                ncfile = NC4Dataset(fname)
            except:
                err_msg = 'Could not open or read input file {!r}'.format(fname)
                raise RuntimeError(err_msg)
            
            # Check attributes
            for aname in ncfile.ncattrs():
                if aname not in attributes:
                    attributes[aname] = ncfile.getncattr(aname)

            # Check dimensions
            for dname, dobj in ncfile.dimensions.iteritems():
                dinfo = DimensionInfo(dobj.name, dobj.size, dobj.isunlimited())
                if dname in dimensions:
                    if dinfo != dimensions[dname]:
                        err_msg = ('Dimension {!r} in input file {!r} is '
                                   'different from expected dimension '
                                   '{!r}').format(dinfo, fname,
                                                  dimensions[dname])
                        raise ValueError(err_msg)
                else:
                    dimensions[dname] = dinfo

            # Check variables
            for vname, vobj in ncfile.variables.iteritems():
                vattrs = OrderedDict()
                for vattr in vobj.ncattrs():
                    vattrs[vattr] = vobj.getncattr(vattr)
                vinfo = VariableInfo(name=vname,
                                     datatype='{!s}'.format(vobj.dtype),
                                     dimensions=vobj.dimensions,
                                     attributes=vattrs)

                if vname in variables:
                    if vinfo != variables[vname]:
                        err_msg = ('{}Variable {!r} in file {!r}:'
                                   '{}{}'
                                   'differs from same variable in other files:'
                                   '{}{}').format(linesep, vname, fname,
                                                  linesep, vinfo,
                                                  linesep, variables[vname])
                        raise ValueError(err_msg)
                    else:
                        varfiles[vname].append(fname)
                else:
                    variables[vname] = vinfo
                    varfiles[vname] = [fname]
                
            ncfile.close()

        # Check variable file occurrences
        for vname, vfiles in varfiles.iteritems():
            if len(vfiles) == 1:
                variables[vname].filename = vfiles[0]
            elif len(vfiles) < len(filenames):
                missing_files = set(filenames) - set(vfiles)
                wrn_msg = ('Variable {!r} appears to be metadata but does '
                           'not appear in the files:{}'
                           '{}').format(vname, linesep, missing_files)
                raise RuntimeWarning(wrn_msg)

        super(InputDataset, self).__init__(name, dimensions,
                                           variables, attributes)
        
        
#=========================================================================
# OutputDataset
#=========================================================================
class OutputDataset(Dataset):

    def __init__(self, name='output', dsdict=OrderedDict()):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            dsdict (dict): Dictionary describing the dataset variables
        """
        attributes = dsdict['attributes']
        print 'attributes', attributes
        variables = OrderedDict()
        print 'variables', variables
        for vname, vdict in dsdict['variables'].iteritems():
            kwargs = {}
            if 'dimensions' not in vdict:
                err_msg = ('Dimensions are required for variable '
                           '{!r}').format(vname)
                raise ValueError(err_msg)
            else:
                kwargs['dimensions'] = vdict['dimensions']
            if 'definition' not in vdict:
                err_msg = ('Definition is required for output variable '
                           '{!r}').format(vname)
                raise ValueError(err_msg)
            else:
                kwargs['definition'] = vdict['definition']
            if 'datatype' in vdict:
                kwargs['datatype'] = vdict['datatype']
            if 'attributes' in vdict:
                kwargs['attributes'] = vdict['attributes']
            if 'filename' in vdict:
                kwargs['filename'] = vdict['filename']
            variables[vname] = VariableInfo(vname, **kwargs)
        super(OutputDataset, self).__init__(name, variables=variables,
                                            gattribs=attributes)
