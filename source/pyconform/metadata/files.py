"""
File Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import OrderedDict
from namedobjects import NamedObject
from variables import Variable
from dimensions import Dimension


class File(NamedObject):
    """
    Metadata describing a NetCDF file
    """

    def __init__(self, name, deflate=1):
        super(File, self).__init__(name)
        self.__attributes = {}
        self.__deflate = self.__validate_deflate(deflate)
        self.__dimensions = OrderedDict()
        self.__variables = OrderedDict()

    def __validate_deflate(self, deflate):
        if not isinstance(deflate, int):
            msg = 'File {} deflate level must be an integer'
            raise TypeError(msg.format(self.name))
        return deflate

    @property
    def attributes(self):
        return self.__attributes

    @property
    def deflate(self):
        return self.__deflate

    @property
    def dimensions(self):
        return tuple(self.__dimensions)

    @property
    def variables(self):
        return tuple(self.__variables)

    def __contains__(self, obj):
        if isinstance(obj, Variable):
            return obj.name in self.__variables and obj is self.__variables[obj.name]
        elif isinstance(obj, Dimension):
            return obj.name in self.__dimensions and obj is self.__dimensions[obj.name]
        else:
            return False

    def add(self, obj):
        objdict = self.__identify_object_dict(obj)
        if obj not in self and obj.name in objdict:
            msg = '{} {} already contained in File {}'
            raise ValueError(msg.format(type(obj), obj.name, self.name))
        objdict[obj.name] = obj
        if isinstance(obj, Dimension) or obj.dimensions is None:
            return
        for d in obj.dimensions:
            self.add(d)

    def __identify_object_dict(self, obj):
        if isinstance(obj, Dimension):
            return self.__dimensions
        elif isinstance(obj, Variable):
            return self.__variables
        else:
            msg = 'Cannot add object of type {} to File {}'
            raise TypeError(msg.format(type(obj), self.name))
