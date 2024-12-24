
def execute(parameters):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import arcpy
    import cuber
    import ui

    from cuber import shared
    from dask.callbacks import Callback

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    ext = parameters[0].value
    out_nc = parameters[1].valueAsText
    start_year = parameters[2].valueAsText
    end_year = parameters[3].valueAsText
    collections = parameters[4].value
    assets = parameters[5].value
    remove_slc_off = parameters[6].value
    out_srs = parameters[7].value
    out_res = parameters[8].value
    max_threads = parameters[9].value

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True
    cuber.set_messenger(arcpy.AddMessage)

    class ArcProgressBar(Callback):
        def _posttask(self, key, result, dsk, state, worker_id):
            if key[0].startswith('block-') and 'gdal_reader_func' in key[0]:
                arcpy.SetProgressorPosition()

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region QUERY STAC ENDPOINT

    arcpy.SetProgressor('default', 'Querying DEA STAC endpoint...')

    in_bbox = (ext.XMin, ext.YMin, ext.XMax, ext.YMax)
    in_epsg = ext.spatialReference.factoryCode

    out_epsg = ui.extract_epsg_code(out_srs)
    out_bbox = shared.reproject_bbox(in_bbox, in_epsg, out_epsg)

    # TODO: renable once projectas working
    #ext = ext.projectAs(arcpy.SpatialReference(out_epsg))
    #out_bbox = (ext.XMin, ext.YMin, ext.XMax, ext.YMax)

    if out_epsg == 4326:
        out_res *= 9.466833186042272E-06

    start_date = f'{start_year}-01-01'
    end_date = f'{end_year}-12-31'

    collections = ui.convert_collections('ga_ls_gm_ard_3', collections)
    assets = ui.convert_assets('ga_ls_gm_ard_3', assets)

    try:
        ds = cuber.fetch(
            collections=collections,
            assets=assets,
            date=(start_date, end_date),
            out_bbox=out_bbox,
            out_epsg=out_epsg,
            out_res=out_res,
            remove_slc_off=remove_slc_off,
            ignore_errors=True  # TODO: add to ui
        )

    except Exception as e:
        arcpy.AddError('Error occurred during DEA STAC query. See messages.')
        arcpy.AddMessage(str(e))
        return

    if 'time' not in ds.dims or len(ds['time']) == 0:
        arcpy.AddWarning('No STAC features were found.')
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region DOWNLOAD WCS VALID DATA

    n_dls = shared.count_xr_chunked(ds)
    arcpy.SetProgressor('step', 'Downloading valid data...', 0, n_dls, 1)

    try:
        with ArcProgressBar():
            ds.load(num_workers=max_threads)

    except Exception as e:
        arcpy.AddError('Error occurred while downloading valid data. See messages.')
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region WRAP UP

    arcpy.SetProgressor('default', 'Wrapping up...')

    ui.print_dates(ds)

    time.sleep(1)

    # endregion

    return


def _make_test_params():
    """For testing outside ArcGIS Pro only."""

    import arcpy

    p00 = arcpy.Parameter(name='in_extent',
                          datatype='GPExtent',
                          parameterType='Required',
                          direction='Input')

    p01 = arcpy.Parameter(name='out_nc',
                          datatype='DEFile',
                          parameterType='Required',
                          direction='Output')

    p02 = arcpy.Parameter(name='in_start_year',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')

    p03 = arcpy.Parameter(name='in_end_year',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')

    p04 = arcpy.Parameter(name='in_collections',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input',
                          multiValue=True)
    p04.filter.type = 'ValueList'

    p05 = arcpy.Parameter(name='in_assets',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input',
                          multiValue=True)
    p05.filter.type = 'ValueList'

    p06 = arcpy.Parameter(name='in_remove_slc_off',
                          datatype='GPBoolean',
                          parameterType='Required',
                          direction='Input')

    p07 = arcpy.Parameter(name='in_srs',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p07.filter.type = 'ValueList'

    p08 = arcpy.Parameter(name='in_res',
                          datatype='GPDouble',
                          parameterType='Required',
                          direction='Input')

    p09 = arcpy.Parameter(name='in_max_threads',
                          datatype='GPLong',
                          parameterType='Optional',
                          direction='Input')
    p09.filter.type = 'Range'

    bbox = (-1516346, -3589160, -1514698, -3586324)
    srs = arcpy.SpatialReference(3577)

    p00.value = arcpy.Extent(*bbox, spatial_reference=srs)
    p01.value = r'C:\Users\Lewis\Desktop\arcdea\ls.nc'
    p02.value = 2008
    p03.value = 2024
    p04.value = ['Landsat 7 ETM+', 'Landsat 8 & 9 OLI']
    p05.value = ['Blue', 'Green', 'Red', 'NIR', 'SMAD']
    p06.value = True
    p07.value = 'GDA94 Australia Albers (EPSG: 3577)'
    p08.value = 30
    p09.value = None


    params = [p00, p01, p02, p03, p04, p05, p06, p07, p08, p09]

    return params

# execute(_make_test_params())  # testing, comment out when done
