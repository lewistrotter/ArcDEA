# # this was a Download method
# def get_percent_overlap_with_bbox(
#         self,
#         query_bbox: tuple[float, float, float, float],
#         query_epsg: int,
# ) -> float:
#     """
#     Calculates the percentage in which the download's feature
#     extent intersects with a query bbox area.
#     :param query_bbox: Tuple of floats representing user bbox.
#     :param query_epsg: Integer representing user bbox EPSG code.
#     :return: Float indicating percentage features overlap.
#     """
#
#     query_poly = Conversions.convert_bbox_to_poly(query_bbox, query_epsg)
#     download_poly = Conversions.convert_coords_to_poly(self.coordinates, 4326)
#
#     intersect = query_poly.intersect(download_poly, 4)  # 4 represents polygon
#     percent_intersect = intersect.area / query_poly.area * 100
#
#     return percent_intersect


# this doesn't work well, dea bboxes don't match actual pixel extents well
# instead, count 0s in mask band before invalid are counted
# downloads = Web.remove_inadequate_overlaps(downloads,
# stac_bbox,
# 4326,
# in_min_percentage_overlap)

# old multi platform downloader
# class DownloadBaselineData(object):
#     def __init__(self):
#         self.label = 'Download Baseline Data'
#         self.description = ''
#         self.canRunInBackground = False
#
#     def getParameterInfo(self):
#         params = []
#
#         p00 = arcpy.Parameter(displayName='Input Extent',
#                               name='in_extent',
#                               datatype='GPFeatureLayer',
#                               parameterType='Required',
#                               direction='Input')
#         p00.filter.list = ['Polygon']
#         params.append(p00)
#
#         p01 = arcpy.Parameter(displayName='Dataset',
#                               name='in_dataset',
#                               datatype='GPString',
#                               parameterType='Required',
#                               direction='Input')
#         p01.filter.type = 'ValueList'
#         p01.filter.list = ['Landsat', 'Sentinel']
#         p01.value = 'Landsat'
#         params.append(p01)
#
#         p02 = arcpy.Parameter(displayName='Start Date',
#                               name='in_start_date',
#                               datatype='GPDate',
#                               parameterType='Required',
#                               direction='Input')
#         p02.value = '2013-01-01'
#         params.append(p02)
#
#         p03 = arcpy.Parameter(displayName='End Date',
#                               name='in_end_date',
#                               datatype='GPDate',
#                               parameterType='Required',
#                               direction='Input')
#         p03.value = datetime.date.today().strftime('%Y-%m-%d')
#         params.append(p03)
#
#         p04 = arcpy.Parameter(displayName='Collections',
#                               name='in_collections',
#                               datatype='GPString',
#                               parameterType='Required',
#                               direction='Input',
#                               multiValue=True,
#                               category='Collections and Assets')
#         p04.filter.type = 'ValueList'
#         p04.filter.list = get_param_collection_list('Landsat')
#         p04.value = get_param_collection_list('Landsat')
#         params.append(p04)
#
#         p05 = arcpy.Parameter(displayName='Asset Type',
#                               name='in_asset_type',
#                               datatype='GPString',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Collections and Assets')
#         p05.filter.type = 'ValueList'
#         p05.filter.list = ['Bands', 'Indices', 'Calculator']
#         p05.value = 'Bands'
#         params.append(p05)
#
#         p06 = arcpy.Parameter(displayName='Band Assets',
#                               name='in_band_assets',
#                               datatype='GPString',
#                               parameterType='Required',
#                               direction='Input',
#                               multiValue=True,
#                               category='Collections and Assets')
#         p06.filter.type = 'ValueList'
#         p06.filter.list = get_param_asset_band_list('Landsat')
#         p06.value = get_param_asset_band_list('Landsat')
#         params.append(p06)
#
#         p07 = arcpy.Parameter(displayName='Index Assets',
#                               name='in_index_assets',
#                               datatype='GPString',
#                               parameterType='Required',
#                               direction='Input',
#                               multiValue=False,
#                               category='Collections and Assets')
#         p07.filter.type = 'ValueList'
#         p07.filter.list = get_param_asset_index_list('Landsat')
#         p07.value = 'NDVI'
#         params.append(p07)
#
#         p08 = arcpy.Parameter(displayName='Include SLC-off Data',
#                               name='in_include_slc_off_data',
#                               datatype='GPBoolean',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Collections and Assets')
#         p08.value = False
#         params.append(p08)
#
#         p09 = arcpy.Parameter(displayName='Quality Mask Flags',
#                               name='in_quality_flags',
#                               datatype='GPString',
#                               parameterType='Required',
#                               direction='Input',
#                               multiValue=True,
#                               category='Quality')
#         p09.filter.type = 'ValueList'
#         p09.filter.list = get_param_quality_flags()
#         p09.value = ['Valid', 'Snow', 'Shadow', 'Water']
#         params.append(p09)
#
#         p10 = arcpy.Parameter(displayName='Maximum Percent Out of Bounds',
#                               name='in_max_out_of_bounds',
#                               datatype='GPDouble',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Quality')
#         p10.filter.type = 'Range'
#         p10.filter.list = [0, 100]
#         p10.value = 10
#         params.append(p10)
#
#         p11 = arcpy.Parameter(displayName='Maximum Percent Invalid Pixels',
#                               name='in_max_invalid_pixels',
#                               datatype='GPDouble',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Quality')
#         p11.filter.type = 'Range'
#         p11.filter.list = [0, 100]
#         p11.value = 5
#         params.append(p11)
#
#         p12 = arcpy.Parameter(displayName='NoData Value',
#                               name='in_nodata_value',
#                               datatype='GPDouble',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Quality')
#         p12.value = -999
#         params.append(p12)
#
#         p13 = arcpy.Parameter(displayName='Spatial Reference System',
#                               name='in_srs',
#                               datatype='GPSpatialReference',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Resampling')
#         p13.value = arcpy.SpatialReference(3577)
#         params.append(p13)
#
#         p14 = arcpy.Parameter(displayName='Spatial Resolution',
#                               name='in_res',
#                               datatype='GPDouble',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Resampling')
#         p14.value = 30  # TODO: need to change if sentinel or landsat
#         params.append(p14)
#
#         p15 = arcpy.Parameter(displayName='Output Type',
#                               name='in_output_type',
#                               datatype='GPString',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Output')
#         p15.filter.type = 'ValueList'
#         p15.filter.list = ['Geodatabase', 'NetCDF', 'Folder']
#         p15.value = 'Geodatabase'
#         params.append(p15)
#
#         p16 = arcpy.Parameter(displayName='Output Geodatabase',
#                               name='in_gdb',
#                               datatype='DEFile',
#                               parameterType='Required',
#                               direction='Output',
#                               category='Output')
#         p16.filter.list = ['gdb']
#         p16.value = get_param_default_gdb()
#         params.append(p16)
#
#         p17 = arcpy.Parameter(displayName='Output NetCDF',
#                               name='in_nc',
#                               datatype='DEFile',
#                               parameterType='Required',
#                               direction='Output',
#                               category='Output')
#         p17.filter.list = ['nc']
#         p17.value = get_param_default_nc()
#         params.append(p17)
#
#         p18 = arcpy.Parameter(displayName='Output Folder',
#                               name='in_folder',
#                               datatype='DEFolder',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Output')
#         p18.value = get_param_default_folder()
#         params.append(p18)
#
#         p19 = arcpy.Parameter(displayName='Output Raster Format',
#                               name='in_file_format',
#                               datatype='GPString',
#                               parameterType='Required',
#                               direction='Input',
#                               category='Output')
#         p19.filter.type = 'ValueList'
#         p19.filter.list = get_param_file_extensions()
#         p19.value = 'TIFF'
#         params.append(p19)
#
#         return params
#
#     def isLicensed(self):
#         """Set whether tool is licensed to execute."""
#         return True
#
#     def updateParameters(self, parameters):
#         global CURRENT_DATASET
#
#         # if parameters[0].value != None:
#         # parameters[1].enabled = True
#         # parameters[1].filter.list = get_dataset_list()
#         # else:
#         # parameters[1].enabled = False
#
#         # if parameters[1].value != None:
#         # parameters[2].enabled = True
#         # parameters[3].enabled = True
#
#         # parameters[4].enabled = True
#         # parameters[4].filter.list = get_collection_list(parameters[1].value)
#
#         # parameters[5].enabled = True
#         # parameters[5].value = "Bands"
#
#         # else:
#         # parameters[2].enabled = False
#         # parameters[3].enabled = False
#         # parameters[4].enabled = False
#         # parameters[5].enabled = False
#
#         if parameters[1].value != CURRENT_DATASET:
#             CURRENT_DATASET = parameters[1].value
#
#             parameters[4].filter.list = get_param_collection_list(CURRENT_DATASET)
#             parameters[4].value = get_param_collection_list(CURRENT_DATASET)
#
#             parameters[6].filter.list = get_param_asset_band_list(CURRENT_DATASET)
#             parameters[6].value = get_param_asset_band_list(CURRENT_DATASET)
#
#             parameters[8].enabled = True if CURRENT_DATASET == 'Landsat' else False
#
#             parameters[14].value = 30 if CURRENT_DATASET == 'Landsat' else 10
#
#         if parameters[5].value == 'Bands':
#             parameters[6].enabled = True
#             parameters[7].enabled = False
#         elif parameters[5].value == 'Indices':
#             parameters[6].enabled = False
#             parameters[7].enabled = True
#         elif parameters[5].value == 'Calculator':
#             parameters[6].enabled = False
#             parameters[7].enabled = False
#
#         if parameters[15].valueAsText == 'Geodatabase':
#             parameters[16].enabled = True
#             parameters[17].enabled = False
#             parameters[18].enabled = False
#             parameters[19].enabled = False
#         elif parameters[15].valueAsText == 'NetCDF':
#             parameters[16].enabled = False
#             parameters[17].enabled = True
#             parameters[18].enabled = False
#             parameters[19].enabled = False
#         elif parameters[15].valueAsText == 'Folder':
#             parameters[16].enabled = False
#             parameters[17].enabled = False
#             parameters[18].enabled = True
#             parameters[19].enabled = True
#
#         return
#
#     def updateMessages(self, parameters):
#
#         return
#
#     def execute(self, parameters, messages):
#         from geoprocessors import downloadbaselinedata
#         downloadbaselinedata.execute(parameters)
#
#         return
#
#     def postExecute(self, parameters):
#         """This method takes place after outputs are processed and
#         added to the display."""
#         return

# from download object...
# def check_mask_and_download_band_data(
#         download: Download,
#         quality_flags: Union[list[int], None],
#         max_out_of_bounds: float,
#         max_invalid_pixels: float,
#         nodata_value: float,
# ) -> dict:
#     """
#     Takes a single download object, checks if download is valid based on
#     number of invalid pixels in mask band, and if valid, downloads the raw
#     band data to a specified location and file format captured within the
#     download.
#     :param download: Download object.
#     :param quality_flags: List of integers representing valid mask values.
#     :param max_out_of_bounds: Float representing max percentage of out of bounds pixels.
#     :param max_invalid_pixels: Float representing max percentage of invalid pixels.
#     :param nodata_value: Float representing the value used to represent no data pixels.
#     :return: A dictionary with download object date and success flag.
#     """
#
#     receipt = {
#         'date': download.date,
#         'success': False,
#         'message': 'Error.'
#     }
#
#     try:
#
#         download.set_mask_dataset_via_wcs()  # TODO: ls9 doesnt have oa_fmask via WCS service?
#         is_valid = download.is_mask_valid(quality_flags,
#                                           max_out_of_bounds,
#                                           max_invalid_pixels)
#
#         if is_valid is True:
#             download.set_band_dataset_via_wcs()
#             download.set_band_dataset_nodata_via_mask(quality_flags,
#                                                       nodata_value)
#
#
#             # TODO: must be a better way then hiding this logic here..?
#             if download.out_extension == '.nc':
#                 download.export_band_dataset_to_netcdf_file(nodata_value)
#             else:
#                 download.export_band_dataset_to_raster_file(nodata_value)
#
#         download.close_datasets()
#
#         receipt.update({
#             'success': True,
#             'message': 'Downloaded successfully.'
#         })
#
#     except Exception as e:
#         return receipt
#
#     return receipt


# # TODO: deprecated
# def check_mask_and_download_index_data(
#         download: Download,
#         index: str,
#         quality_flags: Union[list[int], None],
#         max_out_of_bounds: float,
#         max_invalid_pixels: float,
#         nodata_value: float
# ) -> dict:
#     """
#     Takes a single download object, checks if download is valid based on
#     number of invalid pixels in mask band, and if valid, downloads the raw
#     band data and calculates a specified index. The result is exported to a
#     specified location and file format captured within the download.
#     :param download: Download object.
#     :param index: Name of index.
#     :param quality_flags: List of integers representing valid mask values.
#     :param max_out_of_bounds: Float representing max percentage of out of bounds pixels.
#     :param max_invalid_pixels: Float representing max percentage of invalid pixels.
#     :param nodata_value: Float representing the value used to represent no data pixels.
#     :return: A dictionary with download object date and success flag.
#     """
#
#     receipt = {
#         'date': download.date,
#         'success': False,
#         'message': 'Error.'
#     }
#
#     try:
#         # TODO: ls9 doesnt have oa_fmask via WCS service for some reason
#         download.set_mask_dataset_via_wcs()
#
#         pct_out_of_bounds = download.get_percent_out_of_bounds_mask_pixels()
#         if pct_out_of_bounds is not None and pct_out_of_bounds > max_out_of_bounds:
#             receipt['message'] = 'Too many pixels out of bounds.'
#             return receipt
#
#         pct_invalid = download.get_percent_invalid_mask_pixels(quality_flags)
#         if pct_invalid is not None and pct_invalid > max_invalid_pixels:
#             receipt['message'] = 'Too many invalid quality pixels.'
#             return receipt
#
#         download.set_band_dataset_via_wcs()
#         download.set_band_dataset_as_index(index)
#         download.set_band_dataset_nodata_via_mask(quality_flags, nodata_value)
#
#         # TODO: must be a better way then hiding this logic here..?
#         if download.out_extension == '.nc':
#             download.export_band_dataset_to_netcdf_file(nodata_value)
#         else:
#             download.export_band_dataset_to_raster_file(nodata_value)
#
#         download.close_datasets()
#
#         receipt.update({
#             'success': True,
#             'message': 'Downloaded successfully.'
#         })
#
#     except Exception as e:
#         return receipt
#
#     return receipt

# # TODO: deprecated
# def remove_inadequate_overlaps(
#         downloads: list[Download],
#         query_bbox: tuple[float, float, float, float],
#         query_epsg: int,
#         min_percentage_overlap: int
# ) -> list[Download]:
#     """
#     Takes a list of download objects and removes any downloads that
#     may not have an adequate percentage of overlap with a user query
#     bbox extent.
#     :param downloads: List of Download objects.
#     :param query_bbox: Tuple of floats representing user bbox.
#     :param query_epsg: Integer representing user bbox EPSG code.
#     :param min_percentage_overlap: The minimum percent of required overlap.
#     :return: List of Download objects with adequate percentage overlap.
#     """
#
#     clean_downloads = []
#     for download in downloads:
#         percent_overlap = download.get_percent_overlap_with_bbox(query_bbox,
#                                                                  query_epsg)
#
#         if percent_overlap >= min_percentage_overlap:
#             clean_downloads.append(download)
#
#     num_removed = len(downloads) - len(clean_downloads)
#     arcpy.AddMessage(f'Removed {num_removed} downloads with inadequate overlap.')
#
#     return clean_downloads

# def set_band_dataset_as_index(
#         self,
#         index: str
# ) -> None:
#     """
#
#     :param index:
#     :return:
#     """
#
#     transform = self.__band_dataset.GetGeoTransform()
#     projection = self.__band_dataset.GetProjection()
#     x_size = self.__band_dataset.RasterXSize
#     y_size = self.__band_dataset.RasterYSize
#
#     arr = self.__band_dataset.ReadAsArray()
#     self.__band_dataset = None
#
#     arr_idx = indices.calc_index_from_array(arr, index)
#
#     driver = gdal.GetDriverByName('MEM')
#     self.__band_dataset = driver.Create('',
#                                         x_size,
#                                         y_size,
#                                         1,
#                                         gdal.GDT_Float32)
#
#     self.__band_dataset.SetGeoTransform(transform)
#     self.__band_dataset.SetProjection(projection)
#     self.__band_dataset.WriteArray(arr_idx)

# def downloads_to_folder(
#         data_folder: str,
#         out_folder: str
# ) -> None:
#     """
#
#     :param data_folder:
#     :param out_folder:
#     :return:
#     """
#
#     for file in os.listdir(data_folder):
#         in_file = os.path.join(data_folder, file)
#         out_file = os.path.join(out_folder, file)
#         shutil.move(in_file, out_file)
#
#     try:
#         shutil.rmtree(data_folder)
#     except:
#         arcpy.AddMessage('Could not delete NetCDFs data folder.')

# old helpers
# def convert_bbox_to_poly(
#         bbox: tuple[float, float, float, float],
#         epsg: int
# ) -> arcpy.Polygon:
#     """
#
#     :param bbox:
#     :param epsg:
#     :return:
#     """
#
#     # TODO: metadata
#
#     w, s, e, n = bbox
#
#     vertices = [
#         arcpy.Point(w, s),
#         arcpy.Point(e, s),
#         arcpy.Point(e, n),
#         arcpy.Point(w, n),
#         arcpy.Point(w, s)
#     ]
#
#     arr = arcpy.Array(vertices)
#
#     srs = arcpy.SpatialReference(epsg)
#     poly = arcpy.Polygon(arr, srs)
#
#     return poly
#
#
# def convert_coords_to_poly(
#         coords: list[float],
#         epsg: int
# ) -> arcpy.Polygon:
#
#     vertices = [arcpy.Point(c[0], c[1]) for c in coords]
#     arr = arcpy.Array(vertices)
#
#     srs = arcpy.SpatialReference(epsg)
#     poly = arcpy.Polygon(arr, srs)
#
#     return poly