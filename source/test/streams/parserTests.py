"""
Unit Tests for Definition Parser

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.streams import parser, expressions

import unittest


class ParserTests(unittest.TestCase):

    def test_parse_definition(self):
        definition = 'f(x[4:8:-1] > 4, a=y, c=["g", 3], b={"g": 4.8})'
        result = parser.parse_definition(definition)
        x = expressions.VarType('x', [slice(4, 8, -1)])
        x_gt_4 = expressions.OpType('>', [x, 4])
        y = expressions.VarType('y', [])
        a = expressions.KwdType('a', y)
        c = expressions.KwdType('c', ["g", 3])
        b = expressions.KwdType('b', {'g': 4.8})
        f = expressions.FuncType('f', [x_gt_4, a, c, b])
        self.assertEqual(result, f)
        print result


if __name__ == "__main__":
    unittest.main()
