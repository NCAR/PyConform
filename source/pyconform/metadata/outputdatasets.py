"""
OutputDataset Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import OrderedDict
from datasets import Dataset
from . import Dimension, Variable, File


class OutputDataset(Dataset):
    """
    Dataset computed from a JSON standardization file
    """

    def __init__(self, standardization):
        super(OutputDataset, self).__init__()
        self.__validate_standardization(standardization)
        self.__add_from_standardization(standardization)

    def __validate_standardization(self, standardization):
        if not isinstance(standardization, dict):
            msg = 'Standardization must be a dictionary, not type {}'
            raise TypeError(msg.format(type(standardization)))

    def __add_from_standardization(self, standardization):
        vdicts = standardization.copy()
        vfiles = OrderedDict()
        vattrs = OrderedDict()
        vdims = set()
        for vname in vdicts:
            vdict = vdicts[vname]
            vattrs[vname] = vdict.pop('attributes', {})
            vfiles[vname] = vdict.pop('file', None)
            vdims.update(set(vdict.get('dimensions', ())))
        for dname in vdims:
            self.new_dimension(dname)
        for vname in vdicts:
            self.new_variable(vname, **vdicts[vname])
        for vname in vattrs:
            v = self.get_variable(vname)
            v.attributes.update(vattrs[vname])
        vmeta = [vname for vname in vfiles if vfiles[vname] is None]
        vsers = [vname for vname in vfiles if vname not in vmeta]
        for vname in vsers:
            fdict = vfiles[vname]
            fname = fdict.pop('filename', '{}.nc'.format(vname))
            fatts = fdict.pop('attributes', {})
            fdict['deflate'] = int(fdict.pop('compression', '1'))
            fvars = vmeta + [vname]
            fdims = sum((vdicts[v].get('dimensions', []) for v in fvars), [])
            f = self.new_file(fname, dimensions=fdims,
                              variables=fvars, **fdict)
            f.attributes.update(fatts)
