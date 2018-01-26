"""
Unit Tests for OutputDatasets

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from collections import OrderedDict
from pyconform.metadata import OutputDataset


class OutputDatasetTests(unittest.TestCase):

    def setUp(self):
        std = OrderedDict()
        std['v'] = OrderedDict()
        std['v']['definition'] = 'f(V)'
        std['v']['datatype'] = 'float'
        std['v']['dimensions'] = ['x', 'y', 't']
        std['v']['attributes'] = {'units': 'kg'}
        std['u'] = OrderedDict()
        std['u']['definition'] = 'U'
        std['u']['file'] = OrderedDict()
        std['u']['file']['filename'] = 'u_1.nc'
        std['u']['file']['attributes'] = {'var': 'u'}
        self.standardization = std

    def test_create(self):
        ods = OutputDataset({})
        self.assertIsInstance(ods, OutputDataset)

    def test_create_with_non_dict_raises_type_error(self):
        with self.assertRaises(TypeError):
            OutputDataset('x')

    def test_create_from_standardization(self):
        ods = OutputDataset(self.standardization)
        self.assertIsInstance(ods, OutputDataset)
        self.assertItemsEqual(ods.dimensions, ('x', 'y', 't'))
        self.assertItemsEqual(ods.variables, ('v', 'u'))
        self.assertItemsEqual(ods.files, ('u_1.nc',))
        v = ods.get_variable('v')
        self.assertEqual(v.definition, 'f(V)')
        self.assertEqual(v.datatype, 'float')
        self.assertEqual(v.units, 'kg')
        u = ods.get_variable('u')
        self.assertEqual(u.definition, 'U')
        self.assertEqual(u.attributes, set())
        f = ods.get_file('u_1.nc')
        self.assertItemsEqual(f.dimensions, ('x', 'y', 't'))
        self.assertItemsEqual(f.variables, ('u', 'v'))


if __name__ == "__main__":
    unittest.main()
