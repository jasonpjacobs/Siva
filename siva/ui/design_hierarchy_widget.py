from siva.types.hierarchy import Node
from siva.types.tree_model import TreeModel, TreeView
from siva.types.types import Typed, Str, Int

class Design(Node, Typed):
    name = Str()
    library =  Str()

    def __init__(self, name, library):
        super().__init__(None)
        self.name = name
        self.library = library

class DesignHierarchyWidget(TreeView):
    def __init__(self, model=None):
        TreeView.__init__(self, model=None)
        if model is None:
            model = TreeModel()
        self.setModel(model)

    def load_design(self, design):
        pass

