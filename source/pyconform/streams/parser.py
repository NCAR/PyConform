"""
Definiton Parser Expressions

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from expressions import expr


def parse_definition(string):
    return expr.parseString(string)[0]
