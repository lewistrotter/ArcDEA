def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import xarray as xr
    import arcpy

    from scripts import cube

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    # in_nc = parameters[0].valueAsText
    # out_nc = parameters[1].valueAsText
    # in_frequency = parameters[2].value
    # in_aggregator = parameters[3].value
    # in_interpolate = parameters[4].value

    # uncomment these when testing
    in_nc = r'C:\Users\Lewis\Desktop\arcdea\s2.nc'
    out_nc = r'C:\Users\Lewis\Desktop\arcdea\s2_agg.nc'
    in_frequency = 'Monthly (Start)'
    in_aggregator = 'Mean'
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
        # lazy load xr dataset as dask arrays
        ds = xr.open_dataset(in_nc,
                             chunks={'time': 1},
                             mask_and_scale=False)

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
        arcpy.AddError('No NoData attribute in NetCDF.')
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    # extract attributes
    ds_attrs = ds.attrs
    ds_band_attrs = ds[list(ds)[0]].attrs
    ds_spatial_ref_attrs = ds['spatial_ref'].attrs

    # set all numeric nodata to nan
    ds = ds.where(ds != nodata)

    # ensure datatype is float32
    ds = ds.astype('float32')  # TODO: keep an eye on float64

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region RESAMPLE NETCDF TIMESERIES

    arcpy.SetProgressor('default', 'Resampling NetCDF temporal frequency...')

    # create frequency map
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
    freq_map = {
        'Daily': 'D',
        'Weekly': 'W',
        'Monthly (Start)': 'MS',
        'Monthly (End)': 'M',
        'Semi-Monthly (Start)': 'SMS',
        'Semi-Monthly (End)': 'SM',
        'Quarterly (Start)': 'QS',
        'Quarterly (End)': 'Q',
        'Yearly (Start)': 'AS',
        'Yearly (End)': 'A'
    }

    # extract freq based on user input, error if not found
    freq = freq_map.get(in_frequency)
    if freq is None:
        arcpy.AddError('Frequency not supported.')
        return

    try:
        # perform resample
        ds = ds.resample(time=freq)

    except Exception as e:
        arcpy.AddError('Error occurred when resampling NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region AGGREGATE NETCDF VALUES

    arcpy.SetProgressor('default', 'Aggregating NetCDF values...')

    try:
        # apply user aggregator to resampled netcdf
        if in_aggregator == 'Minimum':
            ds = ds.min('time')
        elif in_aggregator == 'Maximum':
            ds = ds.max('time')
        elif in_aggregator == 'Mean':
            ds = ds.mean('time')
        elif in_aggregator == 'Median':
            ds = ds.median('time')
        elif in_aggregator == 'Sum':
            ds = ds.sum('time')
        elif in_aggregator == 'Standard Deviation':
            ds = ds.std('time')
        else:
            arcpy.AddError('Could not find aggregator.')
            return

    except Exception as e:
        arcpy.AddError('Error occurred when aggregating NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region INTERPOLATE NETCDF IF REQUESTED

    arcpy.SetProgressor('default', 'Interpolating missing NetCDF values...')

    if in_interpolate:

        # warn of slow process
        arcpy.AddWarning('Interpolation is currently unoptimised, will take awhile.')

    try:

        # interpolate variable, use chunks to prevent memory issues
        ds = ds.chunk({'time': -1, 'y': 500, 'x': 500})

        # try:
        #     #i = 0
        #     for var in ds:
        #         # interpolate variable
        #         ds[var] = ds[var].interpolate_na('time')
        #
        #         # increment counter
        #         #i += 1
        #         #arcpy.SetProgressorPosition(i)
        #
        # except Exception as e:
        #     arcpy.AddError('Error occurred when interpolating. Check messages.')
        #     arcpy.AddMessage(str(e))
        #     return

    except Exception as e:
        arcpy.AddError('Error occurred when interpolating. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # reset progressor
    #arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region FINALISE NETCDF

    arcpy.SetProgressor('default', 'Finalising NetCDF...')

    # set nan back to original nodata value
    # TODO: not sure if we want to do this
    #ds = ds.where(~ds.isnull(), nodata)

    # set dtype to float32 (getting float64 back)
    # TODO: keep an eye on float64 issues
    #ds = ds.astype('float32')

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region APPEND ATTRIBUTES BACK ON

    arcpy.SetProgressor('default', 'Appending NetCDF attributes back on...')

    # append attributes back on
    ds.attrs = ds_attrs
    ds['spatial_ref'].attrs = ds_spatial_ref_attrs
    for var in ds:
        ds[var].attrs = ds_band_attrs

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXPORT NETCDF

    arcpy.SetProgressor('default', 'Exporting NetCDF...')

    ds.to_netcdf(out_nc)

    from dask.diagnostics import ProgressBar

    try:
        ds.to_netcdf(out_nc)

        # cast collections to string to prevent warning
        #ds['collection'] = ds['collection'].astype(str)  #TODO: this was lost

        #with ProgressBar():
            #ds.to_netcdf(out_nc)

    except Exception as e:
        arcpy.AddError('Error occurred when exporting NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    #arcpy.SetProgressor('default', 'Cleaning up environment...')

    # time.sleep(1)

    # endregion

execute(None)
