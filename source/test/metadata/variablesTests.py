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
        self.v = Variable('v', dataset=self.ds)

    def test_create(self):
        self.assertIsInstance(self.v, Variable)

    def test_default_definition_is_none(self):
        self.assertEqual(self.v.definition, None)

    def test_setting_definition_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.v.definition = 'f(x)'

    def test_setting_definition_to_str_in_constructor(self):
        v = Variable('v', definition='f(x)', dataset=self.ds)
        self.assertEqual(v.definition, 'f(x)')

    def test_setting_definition_to_array_in_constructor(self):
        defn = numpy.array([1, 2, 3], dtype='f')
        v = Variable('v', definition=defn, dataset=self.ds)
        numpy.testing.assert_array_equal(v.definition, defn)

    def test_setting_definition_to_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            Variable('v', definition=4, dataset=self.ds)

    def test_default_datatype_is_none(self):
        self.assertEqual(self.v.datatype, None)

    def test_setting_datatype_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.v.datatype = 'integer'

    def test_setting_datatype_in_constructor(self):
        v = Variable('v', datatype='int', dataset=self.ds)
        self.assertEqual(v.datatype, 'int')

    def test_setting_datatype_to_invalid_raises_value_error(self):
        with self.assertRaises(ValueError):
            Variable('v', datatype='integer', dataset=self.ds)

    def test_datatype_from_dtype(self):
        for ncdt, npdt in zip(Variable._NETCDF4_TYPES_[:-1], Variable._NUMPY_DTYPES_[:-1]):
            self.assertEqual(ncdt, Variable.datatype_from_dtype(npdt))
        npdt = Variable._NUMPY_DTYPES_[-1]
        self.assertEqual('float', Variable.datatype_from_dtype(npdt))

    def test_default_dimensions_is_none(self):
        self.assertEqual(self.v.dimensions, None)

    def test_setting_dimensions_in_constructor(self):
        dims = ('x', 'y')
        v = Variable('v', dimensions=dims, dataset=self.ds)
        self.assertEqual(v.dimensions, dims)

    def test_setting_dimensions_to_invalid_raises_type_error(self):
        with self.assertRaises(TypeError):
            Variable('v', dimensions='x y z', dataset=self.ds)

    def test_default_attributes_is_empty_dict(self):
        self.assertEqual(self.v.attributes, frozenset())

    def test_setting_attributes_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            self.v.attributes = 4

    def test_setting_attributes_in_constructor(self):
        v = Variable('v', attributes={'a': 'b'}, dataset=self.ds)
        self.assertEqual(v.attributes, {'a'})

    def test_get_attribute(self):
        v = Variable('v', attributes={'x': 'y'}, dataset=self.ds)
        self.assertEqual(v.get_attribute('x'), 'y')

    def test_default_standard_name_is_none(self):
        self.assertEqual(self.v.standard_name, None)

    def test_setting_standard_name_in_attributes(self):
        vatts = {'standard_name': 'name'}
        v = Variable('v', attributes=vatts, dataset=self.ds)
        self.assertEqual(v.standard_name, 'name')

    def test_default_units_is_none(self):
        self.assertEqual(self.v.units, None)

    def test_km_units(self):
        v = Variable('v', attributes={'units': 'km'}, dataset=self.ds)
        self.assertEqual(v.units, 'km')

    def test_known_datetime_units(self):
        vatts = {'units': 'days since 1974-01-01'}
        v = Variable('v', attributes=vatts, dataset=self.ds)
        self.assertEqual(v.units, 'days')

    def test_unknown_datetime_units(self):
        vatts = {'units': '? since 1974-01-01'}
        v = Variable('v', attributes=vatts, dataset=self.ds)
        self.assertEqual(v.units, None)

    def test_default_refdatetime_is_none(self):
        self.assertEqual(self.v.refdatetime, None)

    def test_km_units_has_refdatetime_equal_to_none(self):
        v = Variable('v', attributes={'units': 'km'}, dataset=self.ds)
        self.assertEqual(v.refdatetime, None)

    def test_known_datetime_units_has_refdatetime(self):
        vatts = {'units': 'days since 1974-01-01'}
        v = Variable('v', attributes=vatts, dataset=self.ds)
        self.assertEqual(v.refdatetime, '1974-01-01')

    def test_unknown_datetime_units_has_refdatetime_equal_to_none(self):
        vatts = {'units': 'days since ?'}
        v = Variable('v', attributes=vatts, dataset=self.ds)
        self.assertEqual(v.refdatetime, None)

    def test_default_calendar_is_none(self):
        self.assertEqual(self.v.calendar, None)

    def test_known_calendar(self):
        vatts = {'calendar': 'gregorian'}
        v = Variable('v', attributes=vatts, dataset=self.ds)
        self.assertEqual(v.calendar, 'gregorian')

    def test_km_cfunits(self):
        v = Variable('v', attributes={'units': 'km'}, dataset=self.ds)
        self.assertEqual(v.cfunits(), Unit('km'))

    def test_default_positive_is_none(self):
        self.assertIsNone(self.v.positive)

    def test_positive_set_in_attributes(self):
        v = Variable('v', attributes={'positive': 'up'}, dataset=self.ds)
        self.assertEqual(v.positive, 'up')

    def test_default_auxcoords_is_empty_tuple(self):
        self.assertEqual(self.v.auxcoords, set())

    def test_auxcoords_set_in_attributes(self):
        v = Variable('v', attributes={'coordinates': 'x y'}, dataset=self.ds)
        self.assertEqual(v.auxcoords, {'x', 'y'})

    def test_from_netcdf4(self):
        ncvar = MockNetCDF4Variable('v', 'f', ('x', 'y'))
        v = Variable.from_netcdf4(ncvar, dataset=self.ds)
        self.assertEqual(v.name, 'v')
        self.assertEqual(v.dtype, numpy.dtype('f'))
        self.assertEqual(v.dimensions, ('x', 'y'))

    def test_equal(self):
        v1 = Variable('v', datatype='float',
                      dimensions=('x', 'y'), dataset=self.ds)
        v2 = Variable('v', datatype='float',
                      dimensions=('x', 'y'), dataset=self.ds)
        self.assertIsNot(v1, v2)
        self.assertEqual(v1, v2)

    def test_is_netcdf3_type(self):
        v = Variable('v', datatype='float', dataset=self.ds)
        self.assertTrue(v.is_netcdf3_type())
        v = Variable('v', datatype='int64', dataset=self.ds)
        self.assertFalse(v.is_netcdf3_type())


if __name__ == '__main__':
    unittest.main()
