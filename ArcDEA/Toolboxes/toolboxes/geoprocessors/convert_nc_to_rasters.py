

def execute(
        parameters
        # messages  # TODO: use messages input?
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import os
    import shutil
    import datetime
    import xarray as xr
    import arcpy

    from osgeo import gdal

    from scripts import shared
    #from scripts import conversions
    #from scripts import web

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_nc = parameters[0].valueAsText
    out_folder = parameters[1].valueAsText

    # uncomment these when testing
    # in_nc = r'C:\Users\Lewis\Desktop\arcdea\data\gmed.nc'
    # out_folder = r'C:\Users\Lewis\Desktop\arcdea\data'

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True
    # num_cpu = shared.detect_num_cores(modify_percent=0.95)  # TODO: set this via ui

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region LOAD AND CHECK NETCDF

    arcpy.SetProgressor('default', 'Reading and checking NetCDF data...')

    try:
        ds = xr.open_dataset(in_nc)

    except Exception as e:
        arcpy.AddError('Error occurred when reading NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    if 'time' not in ds:
        arcpy.AddError('No time dimension detected in NetCDF.')
        return

    # TODO: check if nodata value exists

    # TODO: check if has correct attrs

    # TODO: other checks

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region working

    arcpy.SetProgressor('default', 'Converting NetCDF to rasters...')

    tmp_folder = os.path.join(out_folder, 'tmp')

    shared.drop_temp_folder(tmp_folder)
    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)

    # set up step-wise progressor
    arcpy.SetProgressor('step', None, 0, len(ds['time']))

    # TODO: threading?

    try:
        for i in range(len(ds['time'])):
            da = ds.isel(time=i)

            dt = da['time'].dt.strftime('%Y-%m-%d')
            dt = str(dt.values)

            arcpy.AddMessage(f'Converting date: {dt}')

            tmp_bands = []
            for var in list(da.data_vars):
                tmp_nc = os.path.join(tmp_folder, f'{var}.nc')
                da[var].to_netcdf(tmp_nc)

                dataset = gdal.Open(tmp_nc, gdal.GA_ReadOnly)

                tmp_ras = os.path.join(tmp_folder, f'{var}.tif')
                dataset = gdal.Translate(tmp_ras, dataset)
                dataset = None

                tmp_bands.append(tmp_ras)

            if 'platform' in list(da.coords):
                code = str(da['platform'].values)
                fn = f'R{dt}-{code}.tif'
            else:
                fn = f'R{dt}.tif'

            out_ras = os.path.join(out_folder, fn)
            arcpy.management.CompositeBands(in_rasters=tmp_bands,
                                            out_raster=out_ras)

            arcpy.SetProgressorPosition()

    except Exception as e:
        arcpy.AddError('Error occurred when reading NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    # reset progressor
    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    arcpy.SetProgressor('default', 'Cleaning up environment...')

    shared.drop_temp_folder(tmp_folder)

    # endregion

# execute(None)