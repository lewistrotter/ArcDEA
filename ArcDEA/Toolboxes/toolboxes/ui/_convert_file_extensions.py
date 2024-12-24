
def convert_file_extensions(extension: str) -> str:
    """Extract file extension name, converts it to GDAL name."""

    extension_map = {
        'BMP': 'bmp',
        'IMG': 'img',
        'JP2': 'jp2',
        'JPG': 'jpg',
        'PNG': 'png',
        'TIFF': 'tif'
    }

    extension = extension_map[extension]

    return extension
