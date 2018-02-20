"""
Unit Tests for Variable Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest

from cf_units import Unit
from pyconform.specification import Variable, Specification


class VariableTests(unittest.TestCase):

    def setUp(self):
        self.ds = Specification()

    def test_create(self):
        v = self.ds.new_variable('v')
        self.assertIsInstance(v, Variable)

    def test_default_definition_is_none(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.definition, None)

    def test_setting_definition_to_none_saves_none(self):
        v = self.ds.new_variable('v')
        v.definition = None
        self.assertIsNone(v.definition)

    def test_setting_definition_property_to_expression_saves_expression(self):
        v = self.ds.new_variable('v')
        v.definition = 'f(x)'
        self.assertEqual(v.definition, 'f(x)')

    def test_setting_definition_in_constructor_to_expression_saves_expression(self):
        v = self.ds.new_variable('v', definition='f(x)')
        self.assertEqual(v.definition, 'f(x)')

    def test_setting_definition_to_array_like_saves_array_like(self):
        vdef = [[1, 2], [3, 4], [5, 6]]
        v = self.ds.new_variable('v', definition=vdef)
        self.assertEqual(v.definition, vdef)

    def test_setting_definition_to_invalid_type_raises_type_error(self):
        v = self.ds.new_variable('v')
        with self.assertRaises(TypeError):
            v.definition = 2345

    def test_default_datatype_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.datatype)

    def test_setting_datatype_property_to_valid_value_saves_value(self):
        v = self.ds.new_variable('v')
        v.datatype = 'int'
        self.assertEqual(v.datatype, 'int')

    def test_setting_datatype_in_constructor_to_valid_value_saves_value(self):
        v = self.ds.new_variable('v', datatype='int')
        self.assertEqual(v.datatype, 'int')

    def test_setting_datatype_to_invalid_value_raises_type_error(self):
        v = self.ds.new_variable('v')
        with self.assertRaises(ValueError):
            v.datatype = 4

    def test_datatype_from_dtype(self):
        for ncdt, npdt in zip(Variable._NETCDF4_TYPES_[:-1], Variable._NUMPY_DTYPES_[:-1]):
            self.assertEqual(ncdt, Variable.datatype_from_dtype(npdt))
        npdt = Variable._NUMPY_DTYPES_[-1]
        self.assertEqual('float', Variable.datatype_from_dtype(npdt))

    def test_default_dimensions_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.dimensions)

    def test_setting_dimensions_property_to_tuple_saves_tuple(self):
        x = self.ds.new_dimension('x')
        y = self.ds.new_dimension('y')
        v = self.ds.new_variable('v')
        v.dimensions = ('x', 'y')
        self.assertEqual(v.dimensions, {'x': x, 'y': y})

    def test_setting_dimensions_in_constructor_to_tuple_saves_tuple(self):
        x = self.ds.new_dimension('x')
        y = self.ds.new_dimension('y')
        v = self.ds.new_variable('v', dimensions=('x', 'y'))
        self.assertEqual(v.dimensions, {'x': x, 'y': y})

    def test_setting_dimensions_to_invalid_raises_type_error(self):
        v = self.ds.new_variable('v')
        with self.assertRaises(TypeError):
            v.dimensions = 'x y z'

    def test_get_dimensions(self):
        x = self.ds.new_dimension('x')
        v = self.ds.new_variable('v')
        v.dimensions = ('x',)
        self.assertEqual(v.dimensions, {'x': x})

    def test_default_files_is_empty_dict(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.files, {})

    def test_files_added_by_adding_to_file(self):
        f = self.ds.new_file('test.nc')
        v = self.ds.new_variable('v')
        f.add_variables('v')
        self.assertEqual(v.files, {'test.nc': f})

    def test_default_attributes_is_empty_dict(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.attributes, {})

    def test_setting_attributes_raises_attribute_error(self):
        v = self.ds.new_variable('v')
        with self.assertRaises(AttributeError):
            v.attributes = 4

    def test_setting_attributes_by_key_value(self):
        v = self.ds.new_variable('v')
        v.attributes['a'] = 'b'
        self.assertEqual(v.attributes, {'a': 'b'})

    def test_setting_attributes_in_constructor_with_dict(self):
        v = self.ds.new_variable('v', attributes={'a': 'b'})
        self.assertEqual(v.attributes, {'a': 'b'})

    def test_default_standard_name_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.standard_name)

    def test_setting_standard_name_saves_value(self):
        v = self.ds.new_variable('v')
        v.standard_name = 'name'
        self.assertEqual(v.standard_name, 'name')

    def test_default_units_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.units)

    def test_default_refdatetime_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.refdatetime)

    def test_km_units(self):
        v = self.ds.new_variable('v')
        v.units = 'km'
        self.assertEqual(v.units, 'km')
        self.assertIsNone(v.refdatetime)
        self.assertEqual(v.attributes['units'], 'km')

    def test_known_datetime_units(self):
        v = self.ds.new_variable('v')
        v.units = 'days'
        v.refdatetime = '1974-01-01'
        self.assertEqual(v.units, 'days')
        self.assertEqual(v.refdatetime, '1974-01-01')
        self.assertEqual(v.attributes['units'], 'days since 1974-01-01')

    def test_unknown_datetime_units(self):
        v = self.ds.new_variable('v')
        v.units = '?'
        v.refdatetime = '1974-01-01'
        self.assertEqual(v.units, 'unknown')
        self.assertEqual(v.refdatetime, '1974-01-01')
        self.assertEqual(v.attributes['units'], 'unknown since 1974-01-01')

    def test_unknown_datetime_units_has_refdatetime_equal_to_none(self):
        v = self.ds.new_variable('v')
        v.units = '?'
        v.refdatetime = None
        self.assertEqual(v.units, 'unknown')
        self.assertIsNone(v.refdatetime)
        self.assertEqual(v.attributes['units'], 'unknown')

    def test_default_calendar_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.calendar)

    def test_known_calendar(self):
        v = self.ds.new_variable('v')
        v.calendar = 'gregorian'
        self.assertEqual(v.calendar, 'gregorian')

    def test_km_cfunits(self):
        v = self.ds.new_variable('v')
        v.units = 'km'
        self.assertEqual(v.cfunits(), Unit('km'))

    def test_default_positive_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.positive)

    def test_setting_positive(self):
        v = self.ds.new_variable('v')
        v.positive = 'up'
        self.assertEqual(v.positive, 'up')

    def test_default_axis_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.axis)

    def test_setting_axis(self):
        v = self.ds.new_variable('v')
        v.axis = 'x'
        self.assertEqual(v.axis, 'X')

    def test_default_auxcoords_is_empty_dict(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.auxcoords, {})

    def test_setting_auxcoords_to_tuple(self):
        x = self.ds.new_variable('x')
        y = self.ds.new_variable('y')
        v = self.ds.new_variable('v')
        v.auxcoords = ('x', 'y')
        self.assertEqual(v.attributes['coordinates'], 'x y')
        self.assertEqual(v.auxcoords, {'x': x, 'y': y})

    def test_default_bounds_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.bounds)

    def test_setting_bounds_to_string(self):
        v_bnds = self.ds.new_variable('v_bnds')
        v = self.ds.new_variable('v')
        v.bounds = 'v_bnds'
        self.assertEqual(v.bounds, v_bnds)

    def test_coordinates(self):
        self.ds.new_dimension('i')
        self.ds.new_dimension('j')
        i = self.ds.new_variable('i')
        i.dimensions = ('i',)
        j = self.ds.new_variable('j')
        j.dimensions = ('j',)
        x = self.ds.new_variable('x')
        x.dimensions = ('i', 'j')
        y = self.ds.new_variable('y')
        y.dimensions = ('i', 'j')
        v = self.ds.new_variable('v')
        v.dimensions = ('i', 'j')
        v.auxcoords = ('x', 'y')
        self.assertItemsEqual(v.coordinates, {'i': i, 'j': j, 'x': x, 'y': y})

    def test_equal(self):
        ds1 = Specification()
        ds2 = Specification()
        ds1.new_dimension('x')
        ds2.new_dimension('x')
        v1 = ds1.new_variable('v')
        v1.datatype = 'float'
        v1.dimensions = ('x',)
        v2 = ds2.new_variable('v')
        v2.datatype = 'float'
        v2.dimensions = ('x',)
        self.assertIsNot(v1, v2)
        self.assertEqual(v1, v2)

    def test_is_netcdf3_type(self):
        v = self.ds.new_variable('v')
        v.datatype = 'float'
        self.assertTrue(v.is_netcdf3_type())
        u = self.ds.new_variable('u')
        u.datatype = 'int64'
        self.assertFalse(u.is_netcdf3_type())


if __name__ == '__main__':
    unittest.main()
