"""
MemberObject Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from namedobjects import NamedObject


class MemberObject(NamedObject):
    """
    A member of a specification
    """

    def __init__(self, name, specification=None):
        super(MemberObject, self).__init__(name)
        self.__specification = self.__validate_specification(specification)

    def __validate_specification(self, specification):
        from pyconform.specification.specifications import Specification
        if not isinstance(specification, Specification):
            msg = 'Object needs a specification for construction'
            raise TypeError(msg)
        return specification

    @property
    def specification(self):
        return self.__specification
