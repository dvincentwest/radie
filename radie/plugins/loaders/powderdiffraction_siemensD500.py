"""define loader objects that return PowderDiffraction Data Structures"""
import re
import numpy as np
from radie.loaders import Loader, register_loaders

from radie.plugins.structures.powderdiffraction import PowderDiffraction, CuKa


def load_txt(fname):
    """
    .txt file output from Siemens D500 on custom 3M Software

    Parameters
    ----------
    fname : str
        filename

    Returns
    -------
    df_xrd : PowderDiffraction
        PowderDiffraction StructuredDataFrame based on XRD data

    """

    with open(fname, "r") as fid:
        lines = fid.readlines()

    lines = [line.strip() for line in lines]
    settings = lines.pop(0)
    mo = re.compile\
        (r'^"(?P<name>.*)",(?P<min>[0-9\.]+),(?P<max>[0-9\.]+),(?P<step>[0-9\.]+),(?P<count>[0-9\.]+).*$')
    meta = mo.match(settings).groupdict()

    for k in ['min', 'max', 'step', 'count']:
        meta[k] = float(meta[k])

    data = np.array([[float(x) for x in line.split()] for line in lines])
    df_xrd = PowderDiffraction(data=data,
                               columns=['twotheta', 'intensity'],
                               wavelength=CuKa,
                               source='CuKa',
                               xunit="deg",
                               yunit="counts",
                               **meta)

    return df_xrd


siemensD500_txt_loader = Loader(load_txt, PowderDiffraction, [".txt"], "Siemens D500")

register_loaders(
    siemensD500_txt_loader,
)
