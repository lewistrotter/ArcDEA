# imports
import xarray as xr

def get_xr_collection(ds: xr.Dataset) -> str:
    """Determines DEA collection from an Xarray Dataset."""

    collections = ds.attrs.get('collection')

    if collections is None:
        raise AttributeError('DEA collection must be defined')

    # cast to list if not already
    if isinstance(collections, str):
        collections = [collections]

    for collection in collections:
        if 'ga_ls' in collection:
            return 'ga_ls'
        elif 'ga_s2' in collection:
            return 'ga_s2'

    raise AttributeError('DEA Collection not recognised.')

    return
