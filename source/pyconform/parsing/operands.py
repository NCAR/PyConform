"""
Operation Graph Parsing - Operands

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from pyconform.dataset import InputDataset
from pyconform.operators import InputSliceReader
from itertools import cycle

import pyparsing as pp


#===============================================================================
# OperandParser
#===============================================================================
class OperandParser(object):
    """
    Class to parse operands in string variable definitions
    """
    
    def __init__(self, pattern, action=None):
        """
        Initializer
        
        Parameters:
            pattern (str): A regular expression pattern identifying the
                operand type
            action (callable): The function to call to transform the
                operand from string to final form
        """
        self._token = pp.Regex(pattern)
        self._token.setParseAction(self)
        self._action = action

    @property
    def token(self):
        return self._token
    
    def action(self, token):
        if callable(self._action):
            return self._action(token)
        else:
            return token
    
    def __call__(self, string, location, tokens):
        self.action(tokens[0])


#===============================================================================
# VariableOperandParser
#===============================================================================
class VariableOperandParser(OperandParser):
    """
    Class to parse variable-name operands in string variable definitions
    """
    
    def __init__(self, inp):
        """
        Initializer
        
        Parameters:
            inp (InputDataset): Input dataset in which variables can be
                found from their referenced name
        """
        if not isinstance(inp, InputDataset):
            raise TypeError('VariableOperandParser needs an InputDataset')
        self._ids = inp

        fnames = [v.filename for v in self._ids.variables.itervalues()]
        self._ifncycle = cycle(filter(None, fnames))
        
        super(VariableOperandParser, self).__init__(r'[a-zA-Z_][a-zA-Z0-9_]*')
    
    def action(self, token):
        varname = str(token)
        if varname not in self._ids.variables:
            err_msg = ('Found reference to variable {!r} that is not '
                       'is not found in the reference dataset '
                       '{!r}').format(varname, self._ids.name)
            raise KeyError(err_msg)
        if self._ids.variables[varname].filename:
            fname = self._ids.variables[varname].filename
        else:
            fname = self._ifncycle.next()
        op = InputSliceReader(fname, varname)
        self._opgraph.add(op)
        return op
