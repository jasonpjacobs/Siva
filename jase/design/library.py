
import sys, os
import glob

class Lib(dict):
    """

    """
    def __init__(self, name, full_name=None, path=None, desc=None, version=None, tags=None):
        """

        :param name: The name of the library.  Must not contain spaces.
        :param full_name:  The "full", or printer friendly library name.  May contain spaces.
        :param path: The path on the filesystem where the library resides
        :param desc: A text description of the library
        :param version:  The library version
        :param tags:
        :return:
        """
        self.name = name
        self.full_name = full_name
        self.desc = desc
        self.path = path
        self.version = version

        if tags is None:
            self.tags = {}
        else:
            self.tags = tags

    def __getattr__(self, item):
        try:
            return dict.__getattr__(self, item)
        except AttributeError:
            if item in self:
                return self[item]

    def _load_cells(self):
        """Loads cell definitions from the file system.
        """
        assert self.path is not None
        assert os.path.isdir(self.path)

        subdirs = os.listdir(self.path)
        for subdir in subdirs:
            c = Cell(path=subdir)

l = Lib(name="analog_lib", path = ".")
l["nmos"] = 2


print(l["nmos"])
print(l.name)
print(l.nmos)