
import os
import shutil
import numpy as np
import arcpy

from typing import Union

from scripts import constants


def unpack_multivalue_param(value: str) -> list[str]:
    """
    Takes an output from an ESRI multivalue parameter type and converts it into a list
    of strings. ESRI multivalue controls always produce an output as
    "'Value 1';'Value 2';'Value n'", so the value must be unpacked.
    :param value: Single string resulting from an ESRI multivalue control.
    :return: An unpacked list of strings from ESRI multivalue control.
    """

    values = value.split(';')
    values = [v.replace("'", '') for v in values]

    return values


def prepare_collections(raw_collections: str) -> list:
    """
    Convert ArcGIS Pro collection parameter multi-value string into a list.
    :param raw_collections: Single string of collection names.
    :return: List of collection strings.
    """

    if raw_collections is None or raw_collections == '':
        raise ValueError('No collection provided.')

    collections = unpack_multivalue_param(raw_collections)

    collections_map = constants.BASELINE_COLLECTIONS
    collections = [collections_map[e] for e in collections]

    return collections


def prepare_assets(raw_assets: str) -> list:
    """
    Convert ArcGIS Pro assets parameter multi-value string into a list.
    :param raw_assets: Single string of asset names.
    :return: List of asset strings.
    """

    if raw_assets is None or raw_assets == '':
        raise ValueError('No assets provided.')

    assets = unpack_multivalue_param(raw_assets)

    assets_map = constants.BASELINE_BAND_ASSETS
    assets = [assets_map[e] for e in assets]

    return assets


def prepare_mask_algorithm(raw_mask_algorithm: str) -> str:
    """
    Convert ArcGIS Pro mask algorithm parameter multi-value string into
    a list.
    :param raw_mask_algorithm: Single string of mask algorithm name.
    :return: Mask algorithm string.
    """

    if raw_mask_algorithm is None or raw_mask_algorithm == '':
        raise ValueError('No mask algorithm provided.')

    mask_assets_map = constants.MASK_BAND_ASSETS
    mask_asset = mask_assets_map[raw_mask_algorithm]

    return mask_asset


def prepare_quality_flags(raw_quality_flags: str, raw_mask_algorithm: str) -> list:
    """
    Convert ArcGIS Pro quality flags parameter multi-value string into a list.
    :param raw_mask_algorithm: Single string of mask algorithm name.
    :param raw_quality_flags: Single string of quality flag names.
    :return: List of quality flag strings.
    """

    if raw_quality_flags is None or raw_quality_flags == '':
        raise ValueError('No quality flags provided.')
    elif raw_quality_flags is None or raw_quality_flags == '':
        raise ValueError('No mask algorithm provided.')

    quality_flags = unpack_multivalue_param(raw_quality_flags)

    if raw_mask_algorithm == 'fMask':
        quality_map = constants.QUALITY_FMASK_FLAGS
    elif raw_mask_algorithm == 'S2Cloudless':
        quality_map = constants.QUALITY_S2CLOUDLESS_FLAGS
    else:
        raise NotImplemented('Requested mask not supported.')

    quality_flags = [quality_map[e] for e in quality_flags]

    return quality_flags


def append_mask_band(clean_assets: list, clean_mask_algorithm: str) -> list:
    """
    Appends a mask algorithm band to the end of the assets list.
    :param clean_assets: List of clean band asset names.
    :param clean_mask_algorithm: Clean mask band asset name.
    :return: List of all clean assets with mask band asset added to end.
    """

    if len(clean_assets) == 0:
        raise ValueError('Assets has no values.')
    elif clean_mask_algorithm is None or clean_mask_algorithm == '':
        raise ValueError('Mask algorithm not provided.')

    assets = clean_assets + [clean_mask_algorithm]

    return assets


def prepare_max_out_of_bounds(raw_out_of_bounds: float) -> float:
    """
    Assess and correct (if needed) the out of bounds value.
    :param raw_out_of_bounds: Float value ranging 0.0 to 100.0.
    :return: Float value that has been validated.
    """

    if raw_out_of_bounds is None:
        raise ValueError('No out of bounds value provided.')

    if raw_out_of_bounds < 0.0:
        raw_out_of_bounds = 0.0
    elif raw_out_of_bounds > 100.0:
        raw_out_of_bounds = 100.0

    return raw_out_of_bounds


def prepare_max_invalid_pixels(raw_invalid_pixels: float) -> float:
    """
    Assess and correct (if needed) the invalid pixels value.
    :param raw_invalid_pixels: Float value ranging 0.0 to 100.0.
    :return: Float value that has been validated.
    """

    if raw_invalid_pixels is None:
        raise ValueError('No invalid pixels value provided.')

    if raw_invalid_pixels < 0.0:
        raw_invalid_pixels = 0.0
    elif raw_invalid_pixels > 100.0:
        raw_invalid_pixels = 100.0

    return raw_invalid_pixels


def prepare_spatial_reference(raw_srs: str) -> int:
    """
    Extracts EPSG code as integer from spatial reference string.
    :param raw_srs: Single string of spatial reference name.
    :return: Integer EPSG code value.
    """

    if raw_srs is None or raw_srs == '':
        raise ValueError('No spatial reference provided.')

    srs = int(raw_srs.split(': ')[-1].replace(')', ''))

    return srs


def prepare_resolution(raw_res: float, clean_epsg: int) -> float:

    if raw_res is None:
        raise ValueError('Resolution not provided.')
    elif clean_epsg is None:
        raise ValueError('EPSG code not provided.')

    if clean_epsg == 4326:
        raw_res *= 9.466833186042272E-06

    return raw_res


def prepare_max_threads(max_threads: Union[int, None]) -> int:
    """
    Validates requested number of download threads. If None, will
    find optimal based on current computer.
    :return: Integer maximum number of threads.
    """

    if max_threads is None:
        max_threads = os.cpu_count() - 1
        max_threads = 1 if max_threads < 1 else max_threads

    return max_threads


def get_bbox_from_featureclass(fc: str) -> tuple:
    """
    Takes a featureclass from geoprocessor or string path representing a shapefile and
    extracts bounding box from extent.
    :param fc: ESRI Featureclass type or string path to shapefile.
    :return: Tuple of floats representing bounding box (x min, y min, x max, y max).
    """

    extent = arcpy.Describe(fc).extent

    x_min = float(extent.XMin)
    y_min = float(extent.YMin)
    x_max = float(extent.XMax)
    y_max = float(extent.YMax)

    bbox = x_min, y_min, x_max, y_max

    return bbox


def get_epsg_from_featureclass(fc: str) -> int:
    """
    Takes a featureclass from geoprocessor or string path representing a shapefile and
    extracts the EPSG code.
    :param fc: ESRI Featureclass type or string path to shapefile.
    :return: Integer representing EPSG spatial reference code.
    """

    desc = arcpy.Describe(fc)
    srs = desc.spatialReference
    epsg = int(srs.factoryCode)

    return epsg


def reproject_bbox(
        bbox: tuple[float, float, float, float],
        in_epsg: int,
        out_epsg: int
) -> tuple[float, float, float, float]:
    """
    Takes an existing bbox of doubles in order x_min, y_min, x_max, y_max and associated
    EPSG in which the bbox is projected and re-projects the bbox into new coordinates
    of in the new EPSG.

    :param bbox: Tuple of doubles representing a bbox.
    :param in_epsg: The EPSG code in which the bbox is projected.
    :param out_epsg: The output EPSG in which the bbox will be projected.
    :return: The newly projected bbox.
    """

    x_min, y_min, x_max, y_max = bbox

    vertices = [
        arcpy.Point(x_min, y_min),
        arcpy.Point(x_max, y_min),
        arcpy.Point(x_max, y_max),
        arcpy.Point(x_min, y_max),
        arcpy.Point(x_min, y_min)
    ]

    in_srs = arcpy.SpatialReference(in_epsg)
    arr = arcpy.Array(vertices)
    poly = arcpy.Polygon(arr, in_srs)

    out_srs = arcpy.SpatialReference(out_epsg)
    extent = poly.extent.projectAs(out_srs)
    bbox = extent.XMin, extent.YMin, extent.XMax, extent.YMax

    return bbox


def create_temp_folder(tmp_folder: str) -> None:
    """
    Creates temporary folder, if does not exist.
    :param tmp_folder: Windows folder path.
    :return: Nothing.
    """

    try:
        if not os.path.exists(tmp_folder):
            os.mkdir(tmp_folder)

    except:
        arcpy.AddMessage('Could not create temporary folder.')
        pass


def drop_temp_folder(tmp_folder: str) -> None:
    """
    Removes temporary folder, if exists.
    :param tmp_folder: Windows folder path.
    :return: Nothing.
    """

    try:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)

    except:
        arcpy.AddMessage('Could not delete temporary folder.')
        pass


def detect_num_cores(
        modify_percent: Union[float, None] = None
) -> int:
    """

    :return:
    """

    num_cpus = os.cpu_count()
    if modify_percent is not None:
        num_cpus = int(np.floor(num_cpus * modify_percent))

    if num_cpus == 0:
        num_cpus = 1

    return num_cpus
