import pytest

from ..types import Str, Int, Bool, Float, Typed
from ..tree_model import TreeModel, TreeView
from ..hierarchy import Node
from jase.types.test.mock import blue_icon, green_icon
from .modeltest import ModelTest
from ...qt_bindings import Qt, QtCore, QtGui, QTest


class ContractorType(Bool):
    def getIcon(self, obj):
        return green_icon if getattr(obj, self.attr) else blue_icon

class TitleType(Str):
    def getFont(self, obj):
        font = super().getFont(obj)
        if obj.title in ['CEO', 'COO', 'CTO']:
            font.setBold(True)
        return font

class Person(Node, Typed):
    name = Str("Name")
    age = Int(min=0, max=100)
    id = Int(desc="Employee ID")
    title = TitleType()
    contractor = ContractorType(desc="Full time, regular employee", checkbox=True)
    salary = Float(min=0, bg_color='#DDDDDD', font_color='blue')

    def __init__(self, name, age, id, title, contractor=False, parent=None, salary=0):
        super().__init__(parent)
        self.name=name
        self.age=age
        self.id=id
        self.title = title
        self.contractor = contractor
        self.salary = salary

        self._manifest = None


    def __repr__(self):
        return "Person({})".format(self.name)


@pytest.fixture
def people():
    alice = Person(name='Alice', age=30, id=1, title="CEO", salary=5000.0)
    bob = Person(name='Bob', age=31, id=2, title="COO", salary=4000.0)
    charlie = Person( name='Charlie', age=32, id=3, title="CTO", salary=4000.0)
    david = Person(name='David', age=33, id=4, title="VP, Marketing", salary=3500.0)
    elena = Person(name='Elena', age=34, id=5, title="VP, Engineering", salary=3500.0)
    frank = Person(name='Frank', age=35, id=6, title="Engineering Manager", salary=3000.0)
    gina = Person(name='Gina', age=36, id=7, title="Principle Engineer", salary=3000.0)
    helen = Person(name='Helen', age=37, id=8, title="Engineer", salary=3000.0)
    ian = Person(name='Ian', age=38, id=9, title="Engineer", salary=2500.0, contractor=True)

    people = (alice, bob, charlie, david, elena, frank, gina, helen, ian)
    return people

@pytest.fixture
def tree(people):
    (alice, bob, charlie, david, elena, frank, gina, helen, ian) = people

    alice.add_child(bob)
    alice.add_child(charlie)

    bob.add_child(david)
    bob.add_child(elena)

    elena.add_child(frank)
    elena.add_child(gina)

    frank.add_child(helen)
    frank.add_child(ian)

    tree = TreeModel(root=alice, headers=['name', 'age', 'id', 'title', 'contractor', 'salary'])
    return tree


def test_model(tree):
    top = tree.index ( 0, 0, QtCore.QModelIndex() )
    assert top == tree.index ( 0, 0, QtCore.QModelIndex() )

    assert tree.rowCount(QtCore.QModelIndex()) == 1
    print("num rows", tree.rowCount(QtCore.QModelIndex()))

    assert len(tree.headers) > 0

    assert tree.columnCount(QtCore.QModelIndex()) == 6
    print("num cols", tree.columnCount(QtCore.QModelIndex()))


    result = tree.hasIndex(0,0)
    assert result is True

    root_index = tree.index(0,0, QtCore.QModelIndex())
    assert root_index.internalPointer() is not None

    root = root_index.internalPointer()
    assert root.name == "Alice"

    child_index = tree.index(0, 0, root_index)
    child = child_index.internalPointer()
    assert child.name == "Bob"

    grandchild_index_1 = tree.index(0, 0, child_index)
    grandchild_1 = grandchild_index_1.internalPointer()
    assert grandchild_1.name == "David"

    grandchild_index_2 = tree.index(1, 0, child_index)
    grandchild_2 = grandchild_index_2.internalPointer()
    assert grandchild_2.name == "Elena"


    assert tree.parent( grandchild_index_1 ) == child_index
    assert tree.parent( grandchild_index_2 ) == child_index

    ai = tree.index(0,0, QtCore.QModelIndex())
    bi = tree.index(0,0, ai)
    ci = tree.index(1,0, ai)

    di = tree.index(0,0, bi)
    ei = tree.index(1, 0, bi)

    fi = tree.index(0, 0, ei)
    gi = tree.index(1, 0, ei)

    hi = tree.index(0, 0, fi)
    ii = tree.index(1, 0, fi)

    assert ai.internalPointer().name == "Alice"
    assert bi.internalPointer().name == "Bob"
    assert ci.internalPointer().name == "Charlie"
    assert di.internalPointer().name == "David"
    assert ei.internalPointer().name == "Elena"
    assert fi.internalPointer().name == "Frank"
    assert gi.internalPointer().name == "Gina"
    assert hi.internalPointer().name == "Helen"
    assert ii.internalPointer().name == "Ian"


    assert tree.parent(hi).internalPointer().name == "Frank"
    assert tree.parent(hi) == fi
    assert tree.parent(ii).internalPointer().name == "Frank"


    index = tree.index ( 0, 0, fi )
    assert tree.parent( index ) == fi
    tester = ModelTest(model=tree)
    tester.runAllTests()


def test_tree_data(tree):

    ai = tree.index(0,0, QtCore.QModelIndex())
    bi = tree.index(0,0, ai)
    ci = tree.index(1,0, ai)
    di = tree.index(0,0, bi)
    ei = tree.index(1, 0, bi)
    fi = tree.index(0, 0, ei)
    gi = tree.index(1, 0, ei)
    hi = tree.index(0, 0, fi)
    ii = tree.index(1, 0, fi)

    assert tree.data(tree.index(0,0, QtCore.QModelIndex()), Qt.DisplayRole) == "Alice"
    assert tree.data(tree.index(0,1, QtCore.QModelIndex()), Qt.DisplayRole) == "30"
    assert tree.data(tree.index(0,2, QtCore.QModelIndex()), Qt.DisplayRole) == "1"
    assert tree.data(tree.index(0,3, QtCore.QModelIndex()), Qt.DisplayRole) == "CEO"
    assert tree.data(tree.index(0,4, QtCore.QModelIndex()), Qt.DisplayRole) == None


    assert tree.data(tree.index(0,4, QtCore.QModelIndex()), Qt.DecorationRole) is blue_icon

    font = tree.data(tree.index(0,3, QtCore.QModelIndex()), Qt.FontRole)
    assert font.bold() is True

    assert tree.flags(ai) is not 0



@pytest.fixture
def tree_view(tree):
    view = TreeView(model=tree, parent=None, path='')
    return view

def test_tree_creation(tree):
    pass

def test_tree_view(tree_view):

    interactive = True

    if interactive:
        app = QtGui.QApplication.instance()
        tree_view.show()
        QTest.qWaitForWindowShown(tree_view)

        app.exec_()


