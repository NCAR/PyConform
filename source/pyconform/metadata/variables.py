"""
Variable Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from cf_units import Unit
from numpy import ndarray
from namedobjects import NamedObject


class Variable(NamedObject):
    """
    Metadata describing a NetCDF variable
    """

    _NETCDF_TYPES_ = ('byte', 'ubyte', 'char',
                      'short', 'ushort',
                      'int', 'uint',
                      'int64', 'uint64',
                      'float', 'real', 'double')

    def __init__(self, name, definition=None, datatype=None):
        super(Variable, self).__init__(name)
        self.__definition = self.__validate_definition_type(definition)
        self.__datatype = self.__validate_datatype(datatype)
        self.__attributes = {}

    def __validate_definition_type(self, definition):
        if definition is None:
            return None
        if not isinstance(definition, (basestring, ndarray)):
            msg = 'Variable {} must have a string or array definition'
            raise TypeError(msg.format(self.name))
        return definition

    def __validate_datatype(self, datatype):
        if datatype is None:
            return None
        if datatype not in Variable._NETCDF_TYPES_:
            msg = 'Variable {} has invalid datatype {!r}'
            raise ValueError(msg.format(self.name, datatype))
        return datatype

    @property
    def definition(self):
        return self.__definition

    @property
    def datatype(self):
        return self.__datatype

    @property
    def attributes(self):
        return self.__attributes

    @property
    def units(self):
        ustr = str(self.attributes.get('units', '?')).split('since')[0].strip()
        return None if ustr in ('', '?', 'unknown') else ustr

    @property
    def refdatetime(self):
        lstr = str(self.attributes.get('units', '?')).split('since')
        rstr = lstr[1].strip() if len(lstr) > 1 else ''
        return None if rstr in ('', '?', 'unknown') else rstr

    @property
    def calendar(self):
        return self.attributes.get('calendar', None)

    def cfunits(self):
        return Unit(self.attributes.get('units'), calendar=self.calendar)
