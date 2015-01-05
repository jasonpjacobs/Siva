""" 
@License
"""

# Python Imports
import pdb
from collections import OrderedDict

# Third party imports

# ==============================================================
#    HasHierarchy
# ============================================================== 
class Node(object):
    """ 
    A node for a hierarchical tree model.
    
    This class be mixed in (or subclassed) to directly as in the case of the TreeModel.
    
    It can also be one of the hierarchical object's attributes.  With this usage, the Node's
    obj attribute should point to the actual object, and will be returned by the resolve method. 
    """
    
    def __init__(self, parent=None, children=None, obj=None):
        self.set_parent(parent)
        if children is None:
            self._children = OrderedDict()
        self.has_children = False
        
        # If not a mix-in, the actual node object is 'obj'
        self.obj = obj

    def get_root(self):
        if self._parent is None:
            return self
        else:
            return self.get_parent().get_root()
        
    def get_parent(self):
        """Returns the parent object of this object.  
        
        Default implementation returns self._parent"""
        return self._parent
        
    def get_children(self):
        """ Returns the dictionary of name/children pairs.
        
        Default implementation returns self._children.
        """
        return self._children
    
    def set_parent(self, parent):
        self._parent = parent
            
    def get_child_by_index(self, n,):
        "Gets the N-th child from the parent.  If the child does not exist, returns None"
        if len(self._children) > n:
            return [v for v in self._children.values()][n]
        else:
            return None
        
    def get_child_by_name(self, name):
        "Gets the child from the parent by name.  If the child does not exist, returns None"
        if name in self._children:
            return self._children[name]
        else:
            return None
        
    def find_index_of_child(self, child):
        "Returns the row number where the parent's child is assigned"
        if child in self._children.values():
            row = [v for v in self._children.values()].index(child)
            return row
        else:
            return None
        
    def add_child(self, child, name=None):
        if name is None:
            name = "i" + str(len(self._children) + 1)
        self._children[name] = child
        child.set_parent(self)
        self.has_children = True

    def delete_child(self, child):
        key=[kv[0] for kv in self._children.items() if kv[1] is child][0]
        del self._children[key]
        if len(self._children) == 0:
            self.has_children = False
        
    def num_children(self):
        return len(self._children)
    
    def get_child_name(self, child):
        name = [k for k in self._children if self._children[k] is child][0]
        return name

    def traverse(self, callback, n=0, i=0, order="pre"):
        """ Traverses the tree from the given node, and calls the call back for each node
        The callback is given the hierarchy level (n) and the instance number (i) as a convenience
        """
        result = []
        if order == "pre":
            result.append(callback(self, n, i))
        i=0
        for child in self._children.values():
            i+=1
            result.append(child.traverse(callback, n+1, i, order=order))
            
        if order != "pre":
            result.append(callback(self, n, i))
        return result
                        
    def get_path(self):
        """Returns a list of the index names from the root
        to the current node"""
        # Get path to our parent
        if self._parent is not None:
            path = self._parent.get_path()
        else:
            path = []
        # Then add ourself
        path.append(self.get_name())
        return path
    
    def get_relative_path(self, node):
        path = self.get_path()
        other = node.get_path()

        depth = min(len(path), len(other))
        # Compute how many levels are in common
        for i in range(depth):
            a = path[i]
            b = other[i]
            if a == b:
                common = i + 1
            else:
                break

        if (common < depth):
            # They share a common ancestor
            if len(path) > common:
                result = [".."]*(len(path) -  common) + other[common:]
            else:
                result = [".."]*(len(other) - common) + other[common:]     
        elif (common == depth):
            # One is a direct descendant of the other
            if (common < len(path)):
                # We're the descendant
                result = [".."]*(len(path) - common)
            else:
                # We're the ancestor
                result = ["."] + other[common:]
                
        return list(result)


    def resolve(self, path, sep="."):
        """Resolves the given path relative to self via recursion"""
        if type(path) is str:
            path = path.split(sep)
            print(path)
            if path[0].startswith("/"):
                path = ["/"] + [path[0][1:]] + path[1:]
            
        if len(path) == 0: 
            if self.obj is not None:
                return self.obj
            else:
                return self
        else:
            index = path[0]

        if index in self._children:
            child = self.get_child_by_name(index)
            obj = child.resolve(path[1:])
        elif index == ".":
            obj = self.resolve(path[1:])
        elif index == "..":
            parent = self.get_parent()
            obj = parent.resolve(path[1:])
        elif index == "/":
            root = self.get_root()
            obj = root.resolve(path[1:])
        elif hasattr(self, index):
            obj = getattr(self, index)            
        elif hasattr(self.obj, index):
            obj = getattr(self.obj, index)
        else:
            pdb.set_trace()
            raise KeyError
            obj = None
        return obj
        
        
    def __repr__(self):
        return "Node(%s)" % self.get_name()
    
    def get_name(self):
        if self._parent is None:
            # Root's name is an empty string
            name = "/"
        else:
            name = self._parent.get_child_name(self)
        return name
    
