from ...components.parameter import File
from ...components.directive import Directive


class Include(Directive):
    dict_name = "commands"
    path = File()

    def __init__(self, file, name=None):
        super().__init__()

        self.name = name
        self.path = file

    def _store(self, dct):
        self._store_as_list(dct, key="include")

    def card(self):
        txt = ".INCLUDE {}".format(self.path)
        return txt
