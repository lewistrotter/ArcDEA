
def execute(parameters):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import xarray as xr
    import arcpy
    import ui

    from cuber import shared
    from cuber import indices
    from dask.callbacks import Callback

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    in_nc = parameters[0].valueAsText
    out_nc = parameters[1].valueAsText
    # index_type = parameters[2].valueAsText  # used only on ui
    index_name = parameters[3].valueAsText

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True

    class ArcProgressBar(Callback):
        def _posttask(self, key, result, dsk, state, worker_id):
            arcpy.SetProgressorPosition()

    time.sleep(1)

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
    # region PREPARE NETCDF DATA

    arcpy.SetProgressor('default', 'Preparing NetCDF data...')

    ds = ds.drop_vars('mask', errors='ignore')  # no longer want mask

    try:
        # set all nodata to nan (also sets to float32)
        ds = shared.set_xr_nodata_to_nan(ds)

    except Exception as e:
        arcpy.AddError('Error occurred when preparing NetCDF. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region COMPUTE INDEX

    n_dls = len(ds['time'])  # only computing once per date
    arcpy.SetProgressor('step', 'Computing index...', 0, n_dls, 1)

    index_name = index_name.split(':')[0].lower()  # remove ui label

    try:
        collection = ui.extract_xr_collection(ds)  # will error if nothing

        # TODO: maybe indices.calculate() ?
        ds = indices.calc_indices(ds=ds,
                                  index=index_name,
                                  collection=collection,
                                  rescale=True,
                                  drop_bands=True)

        with ArcProgressBar():
            ds.load()

    except Exception as e:
        arcpy.AddError('Error occurred when calculating index. Check messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CONFORM DATA TYPES

    arcpy.SetProgressor('default', 'Conforming data types...')

    try:
        ds = shared.elevate_xr_dtypes(ds)

    except Exception as e:
        arcpy.AddError('Error occurred while conforming data types. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

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

def _make_test_params():
    """For testing outside ArcGIS Pro only."""

    import arcpy

    p00 = arcpy.Parameter(name='in_nc',
                          datatype='DEFile',
                          parameterType='Required',
                          direction='Input')
    p00.filter.list = ['nc']

    p01 = arcpy.Parameter(name='out_nc',
                          datatype='DEFile',
                          parameterType='Required',
                          direction='Output')
    p01.filter.list = ['nc']

    p02 = arcpy.Parameter(name='in_index_type',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p02.filter.type = 'ValueList'

    p03 = arcpy.Parameter(name='in_index_name',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p03.filter.type = 'ValueList'

    p00.value = r'C:\Users\Lewis\Documents\ArcGIS\Projects\ArcDEA\ds.nc'
    p01.value = r'C:\Users\Lewis\Documents\ArcGIS\Projects\ArcDEA\ndvi.nc'
    p02.value = 'Vegetation'
    p03.value = 'NDVI: Normalised Difference Vegetation Index'

    params = [p00, p01, p02, p03]

    return params

# execute(_make_test_params())  # testing, comment out when done
