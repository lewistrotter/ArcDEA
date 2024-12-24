
def convert_mask_algorithm(mask_algorithm: str) -> str:
    """Extract mask algorithm name, converts it to DEA band name."""

    mask_map = {
        'fMask': 'oa_fmask',
        'S2Cloudless': 'oa_s2cloudless_mask'
    }

    mask_band = mask_map[mask_algorithm]

    return mask_band
