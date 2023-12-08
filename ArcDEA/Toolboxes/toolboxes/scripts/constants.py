
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

GEOMED_COLLECTIONS = {
    'Landsat 5 TM':   'ga_ls5t_nbart_gm_cyear_3',
    'Landsat 7 ETM+': 'ga_ls7e_nbart_gm_cyear_3',
    'Landsat 8 OLI':  'ga_ls8c_nbart_gm_cyear_3'
}

GEOMED_BAND_ASSETS = {
    'Blue':   'blue',
    'Green':  'green',
    'Red':    'red',
    'NIR':    'nir',
    'SWIR 1': 'swir1',
    'SWIR 2': 'swir2',
    'EMAD':   'edev',
    'SMAD':   'sdev',
    'BCMAD':  'bcdev'
}

MASK_BAND_ASSETS = {
    'fMask': 'oa_fmask',
    'S2Cloudless': 'oa_s2cloudless_mask'
}

QUALITY_FMASK_FLAGS = {
    'Valid':  1,
    'Cloud':  2,
    'Shadow': 3,
    'Snow':   4,
    'Water':  5
}

QUALITY_S2CLOUDLESS_FLAGS = {
    'Valid': 1,
    'Invalid': 2
}
