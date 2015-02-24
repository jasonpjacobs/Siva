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



@pytest.fixture
def param_storage():

    class P_val(Parameter):
        dict_name = "value_param"

        def _store(self, dct):
            self._store_as_value(dct)

    class P_list(Parameter):
        dict_name = "list_param"

        def _store(self, dct):
            self._store_as_list(dct)


    class A(Component):
        pv = P_val()
        pl1 = P_list()
        pl2 = P_list()

    return A()

def test_storage(param_storage):
    c = param_storage

    assert "list_param" in c.__class__.__dict__
    assert "value_param" in c.__class__.__dict__

    assert 'pv' in c.value_param
    assert 'pl1' in c.list_param
    assert 'pl2' in c.list_param

if __name__ == '__main__':
    unittest.main()
