"""
Unit Tests for Variable Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from cf_units import Unit
from pyconform.metadata import Variable


class VariableTests(unittest.TestCase):

    def setUp(self):
        self.v = Variable('v')

    def test_create(self):
        self.assertIsInstance(self.v, Variable)

    def test_name(self):
        self.assertEqual(self.v.name, 'v')

    def test_default_definition_is_none(self):
        self.assertEqual(self.v.definition, None)

    def test_default_datatype_is_none(self):
        self.assertEqual(self.v.datatype, None)

    def test_default_attributes_is_empty_dict(self):
        self.assertEqual(self.v.attributes, {})

    def test_default_units_is_none(self):
        self.assertEqual(self.v.units, None)

    def test_km_units(self):
        self.v.attributes['units'] = 'km'
        self.assertEqual(self.v.units, 'km')

    def test_known_datetime_units(self):
        self.v.attributes['units'] = 'days since 1974-01-01'
        self.assertEqual(self.v.units, 'days')

    def test_unknown_datetime_units(self):
        self.v.attributes['units'] = '? since 1974-01-01'
        self.assertEqual(self.v.units, None)

    def test_default_refdatetime_is_none(self):
        self.assertEqual(self.v.refdatetime, None)

    def test_km_units_has_refdatetime_equal_to_none(self):
        self.v.attributes['units'] = 'km'
        self.assertEqual(self.v.refdatetime, None)

    def test_known_datetime_units_has_refdatetime(self):
        self.v.attributes['units'] = 'days since 1974-01-01'
        self.assertEqual(self.v.refdatetime, '1974-01-01')

    def test_unknown_datetime_units_has_refdatetime_equal_to_none(self):
        self.v.attributes['units'] = 'days since ?'
        self.assertEqual(self.v.refdatetime, None)

    def test_default_calendar_is_none(self):
        self.assertEqual(self.v.calendar, None)

    def test_known_calendar(self):
        self.v.attributes['calendar'] = 'gregorian'
        self.assertEqual(self.v.calendar, 'gregorian')

    def test_km_cfunits(self):
        self.v.attributes['units'] = 'km'
        self.assertEqual(self.v.cfunits(), Unit('km'))


if __name__ == '__main__':
    unittest.main()
