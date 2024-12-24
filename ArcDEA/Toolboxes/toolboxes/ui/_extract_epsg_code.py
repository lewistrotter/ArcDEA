
def extract_epsg_code(srs: str) -> int:
    """Extract EPSG code from a full spatial reference label."""

    srs = srs.split(':')[1]
    srs = srs.replace(')', '')
    srs = srs.strip()
    srs = int(srs)

    return srs
