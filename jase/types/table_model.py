"""
@License
"""

# Python Imports
from pdb import set_trace as db
from collections import OrderedDict


from ..qt_bindings import Qt, QtCore, QtGui

# Local imports
from jase.types.hierarchy import Node

# ================================================================
#               Table Model
# ================================================================
class TableModel(QtCore.QAbstractTableModel):
    """ A TableModel that interfaces to a list of objects. The list of
    objects form the rows of the table.  The object's attributes are used for the columns.

    Attribute values can be retrieved by a URL of the form item_name.attr_name.

    TODO:  The original version of this module was written in Python 2.7, where
    dict keys and values methods returned lists.  Now that Python 3 dicts return
    Views, I've updated the code to use list comprehensions to translate views into
    lists.  This is a little inefficient, and I should probably store the rows as
    native lists, and a dict to map row number to object name.
    """
    PROJ_NAME = "Table"
    URI_SCHEME = "%s://" % (PROJ_NAME)
    LINK_MIME_TYPE = "application/%s-url" % (PROJ_NAME)
    DUMP_MIME_TYPE = "application/%s-dump" % (PROJ_NAME)

    def __init__(self, data=None, descriptors=None, parent=None, columns=None, path="", parent_model=None):
        super(TableModel, self).__init__(parent=None)

        self.path = path
        self.tree_node = Node(parent=parent_model)

        self.descriptors = OrderedDict()
        # Convert the list of objects into an internal representation
        self.set_model_data(data)

        if descriptors is None:
            for item in data:
                dct = getattr(item, '_descriptors', None)
                if dct:
                    self.descriptors.update(item._descriptors)
        else:
            self.descriptors = descriptors

        assert(self.descriptors is not None)

        # 'columns' is a list of attributes to display.  If None, displays all of them.
        if columns is None:
            columns = [k for k in self.descriptors.keys()]

        self.columns = columns
        self.setSupportedDragActions(Qt.CopyAction | Qt.LinkAction | Qt.MoveAction)

    def set_model_data(self, data):
        """ Stores model data as an ordered dict of name, object pairs.
        """
        if data is None:
            data = {}
        if type(data) is list:
            # Create names for the data
            if set([hasattr(o,'name') for o in data]) == (True):
                data = {o.name: o for o in data}
            else:
                data = OrderedDict([ ("i"+str(n),data[n]) for n in range(len(data))])

        self.model_data=data

        for item in data.values():
            dct = getattr(item, '_descriptors', None)
            if dct:
                self.descriptors.update(item._descriptors)

    # Helper methods
    def get_descriptor(self, index):
        'Helper function to return the descriptor associated with this column.  Used in most of the TableModel interface'
        column = index.column()
        column_name = self.columns[column]
        descriptor = self.descriptors[column_name]
        return descriptor

    def get_row(self, row):
        """Retrieves an object from the model by row index"""
        if row < len(self.model_data):
            return [r for r in self.model_data.values()][row]
        return None

    def get_obj_name(self, row):
        """Returns the object name from the model by row index"""
        return [k for k in self.model_data.keys()][row]

    def get_attr(self, index):
        descriptor = self.get_descriptor(index)
        return descriptor.attr

    def createNewRow(self, index=None):
        cls = self.model_data[0].__class__
        obj = cls()

        row = index.row()
        self.beginInsertRows(index, row, row)
        self.model_data.insert(row, obj)
        self.endInsertRows()

        self.dataChanged.emit(index, index)
        return obj

    # ================================================================
    # TableModel Interface - View Methods
    # ================================================================
    def data(self, index, role):
        descriptor = self.get_descriptor(index)
        row = index.row()
        column = index.column()
        obj = self.get_row(row)

        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            data = descriptor.data(obj)
            if data and data.startswith(self.URI_SCHEME):
                pass
                db()
            return descriptor.data(obj)

        if role == Qt.EditRole:
            return descriptor.data(obj)

        if role == Qt.UserRole:
            return None

        if role == Qt.ToolTipRole:
            return descriptor.tool_tip

        if role == Qt.DecorationRole:
            if row < self.rowCount() - 1:
                return descriptor.getIcon(obj)

        if role == Qt.FontRole:
            return descriptor.getFont(obj)

        if role == Qt.ForegroundRole:
            if row == self.rowCount() - 1:
                return None
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

    def hasChildren(self, parent):
        return len(self.model_data) > 0

    def parent(self, index):
        """
        """
        # Table models have no parent
        return QtCore.QModelIndex()

    def index(self, row, column, parent):
        if row in range(len(self.model_data)) and column in range(len(self.columns)):
            return self.createIndex(row, column, None)
        else:
            return QtCore.QModelIndex()

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                name = self.columns[section]
                name = name.title().replace('_', ' ')
                return name

            if orientation == Qt.Vertical:
                return section

        # Display the descriptors 'desc' attribute as a tool tip
        if role == Qt.ToolTipRole:
            try:
                name = self.columns[section]
                descriptor = self.model_data[0].descriptors[name]
                if descriptor.desc is not None:
                    return QtCore.QString(descriptor.desc)
            except:
                import pdb
                pdb.set_trace()
                raise
        # Default action
        return None

    def rowCount(self, parent=QtCore.QModelIndex()):
        """ Returns the number of rows under the given parent. When the parent is valid it means that rowCount is
        returning the number of children of parent.

        Note:  When implementing a table based model, PySide.QtCore.QAbstractItemModel.rowCount() should
        return 0 when the parent is valid.

        (From the QAbstractTableModel documentation)

        Table models rows don't have a parent, so the empty parent index should always be used
        to access rows
        """
        if parent.isValid():
            return 0

        # Top level items should have an invalid parent index.
        return len(self.model_data)

    def columnCount(self, parent):
        return len(self.columns)

    # ================================================================
    # TableModel Interface - Edit Methods
    # ================================================================
    def flags(self, index):
        if not index.isValid():
            return 0
        row = index.row()
        column = index.column()
        descriptor = self.get_descriptor(index)
        obj = self.get_row(index.row())
        return descriptor.flags(obj)

    def setData(self, index, value, role):
        if index.row() == self.rowCount() and role == Qt.EditRole:
            obj = self.createNewRow(index)

        descriptor = self.get_descriptor(index)
        obj = self.get_row(index.row())
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

    def insertRows(self, position, rows, parentIndex):
        if type(rows) is not list:
            rows = [rows]
        self.beginInsertRows(QtCore.QModelIndex(), position, position + len(rows)-1)
        current_rows = list(self.model_data.values())
        new_rows = list(current_rows[:position] + rows + current_rows[position:])
        self.set_model_data(new_rows)
        self.endInsertRows()
        return True

    def removeRows(self, position, num_rows, parent):
        """ Removes rows from a model, give the position of the 1st row
        and the number of rows to remove"
        """
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + num_rows)
        keys = list(self.model_data.keys())[position:position + num_rows]
        for key in keys:
            del self.model_data[key]
        self.endRemoveRows()
        return True

    def removeListOfRows(self, indices):
        """ Removes a list of rows (by model index) from the model"""

        # Sort in reverse order so the indices of delete
        # rows don't change as the previous entries are deleted
        rows = [index.row() for index in indices]
        rows = sorted(list(rows), reverse=True)
        start = rows[-1]
        stop =  rows[0]

        self.beginRemoveRows(self.createIndex(-1,-1, None), start, stop)
        for index in rows:
            if index != -1:  # Returned if the index was not valid
                del self.model_data.values()[index]

        self.endRemoveRows()
        self.dataChanged.emit(indices[0], indices[-1])
        self.modelReset.emit()

    # ================================================================
    # TableModel Interface - Drag, Drop, MIME data methods
    # ================================================================
    def supportedDropActions(self):
        """Default to these three.  Child classes should re-implement"""
        return Qt.CopyAction | Qt.MoveAction | Qt.LinkAction

    def mimeTypes(self):
        types = []
        types.append('text/plain')
        types.append(self.LINK_MIME_TYPE)
        types.append(self.DUMP_MIME_TYPE)
        return types

    def mimeData(self, listOfItemIndexes):
        index = listOfItemIndexes[0]
        obj = self.get_row(index.row())
        attr = [k for k in self.descriptors.keys()][index.column()]
        value = getattr(obj, attr)

        url= self.get_url(index)
        data = QtCore.QMimeData()
        data.setData(self.LINK_MIME_TYPE, url)
        data.setText(str(value))
        return data

    def dropMimeData(self, data, action, row, column, parent):
        """From the Qt documentation:  When row and column are -1 it means that the dropped data should be considered as
        dropped directly on parent.  Usually this will mean appending the data as child items of parent. If row and
        column are greater than or equal zero, it means that the drop occurred just before the specified row and column
        in the specified parent."""

        row = parent.row()
        column = parent.column()
        obj = self.get_row(row)
        attr_name = self.columns[column]
        descriptor = self.descriptors[attr_name]

        if descriptor.editable is False:
            return True

        if data.hasFormat(self.DUMP_MIME_TYPE):
            data = data.data(self.DUMP_MIME_TYPE)
            new_obj = cPickle.loads(txt)
            result = self.setData(parent, new_obj, Qt.EditRole)

        if data.hasFormat(self.LINK_MIME_TYPE):
            link = str(data.data(self.LINK_MIME_TYPE))
            if action == Qt.LinkAction:
                # Get the URL
                result = self.setData(parent, link, Qt.EditRole)
            else:
                # Get the object's value and set it
                data = self.resolve_url(link)
                result = self.setData(parent, link, Qt.EditRole)
        elif data.hasText():
            db()
            txt = data.text()
            result = descriptor.set(txt)

        return result


    def get_path(self, index, mode="relative"):
        """Retrieves the hierarchical path to the indexed item in the table model.
        The path itself is a list where each element is a path component.
        """
        attr = self.get_attr(index)

        # Get the path to myself
        if mode == "absolute":
            path = self.tree_node.get_path()
        else:
            path = []

        # Append the instance name (row)
        path.append(self.get_obj_name(index.row()))

        # And attribute (column)
        path.append(attr)
        return path

    def get_url(self, index, mode="relative", sep="."):
        """ Returns a URL to the indexed item in the model"""
        # Get the path components
        path = self.get_path(index, mode=mode)
        if mode == "relative":
            return sep.join(path)
        else:
            raise NotImplementedError("Only relative URL is supported")

    def resolve_url(self, path, sep="."):
        """ Resolves a URL to an attribute or item in the model.

        For now, it is assumed the path will be relative:  row_name.attr_name
        """
        path = path.split(sep)
        if len(path) == 1:
            pass
        elif len(path) == 2:
            row_name, attr = path
            obj = self.model_data[row_name]
            value = getattr(obj, attr)
            return value
        else:
            raise ValueError("Could not parse the URL")





    def get_value_by_url(self, url):
        """Resolves a URL to get the object's attribute value"""
        pass


# ================================================================
#               Property Table View Class
# ================================================================
class TableView(QtGui.QTableView):
    """ A view to display a list of objects, with columns for the object's attributes.
        This usually means all objects in the list have the same attributes.
    """

    def __init__(self, data=None, descriptors=None, model=None, parent=None, path='', ):
        super(TableView, self).__init__(parent=parent)

        if model is not None:
            pass
        elif data is None:
            if model is None:
                model=TableModel(data=[], descriptors=None, path=path)
            else:
                model=TableModel(data=data, descriptors=descriptors, path=path)
        else:
            model=TableModel(data=data, descriptors=descriptors, path=path)

        self.setModel(model)
        model.modelReset.connect(self.on_model_reset)
        model.columnsInserted.connect(self.columnsInserted)
        self.on_model_reset()

        self.setShowGrid(True)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        # Drag and Drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

    def set_model_data(self, data, columns=None):
        model = self.model()
        model.set_model_data(data)
        if columns is not None:
            model.columns = columns
        model.reset()

    def on_model_reset(self):
        print("!! Table model reset")

        self.findDelegates()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(TableModel.LINK_MIME_TYPE):
            event.setDropAction(Qt.LinkAction)
            event.accept()
        elif event.mimeData().hasFormat("text/plain"):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        elif event.mimeData().hasFormat("application/plain"):
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

        return event

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Insert:
            self.insertRows()

        if key == Qt.Key_Delete:
            self.hande_delete_key()

    """
    def handle_insert_key(self):
        selection_model = self.selectionModel()
        if selection_model.hasSelection():
            rows = selection_model.selectedRows()

    def handle_delete_key(self):
        selection_model = self.selectionModel()
        if selection_model.hasSelection():
            self.model().removeListOfRows(selection_model.selectedRows())
    """

    def columnsInserted(self):
        self.findDelegates()

    def findDelegates(self):
        # Look at the descriptors used with the model
        # and if the have an editor (delegate) specified
        # set the view to use it.
        column_names = [c for c in self.model().columns]
        for i in range(len(column_names)):
            attr_name = column_names[i]
            descriptor = self.model().descriptors[attr_name]

            if descriptor.editor is not None:
                self.setItemDelegateForColumn(i, descriptor.editor)

# ================================================================
#               Property Table Widget
# ================================================================
class TableWidget(QtGui.QWidget):
    def __init__(self, view=None, data=None, descriptors=None, title="Table", path='', *args):
        super(TableWidget, self).__init__(parent=None)
        self.setWindowTitle(title)

        if view is not None:
            self.view = view
        else:
            self.view = TableView(data=data, descriptors=descriptors, path=path)

        self.view.setAcceptDrops(True)
        self.view.setDragEnabled(True)
        self.view.setDropIndicatorShown(True)
        self.view.verticalHeader().setMovable(True)
        self.view.setAlternatingRowColors(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

    def sizeHint(self):
        return QtCore.QSize(800,400)



