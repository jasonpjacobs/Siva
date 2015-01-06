import pytest
import os, sys

import jase
from jase.design.importer import DesignFinder
from jase.design.library import LibDefs, Library
from jase.design.cell import Cell

@pytest.fixture
def finder():
    f = [f for f in sys.meta_path if isinstance(f, DesignFinder)]
    if f:
        return f[0]

    path = os.path.dirname(__file__)
    root = os.path.join(path, "./example_db_root")

    assert os.path.exists(root)

    library_paths = {
        "lib_a" : os.path.join(root, 'lib_a'),
        "lib_b" : os.path.join(root, 'lib_b'),
        "lib_c" : os.path.join(root, 'lib_c')
    }
    finder = DesignFinder(library_paths=library_paths)
    return finder


def test_importer_install(finder):
    finder.install()
    path = sys.meta_path

    assert any([f for f in sys.meta_path if isinstance(f, DesignFinder)])


def test_basics(finder):

    finder.install()
    import lib_a

    assert 'lib_a' in sys.modules
    assert type(lib_a) is Library
    assert lib_a.__doc__ == "Library for testing the library loader"
    assert lib_a.__version__ == "1.0.0"
    assert lib_a.__author__ == "Jase"
    assert lib_a.__file__ is not None
    assert lib_a.__file__ != ''
    assert os.path.exists(lib_a.__path__[0])
    assert True

def test_library_cell_list(finder):
    finder.install()
    import lib_a, lib_b, lib_c

    assert type(lib_a) is Library
    assert len(lib_a) == 2
    assert len(lib_a) == len(lib_a.__cells__)

    print(lib_a.__cells__)

def test_cell_import():
    import lib_a
    assert 'cell_a' in lib_a

def test_cell_attributes(finder):
    finder.install()

    from lib_a import cell_a

    assert 'lib_a.cell_a' in sys.modules

    assert isinstance(cell_a, Cell)
    assert(cell_a.__doc__[0:9] == 'A cell-ba')
    assert(cell_a.__version__ ==  "1.0.1")
    assert(cell_a.__author__ == "Jase")
    assert(cell_a.__file__ is not None)
    assert(os.path.exists(cell_a.__path__[0]))
    assert(cell_a.__name__ == 'lib_a.cell_a')
    assert(cell_a.__package__ == 'lib_a.cell_a')

    assert len(cell_a.__views__) == 1
    assert 'Symbol' in cell_a.__views__


def cell_access():
    assert 'cell_a' in lib_a.__dict__
    from lib_a.cell_a import CellA
    from cell_a import CellA

    assert CellA is not None
    assert CellA.marker == "This is cell A"
    assert issubclass(CellA, Cell)


def t_db_root():
    """Holding off on running this test until relative imports are fully unit tested.
    """
    path = os.path.dirname(__file__)
    root = os.path.join(path, "../../db_root")

    assert os.path.exists(root)

    lib_defs = {
        "analog_lib" : os.path.join(root, 'analog_lib'),
    }
    loader = DesignFinder(library_paths=lib_defs)
    loader.install()

    import analog_lib
    from analog_lib import nmos

    type(nmos)
