
def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import datetime
    import xarray as xr
    import arcpy

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_nc = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    in_group = parameters[2].value
    in_aggregator = parameters[3].value
    in_interpolate = parameters[4].value

    # uncomment these when testing
    # in_nc = r'C:\Users\Lewis\Desktop\arcdea\data\s2.nc'
    # out_nc = r'C:\Users\Lewis\Desktop\arcdea\data\s2_grp.nc'
    # in_group = 'Season'  #  'Year'  # 'Month'
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
        # load netcdf  # TODO: memory?
        with xr.open_dataset(in_nc) as ds:
            ds.load()

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

    # convert nodata to null
    ds = ds.where(ds != nodata)

    # get start, end years
    #s_year = int(ds['time.year'].isel(time=0))
    e_year = int(ds['time.year'].isel(time=-1))

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region GROUP NETCDF TIMESERIES

    arcpy.SetProgressor('default', 'Grouping NetCDF temporal frequency...')

    # create group map
    # https://docs.xarray.dev/en/stable/generated/xarray.DataArray.groupby.html
    group_map = {
        #'Day': 'time.day',
        #'Day of Week': 'time.dayofweek',
        #'Day of Year': 'time.dayofyear',
        #'Week': 'time.week',
        #'Week of Year': 'time.weekofyear',
        'Month': 'time.month',
        'Quarter': 'time.quarter',
        'Season': 'time.season',
        'Year': 'time.year',
    }

    # extract group based on user input, error if not found
    group = group_map.get(in_group)
    if group is None:
        arcpy.AddError('Could not find group.')
        return

    try:
        # perform groupby
        ds = ds.groupby(group)

    except Exception as e:
        arcpy.AddError('Error occurred when resampling NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

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
        elif in_aggregator == 'Standard Deviation':
            ds = ds.std('time')
        else:
            arcpy.AddError('Could not find aggregator.')
            return

    except Exception as e:
        arcpy.AddError('Error occurred when aggregating NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CORRECT DATETIME VALUES

    arcpy.SetProgressor('default', 'Correcting NetCDF datetime values...')

    # get time dim label from dataset
    lbl = group.split('.')[1]

    try:
        if lbl == 'dayofyear':
            raise NotImplemented('Day of year not yet implemented.')  # TODO: implement
        elif lbl == 'week':
            raise NotImplemented('Week not yet implemented.')  # TODO: implement
        elif lbl == 'month':
            ds[lbl] = [datetime.datetime(e_year, m, 1) for m in ds[lbl].values]
        elif lbl == 'quarter':
            qs = {1: 1, 2: 4, 3: 7, 4: 10}
            ds[lbl] = [datetime.datetime(e_year, qs[q], 1) for q in ds[lbl].values]
        elif lbl == 'season':
            ss = {'DJF': 1, 'MAM': 4, 'JJA': 7, 'SON': 10}
            ds[lbl] = [datetime.datetime(e_year, ss[s], 1) for s in ds[lbl].values]
        elif lbl == 'year':
            ds[lbl] = [datetime.datetime(y, 1, 1) for y in ds[lbl].values]

        # rename grouped time label to time and sort by time
        ds = ds.rename({lbl: 'time'}).sortby('time')

    except Exception as e:
        arcpy.AddError('Error occurred when correcting dates in NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region INTERPOLATE NETCDF IF REQUESTED

    arcpy.SetProgressor('default', 'Interpolating missing NetCDF values...')

    # interpolate if user requested
    if in_interpolate:
        ds = ds.interpolate_na('time')

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

#execute(None)
