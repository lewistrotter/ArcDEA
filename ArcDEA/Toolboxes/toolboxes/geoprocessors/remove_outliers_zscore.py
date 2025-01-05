
def execute(parameters):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import os
    import time
    import numpy as np
    import xarray as xr
    import arcpy
    import ui

    from cuber import shared
    from cuber import outliers

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    in_nc = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    win_size = parameters[2].value
    num_stdvs = parameters[3].value
    fill_outliers = parameters[4].value
    clamp_nodata = parameters[5].value
    max_threads = parameters[6].value

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True
    arc_progress_bar = ui.make_progress_bar()

    if not max_threads:
        max_threads = max(os.cpu_count() // 2, 1)  # keeps ui responsive

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region READ NETCDF

    arcpy.SetProgressor('default', 'Reading NetCDF data...')

    chunks = {'time': -1, 'x': 128, 'y': 128}  # small x, y chunks for low memory

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

    # TODO: check if duplicate dates need removal

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    ds = ds.drop_vars('mask', errors='ignore')  # no longer want mask

    # note: zscore func handles nodata to nan and float32 cast

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region DETECT AND REMOVE OUTLIERS

    n_dls = len(list(ds.data_vars))
    arcpy.SetProgressor('step', 'Detecting and removing outliers...', 0, n_dls, 1)

    # prepare window size
    if win_size is None:
        n_dts = ds['time'].size
        n_yrs = len(np.unique(ds['time.year']))
        win_size = int(2 * ((n_dts / n_yrs) // 7) + 1)

    if win_size % 2 == 0:
        win_size += 1  # win must be odd number

    win_size = max(win_size, 3)  # min size is 3

    arcpy.AddMessage(f'Setting window size size: {win_size}.')

    try:
        for var in ds.data_vars:
            da = ds[var]

            da = outliers.zscore_filter(da=da,
                                        win_size=win_size,
                                        n_sigma=num_stdvs,
                                        fill_outliers=fill_outliers)

            ds[var] = da

        with arc_progress_bar:
            ds.load(num_workers=max_threads)

    except Exception as e:
        arcpy.AddError('Error occurred while removing outliers. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLAMP NODATA

    if clamp_nodata:

        arcpy.SetProgressor('default', 'Clamping NoData...')

        try:
            ds = shared.clamp_nodata(ds)

        except Exception as e:
            arcpy.AddError('Error occurred while clamping NoData. See messages.')
            arcpy.AddMessage(str(e))
            return

        time.sleep(1)

    # endregion

    # note: the above conformed dtypes and nodata

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

    p00 = arcpy.Parameter(displayName='Input NetCDF',
                          name='in_nc',
                          datatype='DEFile',
                          parameterType='Required',
                          direction='Input')

    p01 = arcpy.Parameter(displayName='Output NetCDF',
                          name='out_nc',
                          datatype='DEFile',
                          parameterType='Required',
                          direction='Output')

    p02 = arcpy.Parameter(displayName='Window Size',
                          name='in_win_size',
                          datatype='GPLong',
                          parameterType='Optional',
                          direction='Input')

    p03 = arcpy.Parameter(displayName='Number of Standard Deviations',
                          name='in_num_stdvs',
                          datatype='GPDouble',
                          parameterType='Required',
                          direction='Input')

    p04 = arcpy.Parameter(name='in_fill_outliers',
                          datatype='GPBoolean',
                          parameterType='Required',
                          direction='Input')

    p05 = arcpy.Parameter(name='in_clamp_nodata',
                          datatype='GPBoolean',
                          parameterType='Required',
                          direction='Input')

    p06 = arcpy.Parameter(name='in_max_threads',
                          datatype='GPLong',
                          parameterType='Optional',
                          direction='Input')

    p00.value = r"C:\Users\Lewis\PycharmProjects\cuber\data\ds_small.nc"
    p01.value = r'C:\Users\Lewis\Desktop\tmp\out.nc'
    p02.value = None
    p03.value = 2.0
    p04.value = False
    p05.value = True
    p06.value = None

    params = [p00, p01, p02, p03, p04, p05, p06]

    return params

# execute(_make_test_params())  # testing, comment out when done
