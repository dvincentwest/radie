from collections import OrderedDict
from radie.structures import StructuredDataFrame, register_data_structures


class DSC(StructuredDataFrame):
    """
    StructuredDataFrame for holding Thermogravimetric analysis data
    Default units are minutes, mg, and celsius
    Please convert results to default units during instantiation, no unit checking is done within
    """

    label = "Differential Scanning Calorimetry"

    _required_metadata = StructuredDataFrame._required_metadata.copy()
    _required_metadata['mass'] = 1. # mg, Default to 1 in case none is provided, used for normalization

    _x = "temperature" # celsius
    _y = "heat_flow" # mW
    _z = "time" # min

    _required_columns = OrderedDict((
        ("temperature", float), # celsius
        ("heat_flow", float), # mW
        ("time", float), # min
    ))
    _column_properties = ["norm_heat_flow"]

    @property
    def norm_heat_flow(self):
        """Normalize the heat flow using the mass found in metadata"""
        return self.heat_flow/self.metadata['mass']

register_data_structures(DSC)
