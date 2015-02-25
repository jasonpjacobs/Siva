from ..directive import Directive
from ..component import Component
import unittest
import pytest


class Option(Directive):
    dict_name = "options"

    def __init__(self, name, value):
        self.name = name
        self.value = value
        super().__init__()


    def _store(self, dct):
        self._store_as_dict(dct, key=self.name)

class Test(Component):
    a = 20
    Option("temp", 110)

def test_directive():
    t = Test()

    print(t.__class__.__name__)

    assert "temp" in t.options
    assert "options" in t._component_dicts
    assert t.options["temp"].value == 110