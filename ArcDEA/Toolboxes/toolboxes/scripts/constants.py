
BASELINE_COLLECTIONS = {
    'Landsat 5 TM':    'ga_ls5t_ard_3',
    'Landsat 7 ETM+':  'ga_ls7e_ard_3',
    'Landsat 8 OLI':   'ga_ls8c_ard_3',
    'Landsat 9 OLI-2': 'ga_ls9c_ard_3',
    'Sentinel 2A':     'ga_s2am_ard_3',
    'Sentinel 2B':     'ga_s2bm_ard_3'
}

BASELINE_BAND_ASSETS = {
    'Blue':       'nbart_blue',
    'Green':      'nbart_green',
    'Red':        'nbart_red',
    'Red Edge 1': 'nbart_red_edge_1',
    'Red Edge 2': 'nbart_red_edge_2',
    'Red Edge 3': 'nbart_red_edge_3',
    'NIR':        'nbart_nir',
    'NIR 1':      'nbart_nir_1',
    'NIR 2':      'nbart_nir_2',
    'SWIR 1':     'nbart_swir_1',
    'SWIR 2':     'nbart_swir_2',
    'SWIR 3':     'nbart_swir_3'
}

BASELINE_INDEX_ASSETS = {
    'NDVI':  ['nbart_red', 'nbart_nir']  # TODO: landsat and sentinel differences needed
}

QUALITY_FLAGS = {
    'Valid':  1,
    'Cloud':  2,
    'Shadow': 3,
    'Snow':   4,
    'Water':  5
}

RASTER_EXTENSIONS = {
    'TIFF':   '.tif',
    'PNG':    '.png',
    'NETCDF': '.nc'
}