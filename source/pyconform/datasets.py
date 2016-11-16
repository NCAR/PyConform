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
from numpy import dtype, array, array_equal
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

    def __init__(self, name, size=None, unlimited=None, files=None, variables=None):
        """
        Initializer
        
        Parameters:
            name (str): Dimension name
            size (int): Dimension size
            unlimited (bool): Whether the dimension is unlimited or not
            files (tuple): FileDesc objects in which the dimension is defined
        """
        self._name = name
        self._size = int(size) if size else None
        self._unlimited = bool(unlimited) if unlimited else None

        if files is not None:
            if not isinstance(files, (list, tuple)):
                raise TypeError(('Files for DimensionsDesc {!r} must be given as a list or '
                                 'tuple').format(name))
            for obj in files:
                if not isinstance(obj, FileDesc):
                    raise TypeError(('File {!r} associated with DimensionDesc {!r} must be '
                                     'a FileDesc object').format(obj, name))
            self._files = OrderedDict((obj.name, obj) for obj in files)
        else:
            self._files = OrderedDict()

        if variables is not None:
            if not isinstance(variables, (list, tuple)):
                raise TypeError(('Variables for DimensionsDesc {!r} must be given as a list or '
                                 'tuple').format(name))
            for obj in variables:
                if not isinstance(obj, VariableDesc):
                    raise TypeError(('Variable {!r} associated with DimensionDesc {!r} must be '
                                     'a VariableDesc object').format(obj, name))
            self._variables = OrderedDict((obj.name, obj) for obj in variables)
        else:
            self._variables = OrderedDict()

    @property
    def name(self):
        """Name of the dimension"""
        return self._name

    @property
    def size(self):
        """Numeric size of the dimension"""
        return self._size

    @property
    def unlimited(self):
        """Boolean indicating whether the dimension is unlimited or not"""
        return self._unlimited

    @property
    def files(self):
        """Dictionary of file descriptors with which the dimension is associated"""
        return self._files

    @property
    def variables(self):
        """Dictionary of variable descriptors with which the dimension is associated"""
        return self._variables

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
        return '{!r} [{}{}]'.format(self.name, self.size, '+' if bool(self.unlimited) else '')


#===================================================================================================
# VariableDesc
#===================================================================================================
class VariableDesc(object):
    """
    Descriptor for a variable in a dataset
    
    Contains the variable name, string datatype, dimensions tuple, attributes dictionary,
    name of the file in which the variable data can be found or is to be written (i.e., for
    time-series variables), and a string definition (how to construct the data for the variable)
    or data array (if the data is contained in the variable declaration).
    """

    def __init__(self, name, datatype='float32', definition=None,
                 attributes=OrderedDict(), dimensions=(), files=None):
        """
        Initializer

        Parameters:
            name (str): Name of the variable
            datatype (str): Numpy datatype of the variable data
            definition: String or data definition of variable
            attributes (dict): Dictionary of variable attributes
            dimensions (tuple): Tuple of DimensionDesc objects for the variable
            files (tuple): Tuple of FileDesc objects with which the variable is associated
        """
        self._name = name
        self._datatype = str(dtype(datatype))
        self._definition = definition

        if not isinstance(attributes, dict):
            raise TypeError('Attributes for variable {!r} must be given as a dict'.format(name))
        self._attributes = attributes

        if not isinstance(dimensions, (list, tuple)):
            raise TypeError(('Dimensions for variable {!r} must be given as a tuple or '
                             'list').format(name))
        for obj in dimensions:
            if not isinstance(obj, DimensionDesc):
                raise TypeError(('Dimension for variable {!r} must be DimensionDesc '
                                 'objects').format(name))
        self._dimensions = OrderedDict((obj.name, obj) for obj in dimensions)

        if files is not None:
            if not isinstance(files, (list, tuple)):
                raise TypeError(('Files for DimensionsDesc {!r} must be given as a list or '
                                 'tuple').format(name))
            for f in files:
                if not isinstance(f, FileDesc):
                    raise TypeError(('File {!r} associated with DimensionDesc {!r} must be '
                                     'a FileDesc object').format(f, name))
            self._files = OrderedDict((obj.name, obj) for obj in files)
        else:
            self._files = OrderedDict()

    @property
    def name(self):
        """Name of the variable"""
        return self._name

    @property
    def datatype(self):
        """String datatype of the variable"""
        return self._datatype

    @property
    def definition(self):
        """String or data definition (if defined) or None"""
        return self._definition

    @property
    def attributes(self):
        """Variable attributes dictionary"""
        return self._attributes

    @property
    def dimensions(self):
        """Dictionary of dimension descriptors for dimensions on which the variable depends"""
        return self._dimensions

    @property
    def files(self):
        """Dictionary of file descriptors with which the variable is associated"""
        return self._files

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if self.datatype != other.datatype:
            return False
        if self.dimensions != other.dimensions:
            return False
        for k, v in other.attributes.iteritems():
            if k not in self.attributes:
                return False
            elif not array_equal(v, self.attributes[k]):
                return False
        if not array_equal(self.definition, other.definition):
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
        if len(self.files) > 0:
            strvals += ['   filenames: {!r}'.format(self.files.keys())]
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

    def __init__(self, name, fmt='NETCDF4_CLASSIC', attributes=OrderedDict(),
                 dimensions=(), variables=()):
        """
        Initializer
        
        Parameters:
            name (str): String name of the file (i.e., a path name or file name)
            fmt (str):  String defining the NetCDF file format (one of 'NETCDF4',
                'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC', 'NETCDF3_64BIT_OFFSET' or 
                'NETCDF3_64BIT_DATA')
            attributes (dict):  Dict of global attributes in the file
            dimensions (tuple):  Tuple of DimensionDesc objects describing the file dimensions
            variables (tuple):  Tuple of VariableDesc objects describing the file variables            
        """
        self._name = name

        if fmt not in ('NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_CLASSIC',
                          'NETCDF3_64BIT_OFFSET', 'NETCDF3_64BIT_DATA'):
            raise TypeError(('Unrecognized NetCDF file format {!r} for '
                             'file {!r}').format(fmt, name))
        self._format = fmt

        if not isinstance(attributes, dict):
            raise TypeError(('Global file attributes must be given as a '
                             'dict for file {!r}').format(name))
        self._attributes = attributes

        if not isinstance(dimensions, (list, tuple)):
            raise TypeError(('File dimensions must be given as a '
                             'list or tuple for file {!r}').format(name))
        for obj in dimensions:
            if not isinstance(obj, DimensionDesc):
                raise TypeError(('Dimension {!r} in file {!r} must be given as a '
                                 'DimensionDesc').format(obj, name))
        self._dimensions = OrderedDict((obj.name, obj) for obj in dimensions)

        if not isinstance(variables, (list, tuple)):
            raise TypeError(('File variables must be given as a '
                             'list or tuple for file {!r}').format(name))
        for obj in variables:
            if not isinstance(obj, VariableDesc):
                raise TypeError(('Dimension {!r} in file {!r} must be given as a '
                                 'VariableDesc').format(obj, name))
        self._variables = OrderedDict((obj.name, obj) for obj in variables)

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

        if not isinstance(files, (list, tuple)):
            raise TypeError(('File descriptors in DatasetDesc {!r} must be given as a list or '
                             'tuple').format(name))
        for obj in files:
            if not isinstance(obj, FileDesc):
                raise TypeError(('File descriptor in DatasetDesc {!r} must be a '
                                 'FileDesc').format(name))
        self._files = OrderedDict((obj.name, obj) for obj in files)

        # Declare objects for cross-referenced database
        self._attributes = OrderedDict()
        self._dimensions = OrderedDict()
        self._variables = OrderedDict()

        # Check self-consistency and fill database
        for fname, fdesc in self._files.iteritems():

            self._attributes.update(fdesc.attributes)

            for dname in fdesc.dimensions:
                if dname in self._dimensions:
                    if self._dimensions[dname] == fdesc.dimensions[dname]:
                        fdesc.dimensions[dname] = self._dimensions[dname]
                    else:
                        dfiles = tuple(f for f in fdesc.dimensions[dname].files)
                        raise ValueError(('Dimension {!r} in file {!r} is inconsistent '
                                          'with dimension of same name in files '
                                          '{!r}').format(dname, fname, dfiles))
                else:
                    self._dimensions[dname] = fdesc.dimensions[dname]
                self._dimensions[dname].files[fname] = fdesc

            for vname in fdesc.variables:
                if vname in self._variables:
                    if self._variables[vname] == fdesc.variables[vname]:
                        fdesc.variables[vname] = self._variables[vname]
                    else:
                        vfiles = tuple(f for f in fdesc.variables[vname].files)
                        raise ValueError(('Variable {!r} in file {!r} is inconsistent '
                                          'with variable of same name in files '
                                          '{!r}').format(vname, fname, vfiles))
                else:
                    self._variables[vname] = fdesc.variables[vname]
                self._variables[vname].files[fname] = fdesc

    @property
    def name(self):
        """Name of the dataset (optional)"""
        return self._name

    @property
    def attributes(self):
        """Global dataset attributes dictionary"""
        return self._attributes

    @property
    def dimensions(self):
        """Dicitonary of dimension descriptors contained in the dataset"""
        return self._dimensions

    @property
    def variables(self):
        """Dictionary of variable descriptors contained in the dataset"""
        return self._variables

    def get_dict(self):
        """
        Return the dictionary form of the DatasetDesc definition
        
        Returns:
            dict: The ordered dictionary describing the dataset
        """
        dsdict = OrderedDict()
        dsdict['attributes'] = self.attributes
        dsdict['variables'] = OrderedDict()
        for vname, vdesc in self.variables.iteritems():
            vdict = OrderedDict()
            vdict['datatype'] = vdesc.datatype
            vdict['dimensions'] = vdesc.dimensions.keys()
            if vdesc.definition is not None:
                vdict['definition'] = vdesc.definition
            if len(vdesc.files) > 0:
                vdict['filenames'] = vdesc.files.keys()
            if len(vdesc.attributes) > 0:
                vdict['attributes'] = vdesc.attributes
            dsdict['variables'][vname] = vdict
        return dsdict


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

                # Get global attributes
                fattrs = OrderedDict()
                for aname in ncfile.ncattrs():
                    fattrs[aname] = ncfile.getncattr(aname)

                # Parse dimensions
                fdims = OrderedDict((dname, DimensionDesc(dname, dobj.size, dobj.isunlimited()))
                                    for dname, dobj in ncfile.dimensions.iteritems())

                # Parse variables
                fvars = OrderedDict()
                for vname, vobj in ncfile.variables.iteritems():
                    vattrs = OrderedDict()
                    for vattr in vobj.ncattrs():
                        vattrs[vattr] = vobj.getncattr(vattr)
                    vdims = [fdims[dname] for dname in vobj.dimensions]
                    vdesc = VariableDesc(name=vname, datatype='{!s}'.format(vobj.dtype),
                                         attributes=vattrs, dimensions=vdims)
                    fvars[vname] = vdesc

                files.append(FileDesc(fname, attributes=fattrs, dimensions=fdims, variables=fvars))

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

    The information to define an OutputDatasetDesc must be specified as a two-level nested dictionary,
    where the first level of dictionaries contains:
        1. an 'attributes' dictionary declaring the global attributes of the dataset (which
           will be written to every file), and
        2. a 'variables' dictionary declaring the output variables to be written to files.
    
    Each 'variables' dictionary is assued to contain the following:
        1. 'attributes': A dictionary of the variable's attributes
        2. 'datatype': A string specifying the type of the variable's data
        3. 'dimensions': A tuple of names of dimensions upon which the variable depends
        4. 'definition': Either a string mathematical expression representing how to construct
           the variable's data from input variables or functions, or an array declaring the actual
           data from which to construct the variable
        5. 'filenames': The names of each file into which the variable will be written
    """

    def __init__(self, name='output', dsdict=OrderedDict()):
        """
        Initializer

        Parameters:
            name (str): String name to optionally give to a dataset
            dsdict (dict): Dictionary describing the dataset variables
        """
        # Retrieve the global attributes
        attributes = dsdict.get('attributes', OrderedDict())

        # Look over all variables in the input dictionary
        invars = dsdict.get('variables', OrderedDict())
        variables = OrderedDict()
        for vname, vdict in invars.iteritems():
            kwargs = {}

            # Get the variable attributes, if they are defined
            if 'attributes' in vdict:
                kwargs['attributes'] = vdict['attributes']

            # Get the dimensions of the variable (REQUIRED)
            if 'dimensions' in vdict:
                kwargs['dimensions'] = vdict['dimensions']
            else:
                err_msg = 'Dimensions are required for variable {!r}'.format(vname)
                raise ValueError(err_msg)

            # Get the datatype of the variable, otherwise defaults to VariableDesc default
            if 'datatype' in vdict:
                kwargs['datatype'] = vdict['datatype']

            # Get either the 'definition' or the 'data' of the variables
            if 'definition' in vdict:
                vdef = vdict['definition']
                if isinstance(vdef, basestring):
                    kwargs['definition'] = str(vdef)
                else:
                    kwargs['definition'] = array(vdef, dtype=vdict['datatype'])
            else:
                err_msg = 'Definition is required for output variable {!r}'.format(vname)
                raise ValueError(err_msg)

            # Get the filename (defined for time-series variables, None for metadata)
            if 'filenames' in vdict:
                kwargs['filenames'] = tuple(vdict['filenames'])

            # Construct and store the VariableDesc object for this variable
            variables[vname] = VariableDesc(vname, **kwargs)

        # Loop through all of the newly constructed output variables and
        # gather information about their dimensions
        dimensions = OrderedDict()
        for vname, vinfo in variables.iteritems():

            # If the variable has a string 'definition', record its
            # dimensions as None (i.e., undefined)
            if isinstance(vinfo.definition, basestring):
                for dname in vinfo.dimensions:
                    if dname not in dimensions:
                        dimensions[dname] = None

            # Else, if it has an array 'definition', then construct the full DimensionDesc
            else:
                dshape = vinfo.definition.shape
                if len(dshape) == 0:
                    dshape = (1,)
                for dname, dsize in zip(vinfo.dimensions, dshape):

                    # If the dimension has already been found and defined, then it must
                    # match the size of the previously found dimension
                    if dname in dimensions and dimensions[dname] is not None:
                        if dsize != dimensions[dname].size:
                            err_msg = ('Dimension {!r} is inconsistently defined in '
                                       'OutputDatasetDesc {!r}').format(dname, name)
                            raise ValueError(err_msg)

                    # Else, set/store the DimensionDesc object
                    else:
                        dimensions[dname] = DimensionDesc(dname, dsize)

        # Call the base class to run self-consistency checks
        super(OutputDatasetDesc, self).__init__(name, attributes=attributes,
                                                variables=variables, dimensions=dimensions)
