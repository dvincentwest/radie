"""define loader objects that return PowderDiffraction Data Structures"""
import io
import math

import numpy as np
import pandas as pd

from radie import exceptions
from radie.loaders import Loader, register_loaders
from radie.plugins.structures.powderdiffraction import PowderDiffraction, CuKa, CuKa1, CuKa2


def ras_meta_value(line: bytes, return_type: type=str):
    value = line[line.find(b" "):].strip().replace(b'"', b"")
    if return_type is str:
        return value.decode("ascii")
    else:
        return return_type(value)


def asc_meta_value(line: str, return_type: type=str):
    val = line.split("=")[1].strip()
    if return_type is str:
        return val
    else:
        return return_type(val)


def load_asc(fname, name=None):
    """
    .ras file output from Rigaku XRD.  Tested with files from MiniFlex system, which seem to be bytes-like

    Parameters
    ----------
    fname : str
        filename
    name : str
        measurement identifier

    Returns
    -------
    PowderDiffraction

    """

    with open(fname, "r") as fid:
        lines = fid.readlines()

    # --- begin file check --- #
    if not all((
        lines[0].startswith("*TYPE"),
        lines[8].startswith("*GONIO"),
        lines[41].startswith("*BEGIN"),
        lines[77].startswith("*COUNT"),
    )):
        exceptions.IncorrectFileType

    wavelength1 = asc_meta_value(lines[23], float)
    wavelength2 = asc_meta_value(lines[24], float)
    if wavelength1 == 1.54059 and wavelength2 == 1.54441:
        wavelength = CuKa
    else:
        wavelength = wavelength1
    sample_name = asc_meta_value(lines[2], str)  # type: str
    start = asc_meta_value(lines[43], float)  # type: float
    stop = asc_meta_value(lines[44], float)  # type: float
    num_points = asc_meta_value(lines[77], int)  # type: int
    source = asc_meta_value(lines[23], str)  # type: str

    twotheta = np.linspace(start, stop, num_points, dtype=float)
    data_lines = int(math.ceil(num_points / 4))
    datastart = 78
    intensities = list()
    try:
        for i in range(datastart, datastart + data_lines):
            for point in map(float, lines[i].split(", ")):
                intensities.append(point)
    except Exception:
        raise exceptions.LoaderException

    return PowderDiffraction(
        data=np.array((twotheta, intensities), dtype=float).T, columns=("twotheta", "intensity"),
        name=sample_name, wavelength=wavelength, source=source
    )


def load_ras(fname, name=None):
    """
    .ras file output from Rigaku XRD.  Tested with files from MiniFlex system, which seem to be bytes-like

    Parameters
    ----------
    fname : str
        filename
    name : str
        measurement identifier

    Returns
    -------
    df_xrd : PowderDiffraction
        PowderDiffraction StructuredDataFrame based on XRD data

    """

    with open(fname, "rb") as fid:
        lines = fid.readlines()

    wavelength = None  # type: float
    wavelength1 = None  # type: float
    wavelength2 = None  # type: float
    sample_name = "xray diffaction data"
    start = None  # type: float
    stop = None  # type: float
    step = None  # type: int
    data_start = 0

    for i, line in enumerate(lines):
        if line.startswith(b"*HW_XG_WAVE_LENGTH_ALPHA1 "):
            wavelength1 = ras_meta_value(line, float)
        elif line.startswith(b"*HW_XG_WAVE_LENGTH_ALPHA2 "):
            wavelength2 = ras_meta_value(line, float)
        elif line.startswith(b"*FILE_SAMPLE "):
            sample_name = ras_meta_value(line, str)
        elif line.startswith(b"*MEAS_SCAN_STEP "):
            step = ras_meta_value(line, float)
        elif line.startswith(b"*MEAS_SCAN_START "):
            start = ras_meta_value(line, float)
        elif line.startswith(b"*MEAS_SCAN_STOP "):
            stop = ras_meta_value(line, float)
        elif line.startswith(b"*RAS_INT_START"):
            data_start = i + 1
            break

    if (
        wavelength1 is None or
        start is None or
        stop is None or
        step is None or
        data_start == 0
    ):
        raise exceptions.IncorrectFileType

    if wavelength1 == 1.540593 and wavelength2 == 1.544414:
        wavelength = CuKa
    else:
        wavelength = wavelength1

    n_points = int((stop - start) / step + 1)
    data_stop = data_start + n_points
    data_lines = [line.strip().decode("ascii") for line in lines[data_start:data_stop]]

    data = "\n".join(data_lines)

    if not name:
        name = sample_name

    data_buff = io.StringIO("twotheta intensity uncertainty\n" + data)
    df_xrd = PowderDiffraction(pd.read_csv(data_buff, sep=" "),
                               name=name,
                               wavelength=wavelength,
                               source="CuKa",
                               xunit="deg",
                               yunit="counts")

    return df_xrd


rigaku_ras_loader = Loader(load_ras, PowderDiffraction, [".ras"], "Rigaku XRD")
rigaku_asc_loader = Loader(load_asc, PowderDiffraction, [".asc"], "Rigaku XRD")

register_loaders(
    rigaku_ras_loader,
    rigaku_asc_loader,
)
