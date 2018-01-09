"""
Dataset Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""


class Dataset(object):
    """
    Metadata describing an entire NetCDF dataset
    """

    def __init__(self):
        self.dimensions = {}
        self.variables = {}
        self.files = {}

    def get_dimension(self, name):
        return self.dimensions[name]

    def get_variable(self, name):
        return self.variables[name]

    def get_file(self, name):
        return self.files[name]
