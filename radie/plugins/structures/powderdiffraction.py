import numpy as np
from collections import OrderedDict

from radie.structures import StructuredDataFrame, register_data_structures

CuKa1 = 1.5405980  # angstroms
CuKa2 = 1.5444260  # angstroms
CuKa = (2 * CuKa1 + CuKa2) / 3  # scaled avg of CuKa1 and 2, =1.541874
CuKb1 = 1.392250  # angstroms


def calc_Q(twotheta, wavelength):
    """
    Calculate the length of the reciprocal lattice vector given a diffraction angle and wavelength

    Parameters
    ----------
    twotheta : np.ndarray, float
        diffraction angle in degrees
    wavelength : float
        radiation wavelength in angstroms

    Returns
    -------
    Q : np.ndarray, float
        reciprocal lattice vector length

    """
    return 4 * np.pi / wavelength * np.sin(np.deg2rad(twotheta / 2))


def calc_twotheta(Q, wavelength):
    """
    Calcuate twotheta at a given wavelength from the length of the reciprocal lattice vector `Q`

    Parameters
    ----------
    Q : np.ndarray, float
        the length of the reciprocal lattice vector
    wavelength : float
        the desired wavelength in angstroms

    Returns
    -------
    twotheta : np.ndarray, float
        diffraction angle in degrees

    """
    return np.rad2deg(2 * np.arcsin(Q * wavelength / (2 * np.pi)))


def convert_wavelength(wl1, wl2, twotheta1):
    """
    Convert twotheta values to those for another wavelength

    Parameters
    ----------
    wl1 : float
        the original wavelength in angstroms
    wl2 : float
        the new wavelength in angstroms
    twotheta1 : np.ndarray, float
        the original twotheta values in degrees

    Returns
    -------
    twotheta2 : np.ndarray, float
        the new twotheta values in degrees

    """
    rad1 = np.deg2rad(twotheta1)
    rad2 = 2 * np.arcsin(wl2 / wl1 * np.sin(rad1 / 2))
    return np.rad2deg(rad2)


def calc_d_spacing(x, wavelength=None):
    """
    Calculate the d spacing given the x values, where x is either twotheta or the reciprocal lattice vector length Q

    Parameters
    ----------
    x : np.ndarray, float
        Q or twotheta.  if wavelength is provided, x is twotheta in degrees, otherwise Q
    wavelength : float, optional
        the wavelength

    Returns
    -------
    d_spacing : np.ndarray, float
        the lattice spacing in Angstroms

    """

    if wavelength is None:
        d_spacing = np.pi / x
    else:
        d_spacing = wavelength / (2 * np.sin(np.deg2rad(x) / 2))

    return d_spacing


class PowderDiffraction(StructuredDataFrame):
    """
    StructuredDataFrame for holding Powder diffraction data, valid for any bragg type diffraction measurements:
    Benchtop XRD, Synchrotron XRD, Neutron Diffraction
    """

    label = "Powder Diffraction"

    _required_metadata = StructuredDataFrame._required_metadata.copy()
    _required_metadata.update({
        "wavelength": CuKa,
        "source": "",
    })

    _x = "twotheta"
    _y = "intensity"

    _required_columns = OrderedDict((
        ("twotheta", float),
        ("intensity", float),
    ))
    _column_properties = ["Q", "d_spacing"]

    @property
    def Q(self):
        """return Q, the length of the reciprocal lattice vector"""
        if self.metadata["wavelength"] is None:
            raise ValueError("Must specify a wavelength to determine Q")
        srs = calc_Q(self.twotheta, self.metadata["wavelength"])
        srs.name = "Q"
        return srs

    def twotheta_at_wavelength(self, wavelength):
        return convert_wavelength(self.metadata["wavelength"], wavelength, self.twotheta)

    @property
    def d_spacing(self):
        """return d-spacing calculated from n=1 in the Bragg equation n * lambda = 2 * d sin(theta)"""
        if self.metadata["wavelength"] is None:
            raise ValueError("Must specify a wavelength to determine d-spacing")
        srs = calc_d_spacing(self.twotheta, self.metadata["wavelength"])
        srs.name = "d_spacing"
        return srs

register_data_structures(PowderDiffraction)
