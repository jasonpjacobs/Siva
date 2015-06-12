import pytest

from siva.types.types import Int, Str, Bool, Float, Typed

class Mock(Typed):
    int = Int(0)
    str = Str('Name')
    bool = Bool()
    float = Float()

class MockChild(Mock):
    pass

@pytest.fixture
def mock():
    return MockChild()

@pytest.fixture
def picky_mock():
    class OddInt(Int):
        default = 1
        def validate(self, value):
            return value % 2 == 1

    class Hodor(Str):
        default = 'Hodor'
        def validate(self, value):
            return value.lower() == "hodor"

    class PosFloat(Float):
        def validate(self, value):
            return value >= 0.0

    class OnlyTrue(Bool):
        default = True
        def validate(self, value):
            return value is True

    class Mock:
        int = OddInt()
        str = Hodor()
        float = PosFloat()
        bool = OnlyTrue()

    return Mock()

def test_defaults(mock):
    assert mock.int == 0
    assert mock.str == 'Name'
    assert mock.bool is False
    assert mock.float == 0.0

def test_set_value(mock):
    mock.int = 12
    mock.str = "new string"
    mock.bool = True
    mock.float = 1.0

    assert mock.int == 12
    assert mock.str == "new string"
    assert mock.bool == True
    assert mock.float == 1.0

def test_casting(mock):
    mock.int = '20'
    mock.str = True
    mock.bool = "True"
    mock.float = "10p"

    assert mock.int == 20
    assert mock.str == 'True'
    assert mock.bool is True
    assert mock.float == 10e-12

    mock.bool = "false"
    assert mock.bool is False

    mock.bool = 0
    assert mock.bool is False

def test_formulas(mock):

    mock.int = '=1 + 1'
    mock.str = '="Hello World".upper()'
    mock.bool = '=1 < 3'
    mock.float = '=10/3'

    assert mock.int == 2
    assert mock.str == "HELLO WORLD"
    assert mock.float == 10/3.
    assert mock.bool is True


def test_validation(picky_mock):
    m = picky_mock
    assert m.int == 1
    assert m.str == "Hodor"
    assert m.float == 0.
    assert m.bool is True

    with pytest.raises(ValueError):
        m.int = 2

    with pytest.raises(ValueError):
        m.float = -1

    with pytest.raises(ValueError):
        m.str = "I am groot."

    with pytest.raises(ValueError):
        m.bool = False

    # Assign valid values
    m.int = 3
    m.float = 20
    m.str = "HODOR"
    m.bool = True

def test_descriptor_dict(mock):
    assert len(mock._descriptors) > 0
    assert isinstance(mock._descriptors['int'], Int)
    assert isinstance(mock._descriptors['str'], Str)
    assert isinstance(mock._descriptors['float'], Float)
    assert isinstance(mock._descriptors['bool'], Bool)



