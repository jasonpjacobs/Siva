import pytest

from siva.types.table_model import TableModel, TableView
from siva.tests.mock import Mock
from siva.tests.modeltest import ModelTest
from siva.qt_bindings import Qt, QtCore, QtGui, QTest


class MockIndex:
    def __init__(self, row, col):
        self._row = row
        self._column = col
    def column(self):
        return self._column
    def row(self):
        return self._row

@pytest.fixture
def table():
    objects = [Mock(str='A'), Mock(str='B'), Mock(str='C'), Mock(str='D'), Mock(str='E'), Mock(str='This is a long name'),]
    descriptors = Mock._descriptors

    assert objects[0]._descriptors is objects[1]._descriptors
    model = TableModel(data=objects, descriptors=descriptors, path="Properties",
                       columns = ['str', 'fixed', 'int', 'float', 'bool', 'enum', 'status'])
    return model

def test_get_descriptor(table):
    objects = table.model_data

    descriptors = [table.descriptors[c] for c in table.columns]

    for i in range(len(descriptors)):
        index = MockIndex(col=i, row=0)
        descriptor = descriptors[i]
        try:
            indexed_descriptor = table.get_descriptor(index)
            assert indexed_descriptor.attr == descriptor.attr
        except AssertionError:
            raise AssertionError("table.get_descriptor({}) got {}, was expecting {}".format(i, indexed_descriptor.attr, descriptor.attr))

def test_row_access(table):
    objects = list(table.model_data.values())
    for i in range(len(objects)):
        assert table.get_row(i) is objects[i]

    assert table.get_row(len(objects) + 1) is None

def test_path_access(table):
    objects = list(table.model_data.values())
    descriptors = table.descriptors
    for i in range(len(objects)):
        for j in range(len(descriptors)):
            path = table.get_path(MockIndex(row=i, col=j), mode="relative")
            assert len(path) == 2
            attr = path[1]
            print(attr, path)

def test_url_access(table):
    url = table.get_url(MockIndex(row=0, col=0))
    value = table.resolve_url(url)
    assert url == 'i0.str'
    assert value == 'A'
    assert table.resolve_url(table.get_url(MockIndex(row=0, col=0))) == "A"
    assert table.resolve_url(table.get_url(MockIndex(row=1, col=0))) == "B"
    assert table.resolve_url(table.get_url(MockIndex(row=2, col=0))) == "C"
    assert table.resolve_url(table.get_url(MockIndex(row=3, col=0))) == "D"
    assert table.resolve_url(table.get_url(MockIndex(row=4, col=0))) == "E"

def test_model(table):
    top = table.index ( 0, 0, QtCore.QModelIndex() )
    assert top == table.index ( 0, 0, QtCore.QModelIndex() )
    tester = ModelTest(model=table)
    tester.runAllTests()

@pytest.fixture
def table_view(table):
    view = TableView(model=table, parent=None, path='')
    return view

class TableViewEventHelper(object):
    """ A helper class to simplify sending events to specific row/column locations of a TableView.

    This StackOverflow answer really helped me get on the right track:
    http://stackoverflow.com/questions/12604739/how-can-you-edit-a-qtableview-cell-from-a-qtest-unit-test
    """
    def __init__(self, table_view, delay=-1):
        self.table_view = table_view
        self.delay = delay

    def pt(self, row, col):
        # Returns a QPoint coordinates for the desired row and column
        x = self.table_view.columnViewportPosition(col) + 5;
        y = self.table_view.rowViewportPosition(row) + 5;
        return QtCore.QPoint(x, y)

    def click(self, row, col, button=Qt.LeftButton, modifier=Qt.NoModifier, delay=-1):
        QTest.mouseClick(self.table_view.viewport(), Qt.LeftButton, Qt.NoModifier, self.pt(row,col), self.delay)

    def dclick(self, row, col, button=Qt.LeftButton, modifier=Qt.NoModifier, delay=-1):
        QTest.mouseDClick(self.table_view.viewport(), Qt.LeftButton, Qt.NoModifier, self.pt(row,col), self.delay)

    def down(self):
        QTest.keyClick(self.table_view.viewport().focusWidget(), Qt.Key_Down, self.delay)

    def enter(self):
        QTest.keyClick(self.table_view.viewport().focusWidget(), Qt.Key_Return, self.delay)

    def text(self, txt, enter=True):
        QTest.keyClicks(self.table_view.viewport().focusWidget(), txt, self.delay)
        if enter:
            QTest.keyClick(self.table_view.viewport().focusWidget(), Qt.Key_Return, self.delay)


def test_empty_view(table):
    table_view = TableView(parent=None, path='')
    table_view.show()


def test_delayed_table_model(table):
    interactive = False

    table_view = TableView(parent=None, path='')
    data = table.model_data
    del data[list(data.keys())[3]]
    table_view.set_model_data(data, columns = ['str', 'fixed', 'int', 'float', 'bool', 'enum'])
    table_view.show()

    if interactive:
        table_view.setGeometry(100,100,800,400)
        table_view.show()
        delay = 2000
    else:
        delay = 0

    ev = TableViewEventHelper(table_view, delay=delay)
    QTest.qWaitForWindowShown(table_view)
    ev.click(0,0)

    try:
        app = QtGui.QApplication([])
    except RuntimeError:
        app = QtCore.QCoreApplication.instance()

    if interactive and False:
        app.exec_()

def test_item_roles(table_view):
    # Set to true during development so you can see the test being run
    interactive = True

    if interactive:
        table_view.setGeometry(100,100,800,400)
        table_view.show()
        delay = 2000
    else:
        delay = 0

    ev = TableViewEventHelper(table_view, delay=delay)
    QTest.qWaitForWindowShown(table_view)
    ev.click(0,0)

    model = table_view.model()

    for i in range(7):
        index = model.index(0,i,QtCore.QModelIndex())

        if i == 0:
            assert model.data(index, role=Qt.DisplayRole) == 'A'

            font = model.data(index, role=Qt.FontRole)
            assert font.underline() is True
        if i == 6:
            pass
            #assert model.data(model.index(0,i,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'OK'



def test_item_edit(table_view):
    """Tests editing items in a TableView
    """

    # Set to true during development so you can see the test being run
    interactive = False
    debug = True

    if interactive:
        table_view.setGeometry(100,100,800,400)
        table_view.show()
        delay = 200
    else:
        delay = 0

    ev = TableViewEventHelper(table_view, delay=delay)
    QTest.qWaitForWindowShown(table_view)


    try:
        app = QtGui.QApplication([])
    except RuntimeError:
        app = QtCore.QCoreApplication.instance()

    if interactive and debug:
        app.exec_()
    model = table_view.model()

    # Make sure default Mock data hasn't changed
    assert model.data(model.index(0,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'A'
    assert model.data(model.index(1,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'B'
    assert model.data(model.index(2,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'C'
    assert model.data(model.index(3,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'D'
    assert model.data(model.index(4,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'E'
    assert model.data(model.index(5,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'This is a long name'

    # Edit the first column, a string
    for i in range(model.rowCount(QtCore.QModelIndex())):
        txt = 'newvalue_row' + str(i)
        ev.click(i,0)
        ev.dclick(i,0)
        ev.text(txt)

    ev.click(0,0)

    for i in range(model.rowCount(QtCore.QModelIndex())):
        txt = 'newvalue_row' + str(i)
        assert model.data(model.index(i,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == txt

    # Try to edit the second column.  An un-editable integer
    for i in range(model.rowCount(QtCore.QModelIndex())):
        ev.click(i,2)
        ev.dclick(i,1)
        ev.text(str(i))

    # Extra click to close editing
    ev.click(0,0)
    for i in range(model.rowCount(QtCore.QModelIndex())):
        txt = 'newvalue_row' + str(i)
        assert model.data(model.index(i,1,QtCore.QModelIndex()), role=Qt.DisplayRole) == '0'

    # Edit the third column, an editable integer
    for i in range(model.rowCount(QtCore.QModelIndex())):
        ev.click(i,2)
        ev.dclick(i,2)
        ev.text(str(i))

    # Extra click to close editing
    ev.click(0,0)
    for i in range(model.rowCount(QtCore.QModelIndex())):
        assert model.data(model.index(i,2,QtCore.QModelIndex()), role=Qt.DisplayRole) == str(i)

    # Edit the 4th column, an editable float
    for i in range(model.rowCount(QtCore.QModelIndex())):
        ev.click(i,3)
        ev.dclick(i,3)
        ev.text(str(i/10))

    # Extra click to close editing
    ev.click(0,0)
    for i in range(model.rowCount(QtCore.QModelIndex())):
        assert model.data(model.index(i,3,QtCore.QModelIndex()), role=Qt.DisplayRole) == str(i/10)


    # Edit the 5th column, an checkable boolean
    # Ensure they are all checked
    for i in range(model.rowCount(QtCore.QModelIndex())):
        assert model.data(model.index(i,4,QtCore.QModelIndex()), role=Qt.CheckStateRole) == QtCore.Qt.CheckState.Checked

    # Click the check box
    for i in range(model.rowCount(QtCore.QModelIndex())):
        ev.click(i,4)

    # Extra click to close editing
    ev.click(0,0)
    for i in range(model.rowCount(QtCore.QModelIndex())):
        assert model.data(model.index(i,4,QtCore.QModelIndex()), role=Qt.CheckStateRole) == QtCore.Qt.CheckState.Unchecked

    # Edit the 5th column, an string whose value is chosen via a combobox
    for i in range(model.rowCount(QtCore.QModelIndex())):
        assert model.data(model.index(i,5,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'Type A'

    # This will chose the 3rd item in the combobox "Type C"
    for i in range(model.rowCount(QtCore.QModelIndex())):
        ev.click(i, 5)
        ev.dclick(i, 5)
        ev.down()
        ev.down()
        ev.enter()

    ev.click(0,0)
    for i in range(model.rowCount(QtCore.QModelIndex())):
        assert model.data(model.index(i,5,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'Type C'

    # Try to edit the 7th column, a read-only string that depends on 'str' (Column #1 )
    for i in range(model.rowCount(QtCore.QModelIndex())):
        pass
        # TODO:  Fix formula based descriptors
        #assert model.data(model.index(i,6,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'OK' if i < 3 else 'Bad'

    for i in range(model.rowCount(QtCore.QModelIndex())):
        ev.click(i, 6)
        ev.dclick(i, 6)
        ev.down()
        ev.down()
        ev.enter()

    ev.click(0,0)

    for i in range(model.rowCount(QtCore.QModelIndex())):
        # TODO:  Fix formula based descriptors
        #assert model.data(model.index(i,6,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'OK' if i < 3 else 'Bad'
        pass

def test_insert_remove_rows(table_view):
    objects = [Mock(str='A'), Mock(str='B'), Mock(str='C'), Mock(str='D'), Mock(str='E'), Mock(str='This is a long name'),]

    model = table_view.model()
    # Make sure default Mock data hasn't changed
    assert model.data(model.index(0,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'A'
    assert model.data(model.index(1,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'B'
    assert model.data(model.index(2,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'C'
    assert model.data(model.index(3,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'D'
    assert model.data(model.index(4,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'E'
    assert model.data(model.index(5,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'This is a long name'

    rows = [Mock(str='I1'), Mock(str='I2'), Mock(str='I3')]
    model.insertRows(1, rows, QtCore.QModelIndex())

    # Make sure default Mock data hasn't changed
    assert model.data(model.index(0,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'A'
    assert model.data(model.index(1,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'I1'
    assert model.data(model.index(2,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'I2'
    assert model.data(model.index(3,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'I3'
    assert model.data(model.index(4,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'B'

    model.removeRows(1, 3, QtCore.QModelIndex())

    assert model.data(model.index(0,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'A'
    assert model.data(model.index(1,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'B'
    assert model.data(model.index(2,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'C'
    assert model.data(model.index(3,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'D'
    assert model.data(model.index(4,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'E'
    assert model.data(model.index(5,0,QtCore.QModelIndex()), role=Qt.DisplayRole) == 'This is a long name'

def test_removeListOfRows(table_view):
    pass

def test_dropMimeData(table_view):
    pass

