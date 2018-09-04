import os
import sys
import traceback
import csv
import warnings
import io
import json
import typing
from pathlib import Path

import pandas as pd

from radie import structures
from . import exceptions
from .structures.structureddataframe import StructuredDataFrame

loaders = dict()


class Loader(object):
    """object used to map file-extensions to functions that load StructuredDataFrame subclasses

    The loader object is a place holder that connects a list of file-extensions to a a function that will read those
    files and StructuredDataFrame subclass that the function will return.  Its main purpose is for book-keeping to allow
    automatic operations involving reading data files.  One key principle of operation is that the function will check
    and validate if the file is of the correct type and has all of the required necessary information.  If not, the
    function should raise a LoaderException, otherwise, the function returns an instance (or a list of
    instances) of the `StructuredDataFrame` subclass specified in the `cls` attribute

    Attributes
    ----------

    cls: typing.Type(StructuredDataFrame)
        the `StructuredDataFrame` sub-class that the loader function will load
    extensions : list, str
        a string or list of strings specifying the file types
    label : str
        the readable text that will represent this file loader
    module : str
        the module path of the loader function, helpful for debugging

    """

    def __init__(self, loader_function, cls, extensions, label):
        """
        Parameters
        ----------
        loader_function : function
            the function to load the StructuredDataFrame from a file, expects filename argument
        cls: typing.Type(StructuredDataFrame)
            the `StructuredDataFrame` sub-class that the loader function will load
        extensions : list, str
            a string or list of strings specifying the file types
        label : str
            the readable text that will represent this file loader
        """
        self._load = loader_function  # type: typing.Callable
        self.cls = cls

        if type(extensions) is list:
            self.extensions = extensions
        elif type(extensions) is str:
            self.extensions = [extensions]
        else:  # convert iterable type to list
            self.extensions = list(extensions)

        self.label = label

    @property
    def module(self):
        return self._load.__module__ + "." + self._load.__name__

    def load(self, filename):
        """load a `DataFrame` object from the loader function and return

        Parameters
        ----------
        filename : str

        Returns
        -------
        StructuredDataFrame

        """
        return self._load(filename)

    def __str__(self):
        return self.label + ": " + ", ".join(self.extensions)


def register_loaders(*loader_objects):
    """register Loader objects with the loaders.loaders book-keeping dict so we can keep track

    Parameters
    ----------
    loader_objects : Loader
        Loader objects supplies as arguments

    """
    for loader in loader_objects:  # type: Loader
        for ext in loader.extensions:
            if ext not in loaders.keys():
                loaders[ext] = []
            if loader in loaders[ext]:
                warnings.warn('overwriting Loader Object {:} for file extension {:}'.format(loader.label, ext))
            loaders[ext].append(loader)
        if loader.cls not in loader.cls.loaders():  # setup circular referencing of sorts
            loader.cls.add_loader(loader)


def from_clipboard(*args, **kwargs):
    df = pd.read_clipboard(*args, **kwargs)
    return StructuredDataFrame(df)


def load_csv(fname, name=None, encoding=None):
    """
    a function to read a generic csv file and return a dataframe. It is assumed that the file has the following
    structure:

        1. Metadata (Optional)
        2. DataBlock in CSV format with or without a header line

    The function goes to about 80% of the way through the file, assuming that that location is always within the
    datablock.  At this point, the Python csv module is used to "sniff" the datablock delimiter and also a number
    of columns and numeric signature are determined

    Next we go to the beginning of the file and look for the first sequence of 10 lines that are delimited by the
    sniffed delimiter, and has the same length and numeric signature of the datablock.  This marks the beginning of the
    datablock.

    Lastly we look at the line immediately above the datablock.  If that line has the same delimited length it is
    assumed to be the headerline.

    We use all of this information to pass the filename to pandas.read_csv, to read in the data-block and the headerline


    Parameters
    ----------
    fname : str or io.TextIOWrapper or io.StringIO

    Returns
    -------
    StructuredDataFrame

    """

    if not name:
        name = ''

    if isinstance(fname, Path):
        fname = str(fname)

    if type(fname) is str:
        if not os.path.isfile(fname):
            raise TypeError('fname must be a valid file, string blocks not yet supported')
        with open(fname, "r", encoding=encoding) as fid:
            if not name:
                name = os.path.basename(fname)
            data = io.StringIO(fid.read())
    elif type(fname) is io.TextIOWrapper:
        if not name:
            name = os.path.basename(fname.name)
        data = io.StringIO(fname.read)
    elif type(fname) is io.StringIO:
        data = fname
    else:
        raise TypeError('must provide a filename, a TextIOWrapper object, or a StringIO object')

    lines = data.readlines()
    data.seek(0)

    num_lines = len(lines)
    if num_lines > 100:
        # big file assume we find data_block at the 80% mark
        chunk_start = int(num_lines * 0.8)
        chunk_end = chunk_start + 10
    else:
        # small file, start at the end and work our way back to the first non-blank line
        for chunk_end in range(num_lines - 1, -1, -1):
            if lines[chunk_end] and not lines[chunk_end].isspace():
                break
        chunk_start = chunk_end - 10 if num_lines > 11 else 1

    chunk_lines = lines[chunk_start:chunk_end]
    chunk = "".join(chunk_lines)
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(chunk)
    except:
        err_msg = "\n".join(traceback.format_exception(*sys.exc_info()))
        raise exceptions.LoaderException('Sniffing delimieter failed\n{:s}'.format(err_msg))

    def numeric_signature(values):
        sig = list()
        for value in values:
            try:
                float(value)
                sig.append(True)
            except:
                sig.append(False)
        return sig

    lengths = [len(line.split(dialect.delimiter)) for line in chunk_lines]
    chunk_length = lengths[0]

    # if chunk lines are not all the same length, raise a LoaderException
    if not all([length == chunk_length for length in lengths]):
        raise exceptions.LoaderException('csv sample lines have different lengths')

    chunk_numeric_signature = numeric_signature(chunk_lines[0].split(dialect.delimiter))
    data_block_beginning = -1
    match_count = 0
    header_line_idx = None

    for i, line in enumerate(lines):
        line_vals = line.split(dialect.delimiter)

        if not len(line_vals) == chunk_length:
            match_count = 0
            continue

        line_numeric_signature = numeric_signature(line_vals)
        if not line_numeric_signature == chunk_numeric_signature:
            match_count = 0
            continue

        match_count += 1

        if match_count > 9:
            data_block_beginning = i - match_count + 1

            header_line_idx = data_block_beginning - 1
            if header_line_idx >= 0:
                header_line = lines[header_line_idx]
                header_line_vals = header_line.split(dialect.delimiter)

                if len(header_line_vals) == chunk_length + 1:  # assume we have a commented header
                    explicit_header = header_line_vals[1:]
                    header_line_idx = None;
                elif not len(header_line_vals) == chunk_length:
                    explicit_header = None
                    header_line_idx = None
            else:
                header_line_idx = None
            break

    if data_block_beginning < 0:
        raise exceptions.LoaderException('datablock not found')

    if header_line_idx is None:
        df = pd.read_csv(data, delimiter=dialect.delimiter, names=explicit_header,
                         skiprows=data_block_beginning, header=None, skip_blank_lines=False)
    else:
        df = pd.read_csv(data, delimiter=dialect.delimiter,
                         header=header_line_idx, skip_blank_lines=False)
    df = StructuredDataFrame(df.dropna(axis="index", how="all").dropna(axis='columns', how='all'), name=name)
    return df


def load_dftxt(fname):
    """load files from the `StructuredDataFrame.savetxt` method

    Parameters
    ----------
    fname : str

    Returns
    -------
    StructuredDataFrame
        fully specified datastructure from the dftxt file

    """
    header_block = []
    data_location = None
    data_sample = ''
    with open(fname, 'r') as fid:
        for line in iter(fid.readline, ''):
            if line.isspace():
                data_location = fid.tell()
            elif line.startswith('#'):
                header_block.append(line[1:])
                data_location = fid.tell()
            else:
                break

        if not data_location:
            raise exceptions.IncorrectFileType()
        try:
            meta_data = json.loads(''.join(header_block))  # type: dict
        except json.JSONDecodeError:
            raise exceptions.IncorrectFileType("header is not a valid json")
        except:
            raise exceptions.LoaderException("error when loading JSON")

        try:
            cls_key = meta_data.pop("class")
            file_type = meta_data.pop("file-type")
        except KeyError:
            raise exceptions.IncorrectFileType("df file missing required class for file-type information")
        else:
            try:
                cls = structures.structures[cls_key]  # type: typing.Type[StructuredDataFrame]
            except KeyError:
                raise exceptions.LoaderException("df class {:s} is not supported by any known DF Structure "
                                                 "classes".format(cls_key))

        if not cls.required_metadata().issubset(meta_data):
            raise exceptions.LoaderException("file meta-data does not match the required meta-data for the specified "
                                             "StructuredDataFrame Structure")

        for i, line in enumerate(iter(fid.readline, '')):
            data_sample += line
            if i == 10:
                break

        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(data_sample)
        except:
            err_msg = "\n".join(traceback.format_exception(*sys.exc_info()))
            raise exceptions.LoaderException("Could not determine CSV block in datablock")

        fid.seek(data_location)
        df = pd.read_csv(fid, sep=dialect.delimiter)
        if not cls.required_columns().issubset(df.columns):
            raise exceptions.LoaderException(
                "StructuredDataFrame Columns do not match the required columns"
                "for the specified StructuredDataFrame Structure"
            )
        df = cls(df.dropna(axis="index", how="all").dropna(axis='columns', how='all'), **meta_data)
        return df


df_loader = Loader(load_dftxt, StructuredDataFrame, (".df"), "StructuredDataFrame text file")
register_loaders(df_loader)


def load_file(fname):
    """the catch-all convenience function to automatically load data-files

    This function is at the heart of one of the goals of Radie.  The idea is that any datafile that is supported
    by the radie structures and loaders can be passed to this function without needing to specify anything, and the
    proper Loader function will be determined automatically.  First a list of possible loader functions are found from
    the file extension.  They are then tried one by one, with each inappropriate function returning None, and continuing
    on to the next loader function.  The first time a valid StructuredDataFrame is returned, the function breaks the look and
    returns that object.  If no valid loader function is found, we attempt to read in the file using the load_csv
    automatic csv reader function.

    Parameters
    ----------
    fname : str
        the name of the datafile

    Returns
    -------
    StructuredDataFrame or list or tuple
        the output of the automatically determined loader function, could be a
        single StructuredDataFrame or a list of DataFrames

    """
    ext = os.path.splitext(fname)[1]

    try:
        loaders_ = loaders[ext]
    except KeyError:
        loaders_ = []

    for loader in loaders_:  # type: Loader
        try:
            dfs = loader.load(fname)
            if isinstance(dfs, StructuredDataFrame):
                print("successfully loaded file as {:}".format(type(dfs).__name__))
                return dfs
            elif type(dfs) in (list, tuple):
                df_list = [df for df in dfs if isinstance(df, StructuredDataFrame)]
                if not df_list:
                    raise exceptions.LoaderException("function {:s} did not return any StructuredDataFrame "
                                                     "objects from file {:s}".format(loader.module, fname))
                print("loaded {:d} dataframes from {:}".format(len(df_list), os.path.basename(fname)))
                return df_list
            else:
                raise exceptions.LoaderException("function {:s} did not return any StructuredDataFrame "
                                                 "objects from file {:s}".format(loader.module, fname))
        except exceptions.IncorrectFileType:
            continue
        except exceptions.LoaderException as loader_exception:
            raise loader_exception
        except Exception:
            err_msg = "loader function {:}.{:} failed".format(loader._load.__module__, loader._load.__name__)
            err_msg += "\n" + "\n".join(traceback.format_exception(*sys.exc_info()))
            raise Exception(err_msg)

    # no suitable loader was found, try the universal "load_csv" function
    try:
        df = load_csv(fname)
        return df
    except ValueError:  # in case of a unicode file not loaded properly
        try:
            df = load_csv(fname, encoding="utf-8")
            return df
        except exceptions.LoaderException:
            raise exceptions.LoaderNotFound("No loader found for the specified file")
        except Exception as e:
            raise e
    except exceptions.LoaderException:
        raise exceptions.LoaderNotFound("No loader found for the specified file")
    except Exception:
        raise exceptions.LoaderNotFound("load_csv failed for unexpected reason\n{:s}".format("\n".join(
            traceback.format_exception(*sys.exc_info()))))
