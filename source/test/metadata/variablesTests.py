"""
Unit Tests for Variable Metadata Objects

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

import unittest
import numpy

from cf_units import Unit
from collections import OrderedDict
from pyconform.metadata import Variable
from pyconform.metadata.datasets import Dataset


class MockNetCDF4Variable(object):

    def __init__(self, name, datatype, dims):
        self.name = name
        self.dtype = numpy.dtype(datatype)
        self.dimensions = tuple(dims)
        self._attributes = OrderedDict()

    def ncattrs(self):
        return tuple(self._attributes)

    def setncattr(self, name, value):
        self._attributes[name] = value

    def getncattr(self, name):
        return self._attributes[name]

    def setncatts(self, attdict):
        return self._attributes.update(attdict)


class VariableTests(unittest.TestCase):

    def setUp(self):
        self.ds = Dataset()

    def test_create(self):
        v = self.ds.new_variable('v')
        self.assertIsInstance(v, Variable)

    def test_default_definition_is_none(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.definition, None)

    def test_setting_definition_raises_attribute_error(self):
        v = self.ds.new_variable('v')
        with self.assertRaises(AttributeError):
            v.definition = 'f(x)'

    def test_setting_definition_to_str_in_constructor(self):
        v = self.ds.new_variable('v', definition='f(x)')
        self.assertEqual(v.definition, 'f(x)')

    def test_setting_definition_to_array_in_constructor(self):
        defn = numpy.array([1, 2, 3], dtype='f')
        v = self.ds.new_variable('v', definition=defn)
        numpy.testing.assert_array_equal(v.definition, defn)

    def test_setting_definition_to_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.ds.new_variable('v', definition=4)

    def test_default_datatype_is_none(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.datatype, None)

    def test_setting_datatype_raises_attribute_error(self):
        v = self.ds.new_variable('v')
        with self.assertRaises(AttributeError):
            v.datatype = 'integer'

    def test_setting_datatype_in_constructor(self):
        v = self.ds.new_variable('v', datatype='int')
        self.assertEqual(v.datatype, 'int')

    def test_setting_datatype_to_invalid_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.ds.new_variable('v', datatype='integer')

    def test_datatype_from_dtype(self):
        for ncdt, npdt in zip(Variable._NETCDF4_TYPES_[:-1], Variable._NUMPY_DTYPES_[:-1]):
            self.assertEqual(ncdt, Variable.datatype_from_dtype(npdt))
        npdt = Variable._NUMPY_DTYPES_[-1]
        self.assertEqual('float', Variable.datatype_from_dtype(npdt))

    def test_default_dimensions_is_none(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.dimensions, None)

    def test_setting_dimensions_in_constructor(self):
        dims = ('x', 'y')
        for d in dims:
            self.ds.new_dimension(d)
        v = self.ds.new_variable('v', dimensions=dims)
        self.assertEqual(v.dimensions, dims)

    def test_setting_dimensions_to_invalid_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.ds.new_variable('v', dimensions='x y z')

    def test_get_dimensions(self):
        x = self.ds.new_dimension('x', size=5)
        v = self.ds.new_variable('v', dimensions=('x',))
        self.assertIs(v.get_dimensions()['x'], x)

    def test_default_files_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.files)

    def test_files_added_with_file_construction(self):
        v = self.ds.new_variable('v')
        self.ds.new_file('test.nc', variables=('v',))
        self.assertIn('test.nc', v.files)

    def test_get_files(self):
        v = self.ds.new_variable('v')
        f = self.ds.new_file('test.nc', variables=('v',))
        self.assertEqual(v.get_files(), {'test.nc': f})

    def test_default_attributes_is_empty_dict(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.attributes, frozenset())

    def test_setting_attributes_raises_attribute_error(self):
        v = self.ds.new_variable('v')
        with self.assertRaises(AttributeError):
            v.attributes = 4

    def test_setting_attributes_in_constructor(self):
        v = self.ds.new_variable('v', attributes={'a': 'b'})
        self.assertEqual(v.attributes, {'a'})

    def test_get_attribute(self):
        v = self.ds.new_variable('v', attributes={'x': 'y'})
        self.assertEqual(v.get_attribute('x'), 'y')

    def test_default_standard_name_is_none(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.standard_name, None)

    def test_setting_standard_name_in_attributes(self):
        vatts = {'standard_name': 'name'}
        v = self.ds.new_variable('v', attributes=vatts)
        self.assertEqual(v.standard_name, 'name')

    def test_default_units_is_none(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.units, None)

    def test_km_units(self):
        v = self.ds.new_variable('v', attributes={'units': 'km'})
        self.assertEqual(v.units, 'km')

    def test_known_datetime_units(self):
        vatts = {'units': 'days since 1974-01-01'}
        v = self.ds.new_variable('v', attributes=vatts)
        self.assertEqual(v.units, 'days')

    def test_unknown_datetime_units(self):
        vatts = {'units': '? since 1974-01-01'}
        v = self.ds.new_variable('v', attributes=vatts)
        self.assertEqual(v.units, None)

    def test_default_refdatetime_is_none(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.refdatetime, None)

    def test_km_units_has_refdatetime_equal_to_none(self):
        v = self.ds.new_variable('v', attributes={'units': 'km'})
        self.assertEqual(v.refdatetime, None)

    def test_known_datetime_units_has_refdatetime(self):
        vatts = {'units': 'days since 1974-01-01'}
        v = self.ds.new_variable('v', attributes=vatts)
        self.assertEqual(v.refdatetime, '1974-01-01')

    def test_unknown_datetime_units_has_refdatetime_equal_to_none(self):
        vatts = {'units': 'days since ?'}
        v = self.ds.new_variable('v', attributes=vatts)
        self.assertEqual(v.refdatetime, None)

    def test_default_calendar_is_none(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.calendar, None)

    def test_known_calendar(self):
        vatts = {'calendar': 'gregorian'}
        v = self.ds.new_variable('v', attributes=vatts)
        self.assertEqual(v.calendar, 'gregorian')

    def test_km_cfunits(self):
        v = self.ds.new_variable('v', attributes={'units': 'km'})
        self.assertEqual(v.cfunits(), Unit('km'))

    def test_default_positive_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.positive)

    def test_positive_set_in_attributes(self):
        v = self.ds.new_variable('v', attributes={'positive': 'up'})
        self.assertEqual(v.positive, 'up')

    def test_default_axis_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.axis)

    def test_default_auxcoords_is_empty_tuple(self):
        v = self.ds.new_variable('v')
        self.assertEqual(v.auxcoords, set())

    def test_auxcoords_set_in_attributes(self):
        self.ds.new_variable('x')
        self.ds.new_variable('y')
        v = self.ds.new_variable('v', attributes={'coordinates': 'x y'})
        self.assertEqual(v.auxcoords, {'x', 'y'})

    def test_default_bounds_is_none(self):
        v = self.ds.new_variable('v')
        self.assertIsNone(v.bounds)

    def test_bounds_set_in_attributes(self):
        self.ds.new_variable('v_bnds')
        v = self.ds.new_variable('v', attributes={'bounds': 'v_bnds'})
        self.assertEqual(v.bounds, 'v_bnds')

    def test_coordinates(self):
        self.ds.new_dimension('i')
        self.ds.new_dimension('j')
        self.ds.new_variable('i', dimensions=('i',))
        self.ds.new_variable('j', dimensions=('j',))
        self.ds.new_variable('x', dimensions=('i', 'j'))
        self.ds.new_variable('y', dimensions=('i', 'j'))
        vatts = {'coordinates': 'x y'}
        v = self.ds.new_variable('v', dimensions=('i', 'j'), attributes=vatts)
        self.assertItemsEqual(v.coordinates, {'i', 'j', 'x', 'y'})

    def test_get_coordinates(self):
        self.ds.new_dimension('i')
        self.ds.new_dimension('j')
        i = self.ds.new_variable('i', dimensions=('i',))
        j = self.ds.new_variable('j', dimensions=('j',))
        x = self.ds.new_variable('x', dimensions=('i', 'j'))
        y = self.ds.new_variable('y', dimensions=('i', 'j'))
        vatts = {'coordinates': 'x y'}
        v = self.ds.new_variable('v', dimensions=('i', 'j'), attributes=vatts)
        self.assertEqual(v.get_coordinates(), {'i': i, 'j': j, 'x': x, 'y': y})

    def test_from_netcdf4(self):
        ncvar = MockNetCDF4Variable('v', 'f', ('x', 'y'))
        self.ds.new_dimension('x')
        self.ds.new_dimension('y')
        v = Variable.from_netcdf4(ncvar, dataset=self.ds)
        self.assertEqual(v.name, 'v')
        self.assertEqual(v.dtype, numpy.dtype('f'))
        self.assertEqual(v.dimensions, ('x', 'y'))

    def test_equal(self):
        self.ds.new_dimension('x')
        self.ds.new_dimension('y')
        v1 = self.ds.new_variable('v', datatype='float',
                                  dimensions=('x', 'y'))
        v2 = self.ds.new_variable('u', datatype='float',
                                  dimensions=('x', 'y'))
        self.assertIsNot(v1, v2)
        self.assertEqual(v1, v2)

    def test_is_netcdf3_type(self):
        v = self.ds.new_variable('v', datatype='float')
        self.assertTrue(v.is_netcdf3_type())
        u = self.ds.new_variable('u', datatype='int64')
        self.assertFalse(u.is_netcdf3_type())


if __name__ == '__main__':
    unittest.main()
