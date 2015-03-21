from ...components.parameter import File
from ...components.directive import Directive


class Include(Directive):
    registry_name = "includes"
    path = File()

    def __init__(self, file, name=None):
        super().__init__()

        self.name = name
        self.path = file



    def card(self):
        txt = ".INCLUDE {}".format(self.path)
        return txt
