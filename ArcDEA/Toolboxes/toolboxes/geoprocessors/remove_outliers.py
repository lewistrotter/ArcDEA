
def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS
    import numpy as np
    import xarray as xr
    import arcpy

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_nc = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    in_spike_cutoff = parameters[2].value
    in_interpolate = parameters[3].value

    # uncomment these when testing
    # in_nc = r'C:\Users\Lewis\Desktop\arcdea\data\ls.nc'
    # out_nc = r'C:\Users\Lewis\Desktop\arcdea\data\ls_out.nc'
    # in_spike_cutoff = 2
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
        # load netcdf  # TODO: memory?  # TODO: load later?
        ds = xr.open_dataset(in_nc)

    except Exception as e:
        arcpy.AddError('Error occurred when reading NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    # check if dimensions correct
    if 'time' not in ds:
        arcpy.AddError('No time dimension found in NetCDF.')
        return
    elif 'x' not in ds or 'y' not in ds:
        arcpy.AddError('No x, y dimensions found in NetCDF.')
        return

    # check if netcdf has nodata attribute
    nodata = ds.attrs.get('nodata')
    if nodata is None:
        arcpy.AddError('No nodata attribute in NetCDF.')
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    # extract attributes
    ds_attrs = ds.attrs
    ds_band_attrs = ds[list(ds)[0]].attrs
    ds_spatial_ref_attrs = ds['spatial_ref'].attrs

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region REMOVE OUTLIERS

    arcpy.SetProgressor('default', 'Removing outliers...')

    # check if spike cutoff is valid
    if in_spike_cutoff <= 0:
        arcpy.AddError('Spike cutoff must be > 0.')
        return

    # calc num of dates per year
    num_dates = len(ds['time'])
    num_years = len(np.unique(ds['time.year']))
    num_dates_per_year = num_dates / num_years

    # calculate window size
    win_cen = int(np.floor(num_dates_per_year / 7))

    # initialise progress bar
    arcpy.SetProgressor('step', None, 0, len(ds), 1)

    try:
        i = 0
        for var in ds:
            # notify user
            arcpy.AddMessage(f'Removing outliers for band: {var}...')

            # extract current var as array and set nodata to nan
            da = ds[var]
            da = da.where(da != -999)

            # get std of entire ts vector and multi by user factor
            da_cut = da.std('time', skipna=True)  # FIXME: this is causing a runtimewarning
            da_cut = da_cut * in_spike_cutoff

            # append first/last values to array to pad edges
            da_ext = xr.concat([da[-win_cen:], da, da[:win_cen]], dim='time')

            # generate windows of same size
            da_win = da_ext.rolling(time=2 * win_cen + 1, center=True)
            da_win = da_win.construct('win')

            # xr rolling pads a few wins at start/end with nans, remove them
            da_win = da_win[win_cen:-win_cen]

            # get center win values (same as da) and minus win median
            da_med = np.abs(da - da_win.median('win', skipna=True))  # TODO: this is slow

            # get mean, max of win l, r vals and +/- cutoff, dont remove nans like timesat
            lr = [win_cen - 1, win_cen + 1]
            da_avg = da_win[:, :, :, lr].mean('win', skipna=True) - da_cut
            da_max = da_win[:, :, :, lr].max('win', skipna=True) + da_cut

            # get idxs where med > std dev and cen (same as da) neighbors < avg or > max
            da_err = (da_med >= da_cut) & ((da < da_avg) | (da > da_max))

            # mask error indicies as nan
            da = da.where(~da_err)

            # update in dataset
            ds[var] = da

            # increment counter
            i += 1
            arcpy.SetProgressorPosition(i)

    except Exception as e:
        arcpy.AddError('Error occurred when removing outliers in NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    # TODO: set all values to nan per pixel where any band has nan
    # TODO: ...

    # reset progressor
    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region INTERPOLATE NETCDF IF REQUESTED

    arcpy.SetProgressor('default', 'Interpolating missing NetCDF values...')

    if in_interpolate:

        # initialise progress bar
        arcpy.SetProgressor('step', None, 0, len(ds), 1)

        try:
            i = 0
            for var in ds:
                # interpolate variable
                ds[var] = ds[var].interpolate_na('time')

                # increment counter
                i += 1
                arcpy.SetProgressorPosition(i)

        except Exception as e:
            arcpy.AddError('Error occurred when interpolating. Check messages.')
            arcpy.AddMessage(str(e))
            return

    # reset progressor
    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region FINALISE NETCDF

    arcpy.SetProgressor('default', 'Finalising NetCDF...')

    # set nan back to original nodata value
    # TODO: not sure if we want to do this
    #ds = ds.where(~ds.isnull(), nodata)

    # TODO: set dtype to int? what about index?
    # ...

    # endregion

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
    # region EXPORT NETCDF

    arcpy.SetProgressor('default', 'Exporting NetCDF...')

    try:
        ds.to_netcdf(out_nc)

    except Exception as e:
        arcpy.AddError('Error occurred when exporting NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    #arcpy.SetProgressor('default', 'Cleaning up environment...')

    # endregion

# testing
# execute(None)
