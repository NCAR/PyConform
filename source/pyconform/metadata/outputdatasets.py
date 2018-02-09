"""
OutputDataset Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import OrderedDict
from datasets import Dataset


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
        self.__create_dimensions(vdicts)
        self.__create_variables(vdicts)
        self.__create_files(vdicts)

    def __create_dimensions(self, vdicts):
        dims = self.__collect_dimension_names(vdicts)
        for dname in dims:
            self.new_dimension(dname)

    def __collect_dimension_names(self, vdicts):
        vdims = set()
        for vname in vdicts:
            vdims.update(set(vdicts[vname].get('dimensions', ())))
        return vdims

    def __create_variables(self, vdicts):
        for vname in vdicts:
            self.new_variable(vname, **vdicts[vname])

    def __create_files(self, vdicts):
        vfiles = self.__extract_file_dicts(vdicts)
        vmeta = [vname for vname in vfiles if vfiles[vname] is None]
        vsers = [vname for vname in vfiles if vname not in vmeta]
        for vname in vsers:
            fdict = vfiles[vname]
            fname = fdict.pop('filename', '{}.nc'.format(vname))
            fvars = vmeta + [vname]
            dlist = sum((vdicts[v].get('dimensions', []) for v in fvars), [])
            fdims = list(set(dlist))
            self.__create_file(fname, fdims, fvars, fdict)

    def __extract_file_dicts(self, vdicts):
        vfiles = OrderedDict()
        for vname in vdicts:
            vfiles[vname] = vdicts[vname].pop('file', None)
        return vfiles

    def __create_file(self, fname, fdims, fvars, fdict):
        f = self.new_file(fname, **fdict)
        f.add_dimensions(*fdims)
        f.add_variables(*fvars)
