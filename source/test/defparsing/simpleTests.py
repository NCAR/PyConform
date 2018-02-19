"""
Unit Tests for Parser Tokenizers

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparsing import simple

import unittest


class PatternTests(unittest.TestCase):

    def test_uint_expr(self):
        token = simple.uint_expr.parseString('142')[0]
        self.assertEqual(token, 142)

    def test_int_expr_positive(self):
        token = simple.int_expr.parseString('142')[0]
        self.assertEqual(token, 142)

    def test_int_expr_negative(self):
        token = simple.int_expr.parseString('-142')[0]
        self.assertEqual(token, -142)

    def test_ufloat_expr_with_decimal(self):
        token = simple.ufloat_expr.parseString('1.2')[0]
        self.assertEqual(token, 1.2)

    def test_ufloat_expr_with_decimal_without_trailing_zero(self):
        token = simple.ufloat_expr.parseString('1.')[0]
        self.assertEqual(token, 1.0)

    def test_ufloat_expr_without_decimal_and_positive_exponent(self):
        token = simple.ufloat_expr.parseString('1e+4')[0]
        self.assertEqual(token, 10000.)

    def test_ufloat_expr_without_decimal_and_negative_exponent(self):
        token = simple.ufloat_expr.parseString('1e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_ufloat_expr_with_decimal_and_positive_exponent(self):
        token = simple.ufloat_expr.parseString('1.234e+4')[0]
        self.assertEqual(token, 12340.)

    def test_ufloat_expr_with_decimal_without_trailing_zero_and_negative_exponent(self):
        token = simple.ufloat_expr.parseString('1.e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_float_expr_with_decimal_and_positive_exponent(self):
        token = simple.float_expr.parseString('-1.234e+4')[0]
        self.assertEqual(token, -12340.)

    def test_str_expr_with_single_quotes(self):
        token = simple.str_expr.parseString("'a b c'")[0]
        self.assertEqual(token, 'a b c')

    def test_str_expr_with_double_quotes(self):
        token = simple.str_expr.parseString('"a b c"')[0]
        self.assertEqual(token, 'a b c')

    def test_name_expr_as_solo_underscore(self):
        token = simple.name_expr.parseString('_')[0]
        self.assertEqual(token, '_')

    def test_name_expr_with_underscore_separation(self):
        token = simple.name_expr.parseString('_a_b_c_')[0]
        self.assertEqual(token, '_a_b_c_')

    def test_slice_expr_empty(self):
        token = simple.slice_expr.parseString(':')[0]
        self.assertEqual(token, slice(None))

    def test_slice_expr_start_only(self):
        token = simple.slice_expr.parseString('1:')[0]
        self.assertEqual(token, slice(1, None))

    def test_slice_expr_stop_only(self):
        token = simple.slice_expr.parseString(':-2')[0]
        self.assertEqual(token, slice(None, -2))

    def test_slice_expr_step_only(self):
        token = simple.slice_expr.parseString('::-1')[0]
        self.assertEqual(token, slice(None, None, -1))

    def test_slice_expr_start_stop(self):
        token = simple.slice_expr.parseString('-1 :  3')[0]
        self.assertEqual(token, slice(-1, 3))

    def test_slice_expr_start_stop_step(self):
        token = simple.slice_expr.parseString('-1 :  3 : 8')[0]
        self.assertEqual(token, slice(-1, 3, 8))


if __name__ == '__main__':
    unittest.main()
