"""
Variable Metadata Class

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from cf_units import Unit


class Variable(object):
    """
    Metadata describing a NetCDF variable
    """

    def __init__(self, name):
        self.name = name
        self.definition = None
        self.datatype = None
        self.attributes = {}

    @property
    def units(self):
        ustr = str(self.attributes.get('units', '?')).split('since')[0].strip()
        return None if ustr in ('', '?', 'unknown') else ustr

    @property
    def refdatetime(self):
        lstr = str(self.attributes.get('units', '?')).split('since')
        rstr = lstr[1].strip() if len(lstr) > 1 else ''
        return None if rstr in ('', '?', 'unknown') else rstr

    @property
    def calendar(self):
        return self.attributes.get('calendar', None)

    def cfunits(self):
        return Unit(self.attributes.get('units'), calendar=self.calendar)