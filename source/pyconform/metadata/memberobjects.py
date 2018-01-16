"""
New Module

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from namedobjects import NamedObject


class MemberObject(NamedObject):
    """
    A member of a Dataset
    """

    def __init__(self, name):
        super(MemberObject, self).__init__(name)
        self._dataset = None

    @property
    def dataset(self):
        return self._dataset
