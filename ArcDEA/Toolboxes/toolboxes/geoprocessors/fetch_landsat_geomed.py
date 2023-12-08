
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

    from scripts import shared
    from scripts import constants
    from scripts import web

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_lyr = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    in_start_year = parameters[2].value
    in_end_year = parameters[3].value
    in_collections = parameters[4].valueAsText
    in_band_assets = parameters[5].valueAsText
    in_include_slc_off_data = parameters[6].value
    in_nodata_value = parameters[7].value
    in_srs = parameters[8].value
    in_res = parameters[9].value

    # uncomment these when testing
    # in_lyr = r'C:\Users\Lewis\Desktop\arcdea\perth_sa.shp'
    # out_nc = r'C:\Users\Lewis\Desktop\arcdea\ls_gm.nc'
    # in_start_year = 1990
    # in_end_year = 2023
    # in_collections = "'Landsat 5 TM';'Landsat 7 ETM+';'Landsat 8 OLI'"
    # in_band_assets = "'Blue';'Green';'Red';NIR;SWIR 1;SWIR 2;'EMAD';'SMAD';BCMAD"
    # in_include_slc_off_data = False
    # in_nodata_value = -999
    # in_srs = 'GDA94 Australia Albers (EPSG: 3577)'  # 'WGS84 (EPSG: 4326)'
    # in_res = 30

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True
    num_cpu = shared.detect_num_cores(modify_percent=0.90)  # TODO: set this via ui

    collections_map = constants.GEOMED_COLLECTIONS
    assets_map = constants.GEOMED_BAND_ASSETS

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE QUERY PARAMETERS

    arcpy.SetProgressor('default', 'Preparing DEA STAC query parameters...')

    fc_bbox = shared.get_bbox_from_featureclass(in_lyr)
    fc_epsg = shared.get_epsg_from_featureclass(in_lyr)

    start_date = f'{in_start_year}-01-01'
    end_date = f'{in_end_year}-12-31'

    collections = shared.unpack_multivalue_param(in_collections)
    collections = [collections_map[_] for _ in collections]

    assets = shared.unpack_multivalue_param(in_band_assets)
    assets = [assets_map[_] for _ in assets]

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
        # reproject stac bbox to wgs 1984, fetch all available stac items
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
        # create mask info (none for geomed)
        mask = None

        # reproject output bbox to requested, convert stac features to downloads
        out_bbox = shared.reproject_bbox(fc_bbox, fc_epsg, out_epsg)
        downloads = web.convert_stac_features_to_downloads(stac_features,
                                                           assets,
                                                           mask,
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
            for result in pool.map(web.download, downloads):
                arcpy.AddMessage(result)

                i += 1
                if i % 1 == 0:
                    arcpy.SetProgressorPosition(i)

    except Exception as e:
        arcpy.AddError('Error occurred while downloading. See messages.')
        arcpy.AddMessage(str(e))
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CONFIRM BANDS NAMES BEFORE COMBINE

    arcpy.SetProgressor('default', 'Conforming band names...')

    rename_map = {
        'blue':  'nbart_blue',
        'green': 'nbart_green',
        'red':   'nbart_red',
        'nir':   'nbart_nir',
        'swir1': 'nbart_swir_1',
        'swir2': 'nbart_swir_2',
        'edev':  'nbart_edev',
        'sdev':  'nbart_sdev',
        'bcdev': 'nbart_bcdev'
    }

    try:
        web.rename_bands_in_netcdf_files(folder=tmp_folder,
                                         rename_map=rename_map)

    except Exception as e:
        arcpy.AddError('Error occurred while renaming NetCDF files. See messages.')
        arcpy.AddMessage(str(e))
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region COMBINE NETCDFS

    arcpy.SetProgressor('default', 'Combining NetCDF files...')

    try:
        web.combine_ncs_via_dask(folder=tmp_folder,
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

#execute(None)
