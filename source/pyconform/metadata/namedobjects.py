"""
NamedObject Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""


class NamedObject(object):
    """
    An object with a required name
    """

    __instances__ = {}

    def __new__(cls, name, namespace=None):
        key = (cls, namespace, name)
        if key in NamedObject.__instances__:
            instance = NamedObject.__instances__[key]
        else:
            instance = object.__new__(cls, name, namespace=namespace)
            NamedObject.__instances__[key] = instance
        return instance

    def __init__(self, name, namespace=None):
        self.name = name
        self.namespace = namespace
