
#import arcpy
#import pandas as pd
import os
import numpy as np
import xarray as xr
import scipy

# from scripts import conversions
# from scripts import web


# TODO: move to scripts folder later
def sample_xr_coords(
        ds: xr.Dataset,
        num_samples: int = 10000
) -> tuple[xr.DataArray, xr.DataArray]:
    """

    :param ds:
    :param num_samples:
    :return:
    """

    # extract xs, ys as numpy arrays
    xs = ds['x'].to_numpy()
    ys = ds['y'].to_numpy()

    # generate 2d grid and unpack to coord pairs
    xs, ys = np.meshgrid(xs, ys)
    xys = np.array([xs, ys]).T.reshape(-1, 2)

    # random sample rows (coord pairs)
    row_idxs = np.random.choice(xys.shape[0], size=num_samples, replace=False)
    xys = xys[row_idxs, :]

    # convert to xr data arrays to combine coords
    xs = xr.DataArray(xys[:, 0], dims='coords')
    ys = xr.DataArray(xys[:, 1], dims='coords')

    return xs, ys

# TODO: move to scripts folder later
def extract_xr_values_via_coords(
        ds: xr.Dataset,
        xs: xr.DataArray,
        ys: xr.DataArray,
        keep_xys: bool = True,
        remove_nans: bool = True
) -> np.ndarray:

    # select all xr pixels per xs, ys pair
    da = ds.sel(x=xs, y=ys, method='nearest')

    # convert to 2d numpy array including coords
    da = da.to_array().transpose('coords', 'variable')
    arr = da.to_numpy()

    # combine xys onto to band values
    xys = np.column_stack([xs.to_numpy(), ys.to_numpy()])
    arr = np.concatenate([xys, arr], axis=1)

    if remove_nans:
        # remove coords where any nans
        arr = arr[~np.isnan(arr).any(axis=1), :]

    return arr


def execute(
        parameters  # TODO: set arcpy type
        # messages  # TODO: use messages input?
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # # TODO: uncomment these when not testing
    # in_lyr = parameters[0].valueAsText
    # in_dataset = parameters[1].value
    # in_start_date = parameters[2].value
    # in_end_date = parameters[3].value
    # in_collections = parameters[4].valueAsText
    # in_asset_type = parameters[5].value
    # in_band_assets = parameters[6].valueAsText
    # in_index_assets = parameters[7].valueAsText
    # in_include_slc_off_data = parameters[8].value
    # in_quality_flags = parameters[9].valueAsText
    # in_max_out_of_bounds = parameters[10].value
    # in_max_invalid_pixels = parameters[11].value
    # in_nodata_value = parameters[12].value
    # in_srs = parameters[13].value
    # in_res = parameters[14].value
    # in_output_type = parameters[15].value
    # in_gdb = parameters[16].valueAsText
    # in_nc = parameters[17].valueAsText
    # in_folder = parameters[18].valueAsText
    # in_file_ext = parameters[19].valueAsText
    #
    # # TODO: uncomment these when testing
    in_nc = r'C:\Users\Lewis\Desktop\standardised\s2.nc'
    out_nc = r'C:\Users\Lewis\Desktop\standardised\s2_pif.nc'
    in_r_date = '2022-01-01'
    in_r_mask = None  # RasterLayer. Mask layer for x to exclude pixels which might distort the histogram, i.e. are not present in ref. Any NA pixel in xmask will be ignored (maskvalue = NA).
    in_t_mask = None  # RasterLayer. Mask layer for ref. Any NA pixel in ref will be ignored (maskvalue = NA).
    num_samples = 100000
    # intersect_only
    paired = True  # If TRUE the corresponding pixels will be used in the overlap.
    # return_funcs
    force_int = True

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # region PREPARE ENVIRONMENT
    #
    # arcpy.SetProgressor('default', 'Preparing environment...')
    #
    # orig_overwrite = arcpy.env.overwriteOutput
    # arcpy.env.overwriteOutput = True
    #
    # num_cpu = 12
    #
    # # endregion


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region LOAD AND CHECK NETCDF

    #arcpy.SetProgressor('default', 'Reading and checking NetCDF data...')

    try:
        # load netcdf  # TODO: memory?
        with xr.open_dataset(in_nc) as ds:
            ds.load()

    except Exception as e:
        #arcpy.AddError('Error occurred when reading NetCDF. Check messages.')
        #arcpy.AddMessage(str(e))
        raise #return

    # check if dimensions correct
    if 'x' not in ds or 'y' not in ds:
        #arcpy.AddError('No x, y dimensions found in NetCDF.')
        raise #return

    # check if netcdf has nodata attribute
    nodata = ds.attrs.get('nodata')
    if nodata is None:
        #arcpy.AddError('No nodata attribute in NetCDF.')
        raise #return

    # check xr has collections attr
    # collections = ds.attrs.get('collections')
    # if collections is None:
    #     #arcpy.AddError('No collections attribute in NetCDF.')
    #     return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    #arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    # extract attributes
    ds_attrs = ds.attrs
    ds_band_attrs = ds[list(ds)[0]].attrs
    ds_spatial_ref_attrs = ds['spatial_ref'].attrs

    # # extract collections, ensure it's a list
    # collections = ds.attrs.get('collections')
    # if not isinstance(collections, list):
    #     collections = [collections]

    # # get collection
    # collection = ';'.join([c for c in collections])
    # if 'ls' in collection:
    #     collection = 'ls'
    # elif 's2' in collection:
    #     collection = 's2'
    # else:
    #     arcpy.AddError('Could not find collection.')
    #     return

    # TODO: indices arent changing the nodata val to nan after calc
    # TODO: causing issues here - fix in tool
    ds = ds.where(~ds.isnull(), -999)

    # obtain nodata mask
    ds_mask = ds == nodata

    # convert nodata to null for full xr
    ds = ds.where(ds != nodata)

    # extract original bands for later removal
    raw_bands = list(ds.data_vars)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region ...

    #arcpy.SetProgressor('default', '...')

    # convert reference time to numpy datetime64
    in_r_date = np.datetime64(in_r_date)

    # check reference date exists
    if in_r_date not in ds['time']:
        #arcpy.AddError('Could not find collection.')
        raise #return

    # TODO: REMOVE
    #ds = ds.resample(time='1YS').mean()

    # extract reference time slice as new xr
    ds_r = ds.sel(time=in_r_date)

    # remove reference time slice from existing xr
    ds_t = ds.drop_sel(time=in_r_date)

    # TODO: temp
    #ds_t = ds_t.isel(time=6)

    # TODO: checks?

    # TODO: no need to compare band count, always will be with dea
    # ...

    # endregion


    # ignore: band count check

    # ignore: extent check

    # calculate pairwise similarity
    method = 'cor'

    # TODO: other methods

    if method == 'cor':

        # calc pixel-wise similarity based on pearson corr
        da_cor = xr.corr(da_a=ds_r.to_array(),
                         da_b=ds_t.to_array(),
                         dim='variable')

        # calc pseudo-ivts via thresholds per target date
        da_pis = da_cor > da_cor.quantile(q=0.95)

        das = []
        for dt in ds_t['time'].to_numpy():

            print(dt)

            # get pis mask for current datetime
            da_msk = da_pis.sel(time=[dt]).squeeze(drop=True)
            arr_m = da_msk.to_numpy()

            # select current target slice
            da_t = ds_t.sel(time=dt)

            for var in ds_r:

                # ...
                arr_r = ds_r[var].where(~ds_r[var].isnull() & arr_m).to_numpy().flatten()
                arr_r = arr_r[~np.isnan(arr_r)]

                # ...
                arr_t = da_t[var].where(~da_t[var].isnull() & arr_m).to_numpy().flatten()
                arr_t = arr_t[~np.isnan(arr_t)]

                # ...
                fit = np.polyfit(x=arr_t, y=arr_r, deg=1)
                prd = np.polyval(fit, arr_t)

                # ...
                abs_err = prd - arr_r
                rsqd = 1.0 - (np.var(abs_err) / np.var(arr_r))

                # ...
                prd = np.polyval(fit, da_t[var])
                da_t[var].data = prd

            # ...
            ds_t.loc[{'time': dt}] = da_t

    ds['ndvi'] = (ds['nbart_nir_1'] - ds['nbart_red']) / (ds['nbart_nir_1'] + ds['nbart_red'])
    ds = ds[['ndvi']]
    ds.transpose('time', 'y', 'x').to_netcdf(r'C:\Users\Lewis\Desktop\standardised\ndvi_raw.nc')

    # add reference back on
    ds_out = xr.concat([ds_r, ds_t], 'time').sortby('time')

    ds_out['ndvi'] = (ds_out['nbart_nir_1'] - ds_out['nbart_red']) / (ds_out['nbart_nir_1'] + ds_out['nbart_red'])
    ds_out = ds_out[['ndvi']]
    ds_out.transpose('time', 'y', 'x').to_netcdf(r'C:\Users\Lewis\Desktop\standardised\ndvi_stn.nc')


    #ds = ds - ds_out

    #ds.transpose('time', 'y', 'x').to_netcdf(r"C:\Users\Lewis\Desktop\standardised\ndvi_diff.nc")

    ds['ndvi_stan'] = ds_out['ndvi']
    ds.transpose('time', 'y', 'x').to_netcdf(r"C:\Users\Lewis\Desktop\standardised\ndvi_both.nc")

    _ = 1




#execute(None)