
def execute(parameters):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import xarray as xr
    import arcpy
    import cuber
    import ui

    from cuber import shared

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    ext = parameters[0].value
    out_nc = parameters[1].valueAsText
    start_date = parameters[2].value
    end_date = parameters[3].value
    assets = parameters[4].value
    quality_flags = parameters[5].value
    remove_slc_off = parameters[6].value
    remove_mask = parameters[7].value
    max_empty = parameters[8].value
    max_invalid = parameters[9].value
    out_nodata = parameters[10].value
    out_srs = parameters[11].value
    out_res = parameters[12].value
    max_threads = parameters[13].value

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region PREPARE ENVIRONMENT

    arcpy.SetProgressor('default', 'Preparing environment...')

    arcpy.env.overwriteOutput = True
    cuber.set_messenger(arcpy.AddMessage)
    arc_progress_bar = ui.make_progress_bar()

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region QUERY STAC ENDPOINT FOR FRACTIONAL COVER DATA

    arcpy.SetProgressor('default', 'Querying DEA STAC endpoint...')

    in_bbox = (ext.XMin, ext.YMin, ext.XMax, ext.YMax)
    in_epsg = ext.spatialReference.factoryCode

    out_epsg = ui.extract_epsg_code(out_srs)
    out_bbox = shared.reproject_bbox(in_bbox, in_epsg, out_epsg)

    if out_epsg == 4326:
        out_res *= 9.466833186042272E-06

    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    collection = 'ga_ls_fc_3'
    assets = ui.convert_assets('ga_ls_fc_3', assets)

    try:
        ds = cuber.fetch(
            collections=collection,
            assets=assets,
            date=(start_date, end_date),
            out_bbox=out_bbox,
            out_epsg=out_epsg,
            out_res=out_res,
            remove_slc_off=remove_slc_off,
            ignore_errors=True,  # TODO: add to ui
            full_query=True  # slc-7 off requires full metadata
        )

    except Exception as e:
        arcpy.AddError('Error occurred during DEA STAC query. See messages.')
        arcpy.AddMessage(str(e))
        return

    if ds is None or 'time' not in ds.dims:
        arcpy.AddWarning('No STAC features were found.')
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region QUERY STAC ENDPOINT FOR MASK DATA

    arcpy.SetProgressor('default', 'Querying DEA STAC endpoint...')

    # note: this will have to change if baseline ever updated
    mask_collections = [
        'ga_ls5t_ard_3',
        'ga_ls7e_ard_3',
        'ga_ls8c_ard_3',
        'ga_ls9c_ard_3'
    ]

    mask_asset = 'oa_fmask'

    try:
        ds_mask = cuber.fetch(
            collections=mask_collections,
            assets=mask_asset,
            date=(start_date, end_date),
            out_bbox=out_bbox,
            out_epsg=out_epsg,
            out_res=out_res,
            remove_slc_off=remove_slc_off,
            ignore_errors=True,  # TODO: add to ui
            full_query=False  # slc-7 off requires full metadata
        )

    except Exception as e:
        arcpy.AddError('Error occurred during DEA STAC query. See messages.')
        arcpy.AddMessage(str(e))
        return

    if ds_mask is None or 'time' not in ds_mask.dims:
        arcpy.AddWarning('No STAC features were found.')
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region REMOVE DUPLICATE DATES

    arcpy.SetProgressor('default', 'Removing duplicate dates...')

    try:
        ds = cuber.drop_duped_dates(ds)
        ds_mask = cuber.drop_duped_dates(ds_mask)

    except Exception as e:
        arcpy.AddError('Error occurred while removing duplicate dates. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region MERGING DATASETS

    arcpy.SetProgressor('default', 'Merging data...')

    try:
        ds = xr.merge([ds, ds_mask], join='left', fill_value=0)

    except Exception as e:
        arcpy.AddError('Error occurred while merging data. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region DOWNLOAD WCS MASK DATA

    arcpy.SetProgressor('step', 'Downloading mask data...', 0, 100, 1)

    try:
        with arc_progress_bar:
            ds[mask_asset].load(num_workers=max_threads)

    except Exception as e:
        arcpy.AddError('Error occurred while downloading mask data. See messages.')
        arcpy.AddMessage(str(e))
        return

    time.sleep(1)

    arcpy.ResetProgressor()

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region APPLY WCS MASK DATA

    arcpy.SetProgressor('default', 'Applying mask data...')

    quality_flags = ui.convert_mask_flags(quality_flags)

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

    arcpy.SetProgressor('step', 'Downloading valid data...', 0, 100, 1)

    try:
        with arc_progress_bar:
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

    p02 = arcpy.Parameter(name='in_start_date',
                          datatype='GPDate',
                          parameterType='Required',
                          direction='Input')

    p03 = arcpy.Parameter(name='in_end_date',
                          datatype='GPDate',
                          parameterType='Required',
                          direction='Input')

    p04 = arcpy.Parameter(name='in_assets',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input',
                          multiValue=True)
    p04.filter.type = 'ValueList'

    p05 = arcpy.Parameter(name='in_quality_flags',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input',
                          multiValue=True)
    p05.filter.type = 'ValueList'

    p06 = arcpy.Parameter(name='in_remove_slc_off',
                          datatype='GPBoolean',
                          parameterType='Required',
                          direction='Input')

    p07 = arcpy.Parameter(name='in_remove_mask',
                          datatype='GPBoolean',
                          parameterType='Required',
                          direction='Input')

    p08 = arcpy.Parameter(name='in_max_empty',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')
    p08.filter.type = 'Range'

    p09 = arcpy.Parameter(name='in_max_invalid',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')
    p09.filter.type = 'Range'

    p10 = arcpy.Parameter(name='in_nodata_value',
                          datatype='GPLong',
                          parameterType='Required',
                          direction='Input')

    p11 = arcpy.Parameter(name='in_srs',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p11.filter.type = 'ValueList'

    p12 = arcpy.Parameter(name='in_res',
                          datatype='GPDouble',
                          parameterType='Required',
                          direction='Input')

    p13 = arcpy.Parameter(name='in_max_threads',
                          datatype='GPLong',
                          parameterType='Optional',
                          direction='Input')
    p13.filter.type = 'Range'

    bbox = (-1516346, -3589160, -1514698, -3586324)
    srs = arcpy.SpatialReference(3577)

    p00.value = arcpy.Extent(*bbox, spatial_reference=srs)
    p01.value = r'C:\Users\Lewis\Desktop\arcdea\ls.nc'
    p02.value = '2020-01-01'
    p03.value = '2023-12-31'
    p04.value = ['Bare', 'Green Vegetation', 'Dead Vegetation', 'Unmixing Error']
    p05.value = ['Valid', 'Snow', 'Shadow', 'Water']
    p06.value = True
    p07.value = True
    p08.value = 10
    p09.value = 5
    p10.value = 255
    p11.value = 'GDA94 Australia Albers (EPSG: 3577)'
    p12.value = 30
    p13.value = None

    params = [p00, p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13]

    return params

# execute(_make_test_params())  # testing, comment out when done
