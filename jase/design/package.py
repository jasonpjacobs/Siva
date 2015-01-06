import os
import collections
import types
import importlib

from jtypes import Str, Typed

class PlaceHolder:
    def __init__(self, parent, name):
        self.name = name
        self.parent = parent

    def load(self):
        item = importlib.import_module(self.parent + "." + self.name)
        return item

class Package(types.ModuleType, Typed):
    """ Base class definition for Libraries and Cells.  These are module types, but have a custom importer to support
    the way their children (cells, in the case of a library, or views in the case of a cell) are stored in the file system,
    and to allow their discovery when imported.
    """
    name = Str()
    _dict_name = "_dct"
    def __init__(self, name, full_name=None, path=None, desc=None, version=None, tags=None):
        """
        :param name: The name of the package.  Must not contain spaces.
        :param full_name:  The "full", or printer friendly library name.  May contain spaces.
        :param path: The path on the filesystem where the package resides
        :param desc: A text description of the package
        :param version:  The  version
        :param tags:
        :return:
        """
        types.ModuleType.__init__(self, name)
        Typed.__init__(self)

        self.name = name
        self.full_name = full_name
        self.desc = desc
        self.path = path
        self.version = version

        if tags is None:
            self.tags = {}
        else:
            self.tags = tags

        self._items = collections.OrderedDict()

    def _load_items(self):
        return None

    def __getattr__(self, attr):
        if attr in self._items:
            # Using __getitem__ will load replace the placeholder with the cell definition
            return self.__getitem__(attr)
        else:
            raise AttributeError

    # ------------------------------------------------------------------
    #   Dictionary interface
    # ------------------------------------------------------------------
    def __len__(self):
        return self._items.__len__()

    def __getitem__(self, key):
        # Look for placeholders and load them if needed.
        item = self._items.__getitem__(key)
        if isinstance(item, PlaceHolder):
            item = item.load()
            self._items[key] = item
        return item

    def __setitem__(self, key, value):
        # I can't think of a reason where a library (or cell) would need to
        # be modified.
        raise NotImplementedError("The cell dictionaries of a library are read only.")

        # But in case this changes in the future, we'll do this:
        #return self.__cells__.__setitem__(key, value)

    def __delitem__(self, key):
        return self._items.__delitem__(self, key)

    def __iter__(self):
        return self._items.__iter__()

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def items(self):
        return self._items.items()

