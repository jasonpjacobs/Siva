
from .command import Command
import pdb


class Save(Command):
    toekn = ""
    def __init__(self, *items, analysis=None):
        self.items = items
        self.analysis = analysis
        Command.register_keyword(self, store_as="list", keyword="saves")

    def card(self, format="ascii"):
        txt = ".PRINT {} FORMAT={} {}".format(self.analysis, format, " ".join([i.output() for i in self.items]))
        return txt

class V(Save):
    token = "V"


class I(Save):
    token = "I"
    def __init__(self, item, pin=""):
        self.item = item
        self.pin = pin

    def output(self):
        if type(self.item) is str:
            txt = self.item
        else:
            txt = str(self.item.path)
        return "{}{}({})".format(self.token, str(self.pin), txt)


class Ig(I):
    token = "Ig"