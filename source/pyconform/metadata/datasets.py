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
        self.__coordinates = OrderedDict()
        self.__files = OrderedDict()

    def __contains__(self, obj):
        if isinstance(obj, Variable):
            return obj.name in self.__variables and obj is self.__variables[obj.name]
        elif isinstance(obj, Dimension):
            return obj.name in self.__dimensions and obj is self.__dimensions[obj.name]
        elif isinstance(obj, File):
            return obj.name in self.__files and obj is self.__files[obj.name]
        else:
            return False

    def new_dimension(self, name, **kwds):
        if name in self.__dimensions:
            msg = 'A Dimension with name {!r} is already contained in Dataset'
            raise ValueError(msg.format(name))
        d = Dimension(name, **kwds)
        d._dataset = self
        self._add_dimension(d)
        return d

    def new_variable(self, name, **kwds):
        if name in self.__variables:
            msg = 'A Variable with name {!r} is already contained in Dataset'
            raise ValueError(msg.format(name))
        v = Variable(name, **kwds)
        v._dataset = self
        self._add_variable(v)
        return v

    def new_file(self, name, **kwds):
        if name in self.__files:
            msg = 'A File with name {!r} is already contained in Dataset'
            raise ValueError(msg.format(name))
        f = File(name, **kwds)
        f._dataset = self
        self._add_file(f)
        return f

    def _add_file(self, f):
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

    def _add_variable(self, v):
        self.__check_dimension_references(v.dimensions)
        self.__check_variable_references(v.auxcoords)
        self.__variables[v.name] = v
        self.__add_new_coordinates(v)

    def __add_new_coordinates(self, v):
        if v.dimensions and len(v.dimensions) == 1 and v.dimensions[0] == v.name:
            self.__coordinates[v.name] = v
        elif len(v.auxcoords) > 0:
            for n in v.auxcoords:
                self.__coordinates[n] = self.get_variable(n)

    def _add_dimension(self, d):
        self.__dimensions[d.name] = d

    @property
    def dimensions(self):
        return frozenset(self.__dimensions)

    @property
    def variables(self):
        return frozenset(self.__variables)

    @property
    def coordinates(self):
        return frozenset(self.__coordinates)

    @property
    def files(self):
        return frozenset(self.__files)

    def get_dimension(self, name):
        if name not in self.__dimensions:
            msg = 'Dimension {!r} not found in dataset'
            raise KeyError(msg.format(name))
        return self.__dimensions[name]

    def get_variable(self, name):
        if name not in self.__variables:
            msg = 'Variable {!r} not found in dataset'
            raise KeyError(msg.format(name))
        return self.__variables[name]

    def get_file(self, name):
        if name not in self.__files:
            msg = 'File {!r} not found in dataset'
            raise KeyError(msg.format(name))
        return self.__files[name]
