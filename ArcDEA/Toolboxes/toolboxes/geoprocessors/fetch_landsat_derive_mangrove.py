
def execute(parameters):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region IMPORTS

    import time
    import arcpy
    import cuber
    import ui

    from cuber import shared

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region EXTRACT PARAMETERS

    ext = parameters[0].value
    out_nc = parameters[1].valueAsText
    start_year = parameters[2].valueAsText
    end_year = parameters[3].valueAsText
    out_srs = parameters[4].value
    out_res = parameters[5].value
    max_threads = parameters[6].value

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
    # region QUERY STAC ENDPOINT

    arcpy.SetProgressor('default', 'Querying DEA STAC endpoint...')

    in_bbox = (ext.XMin, ext.YMin, ext.XMax, ext.YMax)
    in_epsg = ext.spatialReference.factoryCode

    out_epsg = ui.extract_epsg_code(out_srs)
    out_bbox = shared.reproject_bbox(in_bbox, in_epsg, out_epsg)

    if out_epsg == 4326:
        out_res *= 9.466833186042272E-06

    start_date = f'{start_year}-01-01'
    end_date = f'{end_year}-12-31'

    collection = 'ga_ls_mangrove_cover_cyear_3'
    asset = 'canopy_cover_class'

    try:
        ds = cuber.fetch(
            collections=collection,
            assets=asset,
            date=(start_date, end_date),
            out_bbox=out_bbox,
            out_epsg=out_epsg,
            out_res=out_res,
            remove_slc_off=False,
            ignore_errors=True  # TODO: add to ui
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

    # arcpy.SetProgressor('default', 'Conforming data types...')
    #
    # try:
    #     ds = shared.elevate_xr_dtypes(ds)
    #
    # except Exception as e:
    #     arcpy.AddError('Error occurred while conforming data types. See messages.')
    #     arcpy.AddMessage(str(e))
    #     return
    #
    # time.sleep(1)

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

    p04 = arcpy.Parameter(name='in_srs',
                          datatype='GPString',
                          parameterType='Required',
                          direction='Input')
    p04.filter.type = 'ValueList'

    p05 = arcpy.Parameter(name='in_res',
                          datatype='GPDouble',
                          parameterType='Required',
                          direction='Input')

    p06 = arcpy.Parameter(name='in_max_threads',
                          datatype='GPLong',
                          parameterType='Optional',
                          direction='Input')
    p06.filter.type = 'Range'

    bbox = (-1675237, -3234559, -1666622, -3244647)
    srs = arcpy.SpatialReference(3577)

    p00.value = arcpy.Extent(*bbox, spatial_reference=srs)
    p01.value = r'C:\Users\Lewis\Desktop\arcdea\ls.nc'
    p02.value = 2008
    p03.value = 2024
    p04.value = 'GDA94 Australia Albers (EPSG: 3577)'
    p05.value = 30
    p06.value = None


    params = [p00, p01, p02, p03, p04, p05, p06]

    return params

execute(_make_test_params())  # testing, comment out when done
