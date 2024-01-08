
import numpy as np
import xarray as xr


def ndvi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        red = 'nbart_red'
        nir = 'nbart_nir'
    elif collection == 's2':
        red = 'nbart_red'
        nir = 'nbart_nir_1'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    # check bands exist
    for band in [red, nir]:
        if band not in ds:
            raise ValueError(f'Band: {band} not in NetCDF.')

    try:
        # calc index, citation rouse (1973)
        ds['ndvi'] = ((ds[nir] - ds[red]) /
                      (ds[nir] + ds[red]))

    except Exception as e:
        raise e

    return ds


def evi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        blue = 'nbart_blue'
        red = 'nbart_red'
        nir = 'nbart_nir'
    elif collection == 's2':
        blue = 'nbart_blue'
        red = 'nbart_red'
        nir = 'nbart_nir_1'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    # check bands exist
    for band in [blue, red, nir]:
        if band not in ds:
            raise ValueError(f'Band: {band} not in NetCDF.')

    try:
        # normalise values 0-10000 to 0-1
        ds = ds / 10000.0

        # calc index, citation huete (2002)
        ds['evi'] = ((2.5 * (ds[nir] - ds[red])) /
                     (ds[nir] + 6 * ds[red] - 7.5 * ds[blue] + 1))

    except Exception as e:
        raise e

    return ds


def lai(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        blue = 'nbart_blue'
        red = 'nbart_red'
        nir = 'nbart_nir'
    elif collection == 's2':
        blue = 'nbart_blue'
        red = 'nbart_red'
        nir = 'nbart_nir_1'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    # check bands exist
    for band in [blue, red, nir]:
        if band not in ds:
            raise ValueError(f'Band: {band} not in NetCDF.')

    try:
        # normalise values 0-10000 to 0-1
        ds = ds / 10000.0

        # calc index, citation boegh (2002)
        ds['lai'] = (3.618 * ((2.5 * (ds[nir] - ds[red])) /
                              (ds[nir] + 6 * ds[red] - 7.5 *
                               ds[blue] + 1)) - 0.118)

    except Exception as e:
        raise e

    return ds


def mavi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        red = 'nbart_red'
        nir = 'nbart_nir'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        red = 'nbart_red'
        nir = 'nbart_nir_1'
        swir_1 = 'nbart_swir_2'

    else:
        raise ValueError(f'Collection: {collection} not supported.')

    # check bands exist
    for band in [red, nir, swir_1]:
        if band not in ds:
            raise ValueError(f'Band: {band} not in NetCDF.')

    try:
        # calc index, citation zhu et al. (2014)
        ds['mavi'] = ((ds[nir] - ds[red]) /
                      (ds[nir] + ds[red] + ds[swir_1]))

    except Exception as e:
        raise e

    return ds


# savi


def msavi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        red = 'nbart_red'
        nir = 'nbart_nir'
    elif collection == 's2':
        red = 'nbart_red'
        nir = 'nbart_nir_1'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    # check bands exist
    for band in [red, nir]:
        if band not in ds:
            raise ValueError(f'Band: {band} not in NetCDF.')

    try:
        # normalise values 0-10000 to 0-1
        ds = ds / 10000.0

        # calc index, citation qi et al. (1994)
        ds['msavi'] = ((2 * ds[nir] + 1 -
                      ((2 * ds[nir] + 1) ** 2 -
                       8 * (ds[nir] - ds[red])) ** 0.5) / 2)

    except Exception as e:
        raise e

    return ds


def ndci(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        raise ValueError('NDCI does not support Landsat.')
    elif collection == 's2':
        red = 'nbart_red'
        redge_1 = 'nbart_red_edge_1'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    # check bands exist
    for band in [red, redge_1]:
        if band not in ds:
            raise ValueError(f'Band: {band} not in NetCDF.')

    try:
        # calc index, citation mishra & mishra (2012)
        ds['ndci'] = ((ds[redge_1] - ds[red]) /
                      (ds[redge_1] + ds[red]))

    except Exception as e:
        raise e

    return ds


def kndvi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        red = 'nbart_red'
        nir = 'nbart_nir'
    elif collection == 's2':
        red = 'nbart_red'
        nir = 'nbart_nir_1'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    # check bands exist
    for band in [red, nir]:
        if band not in ds:
            raise ValueError(f'Band: {band} not in NetCDF.')

    try:
        # calc index, citation camps-Valls et al. (2021)
        ds['kndvi'] = np.tanh(((ds[nir] - ds[red]) /
                               (ds[nir] + ds[red])) ** 2)

    except Exception as e:
        raise e

    return ds


def ndmi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        nir = 'nbart_nir'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        nir = 'nbart_nir_1'
        swir_1 = 'nbart_swir_2'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation gao (1996)
        ds['ndmi'] = ((ds[nir] - ds[swir_1]) /
                      (ds[nir] + ds[swir_1]))

    except Exception as e:
        raise e

    return ds


def ndwi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        green = 'nbart_green'
        nir = 'nbart_nir'
    elif collection == 's2':
        green = 'nbart_green'
        nir = 'nbart_nir_1'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation mcfeeters (1996)
        ds['ndwi'] = ((ds[green] - ds[nir]) /
                      (ds[green] + ds[nir]))

    except Exception as e:
        raise e

    return ds


def mndwi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        green = 'nbart_green'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        green = 'nbart_green'
        swir_1 = 'nbart_swir_2'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation xu (2006)
        ds['mndwi'] = ((ds[green] - ds[swir_1]) /
                       (ds[green] + ds[swir_1]))

    except Exception as e:
        raise e

    return ds


def wi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        green = 'nbart_green'
        red = 'nbart_red'
        nir = 'nbart_nir'
        swir_1 = 'nbart_swir_1'
        swir_2 = 'nbart_swir_2'
    elif collection == 's2':
        green = 'nbart_green'
        red = 'nbart_red'
        nir = 'nbart_nir_1'
        swir_1 = 'nbart_swir_2'
        swir_2 = 'nbart_swir_3'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    # check bands exist
    for band in [green, red, nir, swir_1, swir_2]:
        if band not in ds:
            raise ValueError(f'Band: {band} not in NetCDF.')

    try:
        # normalise values 0-10000 to 0-1
        ds = ds / 10000.0

        # calc index, citation fisher (2016)
        ds['wi'] = (1.7204 + 171 * ds[green] + 3 * ds[red] -
                    70 * ds[nir] - 45 * ds[swir_1] -
                    71 * ds[swir_2])

    except Exception as e:
        raise e

    return ds


def bai(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        red = 'nbart_red'
        nir = 'nbart_nir'
    elif collection == 's2':
        red = 'nbart_red'
        nir = 'nbart_nir_1'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # normalise values 0-10000 to 0-1
        ds = ds / 10000.0

        # calc index, citation martin (1998)
        ds['bai'] = (1.0 / ((0.10 - ds[red]) ** 2 +
                            (0.06 - ds[nir]) ** 2))

    except Exception as e:
        raise e

    return ds


def nbr(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        nir = 'nbart_nir'
        swir_2 = 'nbart_swir_2'
    elif collection == 's2':
        nir = 'nbart_nir_1'
        swir_2 = 'nbart_swir_3'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation lopez garcia (1991)
        ds['nbr'] = ((ds[nir] - ds[swir_2]) /
                     (ds[nir] + ds[swir_2]))

    except Exception as e:
        raise e

    return ds


def ndbi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        nir = 'nbart_nir'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        nir = 'nbart_nir_1'
        swir_1 = 'nbart_swir_2'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation zha (2003)
        ds['ndbi'] = ((ds[swir_1] - ds[nir]) /
                      (ds[swir_1] + ds[nir]))

    except Exception as e:
        raise e

    return ds


def bui(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        red = 'nbart_red'
        nir = 'nbart_nir'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        red = 'nbart_red'
        nir = 'nbart_nir_1'
        swir_1 = 'nbart_swir_2'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation he (2010)
        ds['bui'] = (((ds[swir_1] - ds[nir]) /
                      (ds[swir_1] + ds[nir])) -
                     ((ds[nir] - ds[red]) /
                      (ds[nir] + ds[red])))

    except Exception as e:
        raise e

    return ds


def baei(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        red = 'nbart_red'
        green = 'nbart_green'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        red = 'nbart_red'
        green = 'nbart_green'
        swir_1 = 'nbart_swir_2'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # normalise values 0-10000 to 0-1
        ds = ds / 10000.0

        # calc index, citation bouzekri et al. (2015)
        ds['baei'] = ((ds[red] + 0.3) /
                      (ds[green] + ds[swir_1]))

    except Exception as e:
        raise e

    return ds


def nbi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        red = 'nbart_red'
        nir = 'nbart_nir'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        red = 'nbart_red'
        nir = 'nbart_nir_1'
        swir_1 = 'nbart_swir_2'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation jieli et al. (2010)
        ds['nbi'] = (ds[swir_1] + ds[red]) / ds[nir]

    except Exception as e:
        raise e

    return ds


def bsi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        blue = 'nbart_blue'
        red = 'nbart_red'
        nir = 'nbart_nir'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        blue = 'nbart_blue'
        red = 'nbart_red'
        nir = 'nbart_nir_1'
        swir_1 = 'nbart_swir_2'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation rikimaru et al. (2002)
        ds['bsi'] = (((ds[swir_1] + ds[red]) -
                      (ds[nir] + ds[blue])) /
                     ((ds[swir_1] + ds[red]) +
                      (ds[nir] + ds[blue])))

    except Exception as e:
        raise e

    return ds


def cmr(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        swir_1 = 'nbart_swir_1'
        swir_2 = 'nbart_swir_2'
    elif collection == 's2':
        swir_1 = 'nbart_swir_2'
        swir_2 = 'nbart_swir_3'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation drury (1987)
        ds['cmr'] = (ds[swir_1] / ds[swir_2])

    except Exception as e:
        raise e

    return ds


def fmr(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection == 'ls':
        nir = 'nbart_nir'
        swir_1 = 'nbart_swir_1'
    elif collection == 's2':
        nir = 'nbart_nir_1'
        swir_1 = 'nbart_swir_2'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation segal (1982)
        ds['fmr'] = (ds[swir_1] / ds[nir])

    except Exception as e:
        raise e

    return ds


def ior(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # prepare relevant bands
    if collection in ['ls', 's2']:
        blue = 'nbart_blue'
        red = 'nbart_red'
    else:
        raise ValueError(f'Collection: {collection} not supported.')

    try:
        # calc index, citation segal (1982)
        ds['ior'] = (ds[red] / ds[blue])

    except Exception as e:
        raise e

    return ds


def calc_index(
        ds: xr.Dataset,
        index_type: str,
        index_name: str,
        collection: str
) -> xr.Dataset:
    """
    Calculate one of many indices.

    :param ds: Xarray Dataset.
    :param index_type: Type of index (e.g., Vegetation, Water).
    :param index_name: Name of index (as abbreviation).
    :param collection: Name of satellite collection (either ls or s2).
    :return: Xarray Dataset with index as new variable.
    """

    if index_type == 'Vegetation':
        if index_name.startswith('NDVI:'):
            ds = ndvi(ds=ds, collection=collection)
        elif index_name.startswith('EVI:'):
            ds = evi(ds=ds, collection=collection)
        elif index_name.startswith('LAI:'):
            ds = lai(ds=ds, collection=collection)
        elif index_name.startswith('MAVI:'):
            ds = mavi(ds=ds, collection=collection)
        # savi
        elif index_name.startswith('MSAVI:'):
            ds = msavi(ds=ds, collection=collection)
        elif index_name.startswith('NDCI:'):
            ds = ndci(ds=ds, collection=collection)
        elif index_name.startswith('kNDVI:'):
            ds = kndvi(ds=ds, collection=collection)
        else:
            raise AttributeError('Vegetation index does not exist.')

    elif index_type == 'Water':
        if index_name.startswith('NDMI:'):
            ds = ndmi(ds=ds, collection=collection)
        elif index_name.startswith('NDWI:'):
            ds = ndwi(ds=ds, collection=collection)
        elif index_name.startswith('MNDWI:'):
            ds = mndwi(ds=ds, collection=collection)
        elif index_name.startswith('WI:'):
            ds = wi(ds=ds, collection=collection)
        else:
            raise AttributeError('Water index does not exist.')

    elif index_type == 'Fire':
        if index_name.startswith('BAI:'):
            ds = bai(ds=ds, collection=collection)
        elif index_name.startswith('NBR:'):
            ds = nbr(ds=ds, collection=collection)
        else:
            raise AttributeError('Fire index does not exist.')

    elif index_type == 'Urban':
        if index_name.startswith('NDBI:'):
            ds = ndbi(ds=ds, collection=collection)
        elif index_name.startswith('BUI:'):
            ds = bui(ds=ds, collection=collection)
        elif index_name.startswith('BAEI:'):
            ds = baei(ds=ds, collection=collection)
        elif index_name.startswith('NBI:'):
            ds = nbi(ds=ds, collection=collection)
        elif index_name.startswith('BSI:'):
            ds = bsi(ds=ds, collection=collection)
        else:
            raise AttributeError('Urban index does not exist.')

    elif index_type == 'Minerals':
        if index_name.startswith('CMR:'):
            ds = cmr(ds=ds, collection=collection)
        elif index_name.startswith('FMR:'):
            ds = fmr(ds=ds, collection=collection)
        elif index_name.startswith('IOR:'):
            ds = ior(ds=ds, collection=collection)
        else:
            raise AttributeError('Mineral index does not exist.')

    return ds
