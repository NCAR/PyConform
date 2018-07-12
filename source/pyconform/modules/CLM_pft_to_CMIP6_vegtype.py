#! /usr/bin/env python

import numpy as np
from pyconform.physarray import PhysArray
from pyconform.functions import Function


class CLM_pft_to_CMIP6_vegtype_Function(Function):
    key = 'CLM_pft_to_CMIP6_vegtype'
    numargs = 18

    def __init__(self, GPP, vegType, time, lat, lon, grid1d_ixy, grid1d_jxy, grid1d_lon,
                 grid1d_lat, land1d_lon, land1d_lat, land1d_ityplunit,
                 pfts1d_lon, pfts1d_lat, pfts1d_active, pfts1d_itype_veg,
                 pfts1d_wtgcell, pfts1d_wtlunit):

        super(CLM_pft_to_CMIP6_vegtype_Function, self).__init__(GPP, vegType, time, lat, lon, grid1d_ixy, grid1d_jxy, grid1d_lon,
                                                                grid1d_lat, land1d_lon, land1d_lat, land1d_ityplunit,
                                                                pfts1d_lon, pfts1d_lat, pfts1d_active, pfts1d_itype_veg,
                                                                pfts1d_wtgcell, pfts1d_wtlunit)

    def __getitem__(self, index):

        pGPP = self.arguments[0][index]
        # vegType = grass, shrub, or tree
        vegType = self.arguments[1]
        ptime = self.arguments[2][index]
        plat = self.arguments[3][index]
        plon = self.arguments[4][index]
        pgrid1d_ixy = self.arguments[5][index]
        pgrid1d_jxy = self.arguments[6][index]
        pgrid1d_lon = self.arguments[7][index]
        pgrid1d_lat = self.arguments[8][index]
        pland1d_lon = self.arguments[9][index]
        pland1d_lat = self.arguments[10][index]
        pland1d_ityplunit = self.arguments[11][index]
        ppfts1d_lon = self.arguments[12][index]
        ppfts1d_lat = self.arguments[13][index]
        ppfts1d_active = self.arguments[14][index]
        ppfts1d_itype_veg = self.arguments[15][index]
        ppfts1d_wtgcell = self.arguments[16][index]
        ppfts1d_wtlunit = self.arguments[17][index]

        if index is None:
            return PhysArray(np.zeros((0, 0, 0)), dimensions=[ptime.dimensions[0], plat.dimensions[0], plon.dimensions[0]])

        GPP = pGPP.data
        time = ptime.data
        lat = plat.data
        lon = plon.data
        grid1d_ixy = pgrid1d_ixy.data
        grid1d_jxy = pgrid1d_jxy.data
        grid1d_lon = pgrid1d_lon.data
        grid1d_lat = pgrid1d_lat.data
        land1d_lon = pland1d_lon.data
        land1d_lat = pland1d_lat.data
        land1d_ityplunit = pland1d_ityplunit.data
        pfts1d_lon = ppfts1d_lon.data
        pfts1d_lat = ppfts1d_lat.data
        pfts1d_active = ppfts1d_active.data
        pfts1d_itype_veg = ppfts1d_itype_veg.data
        pfts1d_wtgcell = ppfts1d_wtgcell.data
        pfts1d_wtlunit = ppfts1d_wtlunit.data

        # If 1, pft is active
        active_pft = 1

        # If 1, landunit is veg
        veg_lunit = 1

        # Veg-types and valid pfts
        if 'tree' in vegType:
            beg_pfts = 1
            end_pfts = 8
        elif 'shrub' in vegType:
            beg_pfts = 9
            end_pfts = 11
        elif 'grass' in vegType:
            beg_pfts = 12
            end_pfts = 14
        valid_pfts = ((pfts1d_wtgcell > 0.) *
                      (pfts1d_itype_veg >= beg_pfts) *
                      (pfts1d_itype_veg <= end_pfts))

        # Will contain weighted average for grass pfts on 2d grid
        varo_vegType = np.ones([len(time), len(lat), len(lon)]) * 1e20

        vegtyp_lunit_indices = np.where(land1d_ityplunit == veg_lunit)
        active_ptype_indices = np.where(pfts1d_active == active_pft)

        gcell_pts = np.stack((grid1d_lon, grid1d_lat), axis=1)
        lunit_pts = np.stack(
            (land1d_lon[vegtyp_lunit_indices], land1d_lat[vegtyp_lunit_indices]), axis=1)
        pfts_pts = np.stack(
            (pfts1d_lon[active_ptype_indices], pfts1d_lat[active_ptype_indices]), axis=1)

        gcell_indices = np.where(np.all(np.isin(gcell_pts, lunit_pts), axis=1))
        gcell_pts = gcell_pts[gcell_indices]
        gcell_indices = np.where(np.all(np.isin(gcell_pts, pfts_pts), axis=1))

        gcell_lon = grid1d_lon[gcell_indices]
        gcell_lat = grid1d_lat[gcell_indices]
        gcell_ixy = grid1d_ixy[gcell_indices]
        gcell_jxy = grid1d_jxy[gcell_indices]

        for lon, lat, i, j in np.nditer([gcell_lon, gcell_lat, gcell_ixy, gcell_jxy]):
            pft_idx = np.where(
                np.all((lon, lat) == pfts_pts, axis=1) * valid_pfts)[0]
            dum = GPP[:, pft_idx]
            pfts1d_wtlunit_veg = (pfts1d_wtlunit[pft_idx]).astype(np.float32)
            weights = pfts1d_wtlunit_veg / np.sum(pfts1d_wtlunit_veg)
            varo_vegType[:, j - 1, i - 1] = np.sum(dum * weights)

        new_name = 'CLM_pft_to_CMIP6_vegtype({},{})'.format(pGPP.name, vegType)

        varo_vegType[varo_vegType >= 1e+16] = 1e+20
        ma_varo_vegType = np.ma.masked_values(varo_vegType, 1e+20)

        return PhysArray(ma_varo_vegType,  name=new_name, units=pGPP.units)


# def main():
#
#     import netCDF4 as nc
#
#     sim = "clm50_r243_1deg_GSWP3V2_cropopt_nsc_emergeV2F_dailyo_hist"
#     f_in = sim + ".clm2.h1.2005-01.nc"
#     f_out = sim + ".clm2.h1veg.0001-01.nc"
#     f_dir = "/glade2/scratch2/mickelso/CMIP6_LND_SCRIPTS/DATA/"
#     f_outfir = "/glade2/scratch2/mickelso/CMIP6_LND_SCRIPTS/new/OUTDIR/"
#
#     cdf_file = nc.Dataset(f_dir + f_in, "r")
#
#     ntim = cdf_file.variables['time'][:]
#     nlat = cdf_file.variables['lat'][:]
#     nlon = cdf_file.variables['lon'][:]
#
#     grid1d_ixy = cdf_file.variables['grid1d_ixy'][:]
#     grid1d_jxy = cdf_file.variables['grid1d_jxy'][:]
#     grid1d_lon = cdf_file.variables['grid1d_lon'][:]
#     grid1d_lat = cdf_file.variables['grid1d_lat'][:]
#     land1d_lon = cdf_file.variables['land1d_lon'][:]
#     land1d_lat = cdf_file.variables['land1d_lat'][:]
#     land1d_ityplunit = cdf_file.variables['land1d_ityplunit'][:]
#     pfts1d_lon = cdf_file.variables['pfts1d_lon'][:]
#     pfts1d_lat = cdf_file.variables['pfts1d_lat'][:]
#     pfts1d_active = cdf_file.variables['pfts1d_active'][:]
#     pfts1d_itype_veg = cdf_file.variables['pfts1d_itype_veg'][:]
#     pfts1d_wtgcell = cdf_file.variables['pfts1d_wtgcell'][:]
#     pfts1d_wtlunit = cdf_file.variables['pfts1d_wtlunit'][:]
#
#     GPP = cdf_file.variables['GPP'][:]
#
#     cdf_file.close()
#
#     out_file = nc.Dataset(f_outfir + f_out, "w")
#
#     out_file.createDimension('time', None)
#     out_file.createDimension('lat', len(nlat))
#     out_file.createDimension('lon', len(nlon))
#     gppGrass = out_file.createVariable(
#         'gppGrass', 'f4', ('time', 'lat', 'lon'), fill_value=1.e36)
#     gppShrub = out_file.createVariable(
#         'gppShrub', 'f4', ('time', 'lat', 'lon'), fill_value=1.e36)
#     gppTree = out_file.createVariable(
#         'gppTree', 'f4', ('time', 'lat', 'lon'), fill_value=1.e36)
#
#     print 'Looking for grass'
#     gppGrass[:] = CLM_pft_to_CMIP6_vegtype(GPP, 'grass', ntim, nlat, nlon, grid1d_ixy, grid1d_jxy, grid1d_lon,
#                                            grid1d_lat, land1d_lon, land1d_lat, land1d_ityplunit,
#                                            pfts1d_lon, pfts1d_lat, pfts1d_active, pfts1d_itype_veg,
#                                            pfts1d_wtgcell, pfts1d_wtlunit)
#     print 'Looking for shrubs'
#     gppShrub[:] = CLM_pft_to_CMIP6_vegtype(GPP, 'shrub', ntim, nlat, nlon, grid1d_ixy, grid1d_jxy, grid1d_lon,
#                                            grid1d_lat, land1d_lon, land1d_lat, land1d_ityplunit,
#                                            pfts1d_lon, pfts1d_lat, pfts1d_active, pfts1d_itype_veg,
#                                            pfts1d_wtgcell, pfts1d_wtlunit)
#     print 'Looking for trees'
#     gppTree[:] = CLM_pft_to_CMIP6_vegtype(GPP, 'tree', ntim, nlat, nlon, grid1d_ixy, grid1d_jxy, grid1d_lon,
#                                           grid1d_lat, land1d_lon, land1d_lat, land1d_ityplunit,
#                                           pfts1d_lon, pfts1d_lat, pfts1d_active, pfts1d_itype_veg,
#                                           pfts1d_wtgcell, pfts1d_wtlunit)
#
#     out_file.close()
#
#
# if __name__ == '__main__':
#     main()
