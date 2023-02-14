
import os
import datetime
import uuid
import arcpy

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from scripts import conversions
from scripts import web


# NOTE: ArcGIS Pro toolbox uses execute command to run
# code. Copy and paste below into execute function in
# toolbox when finished testing. Also, ensure parameters
# all work - we cannot access ArcGIS parameters here.
def execute(
        parameters  # TODO: set arcpy type
        # messages  # TODO: use messages input?
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # TODO: uncomment these when not testing
    in_lyr = parameters[0].valueAsText
    in_dataset = parameters[1].value
    in_start_date = parameters[2].value
    in_end_date = parameters[3].value
    in_collections = parameters[4].valueAsText
    in_asset_type = parameters[5].value
    in_band_assets = parameters[6].valueAsText
    in_index_assets = parameters[7].valueAsText
    in_include_slc_off_data = parameters[8].value
    in_quality_flags = parameters[9].valueAsText
    in_max_out_of_bounds = parameters[10].value
    in_max_invalid_pixels = parameters[11].value
    in_nodata_value = parameters[12].value
    in_srs = parameters[13].value
    in_res = parameters[14].value
    in_output_type = parameters[15].value
    in_gdb = parameters[16].valueAsText
    in_nc = parameters[17].valueAsText
    in_folder = parameters[18].valueAsText
    in_file_ext = parameters[19].valueAsText

    # TODO: uncomment these when testing
    # in_lyr = r"C:\Users\Lewis\Desktop\extent test\study area ww.shp"
    # in_dataset = 'Landsat'
    # in_start_date = datetime.datetime(2015, 1, 1)
    # in_end_date = datetime.datetime.now()
    # in_collections = "'Landsat 5 TM';'Landsat 7 ETM+';'Landsat 8 OLI';'Landsat 9 OLI-2'"
    # in_asset_type = 'Bands'  # 'Indices' #
    # in_band_assets = "'Blue';'Green';'Red';'NIR'"
    # in_index_assets = 'NDVI'
    # in_include_slc_off_data = False
    # in_quality_flags = "'Valid';'Shadow';'Snow';'Water'"
    # in_max_out_of_bounds = 10
    # in_max_invalid_pixels = 10
    # in_nodata_value = -999
    # in_srs = arcpy.SpatialReference(3577)
    # in_res = 30
    # in_output_type = 'Folder' #'Folder'  #'NetCDF' # 'Geodatabase'
    # in_gdb = r'C:\Users\Lewis\Desktop\output\ArcDEAData.gdb'
    # in_nc = r'C:\Users\Lewis\Desktop\output\ArcDEAData.nc'
    # in_folder = r'C:\Users\Lewis\Desktop\output'
    # in_file_ext = 'TIFF'

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    orig_overwrite = arcpy.env.overwriteOutput
    arcpy.env.overwriteOutput = True

    num_cpu = 12

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE QUERY PARAMETERS

    arcpy.SetProgressor('default', 'Preparing query parameters...')

    fc_bbox = conversions.get_bbox_from_featureclass(in_lyr)
    fc_epsg = conversions.get_epsg_from_featureclass(in_lyr)

    start_date = in_start_date.date().strftime('%Y-%m-%d')
    end_date = in_end_date.date().strftime('%Y-%m-%d')

    collections = conversions.multivalue_param_string_to_list(in_collections)
    collections = conversions.get_collection_names_from_aliases(collections)

    if in_asset_type == 'Bands':
        assets = conversions.multivalue_param_string_to_list(in_band_assets)
        assets = conversions.get_asset_names_from_band_aliases(assets)
    elif in_asset_type == 'Indices':
        assets = conversions.get_asset_names_from_index_alias(in_index_assets)
    else:
        raise NotImplemented

    index_name = None
    if in_asset_type == 'Indices':
        index_name = in_index_assets

    quality_flags = conversions.multivalue_param_string_to_list(in_quality_flags)
    quality_flags = conversions.get_quality_flag_names_from_aliases(quality_flags)

    out_epsg = in_srs.factoryCode
    out_res = in_res
    # TODO: if epsg is lat,lon, use 9.466833186042272E-06 * 30

    out_type = in_output_type
    out_gdb = in_gdb
    out_nc = in_nc
    out_folder = in_folder

    if out_type == 'NetCDF':
        out_extension = '.nc'
    else:
        out_extension = conversions.get_extension_name_from_alias(in_file_ext)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region QUERY STAC ENDPOINT

    arcpy.SetProgressor('default', 'Querying STAC endpoint...')

    stac_bbox = conversions.reproject_bbox(fc_bbox, fc_epsg, 4326)  # wgs84 for stac
    stac_features = web.fetch_all_stac_features(collections,
                                                start_date,
                                                end_date,
                                                stac_bbox,
                                                100)

    if len(stac_features) == 0:
        arcpy.AddWarning('No STAC features were found.')
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARING STAC FEATURES

    arcpy.SetProgressor('default', 'Preparing downloads...')

    if in_output_type == 'Geodatabase':
        root_folder = os.path.dirname(out_gdb)
    elif in_output_type == 'NetCDF':
        root_folder = os.path.dirname(out_nc)
    elif in_output_type == 'Folder':
        root_folder = out_folder
    else:
        arcpy.AddError('Did not provide an output type.')
        return

    data_folder = os.path.join(root_folder, 'data')
    if os.path.exists(data_folder) is False:
        os.mkdir(data_folder)

    out_bbox = conversions.reproject_bbox(fc_bbox, fc_epsg, out_epsg)
    downloads = web.convert_stac_features_to_downloads(stac_features,
                                                       assets,
                                                       out_bbox,
                                                       out_epsg,
                                                       out_res,
                                                       data_folder,
                                                       out_extension)

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

    i = 0
    results = []
    with ThreadPoolExecutor(max_workers=num_cpu) as pool:
        futures = []
        for download in downloads:
            task = pool.submit(web.validate_and_download,
                               download,
                               index_name,
                               quality_flags,
                               in_max_out_of_bounds,
                               in_max_invalid_pixels,
                               in_nodata_value)

            futures.append(task)

        for future in as_completed(futures):
            arcpy.AddMessage(future.result())

            i += 1
            if i % 1 == 0:
                arcpy.SetProgressorPosition(i)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region POST-PROCESSING

    arcpy.SetProgressor('default', 'Performing post-processing...')

    if out_type == 'Geodatabase':
        web.convert_folder_to_gdb_mosaic(data_folder,
                                         out_gdb,
                                         'Landsat Multispectral',  # TODO: make dynamic
                                         'blue;green;red;nir',  # TODO: make dynamic
                                         3577)  # TODO: make dynamic
    elif out_type == 'NetCDF':
        web.combine_netcdf_files(data_folder,
                                 out_nc)
    elif out_type == 'Folder':
        web.downloads_to_folder(data_folder,
                                out_folder)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    arcpy.SetProgressor('default', 'Cleaning up environment...')

    arcpy.env.overwriteOutput = orig_overwrite

    # endregion


#execute(None)