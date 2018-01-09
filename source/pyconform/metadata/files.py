"""
File Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from namedobjects import NamedObject


class File(NamedObject):
    """
    Metadata describing a NetCDF file
    """

    def __init__(self, name):
        super(File, self).__init__(name)
        self.attributes = {}
        self.deflate = 1
