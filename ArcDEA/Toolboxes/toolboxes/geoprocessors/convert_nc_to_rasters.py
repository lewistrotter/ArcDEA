

def execute(parameters):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import xarray as xr
    import arcpy
    import ui

    from cuber import converters
    from cuber import shared

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    in_nc = parameters[0].valueAsText
    out_folder = parameters[1].valueAsText
    out_extension = parameters[2].valueAsText

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region READ NETCDF

    arcpy.SetProgressor('default', 'Reading NetCDF data...')

    try:
        ds = xr.open_dataset(in_nc,
                             chunks={'time': 1},    # chunk to prevent memory
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CONFORM DATA TYPES AND NODATA VALUES

    arcpy.SetProgressor('default', 'Conforming data types and nodata values...')

    try:
        # converter will do this again, but for clarity...
        ds = shared.elevate_xr_dtypes(ds)
        ds = shared.elevate_xr_nodata(ds)

    except Exception as e:
        arcpy.AddError('Error occurred while conforming data. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXPORT RASTERS

    n_dls = len(ds['time'])  # only computing once per date
    arcpy.SetProgressor('step', 'Exporting rasters...', 0, n_dls, 1)

    out_extension = ui.convert_file_extensions(out_extension)

    try:
        dts = ds['time'].to_numpy()
        for dt in dts:
            ds_sel = ds.sel(time=dt)

            converters.xr_to_raster(ds=ds_sel,
                                    out_folder=out_folder,
                                    out_extension=out_extension)

            arcpy.SetProgressorPosition()

    except Exception as e:
        arcpy.AddError('Error occurred while exporting rasters. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    arcpy.ResetProgressor()

    # endregion

    return


def _make_test_params():
    """For testing outside ArcGIS Pro only."""

    import arcpy

    p00 = arcpy.Parameter(name='in_nc',
                          datatype='DEFile',
                          parameterType='Required',
                          direction='Input')
    p00.filter.list = ['nc']

    p01 = arcpy.Parameter(name='out_folder',
                          datatype='DEFolder',
                          parameterType='Required',
                          direction='Input')

    p02 = arcpy.Parameter(displayName='Output Format',
                          name='in_extension',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p02.filter.type = 'ValueList'


    p00.value = r'C:\Users\Lewis\Documents\ArcGIS\Projects\ArcDEA\ds.nc'
    p01.value = r'C:\Users\Lewis\Desktop\tmp'
    p02.value = 'TIFF'

    params = [p00, p01, p02]

    return params

# execute(_make_test_params())  # testing, comment out when done