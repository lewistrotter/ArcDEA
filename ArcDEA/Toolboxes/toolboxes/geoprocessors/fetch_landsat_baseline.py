
def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import os
    import datetime
    import arcpy

    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import as_completed

    from scripts import shared
    from scripts import constants
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
    # in_start_date = datetime.datetime(1990, 1, 1)
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
    num_cpu = shared.detect_num_cores(modify_percent=0.95)  # TODO: set this via ui

    collections_map = constants.BASELINE_COLLECTIONS
    assets_map = constants.BASELINE_BAND_ASSETS
    quality_fmask_map = constants.QUALITY_FMASK_FLAGS

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE QUERY PARAMETERS

    arcpy.SetProgressor('default', 'Preparing DEA STAC query parameters...')

    fc_bbox = shared.get_bbox_from_featureclass(in_lyr)
    fc_epsg = shared.get_epsg_from_featureclass(in_lyr)

    start_date = in_start_date.date().strftime('%Y-%m-%d')
    end_date = in_end_date.date().strftime('%Y-%m-%d')

    collections = shared.unpack_multivalue_param(in_collections)
    collections = [collections_map[_] for _ in collections]

    assets = shared.unpack_multivalue_param(in_band_assets)
    assets = [assets_map[_] for _ in assets]

    quality_flags = shared.unpack_multivalue_param(in_quality_flags)
    quality_flags = [quality_fmask_map[_] for _ in quality_flags]

    out_nodata = in_nodata_value

    out_epsg = int(in_srs.split(': ')[-1].replace(')', ''))

    out_res = in_res
    if out_epsg == 4326:
        out_res *= 9.466833186042272E-06

    out_nc = out_nc
    out_extension = '.nc'

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region QUERY STAC ENDPOINT

    arcpy.SetProgressor('default', 'Querying DEA STAC endpoint...')

    try:
        # project stac bbox to wgs 1984, fetch all available stac items
        stac_bbox = shared.reproject_bbox(fc_bbox, fc_epsg, 4326)
        stac_features = web.fetch_all_stac_features(collections,
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

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARING STAC FEATURES

    arcpy.SetProgressor('default', 'Preparing downloads...')

    root_folder = os.path.dirname(out_nc)
    tmp_folder = os.path.join(root_folder, 'tmp')

    shared.drop_temp_folder(tmp_folder)
    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)

    try:
        # reproject output bbox to requested, convert stac features to downloads
        out_bbox = shared.reproject_bbox(fc_bbox, fc_epsg, out_epsg)
        downloads = web.convert_stac_features_to_downloads(stac_features,
                                                           assets,
                                                           out_bbox,
                                                           out_epsg,
                                                           out_res,
                                                           out_nodata,
                                                           tmp_folder,
                                                           out_extension)
    except Exception as e:
        arcpy.AddError('Error occurred during download creation. See messages.')
        arcpy.AddMessage(str(e))
        return

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

    try:
        i = 0
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

    except Exception as e:
        arcpy.AddError('Error occurred while downloading. See messages.')
        arcpy.AddMessage(str(e))
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region COMBINE NETCDFS

    arcpy.SetProgressor('default', 'Combining NetCDF files...')

    try:
        web.combine_netcdf_files(folder=tmp_folder,
                                 out_nc=out_nc)

    except Exception as e:
        arcpy.AddError('Error occurred while combining NetCDF files. See messages.')
        arcpy.AddMessage(str(e))
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    arcpy.SetProgressor('default', 'Cleaning up environment...')

    shared.drop_temp_folder(tmp_folder)

    # endregion

# execute(None)
