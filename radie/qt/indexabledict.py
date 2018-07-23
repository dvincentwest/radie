import typing
from collections import OrderedDict


class IndexableDict(OrderedDict):
    """
    A class that defines an ordered dictionary where the items are indexable with common slicing operations as well
    as by the dict key.  We can also retrieve the 'row' of the item as an integer by providing the key, or the value,
    in which case row will return the first instance of value
    """

    def __getitem__(self, key):
        if type(key) is slice:
            return tuple(self.values())[key]

        # can only use this functionality with slice because ints are valid dict keys, leaving here until I'm sure
        # all such uses are gone
        # elif type(key) is int:
        #     try:
        #         key = tuple(self)[key]
        #     except ValueError:
        #         raise ValueError("index {:} out of range".format(key))

        return super(IndexableDict, self).__getitem__(key)

    def getKey(self, index):
        """
        return the dict key at the given index

        Parameters
        ----------
        index : int

        Returns
        -------
        typing.Any
        """
        return tuple(self)[index]

    def getValue(self, index):
        """
        return the value at the given index

        Parameters
        ----------
        index : int

        Returns
        -------
        typing.Any
        """
        return tuple(self.values())[index]

    def getKeyAndValue(self, row):
        """
        return the ith key, value pair at row i

        Parameters
        ----------
        row : int

        Returns
        -------
        key : typing.Hashable
        value : typing.Any
        """
        key = self.getKey(row)
        return key, self[key]

    def rowCount(self):
        """
        QAbstractIndex convenience function

        Returns
        -------
        int
        """
        return len(self)

    def getKeyRow(self, key):
        """
        return the position of key in the dict

        Parameters
        ----------
        key : typing.Hashable

        Returns
        -------
        int
        """
        return tuple(self).index(key)

    def getValueRow(self, value):
        """
        return the position of the first occurence of value in the dict

        Parameters
        ----------
        value : typing.Any

        Returns
        -------
        int
        """
        return tuple(self.values()).index(value)
