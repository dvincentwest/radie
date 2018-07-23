"""a little module for handling colors and color generators"""

_mpl_hex_colors = ['1f77b4', 'ff7f0e', '2ca02c', 'd62728', '9467bd', '8c564b', 'e377c2', '7f7f7f', 'bcbd22', '17becf']


def colors(color_list=_mpl_hex_colors):
    """
    a simple generator to get the next color in the list

    Parameters
    ----------
    color_list : list
        a list of colors, usually hex strings, or other valid pyqgtraph Pen color specifiers

    Returns
    -------
    color : str
        returns whatever type of item in the list is

    """
    count = 0
    num = len(color_list)
    while True:
        yield color_list[count % num]
        count += 1
