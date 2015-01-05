import pytest

from ..list_model import ListModel, ListView
from ..types import Typed, Str
from jase.types.test.mock import green_icon, blue_icon
from .modeltest import ModelTest
from ..qt_binding import Qt, QtCore, QtGui, QTest


class NameType(Str):
    def getIcon(self, obj):
        return obj.icon

class Mock(Typed):
    name = NameType('Hello World', icon=blue_icon)
    def __init__(self, str):
        self.name = str

    @property
    def icon(self):
        return green_icon

    def __str__(self):
        return "Mock({})".format(self.name)

class MockIndex:
    def __init__(self, row, col):
        self._row = row
        self._column = col
    def column(self):
        return self._column
    def row(self):
        return self._row

@pytest.fixture
def list_model():
    objects = [Mock(str='nmos'), Mock(str='pmos'), Mock(str='res'), Mock(str='cap'), Mock(str='inductor')]
    descriptors = Mock._descriptors

    assert objects[0]._descriptors is objects[1]._descriptors
    model = ListModel(data=objects, descriptors=descriptors, path="Properties",
                       columns = ['name'])
    return model



@pytest.fixture
def list_view(list_model):
    view = ListView(model=list_model)
    #view.setViewMode(QtGui.QListView.IconMode)
    #view.setFlow(QtGui.QListView.TopToBottom)
    view.setMovement(QtGui.QListView.Static)
    view.setWrapping(True)
    view.setIconSize(QtCore.QSize(30,30))
    view.setGeometry(100,100,150,600)
    view.setDragDropMode(QtGui.QAbstractItemView.DragOnly)
    return view


def test_empty_list(list_model):
    model = ListModel(data=None, descriptors=None, path="Properties",
                       columns = ['name'])

    view = ListView(model=model)
    assert len(view.model().descriptors) == 0
    view.show()

    view.set_model_data(list_model.model_data)

    assert len(view.model().descriptors) == 1
    view.show()

    interactive = debug = False
    if interactive:
        view.show()
        delay = 2000
    else:
        delay = 0

    QTest.qWaitForWindowShown(view)
    if interactive and debug:
        app = QtCore.QCoreApplication.instance()
        app.exec_()

def test_row_access(list_model):
    objects = list(list_model.model_data)

    assert len(objects) == 5

    for i in range(len(objects)):
        assert list_model.get_row(i) is objects[i]
        if i == 4:
            obj = objects[i]
            assert obj.icon is not None
            assert obj.name == "inductor"

    assert list_model.get_row(len(objects) + 1) is None


def test_icon_role(list_model):
    objects = list(list_model.model_data)

    index = list_model.index(4,0,QtCore.QModelIndex())
    assert index.isValid()

    icon = list_model.data(index, role=Qt.DecorationRole)
    assert icon is not None

    for i in range(len(objects)):
        index = list_model.index(i,0,QtCore.QModelIndex())
        icon = list_model.data(index, role=Qt.DecorationRole)
        if i < 5:
            print("i= ", i)
            assert icon is objects[i].icon

def test_indexing(list_model):
    topIndex1 = list_model.index ( 0, 1, QtCore.QModelIndex() )
    assert topIndex1 == QtCore.QModelIndex()


def test_column_access(list_model):
    assert list_model.columnCount(parent=None) == 1


def test_edit(list_view):
    interactive = False
    debug = True
    try:
        app = QtGui.QApplication([])
    except RuntimeError:
        app = QtCore.QCoreApplication.instance()


    if interactive:
        list_view.show()
        delay = 2000
    else:
        delay = 0

    QTest.qWaitForWindowShown(list_view)
    if interactive and debug:
        app.exec_()



def XXXtest_model(list_model):
    top = list_model.index ( 0, 0, QtCore.QModelIndex() )
    assert top == list_model.index ( 0, 0, QtCore.QModelIndex() )
    tester = ModelTest(model=list_model)
    tester.runAllTests()