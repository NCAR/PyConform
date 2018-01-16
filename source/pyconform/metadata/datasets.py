"""
Dataset Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import OrderedDict
from . import Dimension, Variable, File


class Dataset(object):
    """
    Metadata describing an entire NetCDF dataset
    """

    def __init__(self):
        self.__dimensions = OrderedDict()
        self.__variables = OrderedDict()
        self.__files = OrderedDict()

    def add(self, obj):
        if isinstance(obj, Dimension):
            self.__add_dimension(obj)
        elif isinstance(obj, Variable):
            self.__add_variable(obj)
        elif isinstance(obj, File):
            self.__add_file(obj)
        else:
            msg = 'Cannot add object of type {} to Dataset'
            raise TypeError(msg.format(type(obj)))

    def __add_file(self, f):
        if f.name in self.__files and f is not self.__files[f.name]:
            msg = 'A File with name {} is already contained in Dataset'
            raise ValueError(msg.format(f.name))
        self.__check_dimension_references(f.dimensions)
        self.__check_variable_references(f.variables)
        self.__files[f.name] = f

    def __check_dimension_references(self, dimensions):
        if dimensions is None:
            return
        not_found = [d for d in dimensions if d not in self.__dimensions]
        if not_found:
            dstr = ', '.join('{!r}'.format(d) for d in not_found)
            msg = 'Dimensions {} not found in dataset'
            raise KeyError(msg.format(dstr))

    def __check_variable_references(self, variables):
        if variables is None:
            return
        not_found = [v for v in variables if v not in self.__variables]
        if not_found:
            dstr = ', '.join('{!r}'.format(v) for v in not_found)
            msg = 'Variables {} not found in dataset'
            raise KeyError(msg.format(dstr))

    def __add_variable(self, v):
        if v.name in self.__variables and v is not self.__variables[v.name]:
            msg = 'A Variable with name {!r} is already contained in Dataset'
            raise ValueError(msg.format(v.name))
        self.__check_dimension_references(v.dimensions)
        self.__variables[v.name] = v

    def __add_dimension(self, d):
        if d.name in self.__dimensions and d is not self.__dimensions[d.name]:
            msg = 'A Dimension with name {!r} is already contained in Dataset'
            raise ValueError(msg.format(d.name))
        self.__dimensions[d.name] = d

    def new_dimension(self, name, **kwds):
        self.__add_dimension(Dimension(name, **kwds))
        return self.__dimensions[name]

    def new_variable(self, name, **kwds):
        self.__add_variable(Variable(name, **kwds))
        return self.__variables[name]

    def new_file(self, name, **kwds):
        self.__add_file(File(name, **kwds))
        return self.__files[name]

    @property
    def dimensions(self):
        return tuple(self.__dimensions)

    @property
    def variables(self):
        return tuple(self.__variables)

    @property
    def files(self):
        return tuple(self.__files)

    def __contains__(self, obj):
        if isinstance(obj, Variable):
            return obj.name in self.__variables and obj is self.__variables[obj.name]
        elif isinstance(obj, Dimension):
            return obj.name in self.__dimensions and obj is self.__dimensions[obj.name]
        elif isinstance(obj, File):
            return obj.name in self.__files and obj is self.__files[obj.name]
        else:
            return False
