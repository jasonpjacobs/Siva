class Node:
    def __init__(self, name, parent=None):
        self.name = str(name)
        self.parent = parent

    def output(self):
        return "V({})".format(self.path)

    @property
    def path(self):
        if self.parent:
            path = self.parent.path() + ":" + self.name
        else:
            path = self.name
        return path

    def __str__(self):
        return self.path

class Branch:
    def __init__(self, name, parent=None, p=None, n=None):
        self.name = name
        self.parent = parent
        self.p = p
        self.n = n

    def output(self):
        return "I({},{})".format(self.p.path(0, self.n.path()))

    @property
    def path(self):
        if self.parent:
            path = self.parent.path() + ":" + self.name
        else:
            path = self.name
        return path

