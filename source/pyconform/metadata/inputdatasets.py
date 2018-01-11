"""
InputDataset Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from . import Dataset


class InputDataset(Dataset):
    """
    Metadata for an Input Dataset created from a list of existing files
    """

    def __init__(self, filenames):
        if not isinstance(filenames, (tuple, list)):
            msg = 'InputDataset requires a tuple/list of filenames'
            raise TypeError(msg)
