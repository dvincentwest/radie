"""Loader for csv output of Horiba LA-960 particle size analyzer"""
import numpy as np
import re

from radie import exceptions
from radie.loaders import Loader, register_loaders
from radie.plugins.structures.psd import PSD
from radie.util import iso_date_string


class Parameter(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.reset_defaults(**kwargs)

    def reset_defaults(self, **kwargs):
        d = {'value': None,
             'type': str,
             'key': None,
             'unit': None,
             'delimiter': None,
             'raw_line': None,
             'raw_value': None,
             'format': '',
             'padding': True,
             'merge_consecutive_delimiters': True,
             'value_has_whitespace': True}
        self.update(d)
        self.update(**kwargs)

    def __str__(self):
        if self.get('value') is not None:
            if self.get('unit') is not None:
                return '{key}:{value:{format}} {unit}'.format(**self)
            else:
                return '{key}:{value:{format}}'.format(**self)

    def read_line(self, line):
        self['raw_value'] = line
        self['value'] = self['type'](line)
        return self['value']


class KeyValParameter(Parameter):
    def __init__(self, key=None, **kwargs):
        Parameter.__init__(self, **kwargs)
        self['key'] = key
        if self.get('raw_line') is not None:
            self.read_line(self['raw_line'])

    def read_line(self, line):
        if self.check_line(line):
            try:
                items = line.split(self['delimiter'])
                self['raw_value'] = self['delimiter'].join(items[1:])
                return self.update_value()
            except (TypeError, ValueError, AttributeError):
                self['raw_value'] = None
                self['value'] = None

    def update_value(self):
        valstr = self['raw_value'].strip()
        if self.get('unit', False):
            if self['unit'] in valstr:
                iunit = valstr.index(self['unit'])
                valstr = valstr[:iunit]
        try:
            self['value'] = self['type'](valstr)
        except (ValueError, AttributeError):
            self['value'] = None
        return self['value']

    def check_line(self, line):
        if self.get('key') is not None:
            return line.strip().startswith(self['key'])
        else:
            return False


class RegexParameter(Parameter):
    def __init__(self, regex=None, **kwargs):
        Parameter.__init__(self, **kwargs)
        if regex is None:
            self.gen_regex()
        else:
            self['regex'] = regex
        if self.get('raw_line') is not None:
            self.read_line(self['raw_line'])

    def gen_regex(self):
        # pdb.set_trace()
        key = re.escape(self.get('key')) if self.get('key') else ''
        if self.get('delimiter') is None:
            delimiter = r'\s+'
        else:
            delimiter = '({0})'.format(re.escape(self['delimiter']))
            if self.get('merge_consecutive_delimiters', False):
                delimiter += '+'
        unit = re.escape(self['unit']) if self.get('unit') is not None else ''
        padding = r'\s*?' if self.get('padding') is not None else ''
        if self.get('value_has_whitespace', False):
            raw_value = r'(?P<raw_value>.+)'
        else:
            raw_value = r'(?P<raw_value>\w+)'

        regex = r'{key}{padding}{delimiter}{padding}{raw_value}.*{unit}'.format(key=key, delimiter=delimiter,
                                                                                 unit=unit, padding=padding,
                                                                                 raw_value=raw_value)
        self['regex'] = regex
        return regex

    def read_line(self, line):
        self['raw_line'] = line
        self['m'] = re.compile(self['regex'])
        mo = self['m'].search(line.strip())
        if mo is not None:
            self.update(mo.groupdict())
            self.update_value()
        else:
            self['value'] = None
        return self['value']

    def update_value(self):
        try:
            self['value'] = self['type'](self['raw_value'].strip())
        except ValueError:
            self['value'] = None
        return self['value']


def load_csv(fname):
    """

    Parameters
    ----------
    fname : file path

    Returns
    -------
    df_psd : PSD
        PSD StructuredDataFrame
    """

    starting_lines = [
    "Median size",
    "Mean size",
    "Variance",
    "St. Dev.",
    "Mode size",
    "Span",
    "Geo. mean size",
    "Geo. variance",
    "Diameter on cumulative",
    "D10",
    "D90",
    "D(v,0.1)",
    "D(v,0.5)",
    "D(v,0.9)",]

    # Open while checking for expected format,
    # Want to fail as fast as possible
    lines = []
    with open(fname, "r") as reader:
        for i, line in enumerate(reader):
            if i < len(starting_lines):
                if not line.startswith(starting_lines[i]):
                    raise exceptions.IncorrectFileType()
            lines.append(line)

    # The Horiba can output with a user defined delimiter character
    # commas and tabs are currently supported
    if ',' in lines[0]:
        delimiter = ','
    elif '\t' in lines[0]:
        delimiter = '\t'
    else:
        raise exceptions.IncorrectFileType("only commas and tabs are supported as the delimiter")

    metadata = {}
    parameters = {}
    parameters['sample'] = RegexParameter(key='Sample Name', delimiter=delimiter)
    parameters['lot'] = RegexParameter(key='Lot Number', delimiter=delimiter)

    lines = [line.strip() for line in lines]

    while not lines[0].startswith('Diameter (\xb5m)'):
        line = lines.pop(0)
        for k, p in parameters.items():
            if line.startswith(p['key']):
                try:
                    value = p.read_line(line)
                    if value is not None:
                        break
                except:
                    pass

    if parameters['sample']['value'] is None:
        parameters['sample']['value'] = 'PSD_{}'.format(iso_date_string())

    for k, p in parameters.items():
        metadata[k] = p['value']
    metadata['name'] = parameters['sample']['value']

    lines.pop(0)
    # The last two lines are blank/null values
    data = np.array([[float(x) for x in line.split(delimiter)] for line in lines[:-2]])

    df_psd = PSD(data=data[:,:2],
                 columns=['diameter','frequency'],
                 **metadata)
    return df_psd

LA960_csv_loader = Loader(load_csv, PSD, [".csv"], "Horiba LA-960")

register_loaders(
    LA960_csv_loader,
)


