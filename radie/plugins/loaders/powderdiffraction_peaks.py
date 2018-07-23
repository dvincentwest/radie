import numpy as np
import os.path

from radie.loaders import Loader, register_loaders
from radie.plugins.structures.powderdiffraction import PowderDiffraction, CuKa


def convert_to_line_peaks(xy, ybase=0, ynorm=100.):
    line_peaks = []
    for x, y in xy:
        line_peaks.append([x, ybase])
        line_peaks.append([x, y])
        line_peaks.append([x, ybase])

    # Normalize peaks
    line_peaks = np.array(line_peaks)
    line_peaks[:, 1] = line_peaks[:, 1] / line_peaks[:, 1].max() * ynorm
    return line_peaks


def load_peaks(fname, name=None):
    """
    .peaks file
    Expected format is just "#" commented header and two columns of 2theta and intensities for the peaks
    Data gets reworked to make bars in a line graph with intensities of max 1000

    Parameters
    ----------
    fname : str
        filename
    name : str
        measurement identifier

    Returns
    -------
    df_xrd : single PowderDiffraction

    """
    ybase = 0.0
    ynorm = 100.

    with open(fname, 'rb') as f:
        peaks = np.loadtxt(f, delimiter=",")

    # The expectation is that this is a list of 2theta and peaks, in order to make it a line
    # it should be processed and shoulder point added

    line_peaks = convert_to_line_peaks(peaks, ybase=ybase, ynorm=ynorm)

    # Use filename for name
    name = os.path.splitext(os.path.basename(fname))[0]
    df_xrd = PowderDiffraction(data=line_peaks,
                               columns=['twotheta', 'intensity'],
                               wavelength=CuKa,
                               name=name)

    return df_xrd


def calc_twotheta_from_d(d, wavelength=CuKa):
    """
    Calcuate twotheta at a given wavelength from the length of the reciprocal lattice vector `Q`

    Parameters
    ----------
    d : np.ndarray, float
        d spacings
    wavelength : float
        the desired wavelength in angstroms, defaults to CuKa

    Returns
    -------
    twotheta : np.ndarray, float
        diffraction angle in degrees

    """
    return np.rad2deg(2 * np.arcsin(wavelength / (2 * d)))


def load_dpeaks(fname, name=None):
    """
    .peaks file
    Expected format is just "#" commented header and two columns of 2theta and intensities for the peaks
    Data gets reworked to make bars in a line graph with intensities of max 1000

    Parameters
    ----------
    fname : str
        filename
    name : str
        measurement identifier

    Returns
    -------
    df_xrd : single PowderDiffraction

    """
    ybase = 0.0
    ynorm = 100.

    with open(fname, 'rb') as f:
        peaks = np.loadtxt(f, delimiter=",")

    # The expectation is that this is a list of d spacings
    peaks[:, 0] = calc_twotheta_from_d(peaks[:, 0])
    line_peaks = convert_to_line_peaks(peaks)

    # Use filename for name
    name = os.path.splitext(os.path.basename(fname))[0]
    df_xrd = PowderDiffraction(data=line_peaks,
                               columns=['twotheta', 'intensity'],
                               wavelength=CuKa,
                               name=name)

    return df_xrd


xrd_peaks_loader = Loader(load_peaks, PowderDiffraction, [".peaks"], "twotheta peak file")
xrd_dpeaks_loader = Loader(load_dpeaks, PowderDiffraction, [".dpeaks"], "d-spacing peak file")
register_loaders(xrd_peaks_loader, xrd_dpeaks_loader)
