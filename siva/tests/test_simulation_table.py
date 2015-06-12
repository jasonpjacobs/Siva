import pytest

from siva.simulation.table import Table

@pytest.fixture
def simple_table():
    t = Table(columns = ['name', 'age', 'gender'])
    t.add_row('Adam','22','Male', row=None)
    t.add_row('Betty', '31', 'Female')
    t.add_row('Charlie', '62', 'Female')
    return t

@pytest.fixture
def out_of_order_table():
    t = Table(columns = ['name', 'age', 'gender'])
    t.add_row('Betty', '31', 'Female', row=1)
    t.add_row('Charlie', '62', 'Female', row=2)
    t.add_row('Adam','22','Male', row=0)
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


    assert len(t) == 3

    assert t.get_row(0)["name"] == 'Adam'


def test_out_of_order_table(out_of_order_table):
    t = out_of_order_table

    test_simple_table(t)

def test_row_iteration(simple_table):
    t = simple_table
    num_rows = len(simple_table)

    i=0
    for row in t:
        print(row)
        expected = t.get_row(i)
        for column in expected:
            assert row[column] == expected[column]
        i += 1

def test_add_column(simple_table):
    t = simple_table
    for i in range(len(t)):
        t.add_row({'ID':i}, row=i)

    # Make sure the original table wasn't altered
    test_simple_table(t)

    # And that the new column is correct
    for i,row in enumerate(t):
        assert row["ID"] == i


def test_write_csv(simple_table):
    simple_table.save_as_csv("test.csv", dir=r"P:\work")