"""
Function Registry

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from types import FunctionType


class FunctionRegistry(object):
    """
    A Registry for functions that can be referenced in variable definitions
    """
    __LAMBDA_NAME__ = (lambda: None).__name__

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
        if name == FunctionRegistry.__LAMBDA_NAME__:
            raise TypeError('Lambda functions require a separate name')
        self.__callables[name] = func
