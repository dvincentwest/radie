"""Define loader objects for gsas-type files"""

import io
import os
import sys
import traceback

import numpy as np
import pandas as pd

from radie import exceptions
from radie import loaders
from radie.plugins.structures import powderdiffraction


def parse_gsas_header(fid):
    """a couple of files have the same header structure, so let's read them in one place

    Parameters
    ----------
    fid : io.TextIOBase

    Returns
    -------
    header : dict
    wavelength : float
    data_start_line : int
    bank_line : str

    """

    fid.seek(0)
    headers = dict()
    bank_line = None
    first_data_line = None

    try:
        fid.readline()
    except UnicodeDecodeError:
        raise exceptions.IncorrectFileType

    for i, line in enumerate(fid):
        if line.startswith("#"):
            meta_pair = [value.strip() for value in line[1:].strip().split('=')]
            if len(meta_pair) == 2:
                headers[meta_pair[0]] = meta_pair[1]
        elif line.startswith("BANK"):
            bank_line = line
            first_data_line = i + 2
            break
        else:
            raise exceptions.IncorrectFileType("unrecognized header structure for .fxye files")

    try:
        wavelength = float(headers["Calibrated wavelength"])
    except KeyError:
        raise exceptions.IncorrectFileType("could not find the wavelength")

    return headers, wavelength, first_data_line, bank_line


def load_fxye(fname):
    """.fxye is an Argonne National Labs made file format for powder diffraction that is GSAS compatible

    A more natural csv-type datastructure, as opposed to a GSAS raw file.  Three Columns of data are provided, twotheta
    (in centidegrees), intensity and uncertainty

    Parameters
    ----------
    fname : str
        filename

    Returns
    -------
    powderdiffraction.PowderDiffraction

    Notes
    -----
    from the `11-BM file formats`_ page:

    GSAS supports many formats for powder diffraction data input. The .fxye format for GSAS has an intial header line
    followed by a variable number of comment lines (prefixed by a # character), then an addtional header line. The data
    are listed next in three columns: 1st column is 2θ position (in centidegrees, i.e. degrees × 100), 2nd is intensity,
    and 3rd is standard uncertainty for the intensity values (esd). This format may not be supported by all software
    that claims to read GSAS input files (see GSAS .raw format below)

    When GSAS format files (.fxye or .raw) are requested from the web site, the appropriate GSAS instrument parameter
    file (.prm) is generated and included.

    .. _`11-BM file formats`:
        http://11bm.xray.aps.anl.gov/filetypes.html

    """

    with open(fname, "r") as fid:
        vals = parse_gsas_header(fid)
    headers, wavelength, first_data_line, bank_line = vals

    name = headers.get("User sample name", None)
    if not name:
        name = os.path.basename(fname)

    try:
        df = pd.read_csv(fname, header=None, delimiter=" ", skiprows=first_data_line)
        df.dropna(axis=("index", "columns"), how="all", inplace=True)
    except Exception:
        raise exceptions.IncorrectFileType("\n".join(traceback.format_exception(sys.exc_info())))

    if not len(df.columns) == 3:
        raise exceptions.IncorrectFileType

    if not all(dtype in (float, int) for dtype in df.dtypes):
        raise exceptions.IncorrectFileType

    col_names = dict(zip(df.columns, ("twotheta", "intensity", "uncertainty")))
    df.rename(columns=col_names, inplace=True)
    df["twotheta"] /= 100

    return powderdiffraction.PowderDiffraction(df, name=name, wavelength=wavelength, source="undefined")


def load_raw(fname):
    with open(fname, "r") as fid:
        vals = parse_gsas_header(fid)
        if not vals:
            raise exceptions.IncorrectFileType

        headers, wavelength, first_data_line, bank_line = vals
        bank = bank_line.split()
        try:
            num_points = int(bank[2])
            angle_start = float(bank[5]) / 100
            angle_step = float(bank[6]) / 100
        except Exception:
            raise exceptions.IncorrectFileType

        arr = pd.read_csv(fid, header=None, delim_whitespace=True).values.flatten()[:num_points * 2]

    angle_stop = angle_start + angle_step * (num_points - 1)

    twotheta = np.linspace(angle_start, angle_stop, num_points, dtype=float)
    intensity = arr[0::2]
    uncertainty = arr[1::2]

    name = headers.get("User sample name", None)
    if not name:
        name = os.path.basename(fname)

    return powderdiffraction.PowderDiffraction(
        data=np.vstack((twotheta, intensity, uncertainty)).T,
        columns=["twotheta", "intensity", "uncertainty"],
        name=name,
        wavelength=wavelength
    )


fxye_loader = loaders.Loader(load_fxye, powderdiffraction.PowderDiffraction, (".fxye"), "GSAS .fxye")
gsas_loader = loaders.Loader(load_raw, powderdiffraction.PowderDiffraction,
                             (".raw", ".gsas", ".gsa", ".gs"), "GSAS raw")

loaders.register_loaders(fxye_loader, gsas_loader)
