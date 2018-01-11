"""
File Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import OrderedDict
from namedobjects import NamedObject
from variables import Variable


class File(NamedObject):
    """
    Metadata describing a NetCDF file
    """

    def __init__(self, name, deflate=1, variables=()):
        super(File, self).__init__(name)
        self.__attributes = {}
        self.__deflate = self.__validate_deflate(deflate)
        self.__variables = self.__validate_variables(variables)
        self.__dimensions = self.__extract_variable_dimensions(variables)

    def __validate_deflate(self, deflate):
        if not isinstance(deflate, int):
            msg = 'File {} deflate level must be an integer'
            raise TypeError(msg.format(self.name))
        return deflate

    def __validate_variables(self, variables):
        if (not isinstance(variables, (list, tuple)) or
                not all(isinstance(v, Variable) for v in variables)):
            msg = 'File {} can only accept a list/tuple of Variables'
            raise TypeError(msg.format(self.name))
        return self.__new_dictionary_without_name_collisions(variables)

    def __new_dictionary_without_name_collisions(self, objects):
        objdict = OrderedDict()
        for obj in objects:
            if obj.name in objdict and obj is not objdict[obj.name]:
                msg = 'File {} has different {} with the same name {}'
                raise ValueError(msg.format(
                    self.name, obj.__class__.__name__, obj.name))
            objdict[obj.name] = obj
        return objdict

    def __extract_variable_dimensions(self, variables):
        vars_with_dims = [v for v in variables if v.dimensions is not None]
        var_dims = [d for v in vars_with_dims for d in v.dimensions]
        return self.__new_dictionary_without_name_collisions(var_dims)

    @property
    def attributes(self):
        return self.__attributes

    @property
    def deflate(self):
        return self.__deflate

    @property
    def dimensions(self):
        return self.__dimensions.values()

    @property
    def variables(self):
        return self.__variables.values()
