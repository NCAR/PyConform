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

    def __init__(self, files=()):
        self.__dimensions = OrderedDict()
        self.__variables = OrderedDict()
        self.__files = OrderedDict()
        self.__validate_files(files)

    def __validate_files(self, files):
        if not isinstance(files, (tuple, list)) or not all(isinstance(f, File) for f in files):
            raise TypeError('Dataset files must be a tuple/list of Files')
        for f in files:
            self.__add_file(f)

    def __add_file(self, f):
        if f.name in self.__files and f is not self.__files[f.name]:
            msg = 'A File with name {} is already contained in Dataset'
            raise ValueError(msg.format(f.name))
        self.__files[f.name] = f
        for v in f.variables:
            self.__add_variable(v)

    def __add_variable(self, v):
        if v.name in self.__variables and v is not self.__variables[v.name]:
            msg = 'A Variable with name {} is already contained in Dataset'
            raise ValueError(msg.format(v.name))
        self.__variables[v.name] = v
        if v.dimensions is None:
            return
        for d in v.dimensions:
            self.__add_dimension(d)

    def __add_dimension(self, d):
        if d.name in self.__dimensions and d is not self.__dimensions[d.name]:
            msg = 'A Dimension with name {} is already contained in Dataset'
            raise ValueError(msg.format(d.name))
        self.__dimensions[d.name] = d

    @property
    def dimensions(self):
        return self.__dimensions.values()

    @property
    def variables(self):
        return self.__variables.values()

    @property
    def files(self):
        return self.__files.values()

    def __contains__(self, obj):
        if isinstance(obj, Variable):
            return obj.name in self.__variables and obj is self.__variables[obj.name]
        elif isinstance(obj, Dimension):
            return obj.name in self.__dimensions and obj is self.__dimensions[obj.name]
        elif isinstance(obj, File):
            return obj.name in self.__files and obj is self.__files[obj.name]
        else:
            return False
