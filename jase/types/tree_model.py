"""
@License
"""

# Python Imports
from collections import OrderedDict

# Third party imports
from ..qt_bindings import Qt, QtCore, QtGui

# Local imports
from jase.types.hierarchy import Node


DB = False
class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, root=None, parent=None, descriptors=None, headers=None):

        super(TreeModel, self).__init__(parent)

        self.numColumns = 0

        # From the Qt "Simple Tree Model Example":  The root item in the tree structure has no parent
        # item and it is never referenced outside the model.
        #del.index(0,0, QModelIndex())
        if root is None:
            self.root = Node()
        else:
            self.root = root

        if descriptors is None:
            if hasattr(root, '_descriptors'):
                self.descriptors = root._descriptors
            else:
                self.descriptors = OrderedDict()
        else:
            self.descriptors = descriptors

        if headers is None:
            self.headers = [d.attr for d in self.descriptors.values()]
        else:
            self.headers = headers

    # ----------------------------------------------------------
    #            QAbstractItemModel Interface
    # ----------------------------------------------------------
    def index(self, row, column, parentIndex):
        "Returns the index of the item in the model specified by the given row, column and parent index."

        if not self.hasIndex(row, column, parentIndex):
            return QtCore.QModelIndex()

        if not parentIndex.isValid():
            # If requesting the root node,
            # the column value doesn't matter
            return self.createIndex(row, column, self.root)

        else:
            parent = self.getItem(parentIndex)
            child = parent.get_child_by_index(row)
            return self.createIndex(row, column, child)

    def parent(self, childIndex):
        "Returns an index to the parent of child indexed by childIndex"

        if not childIndex.isValid():
            return QtCore.QModelIndex()

        child = childIndex.internalPointer()

        # The parent of the root is an invalid QModelIndex
        if child is self.root:
            return QtCore.QModelIndex()

        parent = child.get_parent()
        if parent is None:
            return QtCore.QModelIndex()

        grandparent = parent.get_parent()
        if grandparent:
            row = grandparent.find_index_of_child(parent)
        else:
            row = 0
        return self.createIndex(row, 0, parent) # Column is 0 for this tree implementation




    def data(self, index, role):
        if DB:
            print("Data called:", index.row(), index.column(), index.internalPointer().name)

        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop|Qt.AlignLeft)

        if not index.isValid():
            return None

        obj = self.getItem(index)

        col = index.column()
        row = index.row()
        descriptor = obj._descriptors.get(self.headers[col])
        assert descriptor is not None

        if role == Qt.DisplayRole:
            if descriptor.checkbox:
                # No text, just a checkbox
                return None
            return descriptor.data(obj)

        if role == Qt.EditRole:
            return descriptor.data(obj)

        if role == Qt.UserRole:
            return None

        if role == Qt.ToolTipRole:
            return descriptor.tool_tip

        if role == Qt.DecorationRole:
            return descriptor.getIcon(obj)

        if role == Qt.FontRole:
            return descriptor.getFont(obj)

        if role == Qt.ForegroundRole:
            return descriptor.getFontColor(obj)

        if role == Qt.BackgroundRole:
            return descriptor.getBGColor(obj)

        if role == Qt.CheckStateRole:
            if obj is None:
                return None
            if not descriptor.checkbox:
                return None
            return descriptor.checkState(obj)
        return None

    def setData(self, index, value, role):
        descriptor = self.get_descriptor(index)

        obj = self.getItem(index)
        result = False

        if role == Qt.EditRole and descriptor.editable:
            result = descriptor.setData(obj, value)

        if role==Qt.CheckStateRole:
            if descriptor.checkbox:
                if value == Qt.Checked:
                    descriptor.setData(obj, True)
                elif value == Qt.Unchecked:
                    descriptor.setData(obj, False)
            result = True

        if result:
            self.dataChanged.emit(index, index)
        return False

    def flags(self, index):
        if not index.isValid():
            return 0
        descriptor = self.get_descriptor(index)
        obj = self.getItem(index)
        flags = descriptor.flags(obj)
        return flags

    def columnCount(self, parent):
        return len(self.headers)

    def rowCount(self, parentIndex):
        "Returns the number of rows under the given parent"

        # Only column 0 has any children...
        if parentIndex.column() > 0:
            return 0
        if not parentIndex.isValid():
            # Root element(s)
            return 1
        parent = self.getItem(parentIndex)
        return len(parent.get_children())

    def hasIndex(self, row, column, parentIndex=QtCore.QModelIndex()):
        """Returns true if the model returns a valid PySide.QtCore.QModelIndex for row and column with parent,
        otherwise returns false.
        """

        if row < 0 or column < 0:
            return False
        elif row < self.rowCount(parentIndex) and column < self.columnCount(parentIndex):
            return True
        else:
            return False

    def hasChildren(self, parentIndex):
        parent = self.getItem(parentIndex)
        return len(parent.get_children()) > 0

    def headerData(self, section, orientation, role):
        if DB:
            print("HeaderData (", section, "): ", self.descriptors[section])
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.headers[section]
            except IndexError:
                return None
        return None

    # ----------------------------------------------------------
    #            Helper Methods
    # ----------------------------------------------------------

    def getItem(self, index):
        "Retrieves the model item referred to by the QModelIndex"
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root


    def get_descriptor(self, index):
        attr = self.headers[index.column()]
        descriptor = self.descriptors[attr]
        return descriptor

class TreeView(QtGui.QTreeView):

    def __init__(self, parent=None, model=None, path=None):
        super(TreeView, self).__init__(parent)
        self.setSelectionBehavior(QtGui.QTreeView.SelectItems)
        self.setUniformRowHeights(True)

        if model is None:
            model = TreeModel(self)
        self.setModel(model)
        self.expanded()

    def show_headers(self,headers):
        for header in headers:
            self.model().headers.append(header)
    """
    def currentFields(self):
        return self.model().asRecord(self.currentIndex())


    def activated(self, index):
        self.emit(SIGNAL("activated"), self.model().asRecord(index))

    """
    def expanded(self):
        for column in range(self.model().columnCount(
                            QtCore.QModelIndex()
                                        )):
            self.resizeColumnToContents(column)

