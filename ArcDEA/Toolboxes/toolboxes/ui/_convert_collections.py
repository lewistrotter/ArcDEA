
def convert_collections(collection: str, vt) -> list:
    """
    Takes a broad DEA collection name and a ValueTable object from the
    ArcGIS Pro UI and gets the backend DEA collection names. Parameter
    "vt" is a value table.
    """

    if collection == 'ga_ls_ard_3':
        collections_map = {
            'Landsat 5 TM':    'ga_ls5t_ard_3',
            'Landsat 7 ETM+':  'ga_ls7e_ard_3',
            'Landsat 8 OLI':   'ga_ls8c_ard_3',
            'Landsat 9 OLI-2': 'ga_ls9c_ard_3',
        }

    elif collection == 'ga_s2_ard_3':
        collections_map = {
            'Sentinel 2A': 'ga_s2am_ard_3',
            'Sentinel 2B': 'ga_s2bm_ard_3'
        }

    elif collection == 'ga_ls_gm_ard_3':
        collections_map = {
            'Landsat 5 TM':      'ga_ls5t_gm_cyear_3',
            'Landsat 7 ETM+':    'ga_ls7e_gm_cyear_3',
            'Landsat 8 & 9 OLI': 'ga_ls8cls9c_gm_cyear_3'
        }

    else:
        raise ValueError('Invalid collection name.')

    collections = []
    for i in range(vt.rowCount):
        collection = vt.getValue(i, 0)
        collection = collections_map[collection]
        collections.append(collection)

    return collections
