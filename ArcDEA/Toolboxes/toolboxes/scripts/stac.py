
import requests
import arcpy

from typing import Union

from scripts import cube


def build_stac_query_url(
        collection: str,
        start_date: str,
        end_date: str,
        bbox: tuple,
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


def query_stac_endpoint(stac_url: str) -> list[dict]:
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

        except Exception as e:
            raise ValueError(e)

    return features


def fetch_all_stac_feats(
        collections: list[str],
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


def convert_stac_feats_to_stac_downloads(
        features: list[dict],
        assets: list[str],
        mask_algorithm: Union[str, None],
        quality_flags: Union[list, None],
        max_out_of_bounds: Union[float, None],
        max_invalid_pixels: Union[float, None],
        out_bbox: tuple[float, float, float, float],
        out_epsg: int,
        out_res: float,
        out_nodata: Union[int, float],
        out_dtype: str,
        out_path: str
) -> list[cube.Download]:
    """
    Iterates through raw DEA STAC query results and converts them into
    sophisticated Download objects.
    :param features: List of raw DEA STAC result dictionaries.
    :param assets: List of strings represented requested assets.
    :param mask_algorithm: Name of mask algorithm. Can be None.
    :param quality_flags: List of mask quality class values.
    :param max_out_of_bounds: Float between 0 and 100 of max out of bounds pixels.
    :param max_invalid_pixels: Float between 0 and 100 of max invalid pixels.
    :param out_bbox: Tuple of floats representing output bbox.
    :param out_epsg: Integer representing output EPSG code.
    :param out_res: Float representing output pixel resolution.
    :param out_nodata: Int or Float representing output nodata value.
    :param out_dtype: String of output datatype.
    :param out_path: String representing output path for data export.
    :return: List of Download objects.
    """

    downloads = []
    for feature in features:
        collection = feature.get('collection')

        if 'properties' in feature:
            datetime = feature.get('properties').get('datetime')

            if 'geometry' in feature:
                coordinates = feature.get('geometry').get('coordinates')[0]

                download = cube.Download(
                    datetime=datetime,
                    collection=collection,
                    assets=assets,
                    coordinates=coordinates,
                    mask_algorithm=mask_algorithm,
                    quality_flags=quality_flags,
                    max_out_of_bounds=max_out_of_bounds,
                    max_invalid_pixels=max_invalid_pixels,
                    out_bbox=out_bbox,
                    out_epsg=out_epsg,
                    out_res=out_res,
                    out_nodata=out_nodata,
                    out_dtype=out_dtype,
                    out_path=out_path)

                downloads.append(download)

    arcpy.AddMessage(f'Found a total of {len(downloads)} STAC features.')

    return downloads


def group_stac_downloads_by_solar_day(
        downloads: list[cube.Download]
) -> list[cube.Download]:
    """
    Takes a list of download objects and groups them into solar day,
    ensuring each DEA STAC download includes contiguous scene pixels
    from a single satellite pass. Download datestimes are converted to
    date, sorted by date, grouped by date and the first date in each
    group is selected.
    :param downloads: List of Download objects.
    :return: List of Download objects grouped by solar day.
    """

    # TODO: can prolly do this using unique id now

    downloads = sorted(downloads, key=lambda d: d.datetime)

    ids = []
    clean_downloads = []
    for download in downloads:
        date = download.get_date()
        unique_id = date + '-' + download.collection

        if unique_id not in ids:
            clean_downloads.append(download)
            ids.append(unique_id)

    num_removed = len(downloads) - len(clean_downloads)
    arcpy.AddMessage(f'Grouped {num_removed} downloads by solar day.')

    return clean_downloads


def remove_stac_downloads_with_slc_off(
        downloads: list[cube.Download]
) -> list[cube.Download]:
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
