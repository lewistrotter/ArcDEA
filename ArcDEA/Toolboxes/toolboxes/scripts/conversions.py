
import arcpy

from typing import Union

from scripts.constants import BASELINE_COLLECTIONS
from scripts.constants import BASELINE_BAND_ASSETS
from scripts.constants import BASELINE_INDEX_ASSETS
from scripts.constants import QUALITY_FLAGS
from scripts.constants import RASTER_EXTENSIONS


def get_bbox_from_featureclass(
        fc: Union[str]  # TODO: need Union[str, arcpy.???]
) -> tuple[float, float, float, float]:
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


def get_epsg_from_featureclass(
        fc: Union[str]  # TODO: need Union[str, arcpy.???]
) -> int:
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


def convert_bbox_to_poly(
        bbox: tuple[float, float, float, float],
        epsg: int
) -> arcpy.Polygon:
    """

    :param bbox:
    :param epsg:
    :return:
    """

    # TODO: metadata

    w, s, e, n = bbox

    vertices = [
        arcpy.Point(w, s),
        arcpy.Point(e, s),
        arcpy.Point(e, n),
        arcpy.Point(w, n),
        arcpy.Point(w, s)
    ]

    arr = arcpy.Array(vertices)

    srs = arcpy.SpatialReference(epsg)
    poly = arcpy.Polygon(arr, srs)

    return poly


def convert_coords_to_poly(
        coords: list[float],
        epsg: int
) -> arcpy.Polygon:

    vertices = [arcpy.Point(c[0], c[1]) for c in coords]
    arr = arcpy.Array(vertices)

    srs = arcpy.SpatialReference(epsg)
    poly = arcpy.Polygon(arr, srs)

    return poly


def multivalue_param_string_to_list(
        value: str
) -> list[str]:
    """
    Takes an output from an ESRI multivalue parameter type and converts it into a list
    of strings. ESRI multivalue controls always produce an output as
    "'Value 1';'Value 2';'Value n'", so the value must be unpacked.

    :param value: Single string resulting from an ESRI multivalue control.
    :return: An unpacked list of strings from ESRI multivalue control.
    """

    values = value.split(';')
    values = [s.replace("'", '') for s in values]

    return values


def get_collection_names_from_aliases(
        aliases: list[str]
) -> list[str]:
    """
    Takes a list of front-end collection names seen on the ArcGIS Pro front-end (e.g.,
    Landsat 5 TM, Sentinel 2A) and converts it to a list of DEA back-end name (e.g.,
    ga_ls5t_ard_3, ga_s2am_ard_3).

    :param aliases: List of ArcGIS Pro UI collection names.
    :return: List of equivalent DEA back-end collection names.
    """

    name_map = BASELINE_COLLECTIONS
    names = [name_map.get(a) for a in aliases]

    return names


def get_asset_names_from_band_aliases(
        aliases: list[str]
) -> list[str]:
    """
    Takes a list of front-end asset band names seen on the ArcGIS Pro front-end
    (e.g., Red, NIR) and converts it to a list of DEA back-end name (e.g., nbart_red,
    nbart_nir).

    :param aliases: List of ArcGIS Pro UI asset band names.
    :return: List of equivalent DEA back-end asset names.
    """

    name_map = BASELINE_BAND_ASSETS
    names = [name_map.get(a) for a in aliases]

    return names


def get_asset_names_from_index_alias(
        alias: str
) -> list[str]:
    """
    Takes a front-end asset index names seen on the ArcGIS Pro front-end (e.g.,
    NDVI, SAVI) and converts it to a list of DEA back-end band names (e.g.,
    nbart_red, nbart_nir) required to generate index.

    :param alias: String of a ArcGIS Pro UI asset index name.
    :return: List of equivalent DEA back-end asset names.
    """

    name_map = BASELINE_INDEX_ASSETS
    names = name_map.get(alias)

    return names


def get_quality_flag_names_from_aliases(
    aliases: list[str]
) -> list[int]:
    """
    Takes a list of front-end quality mask names seen on the ArcGIS Pro
    front-end (e.g., Valid, Cloud) and converts it to a list of DEA back-end
    name (e.g., 1, 2).

    :param aliases: List of ArcGIS Pro UI quality flag names.
    :return: List of equivalent DEA back-end quality flag names.
    """

    name_map = QUALITY_FLAGS
    names = [name_map.get(a) for a in aliases]

    return names


def get_extension_name_from_alias(
        alias: str
) -> str:
    """
    Takes a string from front-end file extension name seen on the ArcGIS Pro
    front-end (e.g., TIFF, PNG) and converts it to a list of actual back-end
    name (e.g., .tif, .png).

    :param alias: String for supported ArcGIS Pro UI file extension name.
    :return: String for supported Windows back-end file extension name.
    """

    name_map = RASTER_EXTENSIONS
    name = name_map.get(alias)

    return name


