def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import numpy as np
    import xarray as xr
    import arcpy

    from scripts import outliers
    from scripts import cube

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    # in_nc = parameters[0].valueAsText
    # out_nc = parameters[1].valueAsText
    # in_spike_cutoff = parameters[2].value
    # in_interpolate = parameters[3].value

    # uncomment these when testing
    in_nc = r'C:\Users\Lewis\Desktop\arcdea\s2.nc'
    out_nc = r'C:\Users\Lewis\Desktop\arcdea\s2_or.nc'
    in_spike_cutoff = 2
    in_interpolate = True

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region LOAD AND CHECK NETCDF

    arcpy.SetProgressor('default', 'Reading and checking NetCDF data...')

    try:
        ds = xr.open_dataset(in_nc,
                             chunks={'time': -1}, #'x': 250, 'y': 250},   # chunk to prevent memory  # TODO: enable this for ufunc ver
                             mask_and_scale=False)  # ensure dtype maintained

    except Exception as e:
        arcpy.AddError('Error occurred when reading NetCDF. See messages.')
        arcpy.AddMessage(str(e))
        return

    if cube.check_xr_is_valid(ds) is False:
        arcpy.AddError('Input NetCDF is not a valid ArcDEA NetCDF.')
        return

    time.sleep(1)

    # endregion



    #from typing import Union

    # def xr_flatten(
    #         ds: Union[xr.Dataset, xr.DataArray]
    # ):
    #
    #     # cast input datasets to dataarray
    #     if isinstance(ds, xr.Dataset):
    #         ds = ds.to_array()



        # flatten into n var arrays (2d) per coord
        #ds = ds.stack(xy=['x', 'y'])
        #ds = ds.transpose('xy', 'time')
        #ds = ds.to_array()



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    ds_attrs = ds.attrs
    ds_band_attrs = ds[list(ds)[0]].attrs
    ds_spatial_ref_attrs = ds['spatial_ref'].attrs

    nodata = ds.attrs.get('nodata')
    ds = ds.where(ds != nodata).astype('float32')  # set nodata to nan, ensure float32

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region REMOVE OUTLIERS

    arcpy.SetProgressor('default', 'Removing outliers...')

    if in_spike_cutoff <= 0:
        arcpy.AddError('Spike cutoff must be > 0.')
        return

    num_dates = len(ds['time'])
    num_years = len(np.unique(ds['time.year']))
    num_dates_per_year = num_dates / num_years

    win_cen = int(np.floor(num_dates_per_year / 7))

    try:
        #ds = outliers.spike_remove_dask(ds, win_cen, in_spike_cutoff)
        ds = outliers.spike_remove_ufunc(ds, win_cen, in_spike_cutoff)

    except Exception as e:
        arcpy.AddError('Error occurred while removing outliers. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region INTERPOLATE NETCDF IF REQUESTED

    if in_interpolate:

        arcpy.SetProgressor('default', 'Interpolating missing NetCDF values...')

        try:
            ds = ds.interpolate_na('time')

        except Exception as e:
            arcpy.AddError('Error occurred while interpolating. See messages.')
            arcpy.AddMessage(str(e))
            return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region FINALISE NETCDF

    arcpy.SetProgressor('default', 'Finalising NetCDF...')

    # TODO: set nodata back to original value?

    ds.attrs = ds_attrs
    ds['spatial_ref'].attrs = ds_spatial_ref_attrs
    for var in ds:
        ds[var].attrs = ds_band_attrs

    ds.attrs['processing'] += ';' + 'outlier_remove'

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXPORT NETCDF

    arcpy.SetProgressor('default', 'Exporting NetCDF...')

    try:
        cube.export_xr_to_nc(ds, out_nc)

    except Exception as e:
        arcpy.AddError('Error occurred while exporting combined NetCDF. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

execute(None)
