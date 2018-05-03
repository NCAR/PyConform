"""
Unit Tests for Registered Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.functions import FunctionRegistry

import unittest


class Tests(unittest.TestCase):

    def test_contents(self):
        flist = list(FunctionRegistry)
        self.assertItemsEqual(flist, ['sqrt', 'cbrt', 'sin', 'arcsin', 'cos', 'arccos', 'tan', 'arctan', 'arctan2',
                                      'exp', 'log', 'log10', 'sinh', 'arcsinh', 'cosh', 'arccosh', 'tanh', 'arctanh'])

    def test_sqrt(self):
        f = FunctionRegistry['sqrt']
        self.assertEqual(f(4.0), 2.0)

    def test_cbrt(self):
        f = FunctionRegistry['cbrt']
        self.assertEqual(f(8.0), 2.0)


if __name__ == "__main__":
    unittest.main()
