
def convert_assets(collection: str, vt) -> list:
    """
    Takes a broad DEA collection name and a ValueTable object from the
    ArcGIS Pro UI and gets the backend DEA asset names. Parameter
    "vt" is a value table.
    """

    if collection == 'ga_ls_ard_3':
        assets_map = {
            'Blue':   'nbart_blue',
            'Green':  'nbart_green',
            'Red':    'nbart_red',
            'NIR':    'nbart_nir',
            'SWIR 1': 'nbart_swir_1',
            'SWIR 2': 'nbart_swir_2'
        }

    elif collection == 'ga_s2_ard_3':
        assets_map = {
            'Blue':       'nbart_blue',
            'Green':      'nbart_green',
            'Red':        'nbart_red',
            'Red Edge 1': 'nbart_red_edge_1',
            'Red Edge 2': 'nbart_red_edge_2',
            'Red Edge 3': 'nbart_red_edge_3',
            'NIR 1':      'nbart_nir_1',
            'NIR 2':      'nbart_nir_2',
            'SWIR 2':     'nbart_swir_2',
            'SWIR 3':     'nbart_swir_3'
        }

    elif collection == 'ga_ls_gm_ard_3':
        assets_map = {
            'Blue':   'nbart_blue',
            'Green':  'nbart_green',
            'Red':    'nbart_red',
            'NIR':    'nbart_nir',
            'SWIR 1': 'nbart_swir_1',
            'SWIR 2': 'nbart_swir_2',
            'EMAD':   'edev',
            'SMAD':   'sdev',
            'BCMAD':  'bcdev',
            'Count':  'count'
        }

    elif collection == 'ga_ls_fc_3':
        assets_map = {
            'Bare':             'bs',
            'Green Vegetation': 'pv',
            'Dead Vegetation':  'npv',
            'Unmixing Error':   'ue'
        }

    else:
        raise ValueError('Invalid collection name.')

    assets = []
    for i in range(vt.rowCount):
        asset = vt.getValue(i, 0)
        asset = assets_map[asset]
        assets.append(asset)

    return assets
