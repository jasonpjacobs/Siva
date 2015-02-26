import unittest
import pytest

from ..directive import Directive
from ..component import Component
from ..parameter import Float

class Option(Directive):
    dict_name = "options"

    value = Float(0)

    def __init__(self, name, value=None):
        self.name = name
        if value:
            self.value = value
        super().__init__()


    def _store(self, dct):
        self._store_as_dict(dct, key=self.name)

class Test(Component):
    a = 20
    Option("temp", 111)

def test_directive():
    t = Test()

    print(t.__class__.__name__)

    assert "temp" in t.options
    assert "options" in t._component_dicts
    assert t.options["temp"].value == 111

