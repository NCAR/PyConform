"""
PhysArray

Copyright 2017-2018, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from exceptions import PositiveError

import xarray as xr
import cf_units as cu


class PhysArray(object):
    """
    PhysArray - Wrapper around an xarray.DataArray
    """

    def __init__(self, *args, **kwds):
        units = kwds.pop('units', None)
        calendar = kwds.pop('calendar', None)
        positive = kwds.pop('positive', None)
        self.__data = xr.DataArray(*args, **kwds)
        if units:
            self.units = units
        if calendar:
            self.calendar = calendar
        if positive:
            self.positive = positive

    @property
    def data_array(self):
        return self.__data

    @property
    def units(self):
        return self.__data.attrs.get('units', None)

    @units.setter
    def units(self, to_units):
        if to_units is None:
            self.__data.attrs.pop('units', None)
            self.calendar = None
        else:
            self.__data.attrs['units'] = str(to_units)
            if isinstance(to_units, cu.Unit) and to_units.calendar:
                self.calendar = to_units.calendar

    @property
    def calendar(self):
        return self.__data.attrs.get('calendar', None)

    @calendar.setter
    def calendar(self, to_cal):
        if to_cal is None:
            self.__data.attrs.pop('calendar', None)
        else:
            self.__data.attrs['calendar'] = str(to_cal)

    @property
    def positive(self):
        return self.__data.attrs.get('positive', None)

    @positive.setter
    def positive(self, to_pos):
        if to_pos is None:
            self.__data.attrs.pop('positive', None)
        else:
            pstr = str(to_pos).lower()
            if pstr not in ('up', 'down'):
                raise PositiveError('Positive attribute must be up or down')
            self.__data.attrs['positive'] = pstr

    def cfunits(self):
        return cu.Unit(self.units, calendar=self.calendar)
