import inspect


from ..components.registered import Registered
from ..components.component import Component
from ..components.directive import Directive

class Analysis(Component):
    dict_name = "analyses"
    _directive = True

    def __init__(self, *args, **kwargs):
        super().__init__(name=self.analysis_name)
        self.register_as_directive()
        for k,v in kwargs.items():
            setattr(self, k, v)

    def register_as_directive(self):
        frame = inspect.currentframe()
        c_locals = frame.f_back.f_back.f_locals
        if '_directives' not in c_locals:
            c_locals['_directives'] = []
        c_locals['_directives'].append(self)

    def _store(self,  class_dct, registry_name):
        self._store_as_key_value_pair( class_dct=class_dct, registry_name=registry_name)