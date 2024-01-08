
import os
import uuid
import numpy as np
import pandas as pd
import xarray as xr
import arcpy

from typing import Union
from osgeo import gdal

gdal.SetConfigOption('GDAL_HTTP_UNSAFESSL', 'YES')
gdal.SetConfigOption('CPL_VSIL_CURL_ALLOWED_EXTENSIONS', '.tif')
gdal.SetConfigOption('GDAL_HTTP_CONNECTTIMEOUT', '30')
gdal.SetConfigOption('GDAL_HTTP_MAX_RETRY', '3')


class Download:
    def __init__(
            self,
            datetime: str,
            collection: str,
            assets: list[str],
            coordinates: list[float],
            mask_algorithm: Union[str, None],
            quality_flags: Union[list, None],
            max_out_of_bounds: Union[int, None],
            max_invalid_pixels: Union[int, None],
            out_bbox: tuple[float, float, float, float],
            out_epsg: int,
            out_res: float,
            out_nodata: Union[int, float],
            out_dtype: str,
            out_path: str
    ) -> None:
        """
        A custom object representing a single DEA STAC feature. A Download contains
        variables required to create DEA STAC WCS urls and can download data
        using GDAL.
        :param datetime: String representing a feature date.
        :param collection: String representing feature's DEA collection name.
        :param assets: List of strings of DEA asset names.
        :param coordinates: List of floats representing feature geometry.
        :param out_bbox: List of floats representing output bbox extent.
        :param out_epsg: Integer representing output bbox EPSG code.
        :param out_res: Float representing output pixel resolution.
        :param out_nodata: Int or Float representing output nodata value.
        :param out_path: String representing export location.
        """

        self._id = None
        self.datetime = datetime
        self._date = None
        self._time = None
        self.collection = collection
        self._collection_code = None
        self.assets = assets
        self.coordinates = coordinates
        self.mask_algorithm = mask_algorithm
        self.quality_flags = quality_flags
        self.max_out_of_bounds = max_out_of_bounds
        self.max_invalid_pixels = max_invalid_pixels
        self.out_bbox = out_bbox
        self.out_epsg = out_epsg
        self.out_res = out_res
        self.out_nodata = out_nodata
        self.out_dtype = out_dtype
        self._gdal_dtype = None
        self.out_path = out_path
        self._is_mask_valid = None
        self._was_downloaded = None

        self.set_uuid()
        self.set_date()
        self.set_time()  # TODO: ensure all data comes back with time
        self.set_collection_code()
        self.set_gdal_dtype()

    # TODO: conform calls to gets or _params

    def __repr__(self) -> str:
        return '{}({!r})'.format(self.__class__.__name__, self.__dict__)

    def set_uuid(self) -> None:
        """
        Generates and sets a random uuid integer for download.
        :return: None.
        """

        self._id = uuid.uuid4().hex[:8]

    def get_uuid(self) -> Union[int, None]:
        """
        Gets uuid.
        :return: UUID as an integer.
        """

        return self._id

    def set_date(self) -> None:
        """
        Extracts and sets date (as string) from datetime.
        :return: None.
        """

        if self.datetime is None:
            self._date = None
        elif not isinstance(self.datetime, str):
            self._date = None
        else:
            datetime = pd.to_datetime(self.datetime)
            self._date = datetime.strftime('%Y-%m-%d')

    def get_date(self) -> Union[str, None]:
        """
        Gets date.
        :return: Date as a string.
        """

        return self._date

    def set_time(self) -> None:
        """
        Extracts and sets time (as string) from datetime.
        :return: None.
        """

        if self.datetime is None:
            self._date = None
        elif not isinstance(self.datetime, str):
            self._date = None
        else:
            datetime = pd.to_datetime(self.datetime)
            self._time = datetime.strftime('%H:%M:%S.%f')

    def get_time(self) -> Union[str, None]:
        """
        Gets time.
        :return: Time as a string.
        """

        return self._time

    def set_collection_code(self) -> None:
        """
        Sets collection code from collection.
        :return: None.
        """

        if 'ls5t' in self.collection:
            self._collection_code = 'ls5'
        elif 'ls7e' in self.collection:
            self._collection_code = 'ls7'
        elif 'ls8c' in self.collection:
            self._collection_code = 'ls8'
        elif 'ls9c' in self.collection:
            self._collection_code = 'ls9'
        elif 's2am' in self.collection:
            self._collection_code = 's2a'
        elif 's2bm' in self.collection:
            self._collection_code = 's2b'
        else:
            self._collection_code = 'ukn'

    def get_collection_code(self) -> Union[str, None]:
        """
        Gets collection code.
        :return: Collection code as a string.
        """

        return self._collection_code

    def set_gdal_dtype(self) -> None:
        """
        Sets the GDAL datatype based on user string.
        :return: None.
        """

        if self.out_dtype == 'int16':
            self._gdal_dtype = gdal.GDT_Int16
        elif self.out_dtype == 'int32':
            self._gdal_dtype = gdal.GDT_Int32
        elif self.out_dtype == 'float32':
            self._gdal_dtype = gdal.GDT_Float32
        elif self.out_dtype == 'float64':
            self._gdal_dtype = gdal.GDT_Float64
        else:
            raise NotImplemented('Datatype not yet implemented.')

    def is_slc_off(self) -> bool:
        """
        Checks if download contains Landsat-7 data after the known
        slc sensor failure date (2003-05-31).
        :return: Boolean indicating whther download is in slc-off data range.
        """

        if self.collection is None or self._date is None:
            return False  # FIXME: this should throw an error, no?

        if 'ls7e' in self.collection and self._date >= '2003-05-31':
            return True

        return False

    def build_mask_wcs_url(self) -> Union[str, None]:
        """
        Constructs a WCS url used to query DEA public database to obtain
        a mask band of user's choice.
        :return: A string of WCS url or None.
        """

        if self.mask_algorithm is None:
            return

        url = build_wcs_url(self.collection,
                            self.mask_algorithm,
                            self._date,
                            self.out_bbox,
                            self.out_epsg,
                            self.out_res)

        return url

    def build_band_wcs_url(self) -> str:
        """
        Constructs a WCS url used to query DEA public database to obtain
        multibands of user's choice.
        :return: A string of WCS url or None.
        """

        url = build_wcs_url(self.collection,
                            self.assets,
                            self._date,
                            self.out_bbox,
                            self.out_epsg,
                            self.out_res)

        return url

    def read_mask_and_validate(self) -> None:
        """
        Downloads and reads a mask band from DEA into
        a numpy array via GDAL. Checks to see if maximum
        number of out of bounds and invalid pixels is valid.
        If so, flags as valid, otherwise not.
        :return: None.
        """

        if self.mask_algorithm is None:
            return

        try:
            url = self.build_mask_wcs_url()
            dataset = gdal.Open(url, gdal.GA_ReadOnly)
            arr_mask = dataset.ReadAsArray()
            dataset = None

        except Exception as e:
            raise e

        try:
            # calc percent out of bounds, assuming 0 is always out of bounds...
            num_out_bounds = np.sum(arr_mask == 0)
            pct_out_bounds = num_out_bounds / arr_mask.size * 100

            # calc percent invalid pixels, inc out of bounds (0) as valid)...
            num_invalid = np.sum(~np.isin(arr_mask, self.quality_flags + [0]))
            pct_invalid = num_invalid / arr_mask.size * 100

            if pct_out_bounds > self.max_out_of_bounds:
                self._is_mask_valid = False
            elif pct_invalid > self.max_invalid_pixels:
                self._is_mask_valid = False
            else:
                self._is_mask_valid = True

        except Exception as e:
            raise e

    def read_bands_and_export(self) -> None:
        """
        Downloads and reads a multibands from DEA into
        a numpy array via GDAL. If download succeeds, data
        is saved to NetCDF file and flagged. Otherwise, not.
        :return: None.
        """

        try:
            url = self.build_band_wcs_url()
            dataset = gdal.Open(url, gdal.GA_ReadOnly)

            out_filepath = self.build_output_filepath()
            options = gdal.TranslateOptions(xRes=self.out_res,
                                            yRes=self.out_res,
                                            outputType=self._gdal_dtype,
                                            noData=self.out_nodata,
                                            format='netCDF')

            gdal.Translate(out_filepath,
                           dataset,
                           options=options)

            dataset = None

            self._was_downloaded = True

        except Exception as e:
            raise e

    def build_output_filepath(self) -> str:
        """
        Constructs the output NetCDF filepath for download.
        :return:
        """

        fn = f'R-{self._date}-{self._collection_code}-{self._id}.nc'
        out_file = os.path.join(self.out_path, fn)

        return out_file

    def is_mask_valid(self) -> Union[bool, None]:
        """
        Gets boolean indicating whether mask was valid or not.
        :return: None.
        """
        return self._is_mask_valid

    def is_download_successful(self) -> Union[bool, None]:
        """
        :return:
        """

        return self._was_downloaded


def worker_read_mask_and_validate(download: Download) -> str:
    """
    Takes a single download object, checks if download is valid based on
    number of invalid pixels in mask band, and if valid, flags a private
    parameter (_is_mask_valid) as True if adequate.
    :param download: Download object.
    :return: Message indicating success or failure of download.
    """

    date = download.get_date()
    code = download.get_collection_code()

    try:
        download.read_mask_and_validate()

        if download.is_mask_valid() is True:
            message = f'Download {code} {date}: number of valid pixels adequate.'
        elif download.is_mask_valid() is False:
            message = f'Download {code} {date}: number of valid pixels inadequate.'
        else:
            message = f'Download {code} {date}: could not be downloaded.'

    except Exception as e:
        message = f'Download {code} {date}: error occurred: {e}.'

    return message


def worker_read_bands_and_export(download: Download) -> str:
    """
    Takes a single download object and downloads the raw band data to a
    specified location as a NetCDF (.nc) file.
    :param download: Download object.
    :return: Message indicating success or failure of download.
    """

    date = download.get_date()
    code = download.get_collection_code()

    try:
        download.read_bands_and_export()

        if download.is_download_successful() is True:
            message = f'Download {code} {date}: successfully downloaded.'
        elif download.is_download_successful() is False:
            message = f'Download {code} {date}: unsuccessfully downloaded.'
        else:
            message = f'Download {code} {date}: could not be downloaded.'

    except Exception as e:
        message = f'Download {code} {date}: error occurred: {e}.'

    return message


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


def remove_mask_invalid_downloads(
        downloads: list[Download]
) -> list[Download]:
    """
    Takes a list of download objects and removes any downloads
    flagged invalid after mask validation.
    :param downloads: List of Download objects.
    :return: List of Download objects not flagged as invalid via mask.
    """

    clean_downloads = []
    for download in downloads:
        if download.is_mask_valid() is True:
            clean_downloads.append(download)

    num_removed = len(downloads) - len(clean_downloads)
    arcpy.AddMessage(f'Removed {num_removed} invalid downloads.')

    return clean_downloads


def fix_xr_meta_and_combine(downloads: list[Download]) -> xr.Dataset:
    """
    For each successful download in list, reads NetCDF in as dask and
    fixes attributes and coordinates, etc. Then, combines all NetCDFs
    into a single Xarray Dataset (still dask).
    :param downloads: List of Download objects.
    :return: Xarray Dataset.
    """

    ds_list = []
    for download in downloads:
        # TODO: might be better to remove unsuccessful outside funcs... think about it
        if download.is_download_successful() is not True:
            continue

        fp = download.build_output_filepath()
        ds = xr.open_dataset(fp,
                             chunks=-1,
                             mask_and_scale=False)  # mask and scale keeps type as int16

        if 'lat' in ds and 'lon' in ds:
            ds = ds.rename({'lat': 'y', 'lon': 'x'})

        crs_name, crs_wkt = None, None
        for band in ds:
            if len(ds[band].shape) == 0:
                crs_name = band
                crs_wkt = str(ds[band].attrs.get('spatial_ref'))
                ds = ds.drop_vars(crs_name)
                break

        if crs_name is None or crs_wkt is None:
            raise ValueError('Could not find expected CRS band.')

        ds = ds.assign_coords({'spatial_ref': download.out_epsg})
        ds['spatial_ref'].attrs = {
            'spatial_ref': crs_wkt,
            'grid_mapping_name': crs_name
        }

        # TODO: decide whether or not to keep this, will be stripped during reducers
        #ds = ds.assign_coords({'collection': download.collection})

        if 'time' not in ds:
            dt = pd.to_datetime(download.get_date(), format='%Y-%m-%d')
            ds = ds.assign_coords({'time': dt.to_numpy()})
            ds = ds.expand_dims('time')

        for dim in ds.dims:
            if dim in ['x', 'y']:
                ds[dim].attrs = {
                    # 'units': 'metre'  # TODO: how to get units?
                    'resolution': np.mean(np.diff(ds[dim])),
                    'crs': f'EPSG:{download.out_epsg}'
                }

        for i, band in enumerate(ds):
            ds[band].attrs = {
                'units': '1',
                'crs': f'EPSG:{download.out_epsg}',
                'grid_mapping': 'spatial_ref'
            }

            real_band = download.assets[i]
            if real_band.startswith('oa_'):
                real_band = 'mask'
            ds = ds.rename({band: real_band})

        # TODO: put into a shared func
        if download.collection.startswith('ga_ls'):
            collection = 'ls'
        elif download.collection.startswith('ga_s2'):
            collection = 's2'
        else:
            raise AttributeError(f'Platform: {download.collection} not supported.')

        # TODO: this may be redundant as concat will just take first dataset index
        # TODO: use a gloval func outside of this func instead
        ds.attrs = {
            'crs': f'EPSG:{download.out_epsg}',
            'grid_mapping': 'spatial_ref',
            'nodata': download.out_nodata,
            'collection': collection,
            'created_by': 'arcdea',
            'processing': 'raw'
        }

        ds_list.append(ds)

    ds = xr.concat(ds_list, dim='time')
    ds = ds.sortby('time')

    return ds


def apply_xr_mask(
        ds: xr.Dataset,
        quality_flags: list[int],
        nodata: Union[int, float],
        keep_mask: bool
) -> xr.Dataset:
    """
    If mask band in Xarray Dataset, will set all pixels to
    nodata value if invalid on mask band.
    :param ds: Xarray Dataset containing band and mask.
    :param quality_flags: List of mask valies considered valid.
    :param nodata: Invalid pixels will be set to this value.
    :param keep_mask: If False, will drop mask band, else keep.
    :return: Xarray Dataset with masked pixels.
    """

    if 'mask' not in ds:
        return ds

    ds = ds.where(ds['mask'].isin(quality_flags), nodata)

    if keep_mask is False:
        ds = ds.drop_vars('mask')

    return ds


def export_xr_to_nc(ds: xr.Dataset, out_nc: str) -> None:
    """
    Takes a Xarray Dataset and exports it to a NetCDF at a given
    location. Also closes the NetCDF.
    :param ds: Xarray Dataset.
    :param out_nc: Output NetCDF file path.
    :return: None.
    """

    try:
        ds.to_netcdf(out_nc)

        ds.close()
        ds = None

    except Exception as e:
        raise e


def safe_close_ncs(tmp_folder: str) -> None:
    """
    Combining NetCDFs with dask seems to keep some NetCDFs open
    in memory. This function quickly loads and closes all NetCDFs
    used to
    :param ds:
    :param tmp_folder:
    :return:
    """

    # TODO: better to solve this another way

    for nc in os.listdir(tmp_folder):
        try:
            nc = os.path.join(tmp_folder, nc)
            ds = xr.open_dataset(nc)
            ds.close()
            ds = None

        except:
            pass

