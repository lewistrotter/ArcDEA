
def convert_mask_flags(vt) -> list:
    """
    Takes a ValueTable object of full Landsat band qa flag names
    and converts them into a list of backend qa flag names.
    Parameter "vt" is a value table.
    """

    flags_map = {
        'Valid': 1,
        'Cloud': 2,
        'Shadow': 3,
        'Snow': 4,
        'Water': 5
    }

    flags = []
    for i in range(vt.rowCount):
        flag = vt.getValue(i, 0)
        flag = flags_map[flag]
        flags.append(flag)

    return flags