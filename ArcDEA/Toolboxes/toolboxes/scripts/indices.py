
import xarray as xr


def ndvi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # find correct band names
    if collection == 'ls':
        red = 'nbart_red'
        nir = 'nbart_nir'
    elif collection == 's2':
        red = 'nbart_red'
        nir = 'nbart_nir_1'

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


def ndwi(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:
    # find correct band names
    if collection == 'ls':
        green = 'nbart_green'
        nir = 'nbart_nir'
    elif collection == 's2':
        green = 'nbart_green'
        nir = 'nbart_nir_1'

    try:
        # calc index, citation mcfeeters (1996)
        ds['ndwi'] = ((ds[green] - ds[nir]) /
                      (ds[green] + ds[nir]))

    except Exception as e:
        raise e

    return ds


def cmr(
        ds: xr.Dataset,
        collection: str
) -> xr.Dataset:

    # find correct band names
    if collection == 'ls':
        swir_1 = 'nbart_swir_1'
        swir_2 = 'nbart_swir_2'
    elif collection == 's2':
        swir_1 = 'nbart_swir_2'
        swir_2 = 'nbart_swir_3'

    try:
        # calc index, citation drury (1987)
        ds['cmr'] = (ds[swir_1] / ds[swir_2])

    except Exception as e:
        raise e

    return ds
