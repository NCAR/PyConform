"""
Unit Tests for Function Registry

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.streams.functionregistry import FunctionRegistry

import unittest


class RegistryTests(unittest.TestCase):

    def setUp(self):
        self.reg = FunctionRegistry()

    def test_add_lambda_function_with_name(self):
        self.reg.add(lambda: 2, name='two')
        self.assertIn('two', self.reg)

    def test_getitem_lambda_function_with_name(self):
        self.reg.add(lambda: 2, name='two')
        f = self.reg['two']
        self.assertEqual(f(), 2)

    def test_add_lambda_function_without_name_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.reg.add(lambda: 2)

    def test_add_function_with_name(self):
        def f(x): return x + 2
        self.reg.add(f, name='plus2')
        self.assertIn('plus2', self.reg)

    def test_getitem_function_with_name(self):
        def f(x): return x + 2
        self.reg.add(f, name='plus2')
        plus2 = self.reg['plus2']
        self.assertEqual(plus2(1), 3)

    def test_add_function_without_name(self):
        def f(x): return x + 2
        self.reg.add(f)
        self.assertIn('f', self.reg)

    def test_getitem_function_without_name(self):
        def f(x): return x + 2
        self.reg.add(f)
        plus2 = self.reg['f']
        self.assertEqual(plus2(1), 3)

    def test_add_instance_with_name(self):
        class PlusY(object):
            def __init__(self, y=2):
                self.y = y

            def __call__(self, x):
                return x + self.y

        plus2 = PlusY(2)
        self.reg.add(plus2, name='plus2')
        self.assertIn('plus2', self.reg)

    def test_getitem_instance_with_name(self):
        class PlusY(object):
            def __init__(self, y=2):
                self.y = y

            def __call__(self, x):
                return x + self.y

        plus2 = PlusY(2)
        self.reg.add(plus2, name='plus2')
        p = self.reg['plus2']
        self.assertEqual(p(1), 3)

    def test_add_instance_without_name(self):
        class PlusY(object):
            def __init__(self, y=2):
                self.y = y

            def __call__(self, x):
                return x + self.y

        plus2 = PlusY(2)
        self.reg.add(plus2)
        self.assertIn('PlusY', self.reg)

    def test_getitem_instance_without_name(self):
        class PlusY(object):
            def __init__(self, y=2):
                self.y = y

            def __call__(self, x):
                return x + self.y

        plus2 = PlusY(2)
        self.reg.add(plus2)
        p = self.reg['PlusY']
        self.assertEqual(p(1), 3)

    def test_add_duplicate_function_raises_key_error(self):
        self.reg.add(lambda x: x + 2, name='f')
        with self.assertRaises(KeyError):
            self.reg.add(lambda y: y * 2, name='f')

    def test_remove_function(self):
        self.reg.add(lambda x: x + 2, name='f')
        self.reg.add(lambda y: y * 2, name='g')
        self.reg.remove('g')
        self.assertIn('f', self.reg)
        self.assertNotIn('g', self.reg)

    def test_remove_function_not_contained_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.reg.remove('g')

    def test_clear(self):
        self.reg.add(lambda x: x + 2, name='f')
        self.reg.add(lambda y: y * 2, name='g')
        self.reg.clear()
        self.assertNotIn('f', self.reg)
        self.assertNotIn('g', self.reg)


if __name__ == "__main__":
    unittest.main()
