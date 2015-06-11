import unittest
import pytest

from ..directive import Directive
from ..component import Component
from ..parameter import Float

class Option(Directive):
    registry_name = "options"

    def __init__(self, name, value=None):
        self.name = name
        if value:
            self.value = value
        super().__init__()


    def _store(self, class_dct, registry_name):
        self._store_as_key_value_pair(class_dct, registry_name)

class Test(Component):
    a = 20
    Option("temp", 111)

def test_directive():
    t = Test()

    print(t.__class__.__name__)

    assert "temp" in t.options
    assert "options" in t._registries
    assert t.options["temp"].value == 111

