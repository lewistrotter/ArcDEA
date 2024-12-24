
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
    start_date = parameters[2].value
    end_date = parameters[3].value
    collections = parameters[4].value
    assets = parameters[5].value
    mask_algorithm = parameters[6].value
    quality_flags = parameters[7].value
    remove_mask = parameters[8].value
    max_empty = parameters[9].value
    max_invalid = parameters[10].value
    out_nodata = parameters[11].value
    out_srs = parameters[12].value
    out_res = parameters[13].value
    max_threads = parameters[14].value

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

    if out_epsg == 4326:
        out_res *= 9.466833186042272E-06

    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    collections = ui.convert_collections('ga_s2_ard_3', collections)
    assets = ui.convert_assets('ga_s2_ard_3', assets)

    mask_asset = ui.convert_mask_algorithm(mask_algorithm)
    assets += [mask_asset]

    try:
        ds = cuber.fetch(
            collections=collections,
            assets=assets,
            date=(start_date, end_date),
            out_bbox=out_bbox,
            out_epsg=out_epsg,
            out_res=out_res,
            remove_slc_off=False,  # irrelevant for s2
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
    # region REMOVE DUPLICATE DATES

    arcpy.SetProgressor('default', 'Removing duplicate dates...')

    try:
        ds = cuber.drop_duped_dates(ds)

    except Exception as e:
        arcpy.AddError('Error occurred while removing duplicate dates. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region DOWNLOAD WCS MASK DATA

    n_dls = len(ds['time'])
    arcpy.SetProgressor('step', 'Downloading mask data...', 0, n_dls, 1)

    try:
        with ArcProgressBar():
            ds[mask_asset].load(num_workers=max_threads)

    except Exception as e:
        arcpy.AddError('Error occurred while downloading mask data. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region APPLY WCS MASK DATA

    arcpy.SetProgressor('default', 'Applying mask data...')

    quality_flags = ui.convert_mask_flags(quality_flags)  # handles fmask and s2c

    try:
        ds = cuber.apply_mask(ds=ds,
                              mask_asset=mask_asset,
                              max_empty=max_empty,
                              mask_flags=quality_flags,
                              max_invalid=max_invalid,
                              mask_pixels=True,  # TODO: maybe allow user to set in UI
                              nodata=out_nodata,
                              drop_mask_asset=remove_mask)

        if mask_asset in list(ds.data_vars):
            ds = ds.rename({mask_asset: 'mask'})  # makes life easier later

    except Exception as e:
        arcpy.AddError('Error occurred while applying mask data. See messages.')
        arcpy.AddMessage(str(e))
        return

    if 'time' not in ds.dims or len(ds['time']) == 0:
        arcpy.AddWarning('No valid downloads were found.')
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
    # region CONFORM DATATYPES

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

    p02 = arcpy.Parameter(name='in_start_date',
                          datatype='GPDate',
                          parameterType='Required',
                          direction='Input')

    p03 = arcpy.Parameter(name='in_end_date',
                          datatype='GPDate',
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

    p06 = arcpy.Parameter(name='in_mask_algorithm',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p06.filter.type = 'ValueList'

    p07 = arcpy.Parameter(name='in_quality_flags',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input',
                          multiValue=True)
    p07.filter.type = 'ValueList'

    p08 = arcpy.Parameter(name='in_remove_mask',
                          datatype='GPBoolean',
                          parameterType='Required',
                          direction='Input')

    p09 = arcpy.Parameter(name='in_max_empty',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')
    p09.filter.type = 'Range'

    p10 = arcpy.Parameter(name='in_max_invalid',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')
    p10.filter.type = 'Range'

    p11 = arcpy.Parameter(name='in_nodata_value',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')

    p12 = arcpy.Parameter(name='in_srs',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p12.filter.type = 'ValueList'

    p13 = arcpy.Parameter(name='in_res',
                          datatype='GPDouble',
                          parameterType='Required',
                          direction='Input')

    p14 = arcpy.Parameter(name='in_max_threads',
                          datatype='GPLong',
                          parameterType='Optional',
                          direction='Input')
    p14.filter.type = 'Range'

    bbox = (-1516346, -3589160, -1514698, -3586324)
    srs = arcpy.SpatialReference(3577)

    p00.value = arcpy.Extent(*bbox, spatial_reference=srs)
    p01.value = r'C:\Users\Lewis\Desktop\arcdea\s2.nc'
    p02.value = '2020-01-01'
    p03.value = '2023-12-31'
    p04.value = ['Sentinel 2A', 'Sentinel 2B']
    p05.value = ['Blue', 'Green', 'Red', 'NIR 1']
    p06.value = 'S2Cloudless' #'fMask'
    p07.value = ['Valid'] #['Valid', 'Snow', 'Shadow', 'Water']
    p08.value = True
    p09.value = 10
    p10.value = 5
    p11.value = -999
    p12.value = 'GDA94 Australia Albers (EPSG: 3577)'
    p13.value = 10
    p14.value = None

    params = [p00, p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14]

    return params

# execute(_make_test_params())  # testing, comment out when done
