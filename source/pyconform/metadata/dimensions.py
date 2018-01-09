"""
Dimension Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""


class Dimension(object):
    """
    Metadata describing a NetCDF dimension
    """

    def __init__(self, name):
        self.name = name
        self.size = None
        self.is_unlimited = False
