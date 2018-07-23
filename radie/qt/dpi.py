"""A convenience module for getting dimensions in the context of the dpi of the monitor"""

from . import cfg


def scaling(dpi=None):
    """
    get the scaling factor based on the dpi of the current screen

    Parameters
    ----------
    dpi : int or float

    Returns
    -------
    float

    """
    if dpi:
        return dpi / cfg.dpi_100percent
    else:
        return cfg.dpi_scaling


def length(pixels, dpi=None):
    return int(pixels * scaling(dpi))


def width_by_height(w, h, dpi=None):
    scale = scaling(dpi)
    return int(w * scale), int(h * scale)
