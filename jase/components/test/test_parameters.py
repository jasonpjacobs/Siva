__author__ = 'Jase'

import pytest
from ..component import Component
from ..parameter import Parameter, Float

@pytest.fixture
def simple():

    class A(Component):
        x = Parameter(2.34)
        y = Parameter(name='not_x')
        f = Float(2.2)


    a = A(name='root')
    return a


def test_names(simple):
    a = simple

    assert a.name == 'root'
    assert 'x' in a.params
    assert 'y' in a.params
    assert 'f' in a.params

    assert a.x == a.params['x'].value
    assert a.y == a.params['y'].value

    assert a.f == a.params['f'].value

@pytest.fixture
def param_storage():

    class P_val(Parameter):
        registry_name = "value_param"

        def _store(self, class_dct, registry_name):
            self._store_as_key_value_pair(class_dct, registry_name)

    class P_list(Parameter):
        registry_name = "list_param"

        def _store(self, class_dct, registry_name):
            self._store_as_list(class_dct, registry_name)


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

    assert len(c.list_param) == 2

    assert 'pl1' in [item.name for item in c.list_param]
    assert 'pl2' in [item.name for item in c.list_param]

if __name__ == '__main__':
    unittest.main()
