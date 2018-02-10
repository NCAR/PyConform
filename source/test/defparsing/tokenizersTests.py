"""
Unit Tests for Parser Tokenizers

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparsing import tokenizers as tkz

import unittest


class TokenizerTests(unittest.TestCase):

    def test_unsigned_integer(self):
        token = tkz.unsigned_integer.parseString('142')[0]
        self.assertEqual(token, 142)

    def test_unsigned_float_with_decimal(self):
        token = tkz.unsigned_float.parseString('1.2')[0]
        self.assertEqual(token, 1.2)

    def test_unsigned_float_with_decimal_without_trailing_zero(self):
        token = tkz.unsigned_float.parseString('1.')[0]
        self.assertEqual(token, 1.0)

    def test_unsigned_float_without_decimal_and_positive_exponent(self):
        token = tkz.unsigned_float.parseString('1e+4')[0]
        self.assertEqual(token, 10000.)

    def test_unsigned_float_without_decimal_and_negative_exponent(self):
        token = tkz.unsigned_float.parseString('1e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_unsigned_float_with_decimal_and_positive_exponent(self):
        token = tkz.unsigned_float.parseString('1.234e+4')[0]
        self.assertEqual(token, 12340.)

    def test_unsigned_float_with_decimal_without_trailing_zero_and_negative_exponent(self):
        token = tkz.unsigned_float.parseString('1.e-4')[0]
        self.assertEqual(token, 1e-4)

    def test_quoted_string_with_single_quotes(self):
        token = tkz.quoted_string.parseString("'a b c'")[0]
        self.assertEqual(token, 'a b c')

    def test_quoted_string_with_double_quotes(self):
        token = tkz.quoted_string.parseString('"a b c"')[0]
        self.assertEqual(token, 'a b c')

    def test_name_with_single_character(self):
        token = tkz.name.parseString('a')[0]
        self.assertEqual(token, 'a')

    def test_name_with_single_underscore(self):
        token = tkz.name.parseString('_')[0]
        self.assertEqual(token, '_')

    def test_name_with_leading_underscore(self):
        token = tkz.name.parseString('_abc')[0]
        self.assertEqual(token, '_abc')

    def test_name_with_trailing_underscore(self):
        token = tkz.name.parseString('aBc_')[0]
        self.assertEqual(token, 'aBc_')

    def test_name_with_multiple_underscores(self):
        token = tkz.name.parseString('a_B_c')[0]
        self.assertEqual(token, 'a_B_c')


if __name__ == '__main__':
    unittest.main()
