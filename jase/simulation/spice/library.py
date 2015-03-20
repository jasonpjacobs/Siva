from ...components.parameter import File, String
from ...components.directive import Directive


class Library(Directive):
    dict_name = "commands"
    section = String()
    path = File()

    def __init__(self, file, section, name=None):
        super().__init__()

        self.name = name
        self.path = file
        self.section = section

    def _store(self, dct):
        self._store_as_list(dct, key="libs")

    def card(self):
        txt = ".LIB {}".format(self.path)
        return txt
