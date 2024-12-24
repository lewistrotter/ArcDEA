# -*- coding: utf-8 -*-
r""""""
from __future__ import annotations
__all__ = ['CalculateIndices', 'ConvertNetCDFToCloudRaster', 'ConvertNetCDFToRasters', 'FetchLandsatBaselineData', 'FetchLandsatGeomedData', 'FetchSentinel2BaselineData', 'GroupData', 'RemoveOutliers', 'ResampleData', 'Testing']
__alias__ = 'ArcDEA'
from arcpy.geoprocessing._base import gptooldoc, gp, gp_fixargs
from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal
    from arcpy import RecordSet, FeatureSet
    from arcpy._mp import Layer, Table
    from arcpy.typing.gp import Result, Result1, Result2, Result3

# Tools
@gptooldoc('CalculateIndices_ArcDEA', None)
def CalculateIndices(in_nc=None, out_nc=None, in_type: Literal['Vegetation', 'Water', 'Fire', 'Urban', 'Minerals'] | None=None, in_index: Literal['NDVI: Normalised Difference Vegetation Index', 'EVI: Enhanced Vegetation Index', 'LAI: Leaf Area Index', 'MAVI: Moisture Adjusted Vegetation Index', 'MSAVI: Mod. Soil Adjusted Vegetation Index', 'NDCI: Normalised Difference Chlorophyll Index', 'kNDVI: Non-linear Difference Vegetation Index'] | None=None,) -> Result1[str]:
    """CalculateIndices_ArcDEA(in_nc, out_nc, in_type, in_index)

     INPUTS:
      in_nc (File):
          Input NetCDF
      in_type (String):
          Index Type
      in_index (String):
          Index

     OUTPUTS:
      out_nc (File):
          Output NetCDF"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.CalculateIndices_ArcDEA(*gp_fixargs((in_nc, out_nc, in_type, in_index), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('ConvertNetCDFToCloudRaster_ArcDEA', None)
def ConvertNetCDFToCloudRaster(in_nc=None, out_crf=None,) -> Result1[str]:
    """ConvertNetCDFToCloudRaster_ArcDEA(in_nc, out_crf)

     INPUTS:
      in_nc (File):
          Input NetCDF

     OUTPUTS:
      out_crf (File):
          Output Cloud Raster"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.ConvertNetCDFToCloudRaster_ArcDEA(*gp_fixargs((in_nc, out_crf), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('ConvertNetCDFToRasters_ArcDEA', None)
def ConvertNetCDFToRasters(in_nc=None, out_nc=None,) -> Result:
    """ConvertNetCDFToRasters_ArcDEA(in_nc, out_nc)

     INPUTS:
      in_nc (File):
          Input NetCDF
      out_nc (Folder):
          Output Folder"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.ConvertNetCDFToRasters_ArcDEA(*gp_fixargs((in_nc, out_nc), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('FetchLandsatBaselineData_ArcDEA', None)
def FetchLandsatBaselineData(in_extent=None, out_nc=None, in_start_date=None, in_end_date=None, in_collections: list[Literal['Landsat 5 TM', 'Landsat 7 ETM+', 'Landsat 8 OLI', 'Landsat 9 OLI-2']] | Literal['Landsat 5 TM', 'Landsat 7 ETM+', 'Landsat 8 OLI', 'Landsat 9 OLI-2'] | str | None=None, in_assets: list[Literal['Blue', 'Green', 'Red', 'NIR', 'SWIR 1', 'SWIR 2']] | Literal['Blue', 'Green', 'Red', 'NIR', 'SWIR 1', 'SWIR 2'] | str | None=None, in_quality_flags: list[Literal['Valid', 'Cloud', 'Shadow', 'Snow', 'Water']] | Literal['Valid', 'Cloud', 'Shadow', 'Snow', 'Water'] | str | None=None, in_remove_slc_off=None, in_remove_mask=None, in_max_empty=None, in_max_invalid=None, in_nodata_value=None, in_srs: Literal['GDA94 Australia Albers (EPSG: 3577)', 'WGS84 Pseudo-Mercator (EPSG: 3857)', 'WGS84 (EPSG: 4326)'] | None=None, in_res=None, in_max_threads=None,) -> Result1[str]:
    """FetchLandsatBaselineData_ArcDEA(in_extent, out_nc, in_start_date, in_end_date, in_collections;in_collections..., in_assets;in_assets..., in_quality_flags;in_quality_flags..., in_remove_slc_off, in_remove_mask, in_max_empty, in_max_invalid, {in_nodata_value}, in_srs, in_res, {in_max_threads})

        Access DEA's Landsat Surface Reflectance Collection 3 Analysis
        Ready Data (ARD) product. This product offers Landsat 5 Thematic
        Mapper (TM), Landsat 7 Enhanced Thematic Mapper Plus (ETM+) and
        Landsat 8 and 9 Operational Land Imager (OLI) imagery captured since
        1986 for the entirety of Australia. This tool provides full access
        to the NBART corrected Landsat Collection 3 offered by DEA. The
        following collections and their associated metadata are outlined
        below:   Landsat 5 TM (ga_ls5t_ard_3) NBART (  link  ). Landsat 7
        ETM+ (ga_ls7e_ard_3) NBART (  link  ). Landsat 8 OLI (ga_ls8c_ard_3)
        NBART (  link  ). Landsat 9 OLI-2 (ga_ls9c_ard_3) NBART (  link  ).
        <SPAN />

     INPUTS:
      in_extent (Extent):
          The extent of the imagery that will be downloaded. A n extent no
          greater than 100 x 100 km is recommended.
      in_start_date (Date):
          The start date of the imagery.
      in_end_date (Date):
          The end date of the imagery.
      in_collections (String):
          Specifies the  name(s) of the DEA collection to consider for
          download. At least one is required.
      in_assets (String):
          Specifies the  name(s) of the DEA assets (i.e., bands) to consider
          for download. At least one is required.
      in_quality_flags (String):
          Specifies the pixel quality mask categories used to define valid
          pixels in each downloaded image. The selected categories  will be
          considered valid and will not be masked out. See  here  for more
          information about the FMask algorithm used by DEA to derive quality
          mask categories.
      in_remove_slc_off (Boolean):
          Specifies whether Landsat 7 ETM+ imagery captured after the SLC
          failure on 31/05/2003 will be excluded from download.
      in_remove_mask (Boolean):
          Specifies whether the  pixel quality mask  band will be removed
          after pixel masking is completed.
      in_max_empty (Long):
          The maximum percentage of empty (or missing) pixels allowed in an
          image. Empty pixels occur when the user-defined extent extends outside
          of an available satellite image path or row. If an image within the
          download extent has a higher percentage of empty pixels than defined
          here, it will be excluded from download.
      in_max_invalid (Long):
          The maximum percentage of all invalid pixels categorised by the
          pixel quality mask allowed in an image. The pixel quality categories
          not selected in the Quality Mask Flags parameter are only considered
          invalid. If an image within the download extent has a higher
          percentage of invalid pixels than defined here, it will be excluded
          from download.
      in_nodata_value {Long}:
          The value to set empty and invalid pixels to when applying the
          pixel quality mask.
      in_srs (String):
          Specifies the output spatial reference system used to project
          downloaded imagery.
      in_res (Double):
          Specifies the output spatial resolution used to resample the
          downloaded imagery.
      in_max_threads {Long}:
          The maximum number of threads allowed when downloading data.
          Leaving this parameter blank will set the optimal number of threads
          automatically.

     OUTPUTS:
      out_nc (File):
          The NetCDF (i.e., data cube) containing the downloaded imagery."""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.FetchLandsatBaselineData_ArcDEA(*gp_fixargs((in_extent, out_nc, in_start_date, in_end_date, in_collections, in_assets, in_quality_flags, in_remove_slc_off, in_remove_mask, in_max_empty, in_max_invalid, in_nodata_value, in_srs, in_res, in_max_threads), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('FetchLandsatGeomedData_ArcDEA', None)
def FetchLandsatGeomedData(in_extent=None, out_nc=None, in_start_year=None, in_end_year=None, in_collections: list[Literal['Landsat 5 TM', 'Landsat 7 ETM+', 'Landsat 8 & 9 OLI']] | Literal['Landsat 5 TM', 'Landsat 7 ETM+', 'Landsat 8 & 9 OLI'] | str | None=None, in_assets: list[Literal['Blue', 'Green', 'Red', 'NIR', 'SWIR 1', 'SWIR 2', 'EMAD', 'SMAD', 'BCMAD', 'Count']] | Literal['Blue', 'Green', 'Red', 'NIR', 'SWIR 1', 'SWIR 2', 'EMAD', 'SMAD', 'BCMAD', 'Count'] | str | None=None, in_remove_slc_off=None, in_srs: Literal['GDA94 Australia Albers (EPSG: 3577)', 'WGS84 Pseudo-Mercator (EPSG: 3857)', 'WGS84 (EPSG: 4326)'] | None=None, in_res=None, in_max_threads=None,) -> Result1[str]:
    """FetchLandsatGeomedData_ArcDEA(in_extent, out_nc, in_start_year, in_end_year, in_collections;in_collections..., in_assets;in_assets..., in_remove_slc_off, in_srs, in_res, {in_max_threads})

        Access DEA's Landsat Surface Reflectance  Geometric Median and
        Median Absolute Deviation (GeoMAD) Collection  3  Analysis Ready Data
        (ARD) product. This product  uses Geometric Median and Median
        Absolute Deviation statistical techniques to provide information on
        variance in imagery in a given year. They provide insight into the
        "average" annual surface reflectance and variation within a given
        extent and are useful for providing spectrally-robust annual snapshots
        without downloading the full DEA dataset. The Landsat GeoMAD
        Collection 3  offers annual NBART-corrected images for  Landsat 5
        Thematic Mapper (TM), Landsat 7 Enhanced Thematic Mapper Plus (ETM+)
        and Landsat 8 and 9 Operational Land Imager (OLI) imagery captured
        since 1986 for the entirety of Australia. The following collections
        and their associated metadata are outlined below:   Landsat 5 TM
        (ga_ls5t_gm_cyear_3) NBART (  link  ). Landsat 7 ETM+ (ga_ls 7e
        _gm_cyear_3) NBART (  link  ). Landsat 8 OLI
        (ga_ls8cls9c_gm_cyear_3) NBART (  link  ). <SPAN />

     INPUTS:
      in_extent (Extent):
          The extent of the imagery that will be downloaded. A n extent no
          greater than 100 x 100 km is recommended.
      in_start_year (Long):
          The start  year  of the imagery.
      in_end_year (Long):
          The end  year  of the imagery.
      in_collections (String):
          Specifies the  name(s) of the DEA collection to consider for
          download. At least one is required.
      in_assets (String):
          Specifies the  name(s) of the DEA assets (i.e., bands) to consider
          for download. At least one is required.
      in_remove_slc_off (Boolean):
          Specifies whether Landsat 7 ETM+ imagery captured after the SLC
          failure on 31/05/2003 will be excluded from download.
      in_srs (String):
          Specifies the output spatial reference system used to project
          downloaded imagery.
      in_res (Double):
          Specifies the output spatial resolution used to resample the
          downloaded imagery.
      in_max_threads {Long}:
          The maximum number of threads allowed when downloading data.
          Leaving this parameter blank will set the optimal number of threads
          automatically.

     OUTPUTS:
      out_nc (File):
          The NetCDF (i.e., data cube) containing the downloaded imagery."""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.FetchLandsatGeomedData_ArcDEA(*gp_fixargs((in_extent, out_nc, in_start_year, in_end_year, in_collections, in_assets, in_remove_slc_off, in_srs, in_res, in_max_threads), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('FetchSentinel2BaselineData_ArcDEA', None)
def FetchSentinel2BaselineData(in_extent=None, out_nc=None, in_start_date=None, in_end_date=None, in_collections: list[Literal['Sentinel 2A', 'Sentinel 2B']] | Literal['Sentinel 2A', 'Sentinel 2B'] | str | None=None, in_assets: list[Literal['Blue', 'Green', 'Red', 'Red Edge 1', 'Red Edge 2', 'Red Edge 3', 'NIR 1', 'NIR 2', 'SWIR 2', 'SWIR 3']] | Literal['Blue', 'Green', 'Red', 'Red Edge 1', 'Red Edge 2', 'Red Edge 3', 'NIR 1', 'NIR 2', 'SWIR 2', 'SWIR 3'] | str | None=None, in_mask_algorithm: Literal['fMask', 'S2Cloudless'] | None=None, in_quality_flags: list[Literal['Valid', 'Cloud', 'Shadow', 'Snow', 'Water']] | Literal['Valid', 'Cloud', 'Shadow', 'Snow', 'Water'] | str | None=None, in_remove_mask=None, in_max_empty=None, in_max_invalid=None, in_nodata_value=None, in_srs: Literal['GDA94 Australia Albers (EPSG: 3577)', 'WGS84 Pseudo-Mercator (EPSG: 3857)', 'WGS84 (EPSG: 4326)'] | None=None, in_res=None, in_max_threads=None,) -> Result1[str]:
    """FetchSentinel2BaselineData_ArcDEA(in_extent, out_nc, in_start_date, in_end_date, in_collections;in_collections..., in_assets;in_assets..., in_mask_algorithm, in_quality_flags;in_quality_flags..., in_remove_mask, in_max_empty, in_max_invalid, {in_nodata_value}, in_srs, in_res, {in_max_threads})

        Access DEA's  Sentinel-2  Surface Reflectance Collection 3 Analysis
        Ready Data (ARD) product. This product offers  Sentinel-2A and
        Sentinel-2B  imagery captured since  2015  for the entirety of
        Australia. This tool provides full access to the NBART corrected
        Sentinel-2  Collection 3 offered by DEA. The following collections and
        their associated metadata are outlined below:   Sentinel-2A
        (ga_s2am_ard_3) NBART (  link  ). Sentinel-2B  (ga_s2 b m_ard_3)
        NBART (  link  ). <SPAN />

     INPUTS:
      in_extent (Extent):
          The extent of the imagery that will be downloaded. A n extent no
          greater than 100 x 100 km is recommended.
      in_start_date (Date):
          The start date of the imagery.
      in_end_date (Date):
          The end date of the imagery.
      in_collections (String):
          Specifies the  name(s) of the DEA collection to consider for
          download. At least one is required.
      in_assets (String):
          Specifies the  name(s) of the DEA assets (i.e., bands) to consider
          for download. At least one is required.
      in_mask_algorithm (String):
          The pixel quality mask algorithm to considered when masking invalid
          pixels. See  here  for more information about the FMask algorithm
          used by DEA to derive quality mask categories , and here for the
          S2Cloudless algorithm.
      in_quality_flags (String):
          Specifies the pixel quality mask categories used to define valid
          pixels in each downloaded image. <SPAN />  If the FMask algorithm is
          requested, the  selected categories  will be considered valid and will
          not be masked out. If the S2Cloudless algorithm is used, only the
          valid category is considered and no choice is provided. See  here
          for more information about the FMask algorithm used by DEA to derive
          quality mask categories , and here for the S2Cloudless algorithm.
          <SPAN />
      in_remove_mask (Boolean):
          Specifies whether the  pixel quality mask  band will be removed
          after pixel masking is completed.
      in_max_empty (Long):
          The maximum percentage of empty (or missing) pixels allowed in an
          image. Empty pixels occur when the user-defined extent extends outside
          of an available satellite image path or row. If an image within the
          download extent has a higher percentage of empty pixels than defined
          here, it will be excluded from download.
      in_max_invalid (Long):
          The maximum percentage of all invalid pixels categorised by the
          pixel quality mask allowed in an image. <SPAN />  If the FMask
          algorithm is used, only  pixel quality categories not selected in the
          Quality Mask Flags parameter   considered invalid , while the
          S2Cloudless algorithm will used the 'Invalid' category. If an image
          within the download extent has a higher percentage of invalid pixels
          than defined here, it will be excluded from download.
      in_nodata_value {Long}:
          The value to set empty and invalid pixels to when applying the
          pixel quality mask.
      in_srs (String):
          Specifies the output spatial reference system used to project
          downloaded imagery.
      in_res (Double):
          Specifies the output spatial resolution used to resample the
          downloaded imagery.
      in_max_threads {Long}:
          The maximum number of threads allowed when downloading data.
          Leaving this parameter blank will set the optimal number of threads
          automatically.

     OUTPUTS:
      out_nc (File):
          The NetCDF (i.e., data cube) containing the downloaded imagery."""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.FetchSentinel2BaselineData_ArcDEA(*gp_fixargs((in_extent, out_nc, in_start_date, in_end_date, in_collections, in_assets, in_mask_algorithm, in_quality_flags, in_remove_mask, in_max_empty, in_max_invalid, in_nodata_value, in_srs, in_res, in_max_threads), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('GroupData_ArcDEA', None)
def GroupData(in_nc=None, out_nc=None, in_group: Literal['Month', 'Quarter', 'Season', 'Year'] | None=None, in_aggregator: Literal['Minimum', 'Maximum', 'Mean', 'Median', 'Sum', 'Standard Deviation'] | None=None, in_interpolate=None,) -> Result1[str]:
    """GroupData_ArcDEA(in_nc, out_nc, in_group, in_aggregator, in_interpolate)

     INPUTS:
      in_nc (File):
          Input NetCDF
      in_group (String):
          New Temporal Group
      in_aggregator (String):
          Aggregation Method
      in_interpolate (Boolean):
          Interpolate NoData

     OUTPUTS:
      out_nc (File):
          Output NetCDF"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.GroupData_ArcDEA(*gp_fixargs((in_nc, out_nc, in_group, in_aggregator, in_interpolate), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('RemoveOutliers_ArcDEA', None)
def RemoveOutliers(in_nc=None, out_nc=None, in_spike_cutoff=None, in_interpolate=None,) -> Result1[str]:
    """RemoveOutliers_ArcDEA(in_nc, out_nc, in_spike_cutoff, in_interpolate)

     INPUTS:
      in_nc (File):
          Input NetCDF
      in_spike_cutoff (Double):
          Spike Cutoff
      in_interpolate (Boolean):
          Interpolate NoData

     OUTPUTS:
      out_nc (File):
          Output NetCDF"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.RemoveOutliers_ArcDEA(*gp_fixargs((in_nc, out_nc, in_spike_cutoff, in_interpolate), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('ResampleData_ArcDEA', None)
def ResampleData(in_nc=None, out_nc=None, in_frequency: Literal['Daily', 'Weekly', 'Monthly (Start)', 'Monthly (End)', 'Semi-Monthly (Start)', 'Semi-Monthly (End)', 'Quarterly (Start)', 'Quarterly (End)', 'Yearly (Start)', 'Yearly (End)'] | None=None, in_aggregator: Literal['Minimum', 'Maximum', 'Mean', 'Median', 'Sum', 'Standard Deviation'] | None=None, in_interpolate=None,) -> Result1[str]:
    """ResampleData_ArcDEA(in_nc, out_nc, in_frequency, in_aggregator, in_interpolate)

     INPUTS:
      in_nc (File):
          Input NetCDF
      in_frequency (String):
          New Temporal Frequency
      in_aggregator (String):
          Aggregation Method
      in_interpolate (Boolean):
          Interpolate NoData

     OUTPUTS:
      out_nc (File):
          Output NetCDF"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.ResampleData_ArcDEA(*gp_fixargs((in_nc, out_nc, in_frequency, in_aggregator, in_interpolate), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('Testing_ArcDEA', None)
def Testing() -> Result:
    """Testing_ArcDEA()"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.Testing_ArcDEA(*gp_fixargs((), True)))
        return retval
    except Exception as e:
        raise e


# End of generated toolbox code
del gptooldoc, gp, gp_fixargs, convertArcObjectToPythonObject, annotations, TYPE_CHECKING