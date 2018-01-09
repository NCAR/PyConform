"""
NamedObject Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""


class NamedObject(object):
    """
    An object with a required name
    """

    def __init__(self, name):
        self.name = name
