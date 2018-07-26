from collections import OrderedDict
import numpy as np
import pandas as pd
from radie.structures import StructuredDataFrame, register_data_structures


class TGA(StructuredDataFrame):
    """
    StructuredDataFrame for holding Thermogravimetric analysis data
    Default units are minutes, mg, and celsius
    Please convert results to default units during instantiation, no unit checking is done within
    """

    label = "Thermogravimetric Analysis"

    _required_metadata = StructuredDataFrame._required_metadata.copy()

    _x = "time" # minutes
    _y = "weight" # mg
    _z = "temperature" # celsius

    _required_columns = OrderedDict((
        ("temperature", float),
        ("weight", float),
        ("time", float),
    ))
    _column_properties = ["norm_weight", "deriv_norm_weight", "deriv_weight"]

    @property
    def norm_weight(self):
        """Normalize the weight using the first datapoint (samples can gain or lose mass)"""
        return self.weight/self.weight[0]

    @property
    def deriv_norm_weight(self):
        """
        Normalized weight derivative wrt temperature
        Returns
        -------
        Array of derivative of normalized weight wrt time
        """
        y = self.norm_weight.values
        x = self.temperature.values
        return pd.Series(np.gradient(y, x), name='Deriv. Weight (%/°C)')

    @property
    def deriv_weight(self):
        """
        Normalized weight derivative wrt temperature
        Returns
        -------
        Array of derivative of normalized weight wrt time
        """
        y = self.weight
        x = self.temperature
        return pd.Series(np.gradient(y, x), name='Deriv. Weight (mg/°C)')

register_data_structures(TGA)
