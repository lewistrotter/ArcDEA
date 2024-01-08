def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import xarray as xr
    import arcpy

    from scripts import cube
    from scripts import indices

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_nc = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    in_type = parameters[2].valueAsText
    in_index = parameters[3].valueAsText

    # uncomment these when testing
    # in_nc = r'C:\Users\Lewis\Desktop\arcdea\ls.nc'
    # out_nc = r'C:\Users\Lewis\Desktop\arcdea\ls_ndvi.nc'
    # in_type = 'Vegetation'
    # in_index = 'NDVI: (Normalised Difference Vegetation Index)'

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
                             chunks={'time': 1},    # chunk to prevent memory
                             mask_and_scale=False)  # ensure dtype maintained

    except Exception as e:
        arcpy.AddError('Error occurred when reading NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    if cube.check_xr_is_valid(ds) is False:
        arcpy.AddError('Input NetCDF is not a valid ArcDEA NetCDF.')
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    ds_attrs = ds.attrs
    ds_band_attrs = ds[list(ds)[0]].attrs
    ds_spatial_ref_attrs = ds['spatial_ref'].attrs

    collection = ds.attrs.get('collection')
    if collection not in ['ls', 's2']:
        arcpy.AddError('NetCDF is not from Landsat or Sentinel-2 satellites.')
        return

    nodata = ds.attrs.get('nodata')
    ds = ds.where(ds != nodata).astype('float32')  # set nodata to nan, ensure float32

    raw_bands = list(ds)  # store names for easy drop later on

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CALCULATE INDEX

    arcpy.SetProgressor('default', 'Calculating index...')

    try:
        indices.calc_index(ds,
                           in_type,
                           in_index,
                           collection)

    except Exception as e:
        arcpy.AddError('Error occurred when calculating index. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region DROP RAW NETCDF BANDS

    arcpy.SetProgressor('default', 'Dropping raw NetCDF bands...')

    try:
        ds = ds.drop_vars(raw_bands)

    except Exception as e:
        arcpy.AddError('Error occurred when dropping raw bands. Check messages.')
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

    ds.attrs['processing'] += ';' + 'index'

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

# execute(None)
