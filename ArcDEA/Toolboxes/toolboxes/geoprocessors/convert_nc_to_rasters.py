

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

    #from scripts import conversions
    #from scripts import web

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_nc = parameters[0].valueAsText
    out_folder = parameters[1].valueAsText
    #in_frequency = parameters[2].value
    #in_aggregator = parameters[3].value
    #in_interpolate = parameters[4].value

    # uncomment these when testing
    # in_nc = r'C:\Users\Lewis\Desktop\arcdea\s2_2.nc'
    # out_folder = r'C:\Users\Lewis\Desktop\arcdea\rasters'
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

    #if 'time' not in ds:
        #arcpy.AddError('No time dimension detected in NetCDF.')
        #raise  # return

    # TODO: check if nodata value exists

    # TODO: check if has correct attrs

    # TODO: other checks

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    #arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    #ds_attrs = ds.attrs
    #ds_band_attrs = ds[list(ds)[0]].attrs
    #ds_spatial_ref_attrs = ds['spatial_ref'].attrs

    #ds = ds.where(ds != -999)

    # TODO: others?

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region working

    arcpy.SetProgressor('default', 'Converting NetCDF to rasters...')

    tmp_folder = os.path.join(out_folder, 'tmp')
    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)

    # set up step-wise progressor
    arcpy.SetProgressor('step', None, 0, len(ds['time']))

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

                # options = gdal.TranslateOptions()

                tmp_ras = os.path.join(tmp_folder, f'{var}.tif')
                dataset = gdal.Translate(tmp_ras, dataset)
                dataset = None

                # append tif to bands list
                tmp_bands.append(tmp_ras)

            out_ras = os.path.join(out_folder, f'R{dt}.tif')
            arcpy.management.CompositeBands(in_rasters=tmp_bands,
                                            out_raster=out_ras)

            # increment progressor
            arcpy.SetProgressorPosition()

    except Exception as e:
        arcpy.AddError('Error occurred when reading NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        raise  # return

    # reset progressor
    arcpy.ResetProgressor()

    # endregion


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXPORT RESAMPLED NETCDF

    #arcpy.SetProgressor('default', 'Exporting resampled NetCDF...')

    #ds.to_netcdf(out_nc)
    #ds.close()

    # endregion


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    try:
        shutil.rmtree(tmp_folder)

    except:
        arcpy.AddMessage('Could not delete temporary data folder.')

    #arcpy.SetProgressor('default', 'Cleaning up environment...')

    #arcpy.env.overwriteOutput = None  # TODO: make sure setting to none works

    # endregion

#execute(None)