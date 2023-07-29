
def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import os
    import shutil
    import datetime
    import arcpy

    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import as_completed

    from scripts import conversions
    from scripts import web

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
    in_include_slc_off_data = parameters[6].value
    in_quality_flags = parameters[7].valueAsText
    in_max_out_of_bounds = parameters[8].value
    in_max_invalid_pixels = parameters[9].value
    in_nodata_value = parameters[10].value
    in_srs = parameters[11].value
    in_res = parameters[12].value

    # uncomment these when testing
    # in_lyr = r'C:\Users\Lewis\Desktop\arcdea\studyarea.shp'
    # out_nc = r'C:\Users\Lewis\Desktop\arcdea\ls.nc'
    # in_start_date = datetime.datetime(2000, 1, 1)
    # in_end_date = datetime.datetime.now()
    # in_collections = "'Landsat 5 TM';'Landsat 7 ETM+';'Landsat 8 OLI';'Landsat 9 OLI-2'"
    # in_band_assets = "'Blue';'Green';'Red';'NIR'"
    # in_include_slc_off_data = False
    # in_quality_flags = "'Valid';'Shadow';'Snow';'Water'"
    # in_max_out_of_bounds = 10
    # in_max_invalid_pixels = 5
    # in_nodata_value = -999
    # in_srs = 'GDA94 Australia Albers (EPSG: 3577)'  # 'WGS84 (EPSG: 4326)'
    # in_res = 30

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True
    num_cpu = 11  # TODO: set this via ui

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE QUERY PARAMETERS

    arcpy.SetProgressor('default', 'Preparing DEA STAC query parameters...')

    fc_bbox = conversions.get_bbox_from_featureclass(in_lyr)
    fc_epsg = conversions.get_epsg_from_featureclass(in_lyr)

    start_date = in_start_date.date().strftime('%Y-%m-%d')
    end_date = in_end_date.date().strftime('%Y-%m-%d')

    collections = conversions.multivalue_param_string_to_list(in_collections)
    collections = conversions.get_collection_names_from_aliases(collections)

    assets = conversions.multivalue_param_string_to_list(in_band_assets)
    assets = conversions.get_asset_names_from_band_aliases(assets)

    quality_flags = conversions.multivalue_param_string_to_list(in_quality_flags)
    quality_flags = conversions.get_quality_flag_names_from_aliases(quality_flags)

    out_nodata = in_nodata_value

    out_epsg = int(in_srs.split(': ')[-1].replace(')', ''))

    out_res = in_res
    if out_epsg == 4326:
        out_res *= 9.466833186042272E-06  # TODO: if epsg is lat,lon, use 9.466833186042272E-06 * 30

    out_nc = out_nc
    out_extension = '.nc'

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region QUERY STAC ENDPOINT

    arcpy.SetProgressor('default', 'Querying DEA STAC endpoint...')

    # project stac bbox to wgs 1984, fetch all available stac items
    stac_bbox = conversions.reproject_bbox(fc_bbox, fc_epsg, 4326)
    stac_features = web.fetch_all_stac_features(collections,
                                                start_date,
                                                end_date,
                                                stac_bbox,
                                                100)

    # abort if no stac features found
    if len(stac_features) == 0:
        arcpy.AddWarning('No STAC features were found.')
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARING STAC FEATURES

    arcpy.SetProgressor('default', 'Preparing downloads...')

    root_folder = os.path.dirname(out_nc)
    tmp_folder = os.path.join(root_folder, 'tmp')

    try:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)
    except:
        arcpy.AddMessage('Could not delete temporary folder.')
        pass

    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)

    # reproject output bbox to requested, convert stac features to downloads
    out_bbox = conversions.reproject_bbox(fc_bbox, fc_epsg, out_epsg)
    downloads = web.convert_stac_features_to_downloads(stac_features,
                                                       assets,
                                                       out_bbox,
                                                       out_epsg,
                                                       out_res,
                                                       out_nodata,
                                                       tmp_folder,
                                                       out_extension)

    downloads = web.group_downloads_by_solar_day(downloads)

    # TODO: dataset maturity

    if in_include_slc_off_data is False:
        downloads = web.remove_slc_off(downloads)

    if len(downloads) == 0:
        arcpy.AddWarning('No valid downloads were found.')
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region DOWNLOAD WCS DATA

    arcpy.SetProgressor('step', 'Downloading...', 0, len(downloads), 1)

    i = 0
    results = []
    with ThreadPoolExecutor(max_workers=num_cpu) as pool:
        futures = []
        for download in downloads:
            task = pool.submit(web.validate_and_download,
                               download,
                               quality_flags,
                               in_max_out_of_bounds,
                               in_max_invalid_pixels)

            futures.append(task)

        for future in as_completed(futures):
            arcpy.AddMessage(future.result())

            i += 1
            if i % 1 == 0:
                arcpy.SetProgressorPosition(i)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region COMBINE NETCDFS

    arcpy.SetProgressor('default', 'Combining NetCDF files...')

    web.combine_netcdf_files(tmp_folder, out_nc)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    arcpy.SetProgressor('default', 'Cleaning up environment...')

    try:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)
    except:
        arcpy.AddMessage('Could not delete temporary folder.')
        pass

    # endregion

#execute(None)