import unittest
from siva.types.hierarchy import Node
import pdb

class Test(unittest.TestCase):
    def setUp(self):
        self.root = Node()
        root = self.root
        b1 = Node(root)
        b2 = Node(root)
        self.root.add_child(b1, 'b1')
        self.root.add_child(b2, 'b2')
        
        c1 = Node(b1)
        c2 = Node(b1)
        c3 = Node(b1)
        b1.add_child(c1, 'c1')
        b1.add_child(c2, 'c2')
        b1.add_child(c3, 'c3')
        
        d1 = Node(c1)
        d1.desc = "This is an additional attribute"
        c1.add_child(d1, 'd1')
        d2 = Node(c1, obj="I am D2")
        c1.add_child(d2, 'd2')
        
        self.b1 = b1
        self.b2 = b2
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.d1 = d1
        self.d2 = d2
        
    def tearDown(self):
        pass

    def testGetRoot(self):
        self.assertEqual(self.root.get_root(), self.root)        
        self.assertEqual(self.b1.get_root(), self.root)
        self.assertEqual(self.c1.get_root(), self.root)

    def testGetName(self):
        self.assertEqual(self.root.get_name(), '/')
        self.assertEqual(self.b1.get_name(), 'b1')
        self.assertEqual(self.c1.get_name(), 'c1')
        
    def testGetParent(self):
        self.assertEqual(self.root.get_parent(), None, "Root node's parents are None")
        self.assertEqual(self.b1.get_parent(), self.root)
        self.assertEqual(self.c1.get_parent(), self.b1)

    def testGetChildByIndex(self):
        self.assertEqual(self.root.get_child_by_index(0), self.b1)
        self.assertEqual(self.b1.get_child_by_index(0), self.c1)
        self.assertEqual(self.b1.get_child_by_index(1000), None)
        self.assertEqual(self.b2.get_child_by_index(0), None)
        
    def testGetChildByName(self):
        self.assertEqual(self.root.get_child_by_name('b1'), self.b1)
        self.assertEqual(self.root.get_child_by_name('ThisDoesntExist'), None)
        self.assertEqual(self.b1.get_child_by_name('c1'), self.c1)
        self.assertEqual(self.b1.get_child_by_name('ThisDoesntExist'), None)
        self.assertEqual(self.c3.get_child_by_name('Root'), None)  # C3 has no children
        
    def testFindIndexOfChild(self):
        self.assertEqual(self.root.find_index_of_child(self.b1), 0)
        self.assertEqual(self.root.find_index_of_child(self.b2), 1)
        self.assertEqual(self.root.find_index_of_child(None), None,)
        
    def testAddChild(self):
        d1 = Node(self.c3)
        self.c3.add_child(d1, 'd1')
        
    def testDeleteChild(self):
        d1 = Node(self.c3)
        self.c3.add_child(d1, name='d1')
        self.assertEqual(self.c3.get_child_by_name('d1'), d1, "Could not add d1 to c3")
        
        self.c3.delete_child(d1)
        self.assertEqual(self.c3.get_child_by_name('d1'), None)
        
    def testHasChildren(self):
        self.assertEqual(self.root.has_children, True, )
        self.assertEqual(self.c3.has_children, False, )
        
        d1 = Node(self.c3)
        self.c3.add_child(d1,'d1')
        self.assertEqual(self.c3.has_children, True)
        self.c3.delete_child(d1)
        self.assertEqual(self.c3.has_children, False, 'has_chldren returns True even though children were deleted')

    
    def testGetPath(self):
        path = self.root.get_path()
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], '/')
        
        path = self.c1.get_path()
        self.assertEqual(len(path), 3)
        self.assertEqual(path[0], '/')
        self.assertEqual(path[1], 'b1')
        self.assertEqual(path[2], 'c1')
        
        path = self.b1.get_path()
        
    def testGetRelativePath(self):
        # C2 is a sibling of C1 --> ../c2
        path = self.c1.get_relative_path(self.c2)
        self.assertEqual(path[0], '..')
        self.assertEqual(path[1], 'c2')        
        
        # C1 is a parent of d1 --> ".."
        path = self.d1.get_relative_path(self.c1)
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], '..')  
        
        # D1 is a child of c1 -->  "./d1"
        path = self.c1.get_relative_path(self.d1)
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], '.')
        self.assertEqual(path[1], 'd1')
        
        # D1 is a niece of C2 -->  ../../c2
        abs = self.d1.get_path()
        path = self.d1.get_relative_path(self.c1)
        
    def testResolve(self):
        path = self.c1.get_relative_path(self.c2)
        obj = self.c1.resolve(path)
        self.assertEqual(obj, self.c2)
        
        path = self.d1.get_relative_path(self.c2)
        obj = self.d1.resolve(path)
        self.assertEqual(self.c2, obj, "Could not resolve %s" % (path,))

        path = self.root.get_relative_path(self.d1)
        obj = self.root.resolve(path)
        self.assertEqual(self.d1, obj, "Could not resolve %s" % (path,))
        
        path = self.d1.get_relative_path(self.root)
        obj = self.d1.resolve(path)
        self.assertEqual(obj, self.root)
        
        # Test proxy nodes
        path = self.c1.get_relative_path(self.d2)
        obj = self.c1.resolve(path)
        self.assertEqual(obj, self.d2.obj)
        
        path =self.c1.get_path()
        obj = self.c2.resolve(path)
        self.assertEqual(obj, self.c1)
        
        path = ["/", "b1", "c1", "d1", "desc"]
        value = self.c2.resolve(path)
        self.assertEqual(value, self.d1.desc)
        
        path = "/b1.c1.d1.desc"
        value = self.c2.resolve(path)
        self.assertEqual(value, self.d1.desc)
        
        path = ["/", "b1", "c1", "d1", "e4"]
        #obj = self.c1.resolve(path)
        print(obj)
                
    def testTraverse(self):
        names = []

        def name(node, n, i):
            return node.get_name()
        
        nn = self.root.traverse(name, order='pre')
        
if __name__ == "__main__":
    unittest.main()