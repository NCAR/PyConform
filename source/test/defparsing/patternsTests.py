"""
Unit Tests for Parser Tokenizers

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparsing import patterns as p
from pyconform.defparsing import actions as a

import unittest


class PatternTests(unittest.TestCase):

    def test_uint(self):
        token = p.uint.parseString('142')[0]
        self.assertEqual(token, 142)

    def test_ufloat_with_decimal(self):
        token = p.ufloat.parseString('1.2')[0]
        self.assertEqual(token, 1.2)

    def test_ufloat_with_decimal_without_trailing_zero(self):
        token = p.ufloat.parseString('1.')[0]
        self.assertEqual(token, 1.0)

    def test_ufloat_without_decimal_and_positive_exponent(self):
        token = p.ufloat.parseString('1e+4')[0]
        self.assertEqual(token, 10000.)

    def test_ufloat_without_decimal_and_negative_exponent(self):
        token = p.ufloat.parseString('1e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_ufloat_with_decimal_and_positive_exponent(self):
        token = p.ufloat.parseString('1.234e+4')[0]
        self.assertEqual(token, 12340.)

    def test_ufloat_with_decimal_without_trailing_zero_and_negative_exponent(self):
        token = p.ufloat.parseString('1.e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_strings_with_single_quotes(self):
        token = p.string.parseString("'a b c'")[0]
        self.assertEqual(token, 'a b c')

    def test_strings_with_double_quotes(self):
        token = p.string.parseString('"a b c"')[0]
        self.assertEqual(token, 'a b c')

    def test_name_as_solo_underscore(self):
        token = p.name.parseString('_')[0]
        self.assertEqual(token, '_')

    def test_name_with_underscore_separation(self):
        token = p.name.parseString('_a_b_c_')[0]
        self.assertEqual(token, '_a_b_c_')

    def test_variables_without_indices(self):
        token = p.variable.parseString('x')[0]
        self.assertEqual(token, a.VariableType('x', None))

    def test_variables_with_1D_integer_index(self):
        token = p.variable.parseString('x[0]')[0]
        self.assertEqual(token, a.VariableType('x', [0]))

    def test_variables_with_1D_slice_index(self):
        token = p.variable.parseString('x[1:4]')[0]
        self.assertEqual(token, a.VariableType('x', [slice(1, 4)]))

    def test_variables_with_2D_slice_index(self):
        token = p.variable.parseString('x[1:4,6]')[0]
        self.assertEqual(token, a.VariableType('x', [slice(1, 4), 6]))

    def test_variables_with_2D_slice_index_missing_stop_value(self):
        token = p.variable.parseString('x[1:,6]')[0]
        self.assertEqual(token, a.VariableType('x', [slice(1, None), 6]))

    def test_variables_with_2D_slice_index_missing_start_value(self):
        token = p.variable.parseString('x[:3,6]')[0]
        self.assertEqual(token, a.VariableType('x', [slice(3), 6]))


if __name__ == '__main__':
    unittest.main()
