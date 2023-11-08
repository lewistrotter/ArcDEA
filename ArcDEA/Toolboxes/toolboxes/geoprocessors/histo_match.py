
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


# FIXME: this wont work without scipy 1.13 its also incomplete
# FIXME: see rstoolbox histomatch

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
    in_nc = r'C:\Users\Lewis\Desktop\standardised\s2_ndvi.nc'
    out_nc = r'C:\Users\Lewis\Desktop\standardised\s2_ndvi_stand.nc'
    in_r_date = '2022-01-06'
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

    # TODO: checks?

    # TODO: no need to compare band count, always will be with dea
    # ...

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region ...

    #arcpy.SetProgressor('default', '...')

    # get total num pixels in reference xr
    num_pixels = len(ds_r['x']) * len(ds_r['y'])

    # if num samples higher than num pixels, use latter
    num_samples = np.min([num_samples, num_pixels])

    # TODO: no need to do extent intersect, always will be with dea
    # ...

    # TODO: apply r mask
    # ...

    # TODO: apply t mask
    # ...

    # random sample x, y coord pairs
    xs, ys = sample_xr_coords(ds=ds_r, num_samples=num_samples)

    # extract reference xr band values at random  coordinates
    samp_r = extract_xr_values_via_coords(ds=ds_r, xs=xs, ys=ys, remove_nans=True)

    #if paired:
        # extract target band values via same coords
        #samp_t = extract_xr_values_via_coords(ds=ds_t, xs=xs, ys=ys, remove_nans=True)



    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region ...

    #arcpy.SetProgressor('default', '...')

    for dt in ds_t['time']:

        print(dt.to_numpy())

        # extract current slice
        da = ds_t.sel(time=dt)

        if paired:
            # extract target band values via same reference coords
            samp_t = extract_xr_values_via_coords(ds=da, xs=xs, ys=ys, remove_nans=True)
        else:
            raise NotImplemented

        # ensure same coords in both reference and target
        if len(samp_r) != len(samp_t):
            # TODO: subset samp_r to same coords in samp_t
            ...

        for i, band_name in enumerate(raw_bands, start=2):

            # get reference ecdf
            ecdf_r = scipy.stats.ecdf(samp_r[:, i])
            kn = ecdf_r.cdf.quantiles  # TODO: check this is legit - knots?
            y = ecdf_r.cdf.evaluate(kn)

            # get target ecdf
            ecdf_x = scipy.stats.ecdf(samp_t[:, i])

            # get min/max values of reference samples
            # TODO: improve this based on r code
            limits = np.nanmin(samp_r[:, i]), np.nanmax(samp_r[:, i])

            # invert reference ecdf for band value estimation
            inv_ecdf_r = scipy.interpolate.interp1d(x=y,
                                                    y=kn,
                                                    kind='linear',
                                                    fill_value=limits,
                                                    bounds_error=False,
                                                    assume_sorted=True)

            # evaluate raw target band values via inverted reference ecdf
            da_stand = inv_ecdf_r(ecdf_x.cdf.evaluate(da[band_name]))

            # update original band values
            da[band_name].data = da_stand

        # update original xr based on current datetime
        ds_t.loc[dict(time=dt)] = da

    # endregion





    ###

    # TODO: add reference back on to target
    ds = xr.concat([ds_r, ds_t], dim='time').sortby('time')

    #if force_int:
        # force int16 if requested (will round)
        #da_stand = ds_t.astype('int16')


    # reset all prior nan values back to nan
    ds = ds.where(~ds_mask)




    ds = ds.transpose('time', 'y', 'x')

    ds = ds.astype('float32')
    ds.to_netcdf(out_nc)

















#     # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#     # region PREPARE QUERY PARAMETERS
#
#     arcpy.SetProgressor('default', 'Preparing query parameters...')
#
#     fc_bbox = conversions.get_bbox_from_featureclass(in_lyr)
#     fc_epsg = conversions.get_epsg_from_featureclass(in_lyr)
#
#     start_date = in_start_date.date().strftime('%Y-%m-%d')
#     end_date = in_end_date.date().strftime('%Y-%m-%d')
#
#     collections = conversions.multivalue_param_string_to_list(in_collections)
#     collections = conversions.get_collection_names_from_aliases(collections)
#
#     if in_asset_type == 'Bands':
#         assets = conversions.multivalue_param_string_to_list(in_band_assets)
#         assets = conversions.get_asset_names_from_band_aliases(assets)
#     elif in_asset_type == 'Indices':
#         assets = conversions.get_asset_names_from_index_alias(in_index_assets)
#     else:
#         raise NotImplemented
#
#     index_name = None
#     if in_asset_type == 'Indices':
#         index_name = in_index_assets
#
#     quality_flags = conversions.multivalue_param_string_to_list(in_quality_flags)
#     quality_flags = conversions.get_quality_flag_names_from_aliases(quality_flags)
#
#     out_epsg = in_srs.factoryCode
#     out_res = in_res
#     # TODO: if epsg is lat,lon, use 9.466833186042272E-06 * 30
#
#     out_type = in_output_type
#     out_gdb = in_gdb
#     out_nc = in_nc
#     out_folder = in_folder
#
#     if out_type == 'NetCDF':
#         out_extension = '.nc'
#     else:
#         out_extension = conversions.get_extension_name_from_alias(in_file_ext)
#
#     # endregion
#
#     # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#     # region QUERY STAC ENDPOINT
#
#     arcpy.SetProgressor('default', 'Querying STAC endpoint...')
#
#     stac_bbox = conversions.reproject_bbox(fc_bbox, fc_epsg, 4326)  # wgs84 for stac
#     stac_features = web.fetch_all_stac_features(collections,
#                                                 start_date,
#                                                 end_date,
#                                                 stac_bbox,
#                                                 100)
#
#     if len(stac_features) == 0:
#         arcpy.AddWarning('No STAC features were found.')
#         return
#
#     # endregion
#
#     # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#     # region PREPARING STAC FEATURES
#
#     arcpy.SetProgressor('default', 'Preparing downloads...')
#
#     if in_output_type == 'Geodatabase':
#         root_folder = os.path.dirname(out_gdb)
#     elif in_output_type == 'NetCDF':
#         root_folder = os.path.dirname(out_nc)
#     elif in_output_type == 'Folder':
#         root_folder = out_folder
#     else:
#         arcpy.AddError('Did not provide an output type.')
#         return
#
#     data_folder = os.path.join(root_folder, 'data')
#     if os.path.exists(data_folder) is False:
#         os.mkdir(data_folder)
#
#     out_bbox = conversions.reproject_bbox(fc_bbox, fc_epsg, out_epsg)
#     downloads = web.convert_stac_features_to_downloads(stac_features,
#                                                        assets,
#                                                        out_bbox,
#                                                        out_epsg,
#                                                        out_res,
#                                                        data_folder,
#                                                        out_extension)
#
#     downloads = web.group_downloads_by_solar_day(downloads)
#
#     if in_include_slc_off_data is False:
#         downloads = web.remove_slc_off(downloads)
#
#     if len(downloads) == 0:
#         arcpy.AddWarning('No valid downloads were found.')
#         return
#
#     # endregion
#
#     # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#     # region DOWNLOAD WCS DATA
#
#     arcpy.SetProgressor('step', 'Downloading...', 0, len(downloads), 1)
#
#     i = 0
#     results = []
#     with ThreadPoolExecutor(max_workers=num_cpu) as pool:
#         futures = []
#         for download in downloads:
#             task = pool.submit(web.validate_and_download,
#                                download,
#                                index_name,
#                                quality_flags,
#                                in_max_out_of_bounds,
#                                in_max_invalid_pixels,
#                                in_nodata_value)
#
#             futures.append(task)
#
#         for future in as_completed(futures):
#             arcpy.AddMessage(future.result())
#
#             i += 1
#             if i % 1 == 0:
#                 arcpy.SetProgressorPosition(i)
#
#     # endregion
#
#     # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#     # region POST-PROCESSING
#
#     arcpy.SetProgressor('default', 'Performing post-processing...')
#
#     if out_type == 'Geodatabase':
#         web.convert_folder_to_gdb_mosaic(data_folder,
#                                          out_gdb,
#                                          'Landsat Multispectral',  # TODO: make dynamic
#                                          'blue;green;red;nir',  # TODO: make dynamic
#                                          3577)  # TODO: make dynamic
#     elif out_type == 'NetCDF':
#         web.combine_netcdf_files(data_folder,
#                                  out_nc)
#     elif out_type == 'Folder':
#         web.downloads_to_folder(data_folder,
#                                 out_folder)
#
#     # endregion
#
#     # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#     # region CLEAN UP ENVIRONMENT
#
#     arcpy.SetProgressor('default', 'Cleaning up environment...')
#
#     arcpy.env.overwriteOutput = orig_overwrite
#
#     # endregion
#

#execute(None)