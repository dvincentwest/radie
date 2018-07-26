from collections import OrderedDict

import numpy as np
from radie.structures import StructuredDataFrame, register_data_structures


class PSD(StructuredDataFrame):
    """
    StructuredDataFrame for holding Particle Size Distribution data

    """

    label = "PSD"

    _required_metadata = StructuredDataFrame._required_metadata.copy()
    _required_metadata.update({
        "refractive_index": "1.0",
        "distribution_mode": "volume",
        "ultrasound_time": 0,  # ultrasound time in seconds
    })

    _required_columns = OrderedDict((
        ("diameter", float),
        ("frequency", float),
    ))
    _column_properties = ["oversize"]

    @property
    def d50(self):
        """
        Returns
        -------
        D50 : float
            Particles with diameters of D50 or less account for 50% of the volume
        """
        return self.d(50)

    @property
    def d90(self):
        """
        Returns
        -------
        D90 : float
            Particles with diameters of D90 or less account for 90% of the volume
        """
        return self.d(90)

    @property
    def d10(self):
        """
        Returns
        -------
        d10 : float
            Particles with diameters of D10 or less account for 10% of the volume
        """
        return self.d(10)

    @property
    def dmin(self):
        return self.diameter[self.oversize < 100].iloc[0]

    @property
    def dmax(self):
        return self.diameter[self.oversize > 0.0].iloc[-1]

    def d(self, number):
        """
        Parameters
        ----------
        number : int or float
            Distribution fraction used to determine the diameter.
            Assumes D10 means low diameter end and D90 means high diameter end
            Must be in [0,100] range

        Returns
        -------
        d : float
            Particles with diameters of "d" or less account for "number" of the volume

        """
        if number > 100 or number < 0:
            raise ValueError("Supplied number (%s) must be in [0,100] range" % number)
        if number == 0:
            return self.dmin
        elif number == 100:
            return self.dmax

        oversize_target = 100 - number
        oversize_less = self.oversize <= oversize_target
        oversize_more = self.oversize > oversize_target
        d_min, oversize_min = self.diameter[oversize_more].iloc[-1], self.oversize[oversize_more].iloc[-1]
        d_max, oversize_max = self.diameter[oversize_less].iloc[0], self.oversize[oversize_less].iloc[0]
        return np.exp(
            np.interp(oversize_target, np.array([oversize_max, oversize_min]), np.log(np.array([d_max, d_min]))))

    @property
    def oversize(self):
        """
        Returns
        -------
        oversize : ndarray, float
        """
        oversize = 100.0 - self.frequency.cumsum()
        oversize.name = "oversize"
        return oversize


register_data_structures(PSD)
