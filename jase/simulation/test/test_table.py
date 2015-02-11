import pytest

from ..table import Table

@pytest.fixture
def simple_table():
    t = Table(columns = ['name', 'age', 'gender'])
    t.add_row('Adam','22','Male')
    t.add_row('Betty', '31', 'Female')
    t.add_row('Charlie', '62', 'Female')
    return t


def test_blank_table():
    t = Table()

    assert str(t) == "<Empty Table>"

def test_simple_table(simple_table):
    t = simple_table
    assert t.columns['name'][0] == 'Adam'
    assert t.columns['name'][1] == 'Betty'
    assert t.columns['name'][2] == 'Charlie'

    assert t.columns['age'][0] == '22'
    assert t.columns['age'][1] == '31'
    assert t.columns['age'][2] == '62'

    assert t.columns['gender'][0] == 'Male'
    assert t.columns['gender'][1] == 'Female'
    assert t.columns['gender'][2] == 'Female'

