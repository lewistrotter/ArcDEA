
import numpy as np
import xarray as xr

from numpy.lib.stride_tricks import sliding_window_view as swv


def spike_remove_dask(
        ds: xr.Dataset,
        win_cen: int,
        spike_cutoff: int
):
    """

    :param ds:
    :param win_cen:
    :param spike_cutoff:
    :return:
    """

    # fast but memory eaten quickly

    # FIXME: this is memory heavy - ufunc likely safer (but twice as slow)

    try:
        da = ds.to_array('variables')

        # wrap array around both sides, build roll window, trim extra nan slices
        da_ext = da.pad(time=win_cen, mode='wrap')
        da_win = da_ext.rolling(time=2 * win_cen + 1, center=True).construct('win')
        da_win = da_win[:, win_cen:-win_cen]

        # get median and user std of each time series per pixel
        da_std = da.std('time', skipna=True) * spike_cutoff
        da_med = np.abs(da - da_win.median('win', skipna=True))

        # get avg and max of each immediate neighbour per window
        lr = [win_cen - 1, win_cen + 1]
        da_avg = da_win[:, :, :, :, lr].mean('win', skipna=True) - da_std
        da_max = da_win[:, :, :, :, lr].max('win', skipna=True) + da_std

        # build error mask and apply
        da_err = (da_med >= da_std) & ((da < da_avg) | (da > da_max))
        da = da.where(~da_err)

        # convert back to dataset
        ds = da.where(~da_err).to_dataset(dim='variables')

        # rechunk to avoid multiple time dim error
        ds = ds.chunk({'time': -1})  # re-chunk to avoid multiple chunk error

    except Exception as e:
        raise e

    return ds


def spike_remove_ufunc(
        ds: xr.Dataset,
        win_cen: int,
        spike_cutoff: int
):
    # slow but memory not an issue

    #da = ds['nbart_red']  # TODO: handle multi bands

    ds = xr.apply_ufunc(_spike_remove_vector,
                        ds,
                        input_core_dims=[['time']],
                        output_core_dims=[['time']],
                        vectorize=True,
                        dask='parallelized',
                        kwargs={'spike_cutoff': spike_cutoff, 'win_cen': win_cen})

    return ds


def _spike_remove_vector(
        x: np.ndarray,
        win_cen: int,
        spike_cutoff: int
):
    if ~np.all(np.isnan(x)):
        return x

    cut = np.nanstd(x) * spike_cutoff

    wins = swv(x=np.concatenate((x[-win_cen:], x, x[:win_cen])),
               window_shape=2 * win_cen + 1)

    meds = np.abs(x - np.nanmedian(wins, 1))

    avgs = np.nanmean(wins[:, [win_cen - 1, win_cen + 1]], 1) - cut
    maxs = np.nanmax(wins[:, [win_cen - 1, win_cen + 1]], 1) + cut

    errs = (meds >= cut) & ((x < avgs) | (x > maxs))
    x = np.where(~errs, x, np.nan)

    return x