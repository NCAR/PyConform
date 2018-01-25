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

    def __init__(self, name, dataset=None):
        super(MemberObject, self).__init__(name)
        self.__dataset = self.__validate_dataset(dataset)

    def __validate_dataset(self, dataset):
        from datasets import Dataset
        if not isinstance(dataset, Dataset):
            msg = 'Objects needs a dataset for construction'
            raise TypeError(msg)
        return dataset

    @property
    def _dataset(self):
        return self.__dataset
