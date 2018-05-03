"""
Built-in Registered Functions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from functionregistry import _FunctionRegistry

import numpy as np


FunctionRegistry = _FunctionRegistry()

FunctionRegistry.add(np.sqrt)
FunctionRegistry.add(np.cbrt)

FunctionRegistry.add(np.sin)
FunctionRegistry.add(np.arcsin)
FunctionRegistry.add(np.cos)
FunctionRegistry.add(np.arccos)
FunctionRegistry.add(np.tan)
FunctionRegistry.add(np.arctan)
FunctionRegistry.add(np.arctan2)

FunctionRegistry.add(np.exp)
FunctionRegistry.add(np.log)
FunctionRegistry.add(np.log10)

FunctionRegistry.add(np.sinh)
FunctionRegistry.add(np.arcsinh)
FunctionRegistry.add(np.cosh)
FunctionRegistry.add(np.arccosh)
FunctionRegistry.add(np.tanh)
FunctionRegistry.add(np.arctanh)
