
def execute(
        parameters
):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import xarray as xr
    import arcpy

    from scripts import indices

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    # uncomment these when not testing
    in_nc = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    in_type = parameters[2].valueAsText
    in_index_vegetation = parameters[3].valueAsText
    in_index_water = parameters[4].valueAsText
    in_index_minerals = parameters[5].valueAsText

    # uncomment these when testing
    # in_nc = r'C:\Users\Lewis\Desktop\arcdea\s2.nc'
    # out_nc = r'C:\Users\Lewis\Desktop\arcdea\s2_agg.nc'
    # in_type = 'Vegetation'
    # in_index_vegetation = 'NDVI: (Normalised Difference Vegetation Index)'
    # in_index_water = 'NDWI: (Normalised Difference Water Index)'
    # in_index_minerals = 'CMR: Clay Minerals Ratio'

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
    if 'x' not in ds or 'y' not in ds:
        arcpy.AddError('No x, y dimensions found in NetCDF.')
        return

    # check if netcdf has nodata attribute
    nodata = ds.attrs.get('nodata')
    if nodata is None:
        arcpy.AddError('No nodata attribute in NetCDF.')
        return

    # check xr has collections attr
    collections = ds.attrs.get('collections')
    if collections is None:
        arcpy.AddError('No collections attribute in NetCDF.')
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    # extract attributes
    ds_attrs = ds.attrs
    ds_band_attrs = ds[list(ds)[0]].attrs
    ds_spatial_ref_attrs = ds['spatial_ref'].attrs

    # get collection
    collection = ';'.join([c for c in ds.attrs.get('collections')])
    if 'ls' in collections:
        collection = 'ls'
    elif 's2' in collection:
        collection = 's2'
    else:
        arcpy.AddError('Could not find collection.')
        return

    # convert nodata to null
    ds = ds.where(ds != nodata)

    # extract original bands for later removal
    raw_bands = list(ds.data_vars)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CALCULATE INDEX

    arcpy.SetProgressor('default', 'Calculating index...')

    try:
        if in_type == 'Vegetation':
            if in_index_vegetation.startswith('NDVI:'):
                ds = indices.ndvi(ds=ds, collection=collection)
            # elif

        elif in_type == 'Water':
            if in_index_water.startswith('NDWI:'):
                ds = indices.ndwi(ds=ds, collection=collection)
            # elif

        elif in_type == 'Minerals':
            if in_index_minerals.startswith('CMR:'):
                ds = indices.cmr(ds=ds, collection=collection)
            # elif

    except Exception as e:
        arcpy.AddError('Error occurred when calculating index. Check messages.')
        arcpy.AddMessage(str(e))
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region REMOVE RAW NETCDF BANDS

    arcpy.SetProgressor('default', 'Removing raw NetCDF bands...')

    try:
        # remove all raw netcdf bands
        ds = ds.drop_vars(raw_bands)

    except Exception as e:
        arcpy.AddError('Error occurred when dropping raw bands. Check messages.')
        arcpy.AddMessage(str(e))
        return

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region FINALISE NETCDF

    arcpy.SetProgressor('default', 'Finalising NetCDF...')

    # set nan back to original nodata value
    # TODO: not sure if we want to do this
    ds = ds.where(~ds.isnull(), nodata)

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
