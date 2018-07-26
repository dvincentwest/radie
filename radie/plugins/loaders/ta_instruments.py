import numpy as np
import struct

from radie import exceptions
from radie.loaders import Loader, register_loaders
from radie.plugins.structures.dsc import DSC
from radie.plugins.structures.tga import TGA

# Dictionary for unit conversion
# note that all keys are lower case
unit_conversion = {
    's': ('min', lambda x: x/60.),
    'sec': ('min', lambda x: x/60.),
    'seconds': ('min', lambda x: x/60.),
    'h': ('min', lambda x: x*60.),
    'hr': ('min', lambda x: x*60.),
    'hrs': ('min', lambda x: x*60.),
    'hours': ('min', lambda x: x*60.),
    'm': ('min', lambda x: x),
    'min': ('min', lambda x: x),
    'minutes': ('min', lambda x: x),
    'k': ('°C', lambda x: x+273.15),
    'f': ('°C', lambda x: (x-32)*5./9.),
    '°f': ('°C', lambda x: (x-32)*5./9.),
    'μg': ('mg', lambda x: x/1000.),
    'mg': ('mg', lambda x: x),
    'g': ('mg', lambda x: x*1000.),
    'kg': ('mg', lambda x: 1e6*x),
    'μw': ('mW', lambda x: 1000.*x),
    'mw': ('mW', lambda x: x),
    'w': ('mW', lambda x: x/1000.),
    'mj/°c': ('mJ/°C', lambda x: x)
    }


def convert_units(unit, x):
    """Attempts to convert to TGA structure defaults, otherwise returns input"""
    if unit.lower() in unit_conversion.keys():
        return unit_conversion[unit.lower()][0], unit_conversion[unit.lower()][1](x)
    else:
        return unit, x


def load_ta_instruments(fname, required_keys=None, required_kvs=None):
    """
    It appears most TA instruments raw files share a fairly common data structures
    This should return the header as a dictionary and the columns as a numpy array
    Unit conversion is attempted according to the module-level unit_converison dict

    Parameters
    ----------
    fname : basestring
        file path to TA instruments file
    required_keys: list
        list of strings that must be found in the header. "startswith" is used to check for existence
    required_kvs: dict
        dictionary of key-value pairs that should be found in the header, both
        "startswith" is used for both key and value. Useful ensuring the right loader function is used
         for teh right instrument

    Returns
    -------
    metadata : dict
        dictionary of strings corresponding to the header. There are three keys that have been added
        'columns', list of strings corresponding to column names without units (lower case)
        'units', list of strings corresponding to units for the columns (mixed case)
    results : numpy array
        array of floats, number of columns dictated by the input file
        TGA StructuredDataFrame
    """

    results = []
    with open(fname, "rb") as f:
        # Need to read by two or else utf-16 might return an error
        header_byte_string = b''
        while True:
            s = f.read(2)
            if s == b'\x0c\x00' or s == b'':
                break
            header_byte_string += s

        header_text = header_byte_string.decode('utf-16')
        lines = header_text.split('\r\n')

        if required_keys is not None:
            founds = [False] * len(required_keys)
            for i,required_key in enumerate(required_keys):
                for line in lines:
                    if line.startswith(required_key):
                        founds[i] = True
                        break

            if not all(founds):
                raise exceptions.IncorrectFileType

        if required_kvs is not None:
            founds = [False] * len(required_kvs)
            for i,(req_key, req_val) in enumerate(required_kvs.items()):
                for line in lines:
                    items = [x.strip() for x in line.split()]
                    if len(items) > 1:
                        key = items[0]
                        val = ' '.join(items[1:])
                        if key.startswith(req_key) and val.startswith(req_val):
                            founds[i] = True
                            break

            if not all(founds):
                raise exceptions.IncorrectFileType

        raw_column_headers = [s for s in lines if s.startswith('Sig')]

        # If no signals were found returns None
        if not raw_column_headers:
            raise exceptions.IncorrectFileType

        # After the b'\x0c\x00' there is a \x05 pad
        f.read(1)

        # the data is then floats corresponding to the number of signals
        read_format = 'f'*len(raw_column_headers)
        read_len = 4*len(raw_column_headers)

        while True:
            read_val = f.read(read_len)
            if read_val:
                if read_val.startswith(b'\x01\x04'):
                    # Reached "\x04" end of transmission marker
                    break
                else:
                    results.append(struct.unpack(read_format, read_val))
                    if results[-1][0] == -100.0:
                        # Data columns terminated by a -100 in the first column
                        results.pop(-1)
                        break
            else:
                # Reached EOF
                break

    if not results:
        raise exceptions.IncorrectFileType

    results = np.array(results)

    # Convert the header into metadata
    metadata = {}
    for line in lines:
        items = [x.strip() for x in line.split()]
        if len(items) > 1:
            key = items[0]
            val = ' '.join(items[1:])
            metadata[key] = val

    # Use sample as name
    metadata['name'] = metadata.get('Sample', '')

    # Extract column titles and units
    columns = []
    column_units = []
    if raw_column_headers:
        for i in range(len(raw_column_headers)):
            key = 'Sig{}'.format(i+1)
            head = metadata[key]
            columns.append(' '.join(head.split()[:-1]).lower())
            column_units.append(head.split()[-1][1:-1])

    # The TA Instruments default units seem to already be fine but convert just in case
    # Note that convert_units will return input if unable to convert
    for i, unit in enumerate(column_units):
        column_units[i], results[:,i] = convert_units(unit, results[:,i])
    metadata['columns'] = columns
    metadata['units'] = column_units

    return metadata, results


def load_dsc(fname):
    """

    Parameters
    ----------
    fname : file path

    Returns
    -------
    df_dsc : DSC
        DSC StructuredDataFrame
    """
    ta_out = load_ta_instruments(fname, required_kvs={"Instrument": "DSC Q2000"})
    if ta_out is None:
        raise exceptions.IncorrectFileType

    metadata, results = ta_out

    # Header typically reports the sample mass under the keyword "Size"
    size = metadata.get('Size')
    try:
        elements = size.split()
        metadata['mass'] = convert_units(elements[1], float(elements[0]))[1]
    except (AttributeError, ValueError, IndexError):
        metadata['mass'] = 1

    columns = metadata.pop('columns')
    underscored_columns = [s.lower().replace(' ', '_') for s in columns]
    df_dsc = DSC(data=results, columns=underscored_columns,
                 **metadata)
    return df_dsc


TA_Q2000_loader = Loader(load_dsc, DSC, [".001", ".002", ".003"], "TA Instruments Q2000")


def load_tga(fname):
    """
    Parameters
    ----------
    fname : file path

    Returns
    -------
    df_tga : TGA
        TGA StructuredDataFrame
    """
    ta_out = load_ta_instruments(fname, required_kvs={"Instrument": "TGA Q500"})
    if ta_out is None:
        raise exceptions.IncorrectFileType
    metadata, results = ta_out

    columns = metadata.pop('columns')
    underscored_columns = [s.lower().replace(' ', '_') for s in columns]

    df_tga = TGA(data=results,
                 columns=underscored_columns,
                 **metadata)
    return df_tga


TA_Q500_loader = Loader(load_tga, TGA, [".001", ".002", ".003"], "TA Instruments Q500")

register_loaders(
    TA_Q500_loader, TA_Q2000_loader,
)
