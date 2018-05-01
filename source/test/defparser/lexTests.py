"""
Unit Tests for Lex Tokenizer

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparser import lex

import unittest


def get_lex_token(s):
    lex.lex.input(s)  # @UndefinedVariable
    return iter(lex.lex.token, None).next()  # @UndefinedVariable


class LexTest(unittest.TestCase):

    def test_uint(self):
        token = get_lex_token('143')
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, 143)

    def test_int_negative(self):
        token = get_lex_token('-143')
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, -143)

    def test_int_positive(self):
        token = get_lex_token('+143')
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, 143)

    def test_ignored_spaces(self):
        token = get_lex_token('   143')
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, 143)

    def test_ufloat_decimal_full(self):
        token = get_lex_token('12.34')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34)

    def test_ufloat_decimal_tailless(self):
        token = get_lex_token('12.')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.)

    def test_ufloat_decimal_headless(self):
        token = get_lex_token('.12')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 0.12)

    def test_ufloat_exponential_full(self):
        token = get_lex_token('12.34e5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34e5)

    def test_ufloat_positive_exponent(self):
        token = get_lex_token('12.34e+5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34e5)

    def test_ufloat_negative_exponent(self):
        token = get_lex_token('12.34e-5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34e-5)

    def test_ufloat_capital_exponent(self):
        token = get_lex_token('12.34E-5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.34e-5)

    def test_ufloat_exponential_no_decimal(self):
        token = get_lex_token('12E-5')
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12e-5)

    def test_name(self):
        token = get_lex_token('x')
        self.assertEqual(token.type, 'NAME')
        self.assertEqual(token.value, 'x')

    def test_string_1(self):
        token = get_lex_token("' asdf  3 5 dasd '")
        self.assertEqual(token.type, 'STRING')
        self.assertEqual(token.value, ' asdf  3 5 dasd ')

    def test_string_2(self):
        token = get_lex_token('" asdf  3 5 dasd "')
        self.assertEqual(token.type, 'STRING')
        self.assertEqual(token.value, ' asdf  3 5 dasd ')

    def test_lbracket(self):
        token = get_lex_token('[1]')
        self.assertEqual(token.type, '[')
        self.assertEqual(token.value, '[')

    def test_rbracket(self):
        token = get_lex_token(']')
        self.assertEqual(token.type, ']')
        self.assertEqual(token.value, ']')

    def test_lparen(self):
        token = get_lex_token('(1)')
        self.assertEqual(token.type, '(')
        self.assertEqual(token.value, '(')

    def test_rparen(self):
        token = get_lex_token(')')
        self.assertEqual(token.type, ')')
        self.assertEqual(token.value, ')')

    def test_minus(self):
        token = get_lex_token('-')
        self.assertEqual(token.type, '-')
        self.assertEqual(token.value, '-')

    def test_plus(self):
        token = get_lex_token('+')
        self.assertEqual(token.type, '+')
        self.assertEqual(token.value, '+')

    def test_times(self):
        token = get_lex_token('*')
        self.assertEqual(token.type, '*')
        self.assertEqual(token.value, '*')

    def test_divide(self):
        token = get_lex_token('/')
        self.assertEqual(token.type, '/')
        self.assertEqual(token.value, '/')

    def test_power(self):
        token = get_lex_token('**')
        self.assertEqual(token.type, 'POW')
        self.assertEqual(token.value, '**')

    def test_colon(self):
        token = get_lex_token(':')
        self.assertEqual(token.type, ':')
        self.assertEqual(token.value, ':')

    def test_comma(self):
        token = get_lex_token(',')
        self.assertEqual(token.type, ',')
        self.assertEqual(token.value, ',')

    def test_equals(self):
        token = get_lex_token('=')
        self.assertEqual(token.type, '=')
        self.assertEqual(token.value, '=')

    def test_lessthan(self):
        token = get_lex_token('<')
        self.assertEqual(token.type, '<')
        self.assertEqual(token.value, '<')

    def test_greaterthan(self):
        token = get_lex_token('>')
        self.assertEqual(token.type, '>')
        self.assertEqual(token.value, '>')

    def test_lessequal(self):
        token = get_lex_token('<=')
        self.assertEqual(token.type, 'LEQ')
        self.assertEqual(token.value, '<=')

    def test_greaterequal(self):
        token = get_lex_token('>=')
        self.assertEqual(token.type, 'GEQ')
        self.assertEqual(token.value, '>=')

    def test_equalto(self):
        token = get_lex_token('==')
        self.assertEqual(token.type, 'EQ')
        self.assertEqual(token.value, '==')


if __name__ == '__main__':
    unittest.main()
