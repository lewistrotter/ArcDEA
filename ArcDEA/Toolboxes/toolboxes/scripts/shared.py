
import os
import shutil
import numpy as np
import arcpy

from typing import Union


def unpack_multivalue_param(
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


def detect_num_cores(
        modify_percent: Union[float, None] = None
) -> int:
    """

    :return:
    """

    num_cpus = os.cpu_count()
    if modify_percent is not None:
        num_cpus = int(np.floor(num_cpus * modify_percent))

    return num_cpus


def drop_temp_folder(
        tmp_folder: str
) -> None:
    """

    :param tmp_folder:
    :return:
    """

    try:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)
    except:
        print('Could not delete temporary folder.')
        pass


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
