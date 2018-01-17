"""
MemberObject Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from namedobjects import NamedObject


class MemberObject(NamedObject):
    """
    A member of a dataset
    """

    def __init__(self, name):
        super(MemberObject, self).__init__(name)
        self.__dataset = None

    @property
    def dataset(self):
        return self.__dataset

    @dataset.setter
    def dataset(self, ds):
        from datasets import Dataset
        if not isinstance(ds, Dataset):
            msg = 'dataset property must be a Dataset object'
            raise TypeError(msg)
        self.__dataset = ds
