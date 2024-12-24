
# imports
import arcpy

def print_dates(ds) -> None:
    """Provide dates of successful downloads to user."""

    dts = ds['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    dts = dts.to_numpy()

    for dt in dts:
        arcpy.AddMessage(f'Successfully downloaded: {dt}.')

    return
