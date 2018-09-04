from collections import OrderedDict
import uuid
import typing
import json
import os

import pandas
from .. import util


class StructuredDataFrame(pandas.DataFrame):
    """Sub-Class of pandas `DataFrame` that defines data-structures through
       metadata and expected columns of data

    The StructuredDataFrame class is distinguished from a pandas StructuredDataFrame through
    private class variables that provide a way to specify the structure of data,
    which facilitates the easy processing and visualization of that data, e.g.
    in the Radie QtViewer. When creating a subclass of a StructuredDataFrame, the
    following class variables should be defined in the subclass in order to
    define the structure of the subclass.

    _required_columns : OrderedDict()
        a class variable defining the expected data series.  The dict keys are
        the StructuredDataFrame column labels and the values are the expected data types
        (e.g. int, float, etc.)
    _required_metadata : set
        a class variable defining the set of required_metadata keys, used for validation
    _column_properties : OrderedDict()
        a class variable defining the object properties that will return
    _x : typing.Hashable
        the column label for 'x' values, if None defaults to the 1st column
    _y : typing.Hashable
        the column label for 'y' values, if None defaults to the 2nd column
    _z : typing.Hashable
        the column label for 'z' values, if None defaults to the 3rd column

    the pandas `StructuredDataFrame` class has private variable `_metadata`_ which can be
    assigned a list of strings that become instance attributes.  For example, if
    a class class defines :code:`_metadata = ["name", "date"]`, then an instance
    can reference values as :code:`df.name`, and :code:`df.date`.

    Because `_metadata` is more of an ad-hoc feature of `pandas.DataFrame`, and might
    be deprecated in the future, this class uses `_metadata` to define an
    attribute `metadata`, as an `OrderedDict` of metadata that can easily
    interface with the json module for saving.  As such, metadata would be
    accessed by dictionary look-ups, e.g.  :code:`df.metadata["name"]`

    .. _`_metadata`: https://pandas.pydata.org/pandas-docs/stable/internals.html#define-original-properties


    Attributes
    ----------
    metadata : OrderedDict
        an ordered key-value pair for storing all of the metadata, e.g. name,
        date, mass, density, etc.
    x : pandas.Series
        The column of data representing `x` values, default is the first column
    x_col : typing.Hashable
        The column specifier for the `x` values, default is the specifier for
        the first column
    y : pandas.Series
        The column of data representing `y` values, default is the second column
    y_col : typing.Hashable
        The column specifier for the `y` values, default is the specifier for
        the second column
    z : pandas.Series
        The column of data representing `z` values, default is the third column
    z_col : typing.Hashable
        The column specifier for the `z` values, default is the specifier for
        the third column
    uuid : str or None
        a python uuid string for when bookkeeping is necessary, default value is
        None

    """

    label = "StructuredDataFrame"

    _metadata = "metadata"
    _required_metadata = OrderedDict((
        ("name", ""),
        ("date", util.iso_date_string),  # evaluate date-now if none is provided
    ))

    _x = None  # key for default x
    _y = None  # key for default y
    _z = None  # key for default z
    _required_columns = OrderedDict()  # minimum data Series that define the class
    _column_properties = OrderedDict()  # object properties that return a series based on the actual column values
    _loaders = []  # functions that will read in a file and return this class

    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=False, **metadata):
        """The constructor for a StructuredDataFrame, has the same signature as for a Pandas

        Parameters
        ----------
        data
        index
        columns
        dtype
        copy
        metadata
            keyword arguments specifically for the metadata.  Must be JSON compatible

        """
        super(StructuredDataFrame, self).__init__(data, index, columns, dtype, copy)
        self.metadata = OrderedDict()
        self._uuid = None  # type: str

        for meta_key, meta_val in self._required_metadata.items():
            val = metadata.pop(meta_key, meta_val)
            if callable(val):  # can only evaluate functions that take no arguments
                val = val()
            self.metadata[meta_key] = val

        # TODO: implement json checker for metadata
        self.metadata.update(metadata)
        if not self.is_valid():
            raise Exception

    def is_valid(self):
        """determine if the data and metadata match the specifications of the
            StructuredDataFrame class or sublcass

        StructuredDataFrame is meant to be subclassed.  The core specification of a
        StructuredDataFrame are expected columns of data in `._required_columns` and
        also necessary meta-data specified in the `._required_metadata`
        dictionary.  If in the construction or maniuplation of a StructuredDataFrame,
        the object no longer has the required columns or the required metadata,
        it is no longer a valid datastructure.  This function checks the state
        of the instance to see if it matches the class.  All base StructuredDataFrame
        instances should return `True` unless the `name` entry is removed from
        the `.metadata` `dict`.

        Returns
        -------
        bool

        """

        # TODO: implement proper dtype checking
        # dtypes in pandas are not so simple, to start, we're just going to use
        # the consenting adults principle and check only for a column with the
        # correct label, although checking for the correct dtype would be a nice
        # thing to have

        if not self.required_columns().issubset(self.columns):
            return False
        elif not self.required_metadata().issubset(self.metadata):
            return False
        else:
            return True

    @property
    def x(self):
        if not self._x:
            return self.ix[:, 0]
        else:
            return self[self._x]

    @property
    def x_col(self):
        if not self._x:
            return 0
        else:
            return self.columns.get_loc(self._x)

    @property
    def y(self):
        if not self._y:
            return self.ix[:, 1]
        else:
            return self[self._y]

    @property
    def y_col(self):
        if not self._y:
            if len(self.columns) > 1:
                return 1
            else:
                return None
        else:
            return self.columns.get_loc(self._y)

    @property
    def z(self):
        if not self._z:
            return self.ix[:, 2]
        else:
            return self[self._z]

    @property
    def z_col(self):
        if not self._z:
            if len(self.columns) > 2:
                return 2
            else:
                return None
        else:
            return self.columns.get_loc(self._z)

    @classmethod
    def required_metadata(cls):
        return set(cls._required_metadata)

    @classmethod
    def required_columns(cls):
        return set(cls._required_columns)

    @property
    def uuid(self):
        return self._uuid

    def set_uuid(self):
        """
        self.uuid is None by default and must be set.  An error will be
        raised if this function is called twice
        """
        if self.uuid:
            raise AttributeError("self.uuid is already set, specify force_new=True to set a new uuid")
        self._uuid = str(uuid.uuid1())

    def get_uuid(self):
        """get uuid.  If None, set one and then return it"""
        if not self.uuid:
            self.set_uuid()
        return self.uuid

    @classmethod
    def loaders(cls):
        """get a list of all the Loader objects known to return this specific data structure

        Returns
        -------
        list of Loaders

        """
        return cls._loaders

    @classmethod
    def add_loader(cls, loader):
        """append a Loader object to this classes list of known loaders"""
        cls._loaders.append(loader)

    def column_accessors(self):
        """
        return a list of 2-element tuples containing string labels and lambda
        functions (i.e. the accessors) that return column-type values which
        includes the dataframe columns and any properties that return
        column-like values, i.e. the _column_properties.

        Returns
        -------
        accessors : list of tuples

        """

        accessors = list()

        def series_accessor(df, key):
            return lambda: df[key]

        def property_accessor(df, prop):
            return lambda: getattr(df, prop)

        for key in list(self.keys()):
            accessors.append((key, series_accessor(self, key)))

        for prop in self._column_properties:
            accessors.append((prop, property_accessor(self, prop)))

        return accessors

    def savetxt(self, filename, overwrite=False):
        """save an ascii version of the dataframe, with metadata included in comment lines above the datablock

        Parameters
        ----------
        filename : str
        overwrite : bool

        """

        if not filename.endswith(".df"):
            filename += ".df"

        if os.path.isfile(filename) and not overwrite is True:
            raise FileExistsError("You must specify overwrite to be True to overwrite the file")

        with open(filename, "w") as fid:
            fid.write(self.serialize())

    def serialize(self):
        """return a string representation of the StructuredDataFrame, with metadata
            included

        Returns
        -------
        str

        """
        meta = OrderedDict()
        meta["file-type"] = "Radie txt version1"
        meta["class"] = self.__class__.__name__
        meta.update(self.metadata)
        meta_block = "# " + json.dumps(meta, indent=2).replace("\n", "\n# ")
        data_block = self.to_csv(index=None)

        return meta_block + '\n' + data_block

    @classmethod
    def from_clipboard(cls, *args, **kwargs):
        df = pandas.read_clipboard()
        # TODO: figure out a clever way to parse required columns, ignore for now for the sake of convenience
        return cls(data=df, *args, **kwargs)

    @property
    def _constructor(self):
        return self.__class__

    def rdplot(self, *args, **kwargs):
        """Subclasses may implement custom plotting functionality"""
        raise NotImplementedError("only available for specific subclasses of StructuredDataFrame")

