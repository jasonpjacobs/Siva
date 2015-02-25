from jase.old_spice.descriptors import StringType
from jase.old_spice.command import Command


class Library(Command):
    keyword = "LIB"
    def __init__(self, path, section, name=None):

        self.name = name
        self.path = path
        self.section = section
        Command.register_keyword(self, store_as="list")

    def card(self):
        txt = ".LIB {} {}".format(str(self.path), str(self.section))
        return txt

class Include(Command):
    path = StringType()

    def __init__(self, file, name=None):
        self.name = name
        self.path = file
        Command.register_keyword(self, store_as="list", keyword="INC")

    def card(self):
        txt = ".INCLUDE {}".format(self.path)
        return txt
