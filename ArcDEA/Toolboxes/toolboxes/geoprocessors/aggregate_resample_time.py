
def execute(parameters):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import xarray as xr
    import arcpy
    import ui

    #from cuber import shared
    from cuber import aggregators

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    in_nc = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    resampling_method = parameters[2].valueAsText
    percentile= parameters[3].value
    resampling_unit = parameters[4].valueAsText
    resampling_interval = parameters[5].value
    fill_nodata = parameters[6].value
    max_threads = parameters[7].value

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True
    arc_progress_bar = ui.make_progress_bar()

    # note: no need for restricting cpus, func is not intensive

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region READ NETCDF

    arcpy.SetProgressor('default', 'Reading NetCDF data...')

    chunks = {'time': -1, 'x': 256, 'y': 256}  # small x, y chunks for low memory

    try:
        ds = xr.open_dataset(in_nc,
                             chunks=chunks,         # chunk to prevent memory
                             mask_and_scale=False)  # ensure dtype maintained

    except Exception as e:
        arcpy.AddError('Error occurred when reading NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    if 'time' not in ds or 'x' not in ds or 'y' not in ds:
        arcpy.AddError('Input NetCDF missing time, x and/or y dimensions.')
        return

    time.sleep(1)

    # endregion

    # TODO: check if duplicate dates throw error

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    ds = ds.drop_vars('mask', errors='ignore')  # no longer want mask

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region RESAMPLE DATA

    arcpy.SetProgressor('step', 'Resampling data...', 0, 100, 1)

    # prepare resampling unit
    if resampling_unit == 'Daily':
        resampling_unit = 'D'  # TODO: S?
    elif resampling_unit == 'Weekly':
        resampling_unit = 'W'  # TODO: S?
    elif resampling_unit == 'Fortnighly':
        resampling_unit = 'SMS'
    elif resampling_unit == 'Monthly':
        resampling_unit = 'MS'
    elif resampling_unit == 'Quarterly':
        resampling_unit = 'QS'
    elif resampling_unit == 'Yearly':
        resampling_unit = 'YS'

    freq = f'{resampling_interval}{resampling_unit}'

    percentile /= 100  # to decimal

    try:
        for var in ds.data_vars:
            da = ds[var]

            da = aggregators.resample_time(da=da,
                                           resampling_method=resampling_method,
                                           percentile=percentile,
                                           resampling_freq=freq,
                                           fill_nodata=fill_nodata)

            ds[var] = da

        with arc_progress_bar:
            ds.load(num_workers=max_threads)

    except Exception as e:
        arcpy.AddError('Error occurred while resampling data. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    arcpy.ResetProgressor()

    # endregion

    # TODO: conform dtypes and nodata?

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXPORT NETCDF

    arcpy.SetProgressor('default', 'Exporting NetCDF...')

    try:
        ds.to_netcdf(out_nc)

    except Exception as e:
        arcpy.AddError('Error occurred while exporting NetCDF. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    return


def _make_test_params():
    """For testing outside ArcGIS Pro only."""

    import arcpy

    p00 = arcpy.Parameter(name='in_nc',
                          datatype='DEFile',
                          parameterType='Required',
                          direction='Input')

    p01 = arcpy.Parameter(name='out_nc',
                          datatype='DEFile',
                          parameterType='Required',
                          direction='Output')

    p02 = arcpy.Parameter(name='in_resampling_method',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p02.filter.type = 'ValueList'

    p03 = arcpy.Parameter(name='in_percentile',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')

    p04 = arcpy.Parameter(name='in_resampling_unit',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p04.filter.type = 'ValueList'

    p05 = arcpy.Parameter(name='in_resampling_interval',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')

    p06 = arcpy.Parameter(name='in_fill_nodata',
                          datatype='GPBoolean',
                          parameterType='Required',
                          direction='Input')

    p07 = arcpy.Parameter(name='in_max_threads',
                          datatype='GPLong',
                          parameterType='Optional',
                          direction='Input')

    p00.value = r"C:\Users\Lewis\PycharmProjects\cuber\data\ds_small.nc"
    p01.value = r'C:\Users\Lewis\Desktop\tmp'
    p02.value = 'Median'
    p03.value = 95
    p04.value = 'Yearly'
    p05.value = 1
    p06.value = True
    p07.value = None

    params = [p00, p01, p02, p03, p04, p05, p06, p07]

    return params

# execute(_make_test_params())  # testing, comment out when done
