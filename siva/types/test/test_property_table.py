import pytest

from siva.types.property_table import PropertyTable
from siva.types.types import Int, Str, Bool, Float, Typed
from siva.qt_bindings import Qt, QtCore, QtGui

pixmap = QtGui.QPixmap(100,100)
pixmap.fill(QtGui.QColor(Qt.blue))
blue_icon = QtGui.QIcon(pixmap)

pixmap = QtGui.QPixmap(100,100)
pixmap.fill(QtGui.QColor(Qt.green))
green_icon = QtGui.QIcon(pixmap)


class Mock(Typed):
    int = Int(20, editable=True, bold=True, desc="An integer", icon=blue_icon)
    str = Str('Hello World', italic=True, underline=True, font_color=QtCore.Qt.blue)
    bool = Bool(True, checkbox=True, icon=green_icon)
    float = Float(bold=True, desc="A float", tool_tip="A float between 0 and 100")

class I:
    def __init__(self, row, column, parent=None):
        self._row = row
        self._column = column

    def row(self):
        return self._row

    def column(self):
        return self._column

@pytest.fixture
def mock():
    return Mock()

@pytest.fixture
def table(mock):
    table = PropertyTable(mock, rows=['int', 'str', 'bool', 'float'])
    return table


def test_property_table_creation(mock):
    table = PropertyTable(mock)

    app = QtGui.QApplication.instance()
    tv = QtGui.QTableView()
    table = PropertyTable(mock, rows=['int', 'str', 'bool', 'float'])
    tv.setModel(table)
    if False:
        tv.show()
        app.exec_()


def test_property_table_index(table):


    assert table.data(I(0,0), Qt.DisplayRole) == "int"
    assert table.data(I(1,0), Qt.DisplayRole) == "str"
    assert table.data(I(2,0), Qt.DisplayRole) == "bool"
    assert table.data(I(3,0), Qt.DisplayRole) == "float"

    obj = table.obj
    assert table.data(I(0,1), Qt.DisplayRole) == str(obj.int)
    assert table.data(I(1,1), Qt.DisplayRole) == str(obj.str)
    assert table.data(I(2,1), Qt.DisplayRole) == str(obj.bool)
    assert table.data(I(3,1), Qt.DisplayRole) == str(obj.float)

def test_tool_tip(table):
    assert table.data(I(0,1), Qt.ToolTipRole) == "An integer"
    assert table.data(I(1,1), Qt.ToolTipRole) == None
    assert table.data(I(2,1), Qt.ToolTipRole) == None
    assert table.data(I(3,1), Qt.ToolTipRole) == "A float between 0 and 100"

def test_font_role(table):
    for i in range(4):
        font = table.data(I(i,1), Qt.FontRole)
        if i == 0 :
            assert font.bold() is True
            assert font.italic() is False
            assert font.underline() is False
        elif i == 1:
            assert font.italic() is True
            assert font.underline() is True
            assert font.bold() is False
        elif i == 3:
            assert font.bold() is True
            assert font.italic() is False
            assert font.underline() is False


def test_icon(table):
    for i in range(4):
        icon = table.data(I(i,1), Qt.DecorationRole)
        if i == 0:
            assert icon is blue_icon
        elif i == 2:
            assert icon is green_icon
        else:
            assert icon is None


def test_checkstate_role(table):
    for i in range(4):
        result = table.data(I(i,1), Qt.CheckStateRole)
        if i == 2:
            assert result is Qt.Unchecked


def test_set_data(table):
    obj = table.obj

    assert table.data(I(0,1), Qt.DisplayRole) == str(obj.int)
    assert table.data(I(1,1), Qt.DisplayRole) == str(obj.str)
    assert table.data(I(2,1), Qt.DisplayRole) == str(obj.bool)
    assert table.data(I(3,1), Qt.DisplayRole) == str(obj.float)


    table.setData(I(0,1), -1, Qt.EditRole)
    table.setData(I(1,1), "Goodbye, cruel world.", Qt.EditRole)
    table.setData(I(2,1), False, Qt.EditRole)
    table.setData(I(3,1), -1.2, Qt.EditRole)


    assert table.data(I(0,1), Qt.DisplayRole) == str(-1)
    assert table.data(I(1,1), Qt.DisplayRole) == str("Goodbye, cruel world.")
    assert table.data(I(2,1), Qt.DisplayRole) == str(False)
    assert table.data(I(3,1), Qt.DisplayRole) == str(-1.2)

    if False:
        app = QtGui.QApplication.instance()
        tv = QtGui.QTableView()
        tv.setModel(table)
        tv.show()
        app.exec_()

