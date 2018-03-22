#! /usr/bin/env python


import time, sys
import numpy as np
from pyconform.physarray import PhysArray, UnitsError, DimensionsError
from pyconform.functions import Function, is_constant


class CLM_landunit_to_CMIP6_Lut_Function(Function):
    key = 'CLM_landunit_to_CMIP6_Lut'

    def __init__(self, EFLX_LH_TOT, ntim, nlat, nlon, grid1d_ixy, grid1d_jxy, grid1d_lon,
                              grid1d_lat, land1d_lon, land1d_lat, land1d_ityplunit,
                              land1d_active, land1d_wtgcell):

        super(CLM_landunit_to_CMIP6_Lut_Function, self).__init__(EFLX_LH_TOT, ntim, nlat, nlon, grid1d_ixy, grid1d_jxy, grid1d_lon,
                              grid1d_lat, land1d_lon, land1d_lat, land1d_ityplunit,
                              land1d_active, land1d_wtgcell)
  

    def __getitem__(self, index):

        EFLX_LH_TOT = self.arguments[0] if is_constant(self.arguments[0]) else self.arguments[0][index]
        ntim = self.arguments[1] if is_constant(self.arguments[1]) else self.arguments[1][index]
        nlat = self.arguments[2] if is_constant(self.arguments[2]) else self.arguments[2][index]
        nlon = self.arguments[3] if is_constant(self.arguments[3]) else self.arguments[3][index]
        grid1d_ixy = self.arguments[4] if is_constant(self.arguments[4]) else self.arguments[4][index]
        grid1d_jxy  = self.arguments[5] if is_constant(self.arguments[5]) else self.arguments[5][index]
        grid1d_lon = self.arguments[6] if is_constant(self.arguments[6]) else self.arguments[6][index]
        grid1d_lat = self.arguments[7] if is_constant(self.arguments[7]) else self.arguments[7][index]
        land1d_lon = self.arguments[8] if is_constant(self.arguments[8]) else self.arguments[8][index]
        land1d_lat = self.arguments[9] if is_constant(self.arguments[9]) else self.arguments[9][index]
        land1d_ityplunit = self.arguments[10] if is_constant(self.arguments[10]) else self.arguments[10][index]
        land1d_active = self.arguments[11] if is_constant(self.arguments[11]) else self.arguments[11][index]
        land1d_wtgcell = self.arguments[12] if is_constant(self.arguments[12]) else self.arguments[12][index]


	long_name = "latent heat flux on land use tile (lut=0:natveg, =1:crop, =2:pasture, =3:urban)"
	nlut    = 4
	veg     = 0
	crop    = 1
	pasture = 2
	urban   = 3

	# Tolerance check for weights summing to 1
	eps = 1.e-5

	# Will contain landunit variables for veg, crop, pasture, and urban on 2d grid
	varo_lut = np.full([len(ntim),4,len(nlat),len(nlon)],fill_value=1.e36)
	# Set pasture to fill value
	varo_lut[:,pasture,:,:] = 1.e36

	# If 1, landunit is active
	active_lunit = 1
	# If 1, landunit is veg
	veg_lunit  = 1
	# If 2, landunit is crop
	crop_lunit  = 2
	# If 7,8, or 9, landunit is urban
	beg_urban_lunit  = 7
	end_urban_lunit  = 9

	# Set up numpy array to compare against
	t = np.stack((land1d_lon,land1d_lat,land1d_active,land1d_ityplunit), axis=1)
	tu = np.stack((land1d_lon,land1d_lat,land1d_active), axis=1)

	ind = np.stack((grid1d_ixy,grid1d_jxy), axis=1)

	# Loop over lat/lons
	for ixy in range(len(nlon)):
	    for jxy in range(len(nlat)):

		grid_indx = -99 
		# 1d grid index
		ind_comp = (ixy+1,jxy+1)
		gi = np.where(np.all(ind==ind_comp, axis=1))[0]
		if len(gi) > 0:
		    grid_indx = gi[0]

		landunit_indx_veg = 0.0
		landunit_indx_crop = 0.0
		landunit_indx_urban = 0.0
		# Check for valid land gridcell
		if grid_indx != -99:
     
		    # Gridcell lat/lons
		    grid1d_lon_pt = grid1d_lon[grid_indx]
		    grid1d_lat_pt = grid1d_lat[grid_indx]

		    # veg landunit index for this gridcell
		    t_var = (grid1d_lon_pt, grid1d_lat_pt, active_lunit, veg_lunit) 
		    landunit_indx_veg = np.where(np.all(t_var == t, axis=1) * (land1d_wtgcell>0))[0]
		    
		    # crop landunit index for this gridcell
		    t_var = (grid1d_lon_pt, grid1d_lat_pt, active_lunit, crop_lunit)
		    landunit_indx_crop = np.where(np.all(t_var == t, axis=1) * (land1d_wtgcell>0))[0]

		    # urban landunit indices for this gridcell
		    t_var = (grid1d_lon_pt, grid1d_lat_pt, active_lunit)
		    landunit_indx_urban = np.where( np.all(t_var == tu, axis=1) * (land1d_ityplunit>=beg_urban_lunit) * (land1d_ityplunit<=end_urban_lunit) * (land1d_wtgcell>0))[0]

		    # Check for valid veg landunit 
		    if landunit_indx_veg.size > 0:
			varo_lut[:,veg,jxy,ixy] = EFLX_LH_TOT[:,landunit_indx_veg].squeeze()
		    else:
			varo_lut[:,veg,jxy,ixy] = 1.e36

		    # Check for valid crop landunit
		    if landunit_indx_crop.size > 0:
			varo_lut[:,crop,jxy,ixy] = EFLX_LH_TOT[:,landunit_indx_crop].squeeze()
		    else:
			varo_lut[:,crop,jxy,ixy] = 1.e36

		    # Check for valid urban landunit and compute weighted-average
		    if landunit_indx_urban.size > 0:
			dum = EFLX_LH_TOT[:,landunit_indx_urban].squeeze()
			land1d_wtgcell_pts = (land1d_wtgcell[landunit_indx_urban]).astype(np.float32)
			weights = land1d_wtgcell_pts / np.sum(land1d_wtgcell_pts)
			if (np.absolute(1. - np.sum(weights)) > eps):
			    print ("Weights do not sum to 1, exiting")
			    sys.exit(-1)
			varo_lut[:,urban,jxy,ixy] = np.sum(dum * weights)
		    else:
			varo_lut[:,urban,jxy,ixy] = 1.e36

        new_name = 'CLM_landunit_to_CMIP6_Lut({}{}{}{}{}{}{}{}{}{}{}{}{})'.format(EFLX_LH_TOT.name, 
                              ntim.name, nlat.name, nlon.name, grid1d_ixy.name, grid1d_jxy.name, grid1d_lon.name,
                              grid1d_lat.name, land1d_lon.name, land1d_lat.name, land1d_ityplunit.name,
                              land1d_active.name, land1d_wtgcell.name) 
	return PhysArray(varo_lut,  name=new_name)


