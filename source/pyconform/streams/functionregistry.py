"""
Function Registry

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from types import FunctionType


__LAMBDA_NAME__ = (lambda: None).__name__


class FunctionRegistry(object):
    """
    A Registry for functions that can be referenced in variable definitions
    """

    def __init__(self):
        self.__callables = {}

    def __contains__(self, name):
        return name in self.__callables

    def __getitem__(self, name):
        return self.__callables[name]

    def __get_func_name__(self, func):
        if isinstance(func, FunctionType):
            return func.__name__
        elif callable(func):
            return func.__class__.__name__
        else:
            raise TypeError('Object {} not callable'.format(func))

    def add(self, func, name=None):
        if name is None:
            name = self.__get_func_name__(func)
        if name == __LAMBDA_NAME__:
            raise TypeError('Lambda functions require a separate name')
        if name in self:
            raise KeyError('Function {!r} already registered'.format(name))
        self.__callables[name] = func

    def remove(self, name):
        del self.__callables[name]

    def clear(self):
        self.__callables.clear()


registry = FunctionRegistry()
