"""
Dimension Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from namedobjects import NamedObject


class Dimension(NamedObject):
    """
    Metadata describing a NetCDF dimension
    """

    def __init__(self, name):
        super(Dimension, self).__init__(name)
        self.size = None
        self.is_unlimited = False
