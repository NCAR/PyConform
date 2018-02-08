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
            v = self.new_variable(vname)
            v.definition = vdicts[vname]['definition']
            v.datatype = vdicts[vname].get('datatype', None)
            v.dimensions = vdicts[vname].get('dimensions', None)
            v.attributes.update(vdicts[vname].get('attributes', {}))

    def __create_files(self, vdicts):
        vfiles = self.__extract_file_dicts(vdicts)
        vmeta = [vname for vname in vfiles if vfiles[vname] is None]
        vsers = [vname for vname in vfiles if vname not in vmeta]
        for vname in vsers:
            fdict = vfiles[vname]
            fname = fdict.pop('filename', '{}.nc'.format(vname))
            fdict['deflate'] = int(fdict.pop('compression', '1'))
            fvars = vmeta + [vname]
            fdims = sum((vdicts[v].get('dimensions', []) for v in fvars), [])
            self.__create_file(fname, fdims, fvars, fdict)

    def __extract_file_dicts(self, vdicts):
        vfiles = OrderedDict()
        for vname in vdicts:
            vfiles[vname] = vdicts[vname].pop('file', None)
        return vfiles

    def __create_file(self, fname, fdims, fvars, fdict):
        f = self.new_file(fname)
        for d in fdims:
            f.add_dimension(d)
        for v in fvars:
            f.add_variable(v)
        if 'format' in fdict:
            f.format = fdict['format']
        if 'deflate' in fdict:
            f.deflate = fdict['deflate']
        if 'shuffle' in fdict:
            f.shuffle = fdict['shuffle']
        f.attributes.update(fdict.get('attributes', {}))
