import pytest
import os

import db_root
from jase import Component
from jase.design_database.library import LibDefs

@pytest.fixture
def lib_defs():
    defs = LibDefs(path=os.path.abspath(db_root.__path__[0]))
    return defs

@pytest.fixture
def analog_lib(lib_defs):
    return lib_defs['analog_lib']

def test_library_creation(lib_defs):
    assert len(lib_defs) > 0
    assert 'analog_lib' in lib_defs


def test_analog_lib(analog_lib):
    assert len(analog_lib) > 0

