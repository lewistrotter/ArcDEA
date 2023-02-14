
import os
import shutil
import requests
import numpy as np
import pandas as pd
import xarray as xr
import arcpy

from typing import Union
from osgeo import gdal

from scripts import indices

# region GDAL SET UP
gdal.SetConfigOption('GDAL_HTTP_UNSAFESSL', 'YES')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS', 'tif')
gdal.SetConfigOption('GDAL_HTTP_MULTIRANGE', 'YES')
gdal.SetConfigOption('GDAL_HTTP_MERGE_CONSECUTIVE_RANGES', 'YES')

# endregion


# region CLASSES
class Download:
    def __init__(
            self,
            date: str,
            collection: str,
            assets: list[str],
            coordinates: list[float],
            out_bbox: tuple[float, float, float, float],
            out_epsg: int,
            out_res: float,
            out_path: str,
            out_extension: str
    ) -> None:
        """
        A custom object representing a single DEA STAC feature. A Download contains
        variables required to create DEA STAC WCS urls and can download data
        using GDAL.
        :param date: String representing a feature date.
        :param collection: String representing feature's DEA collection name.
        :param assets: List of strings of DEA asset names.
        :param coordinates: List of floats representing feature geometry.
        :param out_bbox: List of floats representing output bbox extent.
        :param out_epsg: Integer representing output bbox EPSG code.
        :param out_res: Float representing output pixel resolution.
        :param out_path: String representing export location.
        :param out_extension: String representing output filetype extension.
        """

        self.date = date
        self.collection = collection
        self.assets = assets
        self.coordinates = coordinates
        self.out_bbox = out_bbox
        self.out_epsg = out_epsg
        self.out_res = out_res
        self.out_path = out_path
        self.out_extension = out_extension
        self.__mask_dataset = None
        self.__band_dataset = None

    def __repr__(
            self
    ) -> str:
        return '{}({!r})'.format(self.__class__.__name__, self.__dict__)

    def convert_datetime_to_date(
            self
    ) -> None:
        """
        Convert datetime string in date field to just date.
        :return: Nothing.
        """

        if isinstance(self.date, str):
            date = pd.to_datetime(self.date)
            self.date = date.strftime('%Y-%m-%d')

    def is_slc_off(
            self
    ) -> bool:
        """
        Checks if download contains Landsat-7 data after the known
        slc sensor failure date (2003-05-31).
        :return: Boolean indicating whther download is in slc-off data range.
        """

        if self.date is None or self.collection is None:
            return False

        if 'ls7e' in self.collection and self.date >= '2003-05-31':
            return True

        return False

    def build_mask_wcs_url(
            self
    ) -> str:

        # TODO: meta

        url = build_wcs_url(self.collection,
                            'oa_fmask',
                            self.date,
                            self.out_bbox,
                            self.out_epsg,
                            self.out_res)

        return url

    def build_band_wcs_url(
            self
    ) -> str:
        # TODO: meta

        url = build_wcs_url(self.collection,
                            self.assets,
                            self.date,
                            self.out_bbox,
                            self.out_epsg,
                            self.out_res)

        return url

    def build_output_filepath(
            self
    ) -> str:
        """

        :return:
        """

        out_file = os.path.join(self.out_path, 'R' + self.date + self.out_extension)

        return out_file

    def set_mask_dataset_via_wcs(
            self,
    ) -> None:
        """

        :return:
        """

        try:
            url = self.build_mask_wcs_url()
            self.__mask_dataset = gdal.Open(url, gdal.GA_ReadOnly)  # TODO: ready only for now
        except Exception as e:
            raise e

    def set_band_dataset_via_wcs(
            self,
    ) -> None:
        """

        :return:
        """

        try:
            url = self.build_band_wcs_url()
            self.__band_dataset = gdal.Open(url, gdal.GA_Update)  # TODO: update only for now
        except Exception as e:
            raise e

    def get_percent_out_of_bounds_mask_pixels(
            self
    ) -> Union[float, None]:
        """

        :return:
        """

        if self.__mask_dataset is not None:
            arr = self.__mask_dataset.ReadAsArray()

            invalid_size = np.sum(arr == 0)  # TODO: assuming 0 is always out of bounds...
            total_size = arr.size
            percent_out_of_bounds = invalid_size / total_size * 100

            return percent_out_of_bounds

        return

    def get_percent_invalid_mask_pixels(
            self,
            quality_flags: list[int]
    ) -> Union[float, None]:
        """

        :param quality_flags:
        :return:
        """

        if self.__mask_dataset is not None:
            arr = self.__mask_dataset.ReadAsArray()

            invalid_size = np.sum(~np.isin(arr, quality_flags + [0]))  # TODO: including 0 as valid
            total_size = arr.size
            percent_invalid = invalid_size / total_size * 100

            return percent_invalid

        return

    def set_band_dataset_as_index(
            self,
            index: str
    ) -> None:
        """

        :param index:
        :return:
        """

        transform = self.__band_dataset.GetGeoTransform()
        projection = self.__band_dataset.GetProjection()
        x_size = self.__band_dataset.RasterXSize
        y_size = self.__band_dataset.RasterYSize

        arr = self.__band_dataset.ReadAsArray()
        self.__band_dataset = None

        arr_idx = indices.calc_index_from_array(arr, index)

        driver = gdal.GetDriverByName('MEM')
        self.__band_dataset = driver.Create('',
                                            x_size,
                                            y_size,
                                            1,
                                            gdal.GDT_Float32)

        self.__band_dataset.SetGeoTransform(transform)
        self.__band_dataset.SetProjection(projection)
        self.__band_dataset.WriteArray(arr_idx)

    def set_band_dataset_nodata_via_mask(
            self,
            quality_flags: list[int],
            no_data_value: Union[int, float]
    ) -> None:
        """

        :param quality_flags:
        :param no_data_value:
        :return:
        """

        arr_mask = self.__mask_dataset.ReadAsArray()
        arr_mask = np.isin(arr_mask, quality_flags)  # TODO: not including 0 as valid

        arr_band = self.__band_dataset.ReadAsArray()
        arr_band = np.where(arr_band == -999, no_data_value, arr_band)  # TODO: set DEA nodata (-999) to user no data
        arr_band = np.where(arr_mask, arr_band, no_data_value)

        self.__band_dataset.WriteArray(arr_band)

    def export_band_dataset_to_raster_file(
            self,
            nodata_value: Union[int, float]
    ) -> None:

        options = {'noData': nodata_value}  # TODO: move this to earlier method?

        out_filepath = self.build_output_filepath()
        gdal.Translate(out_filepath,
                       self.__band_dataset,
                       **options)

    def export_band_dataset_to_netcdf_file(
            self,
            nodata_value: Union[int, float]
    ) -> None:

        options = {'noData': nodata_value}  # TODO: move this to earlier method?

        out_filepath = self.build_output_filepath()
        gdal.Translate(out_filepath,
                       self.__band_dataset,
                       **options)

        self.fix_netcdf_metadata()

    def fix_netcdf_metadata(
            self
    ) -> None:

        filepath = self.build_output_filepath()
        ds = xr.open_dataset(filepath)  # TODO: using with has caused issues before, avoiding

        # TODO: newer versions of gdal may break this
        for band in ds:
            if len(ds[band].shape) == 0:
                crs_name = band
                crs_wkt = str(ds[band].attrs.get('spatial_ref'))
                ds = ds.drop_vars(crs_name)
                break

        ds = ds.assign_coords({'spatial_ref': self.out_epsg})
        ds['spatial_ref'].attrs = {
            'spatial_ref': crs_wkt,
            'grid_mapping_name': crs_name
        }

        if 'time' not in ds:
            dt = pd.to_datetime(self.date, format='%Y-%m-%d')
            ds = ds.assign_coords({'time': dt.to_numpy()})
            ds = ds.expand_dims('time')

        for dim in ds.dims:
            if dim in ['x', 'y', 'lat', 'lon']:
                ds[dim].attrs = {
                    #'units': 'metre'  # TODO: how to get units?
                    'resolution': np.mean(np.diff(ds[dim])),
                    'crs': f'EPSG:{self.out_epsg}'
                }

        for i, band in enumerate(ds):
            ds[band].attrs = {
                'units': '1',
                #'nodata': self.nodata,  TODO: implemented out_nodata
                'crs': f'EPSG:{self.out_epsg}',
                'grid_mapping': 'spatial_ref',
            }

            ds = ds.rename({band: self.assets[i]})

        # TODO: we wipe gdal, history, conventions, other metadata
        ds.attrs = {
            'crs': f'EPSG:{self.out_epsg}',
            'grid_mapping': 'spatial_ref'
        }

        ds.to_netcdf(filepath)
        ds.close()

    def close_datasets(
            self
    ) -> None:
        """

        :return:
        """

        self.__mask_dataset = None
        self.__band_dataset = None



    def is_mask_valid(
            self,
            quality_flags: Union[list[int], None],
            max_out_of_bounds: float,
            max_invalid_pixels: float,
    ) -> bool:
        """

        :param quality_flags:
        :param max_out_of_bounds:
        :param max_invalid_pixels:
        :return:
        """

        if self.__mask_dataset is None:
            return False

        pct_out_of_bounds = self.get_percent_out_of_bounds_mask_pixels()
        if pct_out_of_bounds is not None and pct_out_of_bounds > max_out_of_bounds:
            return False

        pct_invalid = self.get_percent_invalid_mask_pixels(quality_flags)
        if pct_invalid is not None and pct_invalid > max_invalid_pixels:
            return False

        return True




# endregion


# region CONSTRUCTORS
def build_stac_query_url(
        collection: str,
        start_date: str,
        end_date: str,
        bbox: tuple[float, float, float, float],
        limit: int,
        full: bool = False
) -> str:
    """
    Takes key query parameters (collection, date range, bbox, limit) required
    by STAC endpoint to perform a query.
    :param collection: String representing a DEA collection name.
    :param start_date: String representing query start date (YYYY-MM-DD).
    :param end_date: String representing query end date (YYYY-MM-DD).
    :param bbox: Tuple of coordinates representing query bbox.
    :param limit: Integer representing max features to return per query.
    :param full: Boolean indicating whether to do a full, deep search of STAC.
    :return: String representing STAC query url.
    """

    url = 'https://explorer.sandbox.dea.ga.gov.au/stac/search?'
    url += f'&collection={collection}'
    url += f'&time={start_date}/{end_date}'
    url += f'&bbox={",".join(map(str, bbox))}'
    url += f'&limit={limit}'
    url += f'&_full={full}'

    return url


def build_wcs_url(
        collection: str,
        assets: Union[str, list[str]],
        date: str,
        bbox: tuple[float, float, float, float],
        epsg: int,
        res: float
) -> str:
    """
    Takes key query parameters (collection, assets, date, bbox, epsg, res)
    and constructs a WCS url to download data from DEA public database.
    :param collection: String representing a DEA collection name.
    :param assets: List of strings representing DEA asset names.
    :param date: String representing query date (YYYY-MM-DD).
    :param bbox: Tuple of coordinates representing bbox of output data.
    :param epsg: Integer representing EPSG code of output data.
    :param res: Float representing pixel resolution of output data.
    :return: String representing WCS url.
    """

    if isinstance(assets, (list, tuple)):
        assets = ','.join(map(str, assets))

    if isinstance(bbox, (list, tuple)):
        bbox = ','.join(map(str, bbox))

    url = 'https://ows.dea.ga.gov.au/wcs?service=WCS'
    url += '&VERSION=1.0.0'
    url += '&REQUEST=GetCoverage'
    url += '&COVERAGE={}'.format(collection)
    url += '&MEASUREMENTS={}'.format(assets)
    url += '&TIME={}'.format(date)
    url += '&BBOX={}'.format(bbox)
    url += '&CRS=EPSG:{}'.format(epsg)
    url += '&RESX={}'.format(res)
    url += '&RESY={}'.format(res)
    url += '&FORMAT=GeoTIFF'

    return url


def query_stac_endpoint(
        stac_url: str
) -> list[dict]:
    """
    Takes a single DEA STAC endpoint query url and returns all available features
    found for the search parameters.
    :param stac_url: String containing a valid DEA STAC endpoint query url.
    :return: List of dictionaries representing returned STAC metadata.
    """

    features = []
    while stac_url:
        try:
            with requests.get(stac_url) as response:
                response.raise_for_status()
                result = response.json()

            if len(result) > 0:
                features += result.get('features')

            stac_url = None
            for link in result.get('links'):
                if link.get('rel') == 'next':
                    stac_url = link.get('href')
                    break

        # TODO: improve specific exception type. implement retry.
        except Exception as e:
            raise ValueError(e)

    return features


def fetch_all_stac_features(
        collections: list[str],  # TODO: could be Union[str, list[str]]
        start_date: str,
        end_date: str,
        bbox: tuple[float, float, float, float],
        limit: int
) -> list[dict]:
    """
    Iterates through provided DEA collections and queries DEA STAC endpoint
    for features existing for each. Once all collections are obtained, all
    results are merged and a list of STAC metadata dictionaries are merged.
    :param collections: List of strings representing DEA STAC collection names.
    :param start_date: String representing query start date (YYYY-MM-DD).
    :param end_date: String representing query end date (YYYY-MM-DD).
    :param bbox: Tuple of coordinates representing query bbox.
    :param limit: Integer representing max features to return per query.
    :return: List of dictionaries representing all returned STAC metadata merged.
    """

    all_features = []
    for collection in collections:
        arcpy.AddMessage(f'Querying STAC endpoint for {collection} data.')

        stac_url = build_stac_query_url(collection,
                                        start_date,
                                        end_date,
                                        bbox,
                                        limit)

        new_features = query_stac_endpoint(stac_url)

        if len(new_features) > 0:
            all_features += new_features

    return all_features


def convert_stac_features_to_downloads(
        features: list[dict],
        assets: list[str],  # TODO: could be Union[str, list[str]]
        out_bbox: tuple[float, float, float, float],
        out_epsg: int,
        out_res: float,
        out_path: str,
        out_extension: str
) -> list[Download]:
    """
    Iterates through raw DEA STAC query results and converts them into
    more sophisticated Download objects.
    :param features: List of raw DEA STAC result dictionaries.
    :param assets: List of strings represented requested assets.
    :param out_bbox: Tuple of floats representing output bbox.
    :param out_epsg: Integer representing output EPSG code.
    :param out_res: Float representing output pixel resolution.
    :param out_path: String representing output path for data export.
    :param out_extension: String representing output file extension.
    :return: List of Download objects.
    """

    # TODO: clean up and error handling needed

    downloads = []
    for feature in features:
        collection = feature.get('collection')

        if 'properties' in feature:
            date = feature.get('properties').get('datetime')

            if 'geometry' in feature:
                coordinates = feature.get('geometry').get('coordinates')[0]

                download = Download(
                    date=date,
                    collection=collection,
                    assets=assets,
                    coordinates=coordinates,
                    out_bbox=out_bbox,
                    out_epsg=out_epsg,
                    out_res=out_res,
                    out_path=out_path,
                    out_extension=out_extension
                )

                downloads.append(download)

    arcpy.AddMessage(f'Found a total of {len(downloads)} STAC features.')

    return downloads


def group_downloads_by_solar_day(
        downloads: list[Download]
) -> list[Download]:
    """
    Takes a list of download objects and groups them into solar day,
    ensuring each DEA STAC download includes contiguous scene pixels
    from a single satellite pass. Download datestimes are converted to
    date, sorted by date, grouped by date and the first date in each
    group is selected.
    :param downloads: List of Download objects.
    :return: List of Download objects grouped by solar day.
    """

    for download in sorted(downloads, key=lambda d: d.date):
        download.convert_datetime_to_date()

    clean_downloads = []
    processed_dates = []
    for download in downloads:
        if download.date not in processed_dates:
            clean_downloads.append(download)
            processed_dates.append(download.date)

    num_removed = len(downloads) - len(clean_downloads)
    arcpy.AddMessage(f'Grouped {num_removed} downloads by solar day.')

    return clean_downloads


# TODO: deprecated
def remove_inadequate_overlaps(
        downloads: list[Download],
        query_bbox: tuple[float, float, float, float],
        query_epsg: int,
        min_percentage_overlap: int
) -> list[Download]:
    """
    Takes a list of download objects and removes any downloads that
    may not have an adequate percentage of overlap with a user query
    bbox extent.
    :param downloads: List of Download objects.
    :param query_bbox: Tuple of floats representing user bbox.
    :param query_epsg: Integer representing user bbox EPSG code.
    :param min_percentage_overlap: The minimum percent of required overlap.
    :return: List of Download objects with adequate percentage overlap.
    """

    clean_downloads = []
    for download in downloads:
        percent_overlap = download.get_percent_overlap_with_bbox(query_bbox,
                                                                 query_epsg)

        if percent_overlap >= min_percentage_overlap:
            clean_downloads.append(download)

    num_removed = len(downloads) - len(clean_downloads)
    arcpy.AddMessage(f'Removed {num_removed} downloads with inadequate overlap.')

    return clean_downloads


def remove_slc_off(
        downloads: list[Download]
) -> list[Download]:
    """
    Takes a list of download objects and removes any downloads
    containing Landsat-7 data after the known slc sensor failure
    date (2003-05-31).
    :param downloads: List of Download objects.
    :return: List of Download objects without slc-off data.
    """

    clean_downloads = []
    for download in downloads:
        is_slc_off = download.is_slc_off()

        if is_slc_off is False:
            clean_downloads.append(download)

    num_removed = len(downloads) - len(clean_downloads)
    arcpy.AddMessage(f'Removed {num_removed} SLC-off downloads.')

    return clean_downloads


def validate_and_download(
        download: Download,
        index: Union[str, None],
        quality_flags: Union[list[int], None],
        max_out_of_bounds: float,
        max_invalid_pixels: float,
        nodata_value: float,
) -> str:
    """
    Takes a single download object, checks if download is valid based on
    number of invalid pixels in mask band, and if valid, downloads the raw
    band data to a specified location and file format captured within the
    download.
    :param download: Download object.
    :param index: String name of index if requested, else None.
    :param quality_flags: List of integers representing valid mask values.
    :param max_out_of_bounds: Float representing max percentage of out of bounds pixels.
    :param max_invalid_pixels: Float representing max percentage of invalid pixels.
    :param nodata_value: Float representing the value used to represent no data pixels.
    :return: String message indicating success or failure of download.
    """

    try:
        download.set_mask_dataset_via_wcs()  # TODO: ls9 doesnt have oa_fmask via WCS service?
        is_valid = download.is_mask_valid(quality_flags,
                                          max_out_of_bounds,
                                          max_invalid_pixels)

        if is_valid is True:
            download.set_band_dataset_via_wcs()

            if index is not None:
                download.set_band_dataset_as_index(index)

            download.set_band_dataset_nodata_via_mask(quality_flags,
                                                      nodata_value)

            # TODO: must be a better way then hiding this logic here..?
            if download.out_extension == '.nc':
                download.export_band_dataset_to_netcdf_file(nodata_value)
            else:
                download.export_band_dataset_to_raster_file(nodata_value)

            message = f'Download {download.date}: successful.'
        else:
            message = f'Download {download.date}: invalid mask.'
    except:
        message = f'Download {download.date}: error.'

    download.close_datasets()

    return message











def check_mask_and_download_band_data(
        download: Download,
        quality_flags: Union[list[int], None],
        max_out_of_bounds: float,
        max_invalid_pixels: float,
        nodata_value: float,
) -> dict:
    """
    Takes a single download object, checks if download is valid based on
    number of invalid pixels in mask band, and if valid, downloads the raw
    band data to a specified location and file format captured within the
    download.
    :param download: Download object.
    :param quality_flags: List of integers representing valid mask values.
    :param max_out_of_bounds: Float representing max percentage of out of bounds pixels.
    :param max_invalid_pixels: Float representing max percentage of invalid pixels.
    :param nodata_value: Float representing the value used to represent no data pixels.
    :return: A dictionary with download object date and success flag.
    """

    receipt = {
        'date': download.date,
        'success': False,
        'message': 'Error.'
    }

    try:

        download.set_mask_dataset_via_wcs()  # TODO: ls9 doesnt have oa_fmask via WCS service?
        is_valid = download.is_mask_valid(quality_flags,
                                          max_out_of_bounds,
                                          max_invalid_pixels)

        if is_valid is True:
            download.set_band_dataset_via_wcs()
            download.set_band_dataset_nodata_via_mask(quality_flags,
                                                      nodata_value)


            # TODO: must be a better way then hiding this logic here..?
            if download.out_extension == '.nc':
                download.export_band_dataset_to_netcdf_file(nodata_value)
            else:
                download.export_band_dataset_to_raster_file(nodata_value)

        download.close_datasets()

        receipt.update({
            'success': True,
            'message': 'Downloaded successfully.'
        })

    except Exception as e:
        return receipt

    return receipt


def check_mask_and_download_index_data(
        download: Download,
        index: str,
        quality_flags: Union[list[int], None],
        max_out_of_bounds: float,
        max_invalid_pixels: float,
        nodata_value: float
) -> dict:
    """
    Takes a single download object, checks if download is valid based on
    number of invalid pixels in mask band, and if valid, downloads the raw
    band data and calculates a specified index. The result is exported to a
    specified location and file format captured within the download.
    :param download: Download object.
    :param index: Name of index.
    :param quality_flags: List of integers representing valid mask values.
    :param max_out_of_bounds: Float representing max percentage of out of bounds pixels.
    :param max_invalid_pixels: Float representing max percentage of invalid pixels.
    :param nodata_value: Float representing the value used to represent no data pixels.
    :return: A dictionary with download object date and success flag.
    """

    receipt = {
        'date': download.date,
        'success': False,
        'message': 'Error.'
    }

    try:
        # TODO: ls9 doesnt have oa_fmask via WCS service for some reason
        download.set_mask_dataset_via_wcs()

        pct_out_of_bounds = download.get_percent_out_of_bounds_mask_pixels()
        if pct_out_of_bounds is not None and pct_out_of_bounds > max_out_of_bounds:
            receipt['message'] = 'Too many pixels out of bounds.'
            return receipt

        pct_invalid = download.get_percent_invalid_mask_pixels(quality_flags)
        if pct_invalid is not None and pct_invalid > max_invalid_pixels:
            receipt['message'] = 'Too many invalid quality pixels.'
            return receipt

        download.set_band_dataset_via_wcs()
        download.set_band_dataset_as_index(index)
        download.set_band_dataset_nodata_via_mask(quality_flags, nodata_value)

        # TODO: must be a better way then hiding this logic here..?
        if download.out_extension == '.nc':
            download.export_band_dataset_to_netcdf_file(nodata_value)
        else:
            download.export_band_dataset_to_raster_file(nodata_value)

        download.close_datasets()

        receipt.update({
            'success': True,
            'message': 'Downloaded successfully.'
        })

    except Exception as e:
        return receipt

    return receipt


def convert_folder_to_gdb_mosaic(
        data_folder: str,
        gdb: str,
        product_name: str,
        assets: Union[str, list],
        epsg: int
) -> None:
    """

    :param data_folder:
    :param gdb:
    :param product_name:
    :param assets:
    :param epsg:
    :return:
    """

    gdb_path = os.path.dirname(gdb)
    gdb_name = os.path.basename(gdb)

    arcpy.management.CreateFileGDB(out_folder_path=gdb_path,
                                   out_name=gdb_name)

    arcpy.management.CreateMosaicDataset(in_workspace=gdb,
                                         in_mosaicdataset_name='ArcDEADataset',
                                         coordinate_system=epsg,
                                         product_definition='CUSTOM',
                                         product_band_definitions=assets)

    gdb_dataset = os.path.join(gdb, 'ArcDEADataset')
    arcpy.management.AddRastersToMosaicDataset(in_mosaic_dataset=gdb_dataset,
                                               raster_type='Raster Dataset',
                                               input_path=data_folder,
                                               build_pyramids='BUILD_PYRAMIDS',
                                               calculate_statistics='CALCULATE_STATISTICS')

    arcpy.management.CalculateField(in_table=gdb_dataset,
                                    field='ProductName',
                                    expression=f"'{product_name}'")

    arcpy.management.AddField(in_table=gdb_dataset,
                              field_name='StdTime',
                              field_type='DATE')

    arcpy.management.CalculateField(in_table=gdb_dataset,
                                    field='StdTime',
                                    expression="datetime.datetime.strptime(!Name!.replace('R', ''), '%Y-%m-%d')")

    arcpy.md.BuildMultidimensionalInfo(in_mosaic_dataset=gdb_dataset,
                                       variable_field='ProductName',
                                       dimension_fields='StdTime',
                                       variable_desc_units=f"'{product_name}'")

    return





def combine_netcdf_files(
        data_folder: str,
        out_nc: str
) -> None:
    """

    :param data_folder:
    :return:
    """

    arcpy.AddMessage('WORKING.')

    files = []
    for file in os.listdir(data_folder):
        if file.endswith('.nc'):
            files.append(os.path.join(data_folder, file))

    if len(files) < 2:
        return

    # TODO: check memory

    ds_list = []
    for file in files:
        ds = xr.open_dataset(file)
        ds_list.append(ds)

    ds = xr.concat(ds_list, dim='time').sortby('time')
    ds.to_netcdf(out_nc)
    ds.close()

    for ds in ds_list:
        ds.close()

    try:
        shutil.rmtree(data_folder)
    except:
        arcpy.AddMessage('Could not delete NetCDFs data folder.')

    return


def downloads_to_folder(
        data_folder: str,
        out_folder: str
) -> None:
    """

    :param data_folder:
    :param out_folder:
    :return:
    """

    for file in os.listdir(data_folder):
        in_file = os.path.join(data_folder, file)
        out_file = os.path.join(out_folder, file)
        shutil.move(in_file, out_file)

    try:
        shutil.rmtree(data_folder)
    except:
        arcpy.AddMessage('Could not delete NetCDFs data folder.')


# endregion

