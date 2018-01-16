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

    def __init__(self, name, **kwds):
        super(MemberObject, self).__init__(name)
        if 'dataset' not in kwds:
            clsname = self.__class__.__name__
            msg = '{} {!r} needs a dataset for construction'
            raise AttributeError(msg.format(clsname, self.name))
        self.__dataset = kwds['dataset']

    @property
    def dataset(self):
        return self.__dataset
