"""
Unit Tests for Variable Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from cf_units import Unit
from numpy import array
from numpy.testing import assert_array_equal
from pyconform.metadata import Variable, Dimension


class VariableTests(unittest.TestCase):

    def setUp(self):
        self.v = Variable('v')

    def test_create(self):
        self.assertIsInstance(self.v, Variable)

    def test_default_definition_is_none(self):
        self.assertEqual(self.v.definition, None)

    def test_setting_definition_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.v.definition = 'f(x)'

    def test_setting_definition_to_str_in_constructor(self):
        v = Variable('v', definition='f(x)')
        self.assertEqual(v.definition, 'f(x)')

    def test_setting_definition_to_array_in_constructor(self):
        defn = array([1, 2, 3], dtype='f')
        v = Variable('v', definition=defn)
        assert_array_equal(v.definition, defn)

    def test_setting_definition_to_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            Variable('v', definition=4)

    def test_default_datatype_is_none(self):
        self.assertEqual(self.v.datatype, None)

    def test_setting_datatype_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.v.datatype = 'integer'

    def test_setting_datatype_in_constructor(self):
        v = Variable('v', datatype='int')
        self.assertEqual(v.datatype, 'int')

    def test_setting_datatype_to_invalid_raises_value_error(self):
        with self.assertRaises(ValueError):
            Variable('v', datatype='integer')

    def test_datatype_from_dtype(self):
        for ncdt, npdt in zip(Variable._NETCDF_TYPES_[:-1], Variable._NUMPY_DTYPES_[:-1]):
            self.assertEqual(ncdt, Variable.datatype_from_dtype(npdt))
        npdt = Variable._NUMPY_DTYPES_[-1]
        self.assertEqual('float', Variable.datatype_from_dtype(npdt))

    def test_default_dimensions_is_none(self):
        self.assertEqual(self.v.dimensions, None)

    def test_setting_dimensions_in_constructor(self):
        dims = (Dimension('x'), Dimension('y'))
        v = Variable('v', dimensions=dims)
        self.assertEqual(v.dimensions, dims)

    def test_setting_dimensions_to_invalid_raises_type_error(self):
        with self.assertRaises(TypeError):
            Variable('v', dimensions='x y z')

    def test_default_attributes_is_empty_dict(self):
        self.assertEqual(self.v.attributes, {})

    def test_setting_attributes_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.v.attributes = 4

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
