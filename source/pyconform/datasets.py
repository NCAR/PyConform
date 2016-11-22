"""
DatasetDesc Interface Class

This file contains the interface classes to the input and output multi-file
datasets.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from os import linesep
from os.path import exists
from collections import OrderedDict
from numpy import dtype, array
from netCDF4 import Dataset as NC4Dataset
from cf_units import Unit


#===================================================================================================
# DimensionDesc
#===================================================================================================
class DimensionDesc(object):
    """
    Descriptor for a dimension in a DatasetDesc
    
    Contains the name of the dimensions, its size, and whether the dimension is limited or
    unlimited.
    """

    def __init__(self, name, size=None, unlimited=None):
        """
        Initializer
        
        Parameters:
            name (str): Dimension name
            size (int): Dimension size
            unlimited (bool): Whether the dimension is unlimited or not
        """
        self._name = name
        self._size = int(size) if size is not None else None
        self._unlimited = bool(unlimited)

    @property
    def name(self):
        """Name of the dimension"""
        return self._name

    @property
    def size(self):
        """Numeric size of the dimension (if set)"""
        return self._size

    @property
    def unlimited(self):
        """Boolean indicating whether the dimension is unlimited or not"""
        return self._unlimited

    def is_set(self):
        """
        Return True if the dimension size and unlimited status is set, False otherwise
        """
        return self._size is not None

    def unset(self):
        """
        Unset the dimension's size and unlimited status
        """
        self._size = None
        self._unlimited = False

    def set(self, dd):
        """
        Set the size and unlimited status from another DimensionDesc
        
        Parameters:
            dd (DimensionDesc): The DimensionDesc from which to set the size and unlimited status
        """
        if not isinstance(dd, DimensionDesc):
            err_msg = ('Cannot set dimension {!r} from object of type {!r}, needs to be a '
                       'DimensionDesc.').format(self.name, type(dd))
            raise TypeError(err_msg)
        self._size = dd.size
        self._unlimited = dd.unlimited

    def __eq__(self, other):
        if not isinstance(other, DimensionDesc):
            return False
        if self.name != other.name:
            return False
        if self.is_set() and other.is_set():
            if self.size != other.size:
                return False
            if self.unlimited != other.unlimited:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '{!r} [{}{}]'.format(self.name, self.size, '+' if bool(self.unlimited) else '')


#===================================================================================================
# VariableDesc
#===================================================================================================
class VariableDesc(object):
    """
    Descriptor for a variable in a dataset
    
    Contains the variable name, string datatype, dimensions tuple, attributes dictionary,
    and a string definition (how to construct the data for the variable) or data array (if
    the data is contained in the variable declaration).
    """

    def __init__(self, name, datatype='float32', dimensions=(), definition=None, attributes={}):
        """
        Initializer

        Parameters:
            name (str): Name of the variable
            datatype (str): Numpy datatype of the variable data
            dimensions (tuple): Tuple of DimensionDesc objects for the variable
            definition: String or data definition of variable
            attributes (dict): Dictionary of variable attributes
        """
        self._name = name
        self._datatype = str(dtype(datatype))
        self.definition = definition

        if not isinstance(dimensions, (list, tuple)):
            err_msg = ('Dimensions for variable {!r} cannot be of type {!r}, must be a list or '
                       'tuple').format(self.name, type(dimensions))
            raise TypeError(err_msg)
        for i, obj in enumerate(dimensions):
            if not isinstance(obj, DimensionDesc):
                err_msg = ('Dimension {} for variable {!r} cannot be of type {!r}, must be a '
                           'DimensionDesc').format(i, self.name, type(obj))
                raise TypeError(err_msg)
        self._dimensions = OrderedDict((obj.name, obj) for obj in dimensions)

        if not isinstance(attributes, dict):
            raise TypeError('Attributes for variable {!r} not dict'.format(name))
        self._attributes = attributes

    @property
    def name(self):
        """Name of the variable"""
        return self._name

    @property
    def datatype(self):
        """String datatype of the variable"""
        return self._datatype

    @property
    def attributes(self):
        """Variable attributes dictionary"""
        return self._attributes

    @property
    def dimensions(self):
        """Dictionary of dimension descriptors for dimensions on which the variable depends"""
        return self._dimensions

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.datatype != other.datatype:
            return False
        if self.dimensions != other.dimensions:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        strvals = ['Variable: {!r}'.format(self.name)]
        strvals += ['   datatype: {!r}'.format(self.datatype)]
        strvals += ['   dimensions: {!s}'.format(self.dimensions.keys())]
        if self.definition is not None:
            strvals += ['   definition: {!r}'.format(self.definition)]
        if len(self.attributes) > 0:
            strvals += ['   attributes:']
            for aname, avalue in self.attributes.iteritems():
                strvals += ['      {}: {!r}'.format(aname, avalue)]
        return linesep.join(strvals)

    def units(self):
        """Retrieve the units attribute, if it exists, otherwise 1"""
        return self.attributes.get('units', 1)

    def calendar(self):
        """Retrieve the calendar attribute, if it exists, otherwise None"""
        return self.attributes.get('calendar', None)

    def cfunits(self):
        """Construct a cf_units.Unit object from the units/calendar attributes"""
        return Unit(self.units(), calendar=self.calendar())


#===================================================================================================
# FileDesc
#===================================================================================================
class FileDesc(object):
    """
    A class describing the contents of a single dataset file
    
    In simplest terms, the FileDesc contains the header information for a single NetCDF file.  It
    contains the name of the file, the type of the file, a dictionary of global attributes in the
    file, a dict of DimensionDesc objects, and a dict of VariableDesc objects. 
    """

    def __init__(self, name, fmt='NETCDF4_CLASSIC', variables=(), attributes={}):
        """
        Initializer
        
        Parameters:
            name (str): String name of the file (i.e., a path name or file name)
            fmt (str):  String defining the NetCDF file format (one of 'NETCDF4',
                'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC', 'NETCDF3_64BIT_OFFSET' or 
                'NETCDF3_64BIT_DATA')
            variables (tuple):  Tuple of VariableDesc objects describing the file variables            
            attributes (dict):  Dict of global attributes in the file
        """
        self._name = name

        if fmt not in ('NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC',
                          'NETCDF3_64BIT_OFFSET', 'NETCDF3_64BIT_DATA'):
            err_msg = 'NetCDF file format {!r} unrecognized in file {!r}'.format(fmt, self.name)
            raise TypeError(err_msg)
        self._format = fmt

        if not isinstance(variables, (list, tuple)):
            err_msg = ('Variables in file {!r} cannot be of type {!r}, needs to be list or '
                       'tuple').format(self.name, type(variables))
            raise TypeError(err_msg)
        for obj in variables:
            if not isinstance(obj, VariableDesc):
                err_msg = ('Variable {!r} in file {!r} cannot be of type {!r}, needs to be a '
                           'VariableDesc').format(obj, self.name, type(obj))
                raise TypeError(err_msg)
        self._variables = OrderedDict((obj.name, obj) for obj in variables)

        self._dimensions = OrderedDict()
        for vdesc in self.variables.itervalues():
            for dname, ddesc in vdesc.dimensions.iteritems():
                if dname in self.dimensions:
                    if not self.dimensions[dname].is_set() and ddesc.is_set():
                        self.dimensions[dname].set(ddesc)
                    if self.dimensions[dname] == ddesc:
                        vdesc.dimensions[dname] = self.dimensions[dname]
                    else:
                        err_msg = ('Dimension {!r} is inconsistent across variables in file '
                                   '{!r}').format(dname, self.name)
                        raise ValueError(err_msg)
                else:
                    self.dimensions[dname] = ddesc

        if not isinstance(attributes, dict):
            err_msg = ('Global attributes in file {!r} cannot be of type {!r}, needs to be a '
                       'dict').format(self.name, type(attributes))
            raise TypeError(err_msg)
        self._attributes = attributes

    @property
    def name(self):
        """Name of the file"""
        return self._name

    def exists(self):
        """Whether the file exists or not"""
        return exists(self.name)

    @property
    def format(self):
        """Format of the file"""
        return self._format

    @property
    def attributes(self):
        """Dictionary of global attributes of the file"""
        return self._attributes

    @property
    def dimensions(self):
        """Dictionary of dimension descriptors associated with the file"""
        return self._dimensions

    @property
    def variables(self):
        """Dictionary of variable descriptors associated with the file"""
        return self._variables

#===================================================================================================
# DatasetDesc
#===================================================================================================
class DatasetDesc(object):
    """
    A class describing a self-consistent set of dimensions and variables in one or more files
    
    In simplest terms, a single NetCDF file is a dataset.  Hence, the DatasetDesc object can be
    viewed as a simple container for the header information of a NetCDF file.  However, the
    DatasetDesc can span multiple files, as long as dimensions and variables are consistent across
    all of the files in the DatasetDesc.
    
    Self-consistency is defined as:
        1. Dimensions with names that appear in multiple files must all have the same size and
           limited/unlimited status, and
        2. Variables with names that appear in multiple files must have the same datatype and
           dimensions, and they must refer to the same data.
    """

    def __init__(self, name='dataset', files=()):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            files (tuple): Tuple of FileDesc objects contained in the dataset
        """
        self._name = name
        self._dimensions = OrderedDict()
        self._variables = OrderedDict()

        if not isinstance(files, (list, tuple)):
            err_msg = ('File descriptors in DatasetDesc {!r} cannot be of type {!r}, needs to be '
                       'list or tuple').format(self.name, type(files))
            raise TypeError(err_msg)
        for obj in files:
            if not isinstance(obj, FileDesc):
                err_msg = ('File descriptor {!r} in DatasetDesc {!r} cannot be of type {!r}, '
                           'needs to be a FileDesc').format(obj, self.name, type(obj))
                raise TypeError(err_msg)
        self._files = OrderedDict((obj.name, obj) for obj in files)

        # Check self-consistency and cross-reference
        for fname, fdesc in self._files.iteritems():

            for vname in fdesc.variables:
                if vname in self.variables:
                    if self.variables[vname] == fdesc.variables[vname]:
                        fdesc.variables[vname] = self.variables[vname]
                    else:
                        err_msg = ('Variable {!r} in file {!r} is inconsistent with variables '
                                   'in other files').format(vname, fname)
                        raise ValueError(err_msg)
                else:
                    self.variables[vname] = fdesc.variables[vname]

                for dname in fdesc.variables[vname].dimensions:
                    if dname in self.dimensions:
                        if not self.dimensions[dname].is_set() and fdesc.variables[vname].dimensions[dname].is_set():
                            self.dimensions[dname].set(fdesc.variables[vname].dimensions[dname])
                        if self.dimensions[dname] == fdesc.variables[vname].dimensions[dname]:
                            fdesc.dimensions[dname] = self.dimensions[dname]
                        else:
                            err_msg = ('Dimension {!r} is inconsistent across variables in file '
                                       '{!r}').format(dname, self.name)
                            raise ValueError(err_msg)
                    else:
                        self.dimensions[dname] = fdesc.variables[vname].dimensions[dname]

    @property
    def name(self):
        """Name of the dataset (optional)"""
        return self._name

    @property
    def dimensions(self):
        """Dicitonary of dimension descriptors contained in the dataset"""
        return self._dimensions

    @property
    def variables(self):
        """Dictionary of variable descriptors contained in the dataset"""
        return self._variables

    @property
    def files(self):
        """Dictionary of file descriptors contained in the dataset"""
        return self._files


#===================================================================================================
# InputDatasetDesc
#===================================================================================================
class InputDatasetDesc(DatasetDesc):
    """
    DatasetDesc that can be used as input (i.e., can be read from file)
    
    The InputDatasetDesc is a kind of DatasetDesc where all of the DatasetDesc information is read from 
    the headers of existing NetCDF files.  The files must be self-consistent according to the
    standard DatasetDesc definition.
    
    Variables in an InputDatasetDesc must have unset "definition" parameters, and the "filenames"
    parameter will contain the names of files from which the variable data can be read.  
    """

    def __init__(self, name='input', filenames=[]):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            filenames (list): List of filenames in the dataset
        """
        files = []

        # Loop over all of the input filenames
        for fname in filenames:
            with NC4Dataset(fname) as ncfile:

                # Get file format
                ffmt = ncfile.file_format

                # Get global attributes
                fattrs = OrderedDict()
                for aname in ncfile.ncattrs():
                    fattrs[aname] = ncfile.getncattr(aname)

                # Get the file dimensions
                fdims = OrderedDict()
                for dname, dobj in ncfile.dimensions.iteritems():
                    fdims[dname] = DimensionDesc(dname, size=dobj.size, unlimited=dobj.isunlimited())

                # Parse variables
                fvars = []
                for vname, vobj in ncfile.variables.iteritems():

                    vattrs = OrderedDict()
                    for vattr in vobj.ncattrs():
                        vattrs[vattr] = vobj.getncattr(vattr)

                    vdims = [fdims[dname] for dname in vobj.dimensions]

                    fvars.append(VariableDesc(vname, datatype='{!s}'.format(vobj.dtype),
                                              dimensions=vdims, attributes=vattrs))

                files.append(FileDesc(fname, fmt=ffmt, attributes=fattrs, variables=fvars))

        # Call the base class initializer to check self-consistency
        super(InputDatasetDesc, self).__init__(name, files=files)


#===================================================================================================
# OutputDatasetDesc
#===================================================================================================
class OutputDatasetDesc(DatasetDesc):
    """
    DatasetDesc that can be used for output (i.e., to be written to files)
    
    The OutputDatasetDesc contains all of the header information needed to write a DatasetDesc to
    files.  Unlike the InputDatasetDesc, it is not assumed that all of the variable and dimension
    information can be found in existing files.  Instead, the OutputDatasetDesc contains a minimal
    subset of the output file headers, and information about how to construct the variable data
    and dimensions by using the 'definition' parameter of the variables.

    The information to define an OutputDatasetDesc must be specified as a nested dictionary,
    where the first level of the dictionary are unique names of variables in the dataset.  Each
    named variable defines another nested dictionary.
    
    Each 'variable' dictionary is assued to contain the following:
        1. 'attributes': A dictionary of the variable's attributes
        2. 'datatype': A string specifying the type of the variable's data
        3. 'dimensions': A tuple of names of dimensions upon which the variable depends
        4. 'definition': Either a string mathematical expression representing how to construct
            the variable's data from input variables or functions, or an array declaring the actual
            data from which to construct the variable
        5. 'file': A dictionary containing a string 'filename', a string 'format' (which can be
            one of 'NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC', 'NETCDF3_64BIT_OFFSET' or 
            'NETCDF3_64BIT_DATA'), a dictionary of 'attributes', and a list of 'metavars' specifying
            the names of other variables that should be added to the file, in addition to obvious
            metadata variables and the variable containing the 'file' section.
    """

    def __init__(self, name='output', dsdict=OrderedDict()):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            dsdict (dict): Dictionary describing the dataset variables
        """
        # Initialize a dictionary of file sections
        files = {}

        # Look over all variables in the dataset dictionary
        variables = OrderedDict()
        metavars = []
        for vname, vdict in dsdict.iteritems():
            vkwds = {}

            # Get the variable attributes, if they are defined
            if 'attributes' in vdict:
                vkwds['attributes'] = vdict['attributes']

            # Get the datatype of the variable, otherwise defaults to VariableDesc default
            vkwds['datatype'] = 'float32'
            if 'datatype' in vdict:
                vkwds['datatype'] = vdict['datatype']

            # Get either the 'definition' or the 'data' of the variables
            if 'definition' in vdict:
                vdef = vdict['definition']
                if isinstance(vdef, basestring):
                    vkwds['definition'] = vdef
                    vshape = None
                else:
                    vdat = array(vdef, dtype=vkwds['datatype'])
                    vshape = vdat.shape
                    vkwds['definition'] = vdat
            else:
                err_msg = ('Definition is required for output variable {!r} in dataset '
                           '{!r}').format(vname, name)
                raise ValueError(err_msg)

            # Get the dimensions of the variable (REQUIRED)
            if 'dimensions' in vdict:
                if vshape is None:
                    vkwds['dimensions'] = tuple(DimensionDesc(d) for d in vdict['dimensions'])
                else:
                    vkwds['dimensions'] = tuple(DimensionDesc(d, s) for d, s in
                                                zip(vdict['dimensions'], vshape))
            else:
                err_msg = ('Dimensions are required for variable {!r} in dataset '
                           '{!r}').format(vname, name)
                raise ValueError(err_msg)

            variables[vname] = VariableDesc(vname, **vkwds)

            # Parse the file section (if present)
            if 'file' in vdict:
                fdict = vdict['file']

                if 'filename' not in fdict:
                    err_msg = ('Filename is required in file section of variable {!r} in dataset '
                               '{!r}').format(vname, name)
                    raise ValueError(err_msg)

                fname = fdict['filename']
                if fname in files:
                    err_msg = ('Variable {!r} in dataset {!r} claims to own file '
                               '{!r}, but this file is already owned by variable '
                               '{!r}').format(vname, name, fname, files[fname]['variables'][0])
                    raise ValueError(err_msg)
                files[fname] = {}

                if 'format' in fdict:
                    files[fname]['fmt'] = fdict['format']

                if 'attributes' in fdict:
                    files[fname]['attributes'] = fdict['attributes']

                files[fname]['variables'] = [vname]

                if 'metavars' in fdict:
                    for mvname in fdict['metavars']:
                        if mvname not in files[fname]['variables']:
                            files[fname]['variables'].append(mvname)

            else:
                metavars.append(vname)

        # Loop through all found files and create the file descriptors
        filedescs = []
        for fname, fdict in files.iteritems():

            # Get the variable descriptors for each variable required to be in the file
            vlist = [variables[vname] for vname in fdict['variables']]

            # Get the unique list of dimension names for required by these variables
            fdims = set()
            for vdesc in vlist:
                for dname in vdesc.dimensions:
                    fdims.add(dname)

            # Loop through all the variable names identified as metadata (i.e., no 'file')
            for mvname in metavars:
                if mvname not in fdict['variables']:
                    vdesc = variables[mvname]

                    # Include this variable in the file only if all of its dimensions are included
                    if set(vdesc.dimensions.keys()).issubset(fdims):
                        vlist.append(vdesc)

            fdict['variables'] = vlist
            filedescs.append(FileDesc(fname, **fdict))

        # Call the base class to run self-consistency checks
        super(OutputDatasetDesc, self).__init__(name, files=filedescs)
