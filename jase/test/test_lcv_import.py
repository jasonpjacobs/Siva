import pytest
import os, sys
import types

import jase
from jase.design.importer import DesignLoader
from jase.design.library import LibDefs, Library
from jase.design.cell import Cell

def test_basic_loading():

    path = os.path.dirname(__file__)
    root = os.path.join(path, "./example_db_root")

    assert os.path.exists(root)

    lib_defs = {
        "lib_a" : os.path.join(root, 'lib_a'),
        "lib_b" : os.path.join(root, 'lib_b'),
        "lib_c" : os.path.join(root, 'lib_c')
    }
    loader = DesignLoader(lib_defs=lib_defs)
    loader.install()

    import lib_a, lib_b, lib_c

    assert type(lib_a) is Library
    assert type(lib_b) is Library
    assert type(lib_c) is Library

    assert lib_a.__doc__ == "Library for testing the library loader"
    assert lib_a.__version__ == "1.0.0"
    assert lib_a.__author__ == "Jase"


def cell_access():
    #assert 'cell_a' in lib_a.__dict__
    from lib_a.cell_a import CellA
    from cell_a import CellA

    assert CellA is not None
    assert CellA.marker == "This is cell A"
    assert issubclass(CellA, Cell)




