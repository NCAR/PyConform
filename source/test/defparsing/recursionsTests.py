"""
Unit Tests for Definition Parser Recursive Patterns

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.defparsing import recursions as rcr

import unittest


class Tests(unittest.TestCase):

    def test_lists_empty(self):
        token = rcr.expression.parseString('[]')[0]
        self.assertEqual(token, [])

    def test_lists_of_patterns(self):
        token = rcr.expression.parseString('[1, 2.3, "c", x2]')[0]
        self.assertEqual(token, [1, 2.3, 'c', 'x2'])

    def test_lists_of_lists(self):
        token = rcr.expression.parseString('[1, 2.3, ["c", x2]]')[0]
        self.assertEqual(token, [1, 2.3, ['c', 'x2']])


if __name__ == "__main__":
    unittest.main()
