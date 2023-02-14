# -*- coding: utf-8 -*-
r""""""
__all__ = ['DownloadBaselineData']
__alias__ = 'ArcDEA'
from arcpy.geoprocessing._base import gptooldoc, gp, gp_fixargs
from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject

# Tools
@gptooldoc('DownloadBaselineData_ArcDEA', None)
def DownloadBaselineData(in_extent=None, in_dataset=None, in_start_date=None, in_end_date=None, in_collections=None, in_asset_type=None, in_assets=None, in_include_slc_off_data=None, in_quality_flags=None, in_percent_overlap=None, in_max_invalid_pixels=None, in_srs=None, in_res=None, in_folder=None, in_file_format=None):
    """DownloadBaselineData_ArcDEA(in_extent, in_dataset, in_start_date, in_end_date, in_collections;in_collections..., in_asset_type, in_assets;in_assets..., in_include_slc_off_data, in_quality_flags;in_quality_flags..., in_percent_overlap, in_max_invalid_pixels, in_srs, in_res, in_folder, in_file_format)

     INPUTS:
      in_extent (Feature Layer):
          Input Extent
      in_dataset (String):
          Dataset
      in_start_date (Date):
          Start Date
      in_end_date (Date):
          End Date
      in_collections (String):
          Collections
      in_asset_type (String):
          Asset Type
      in_assets (String):
          Assets
      in_include_slc_off_data (Boolean):
          Include SLC-off Data
      in_quality_flags (String):
          Quality Mask Flags
      in_percent_overlap (Double):
          Percent Overlap
      in_max_invalid_pixels (Double):
          Maximum Percent Invalid Pixels
      in_srs (Spatial Reference):
          Spatial Reference System
      in_res (Double):
          Spatial Resolution
      in_folder (Folder):
          Output Folder
      in_file_format (String):
          Output File Format"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.DownloadBaselineData_ArcDEA(*gp_fixargs((in_extent, in_dataset, in_start_date, in_end_date, in_collections, in_asset_type, in_assets, in_include_slc_off_data, in_quality_flags, in_percent_overlap, in_max_invalid_pixels, in_srs, in_res, in_folder, in_file_format), True)))
        return retval
    except Exception as e:
        raise e


# End of generated toolbox code
del gptooldoc, gp, gp_fixargs, convertArcObjectToPythonObject