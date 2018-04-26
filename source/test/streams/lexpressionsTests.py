"""
Unit Tests for Definition Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.streams import lexpressions

import unittest


class LexTests(unittest.TestCase):

    def test_uint(self):
        lexpressions.lex_input('   142 5   ')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, 142)

    def test_int_positive(self):
        lexpressions.lex_input('+142')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, 142)

    def test_int_negative(self):
        lexpressions.lex_input('-142')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'INT')
        self.assertEqual(token.value, -142)

    def test_ufloat_decimal_no_trailing(self):
        lexpressions.lex_input('12.')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 12.0)

    def test_ufloat_decimal_no_leading(self):
        lexpressions.lex_input('.12')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, .12)

    def test_ufloat_decimal(self):
        lexpressions.lex_input('34.12')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 34.12)

    def test_ufloat_decimal_positive(self):
        lexpressions.lex_input('+34.12')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 34.12)

    def test_ufloat_decimal_negative(self):
        lexpressions.lex_input('-34.12')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, -34.12)

    def test_ufloat_negative_exponent(self):
        lexpressions.lex_input('34.12e-5')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, 34.12e-5)

    def test_ufloat_positive_exponent(self):
        lexpressions.lex_input('-34.12e+5')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, -34.12e+5)

    def test_ufloat_exponent_no_decimal(self):
        lexpressions.lex_input('-34e-5')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'FLOAT')
        self.assertEqual(token.value, -34e-5)

    def test_str_with_double_quotes(self):
        lexpressions.lex_input('   "ab cd e" 4')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'STRING')
        self.assertEqual(token.value, 'ab cd e')

    def test_str_with_single_quotes(self):
        lexpressions.lex_input("'ab cd e'")
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'STRING')
        self.assertEqual(token.value, 'ab cd e')

    def test_str_with_mixed_quotes(self):
        lexpressions.lex_input("'ab \"cd\" e'")
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'STRING')
        self.assertEqual(token.value, 'ab "cd" e')

    def test_name_solo_underscore(self):
        lexpressions.lex_input('_')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'NAME')
        self.assertEqual(token.value, '_')

    def test_name_with_underscore_separation(self):
        lexpressions.lex_input('_a_b_c_')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'NAME')
        self.assertEqual(token.value, '_a_b_c_')

    def test_colon(self):
        lexpressions.lex_input(':')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'COLON')
        self.assertEqual(token.value, ':')

    def test_lbracket(self):
        lexpressions.lex_input('[')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'LBRACKET')
        self.assertEqual(token.value, '[')

    def test_rbracket(self):
        lexpressions.lex_input(']')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'RBRACKET')
        self.assertEqual(token.value, ']')

    def test_lparen(self):
        lexpressions.lex_input('(')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'LPAREN')
        self.assertEqual(token.value, '(')

    def test_rparen(self):
        lexpressions.lex_input(')')
        token = lexpressions.lex_next_token()
        self.assertEqual(token.type, 'RPAREN')
        self.assertEqual(token.value, ')')


class YaccTests(unittest.TestCase):

    def test_float(self):
        p = lexpressions.yacc_parse('1.3e6')
        self.assertEqual(p, 1.3e6)

    def test_int(self):
        p = lexpressions.yacc_parse(' 123   ')
        self.assertEqual(p, 123)


if __name__ == "__main__":
    unittest.main()
