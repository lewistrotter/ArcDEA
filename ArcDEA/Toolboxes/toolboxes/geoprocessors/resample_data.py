import os
import datetime
import xarray as xr
import arcpy

from scripts import conversions
from scripts import web


def execute(
        parameters
        # messages  # TODO: use messages input?
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_nc = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    in_frequency = parameters[2].value
    in_aggregator = parameters[3].value
    in_interpolate = parameters[4].value

    # uncomment these when testing
    # in_nc = r'C:\Users\Lewis\Desktop\test_nc\ls.nc'
    # out_nc = r'C:\Users\Lewis\Desktop\test_nc\ls_monthly_mean.nc'
    # in_frequency = 'Monthly Ending'
    # in_aggregator = 'Mean'
    # in_interpolate = True

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region LOAD AND CHECK NETCDF

    arcpy.SetProgressor('default', 'Reading and checking NetCDF data...')

    try:
        ds = xr.open_dataset(in_nc)

    except Exception as e:
        arcpy.AddError('Error occurred when reading NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        raise  # return

    if 'time' not in ds:
        arcpy.AddError('No time dimension detected in NetCDF.')
        raise  # return

    # TODO: check if nodata value exists

    # TODO: check if has correct attrs

    # TODO: other checks

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    ds_attrs = ds.attrs
    ds_band_attrs = ds[list(ds)[0]].attrs
    ds_spatial_ref_attrs = ds['spatial_ref'].attrs

    ds = ds.where(ds != -999)

    # TODO: others?

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region RESAMPLE NETCDF

    arcpy.SetProgressor('default', 'Resampling NetCDF...')

    # D, W, SM, MS, SMS, Q, QS, Y, YS
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
    ds = ds.resample(time='M')  # TODO: hook up with in_frequency

    # TODO: get method from user
    if in_aggregator == 'Mean':
        ds = ds.mean('time')

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region INTERPOLATE NETCDF IF REQUESTED

    arcpy.SetProgressor('default', 'Interpolating NetCDF...')

    if in_interpolate:
        ds = ds.interpolate_na('time')

    # endregion

    # TODO: change nans back to original nodata value
    # make user choice

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region APPEND ATTRIBUTES BACK ON

    arcpy.SetProgressor('default', 'Appending NetCDF attributes back on...')

    # append attributes back on
    ds.attrs = ds_attrs
    ds['spatial_ref'].attrs = ds_spatial_ref_attrs
    for var in ds:
        ds[var].attrs = ds_band_attrs

    # endregion



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXPORT RESAMPLED NETCDF

    arcpy.SetProgressor('default', 'Exporting resampled NetCDF...')

    ds.to_netcdf(out_nc)
    ds.close()

    # endregion


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    arcpy.SetProgressor('default', 'Cleaning up environment...')

    arcpy.env.overwriteOutput = None  # TODO: make sure setting to none works

    # endregion

#xecute(None)