__author__ = 'Jase'

import pytest
from ..component import Component
from ..parameter import Parameter

@pytest.fixture
def simple():

    class A(Component):
        x = Parameter(2.34)
        y = Parameter(name='not_x')


    a = A(name='root')
    return a


def test_names(simple):
    a = simple

    assert a.name == 'root'
    assert 'x' in a.params
    assert 'y' in a.params

    assert a.x == a.params['x'].value
    assert a.y == a.params['y'].value


if __name__ == '__main__':
    unittest.main()
