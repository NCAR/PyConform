"""
Unit Tests for Lex-based Tokenizer

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparser import tokenizer as tknz

import unittest


class TokenizerTests(unittest.TestCase):

    def setUp(self):
        self.tokenizer = tknz.Tokenizer()

    def test_init(self):
        self.assertIsInstance(self.tokenizer, tknz.Tokenizer)

    def test_int(self):
        token = self.tokenizer.tokenize('123')
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, 123)

    def test_int_negative(self):
        token = self.tokenizer.tokenize('-143')
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, -143)

    def test_int_positive(self):
        token = self.tokenizer.tokenize('+143')
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, 143)

    def test_ignored_spaces(self):
        token = self.tokenizer.tokenize('   143')
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, 143)

    def test_float_decimal_full(self):
        token = self.tokenizer.tokenize('12.34')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34)

    def test_float_decimal_tailless(self):
        token = self.tokenizer.tokenize('12.')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.)

    def test_float_decimal_headless(self):
        token = self.tokenizer.tokenize('.12')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 0.12)

    def test_float_exponential_full(self):
        token = self.tokenizer.tokenize('12.34e5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34e5)

    def test_float_positive_exponent(self):
        token = self.tokenizer.tokenize('12.34e+5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34e5)

    def test_float_negative_exponent(self):
        token = self.tokenizer.tokenize('12.34e-5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34e-5)

    def test_float_capital_exponent(self):
        token = self.tokenizer.tokenize('12.34E-5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34e-5)

    def test_float_exponential_no_decimal(self):
        token = self.tokenizer.tokenize('12E-5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12e-5)

    def test_string_1(self):
        token = self.tokenizer.tokenize("' asdf  3 5 dasd '")
        self.assertEqual(token.type, 'STRING')
        self.assertEqual(token.value, ' asdf  3 5 dasd ')

    def test_string_2(self):
        token = self.tokenizer.tokenize('" asdf  3 5 dasd "')
        self.assertEqual(token.type, 'STRING')
        self.assertEqual(token.value, ' asdf  3 5 dasd ')

    def test_name(self):
        token = self.tokenizer.tokenize('x')
        self.assertEqual(token.type, 'NAME')
        self.assertEqual(token.value, 'x')

    def test_name_time(self):
        token = self.tokenizer.tokenize('time')
        self.assertEqual(token.type, 'NAME')
        self.assertEqual(token.value, 'time')

    def test_lbracket(self):
        token = self.tokenizer.tokenize('[1]')
        self.assertEqual(token.type, '[')
        self.assertEqual(token.value, '[')

    def test_rbracket(self):
        token = self.tokenizer.tokenize(']')
        self.assertEqual(token.type, ']')
        self.assertEqual(token.value, ']')

    def test_lparen(self):
        token = self.tokenizer.tokenize('(1)')
        self.assertEqual(token.type, '(')
        self.assertEqual(token.value, '(')

    def test_rparen(self):
        token = self.tokenizer.tokenize(')')
        self.assertEqual(token.type, ')')
        self.assertEqual(token.value, ')')

    def test_minus(self):
        token = self.tokenizer.tokenize('-')
        self.assertEqual(token.type, '-')
        self.assertEqual(token.value, '-')

    def test_plus(self):
        token = self.tokenizer.tokenize('+')
        self.assertEqual(token.type, '+')
        self.assertEqual(token.value, '+')

    def test_times(self):
        token = self.tokenizer.tokenize('*')
        self.assertEqual(token.type, '*')
        self.assertEqual(token.value, '*')

    def test_divide(self):
        token = self.tokenizer.tokenize('/')
        self.assertEqual(token.type, '/')
        self.assertEqual(token.value, '/')

    def test_power(self):
        token = self.tokenizer.tokenize('**')
        self.assertEqual(token.type, 'POW')
        self.assertEqual(token.value, '**')

    def test_colon(self):
        token = self.tokenizer.tokenize(':')
        self.assertEqual(token.type, ':')
        self.assertEqual(token.value, ':')

    def test_comma(self):
        token = self.tokenizer.tokenize(',')
        self.assertEqual(token.type, ',')
        self.assertEqual(token.value, ',')

    def test_equals(self):
        token = self.tokenizer.tokenize('=')
        self.assertEqual(token.type, '=')
        self.assertEqual(token.value, '=')

    def test_lessthan(self):
        token = self.tokenizer.tokenize('<')
        self.assertEqual(token.type, '<')
        self.assertEqual(token.value, '<')

    def test_greaterthan(self):
        token = self.tokenizer.tokenize('>')
        self.assertEqual(token.type, '>')
        self.assertEqual(token.value, '>')

    def test_lessequal(self):
        token = self.tokenizer.tokenize('<=')
        self.assertEqual(token.type, 'LEQ')
        self.assertEqual(token.value, '<=')

    def test_greaterequal(self):
        token = self.tokenizer.tokenize('>=')
        self.assertEqual(token.type, 'GEQ')
        self.assertEqual(token.value, '>=')

    def test_equalto(self):
        token = self.tokenizer.tokenize('==')
        self.assertEqual(token.type, 'EQ')
        self.assertEqual(token.value, '==')


if __name__ == "__main__":
    unittest.main()
