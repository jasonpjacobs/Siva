from collections import OrderedDict
class Node:
    def __init__(self, parent=None, children=None):
        self.parent = parent
        if children is None:
            self.children = OrderedDict()
        else:
            self.children = children

    def __len__(self):
        return len(self.children)

class Tree:
    def __init__(self, top=None):
        if top is None:
            top = Node(parent=None)
        else:
            self.top = top

        self.current = top

    def add(self, node, name=None):
        self.current.children[name] = node

    def traverse(self, method="pre", callback=None):
        pass





