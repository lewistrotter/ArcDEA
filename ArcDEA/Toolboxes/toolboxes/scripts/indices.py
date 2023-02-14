
import numpy as np


def ndvi(
        red: np.ndarray,
        nir: np.ndarray
) -> np.ndarray:
    """

    :param red:
    :param nir:
    :return:
    """

    arr = (nir - red) / (nir + red)

    return arr






def calc_index_from_array(
        arr: np.ndarray,
        index: str
) -> np.ndarray:
    """

    :param arr:
    :param index:
    :return:
    """

    arr_idx = None

    if index == 'NDVI':
        red = arr[0].astype('float32')
        nir = arr[1].astype('float32')
        arr_idx = ndvi(red, nir)

    elif index == 'SAVI':
        ...

    else:
        raise NotImplemented

    return arr_idx
