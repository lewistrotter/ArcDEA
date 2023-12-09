def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import os
    import time
    import datetime
    import arcpy

    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import as_completed

    from scripts import stac
    from scripts import cube
    from scripts import shared

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_lyr = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    in_start_date = parameters[2].value
    in_end_date = parameters[3].value
    in_collections = parameters[4].valueAsText
    in_band_assets = parameters[5].valueAsText
    in_mask_algorithm = parameters[6].value
    in_quality_flags = parameters[7].valueAsText
    in_max_out_of_bounds = parameters[8].value
    in_max_invalid_pixels = parameters[9].value
    in_keep_mask = parameters[10].value
    in_nodata_value = parameters[11].value
    in_srs = parameters[12].value
    in_res = parameters[13].value
    in_max_threads = parameters[14].value

    # uncomment these when testing
    # in_lyr = r'C:\Users\Lewis\Desktop\arcdea\perth_sa.shp'
    # out_nc = r'C:\Users\Lewis\Desktop\arcdea\s2.nc'
    # in_start_date = datetime.datetime(2023, 1, 1)
    # in_end_date = datetime.datetime.now()
    # in_collections = "'Sentinel 2A';'Sentinel 2B'"
    # in_band_assets = "'Blue';'Green';'Red'"
    # in_mask_algorithm = 'S2Cloudless' #'fMask'  # 'S2Cloudless'
    # in_quality_flags = "Valid"  #"'Valid';'Shadow';'Snow';'Water'"  # "Valid"
    # in_max_out_of_bounds = 10
    # in_max_invalid_pixels = 5
    # in_keep_mask = False
    # in_nodata_value = -999
    # in_srs = 'GDA94 Australia Albers (EPSG: 3577)'  # 'WGS84 (EPSG: 4326)'
    # in_res = 10
    # in_max_threads = None

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    # allow output overwrites
    arcpy.env.overwriteOutput = True

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE PARAMETERS

    arcpy.SetProgressor('default', 'Preparing DEA STAC query parameters...')

    # convert featureclass to bbox and epsg
    fc_bbox = shared.get_bbox_from_featureclass(in_lyr)
    fc_epsg = shared.get_epsg_from_featureclass(in_lyr)

    # convert start and end datetime to date strings
    start_date = in_start_date.date().strftime('%Y-%m-%d')
    end_date = in_end_date.date().strftime('%Y-%m-%d')

    # convert collections and assets to lists
    collections = shared.prepare_collections(in_collections)
    assets = shared.prepare_assets(in_band_assets)

    # convert mask algorithm and flags to list, append to assets
    quality_flags = shared.prepare_quality_flags(in_quality_flags, in_mask_algorithm)
    mask_algorithm = shared.prepare_mask_algorithm(in_mask_algorithm)
    assets = shared.append_mask_band(assets, mask_algorithm)

    # convert max out of bounds, invalid pixel values
    max_out_of_bounds = shared.prepare_max_out_of_bounds(in_max_out_of_bounds)
    max_invalid_pixels = shared.prepare_max_invalid_pixels(in_max_invalid_pixels)

    # convert nodata, epsg and resolution to numerics
    out_nodata = in_nodata_value
    out_epsg = shared.prepare_spatial_reference(in_srs)
    out_res = shared.prepare_resolution(in_res, out_epsg)

    # set output dtype (always int16 for baseline)
    out_dtype = 'int16'

    # validate num threads, if none will use num of cores - 1
    max_threads = shared.prepare_max_threads(in_max_threads)

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region QUERY STAC ENDPOINT

    arcpy.SetProgressor('default', 'Querying DEA STAC endpoint...')

    try:
        # reproject stac bbox to wgs 1984, fetch all available stac items
        stac_bbox = shared.reproject_bbox(fc_bbox, fc_epsg, 4326)
        stac_features = stac.fetch_all_stac_feats(collections,
                                                  start_date,
                                                  end_date,
                                                  stac_bbox,
                                                  100)
    except Exception as e:
        arcpy.AddError('Error occurred during DEA STAC query. See messages.')
        arcpy.AddMessage(str(e))
        return

    # abort if no stac features found
    if len(stac_features) == 0:
        arcpy.AddWarning('No STAC features were found.')
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARING STAC FEATURES

    arcpy.SetProgressor('default', 'Preparing STAC downloads...')

    root_folder = os.path.dirname(out_nc)
    tmp_folder = os.path.join(root_folder, 'tmp')

    shared.drop_temp_folder(tmp_folder)
    shared.create_temp_folder(tmp_folder)

    try:
        # reproject output bbox to requested, convert stac to download objects
        out_bbox = shared.reproject_bbox(fc_bbox, fc_epsg, out_epsg)
        stac_downloads = stac.convert_stac_feats_to_stac_downloads(stac_features,
                                                                   assets,
                                                                   mask_algorithm,
                                                                   quality_flags,
                                                                   max_out_of_bounds,
                                                                   max_invalid_pixels,
                                                                   out_bbox,
                                                                   out_epsg,
                                                                   out_res,
                                                                   out_nodata,
                                                                   out_dtype,
                                                                   tmp_folder)

    except Exception as e:
        arcpy.AddError('Error occurred during STAC download preparation. See messages.')
        arcpy.AddMessage(str(e))
        return

    stac_downloads = stac.group_stac_downloads_by_solar_day(stac_downloads)

    if len(stac_downloads) == 0:
        arcpy.AddWarning('No valid downloads were found.')
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region DOWNLOAD WCS MASK DATA

    arcpy.SetProgressor('step', 'Downloading and validating mask data...', 0, len(stac_downloads), 1)

    try:
        i = 0
        with ThreadPoolExecutor(max_workers=max_threads) as pool:
            futures = []
            for stac_download in stac_downloads:
                task = pool.submit(cube.worker_read_mask_and_validate, stac_download)
                futures.append(task)

            for future in as_completed(futures):
                arcpy.AddMessage(future.result())

                i += 1
                if i % 1 == 0:
                    arcpy.SetProgressorPosition(i)

    except Exception as e:
        arcpy.AddError('Error occurred while downloading and validating mask data. See messages.')
        arcpy.AddMessage(str(e))
        return

    stac_downloads = cube.remove_mask_invalid_downloads(stac_downloads)

    if len(stac_downloads) == 0:
        arcpy.AddWarning('No valid downloads were found.')
        return

    time.sleep(1)

    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region DOWNLOAD WCS VALID DATA

    arcpy.SetProgressor('step', 'Downloading valid data...', 0, len(stac_downloads), 1)

    try:
        i = 0
        with ThreadPoolExecutor(max_workers=max_threads) as pool:
            futures = []
            for download in stac_downloads:
                task = pool.submit(cube.worker_read_bands_and_export, download)
                futures.append(task)

            for future in as_completed(futures):
                arcpy.AddMessage(future.result())

                i += 1
                if i % 1 == 0:
                    arcpy.SetProgressorPosition(i)

    except Exception as e:
        arcpy.AddError('Error occurred while downloading valid data. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN AND COMBINE NETCDFS

    arcpy.SetProgressor('default', 'Cleaning and combining NetCDFs...')

    try:
        ds = cube.fix_xr_meta_and_combine(stac_downloads)

    except Exception as e:
        arcpy.AddError('Error occurred while cleaning and combining NetCDFs. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region MASK OUT INVALID NETCDF PIXELS

    arcpy.SetProgressor('default', 'Masking out invalid NetCDF pixels...')

    try:
        ds = cube.apply_xr_mask(ds,
                                quality_flags,
                                out_nodata,
                                in_keep_mask)

    except Exception as e:
        arcpy.AddError('Error occurred while masking out invalid NetCDF pixels. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXPORT COMBINED NETCDF

    arcpy.SetProgressor('default', 'Exporting combined NetCDF...')

    try:
        cube.export_xr_to_nc(ds, out_nc)

    except Exception as e:
        arcpy.AddError('Error occurred while exporting combined NetCDF. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    arcpy.SetProgressor('default', 'Cleaning up environment...')

    cube.safe_close_ncs(tmp_folder)  # TODO: surely there is better way
    shared.drop_temp_folder(tmp_folder)

    time.sleep(1)

    # endregion

#execute(None)
