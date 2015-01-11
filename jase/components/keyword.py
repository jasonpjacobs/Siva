
import inspect
import collections

class Keyword:

    _props = []
    keyword = None
    def __init__(self):
        self.nodes = {}
        self.devices = {}

    @property
    def nodes(self):
        return self._nodes

    @staticmethod
    def register_keyword(self, store_as="attr", keyword=None):
        frame = inspect.currentframe()
        c_locals = frame.f_back.f_back.f_locals

        if '_commands' not in c_locals:
            c_locals['_commands'] = {}

        if keyword not in c_locals['_commands']:
            c_locals['_commands'][keyword] = []

        if store_as == "attr":
            c_locals['_commands'][keyword] = self

        elif store_as == "list":
            c_locals['_commands'][keyword].append(self)



