from ..qt_bindings import QtGui, QtCore, Qt
from .tree import Tree, Node

import pdb

class PlotGroup(Node, QtGui.QGraphicsItemGroup):
    """ A Tree node structure to store groups of plots.
    """
    def __init__(self, view=None, expanded=True, height=200, width=800):
        QtGui.QGraphicsItemGroup.__init__(self)
        Node.__init__(self)

        # self.view = view -- Not used. Should delete.
        self.plot_axes = []
        self.expanded = expanded

        self.width = width
        self.height = height

        # Let the plots handle mouse and key events themselves
        self.setHandlesChildEvents(False)

        # Plots are stored in a set of vertical strips
        #self.layout = QtGui.QGraphicsLinearLayout(Qt.Vertical)
        #self.setLayout(self.layout)
        self.spacing = 10

    def add_plot(self, item, name=None):
        if name is None:
            name = "plot_{}".format(len(self.children) + 1)
            item.name = name

        #self.layout.addItem(item)
        self.addToGroup(item)
        self.children[name] = item

        self.layout()

    @property
    def height(self):
        """The height of the plot group, in screen coordinates
        """
        if self.children and self.expanded:
            h= sum([c.height for c in self.children.values()])
        else:
            # Empty plot
            h = 100
        return h

    @height.setter
    def height(self, value):
        self._height = value
        if self.children and self.expanded:
            h = self._height/len(self.children)
            for child in self.children.values():
                child.height = h

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        for child in self.children.values():
            child.width = value
            child.update()

    @property
    def spacing(self):
        return self.__spacing

    @spacing.setter
    def spacing(self, value):
        self.__spacing = value

    def layout(self):
        """Arranges the Plots into the desired height of the plot group"""

        if len(self.children) == 0:
            ideal_height = self.height
        else:
            ideal_height = self.height/len(self.children)

        # Set the height of each plot.  The plots use this value a desired height,
        # but may make them selves larger or smaller based on min/max size requirements
        for child in self.children.values():
            child.height = ideal_height

        # Now set the positions of each plot based on the final height and
        # position of the plots before it
        y = 0
        for child in self.children.values():
            child.setPos(QtCore.QPoint(0,y))
            y = y + child.height + self.spacing

    def drawForeground(self, painter, rect):
        for child in self.children.values():
            child.drawForeground(painter, rect)

    def drawBackground(self, painter, rect):
        for child in self.children.values():
            child.drawBackground(painter, rect)

    def boundingRect2(self):
        rect = QtCore.QRectF()
        for plot in self.children.values():
            item_rect = plot.boundingRect()
            rect = rect.unite(item_rect)
        return rect

    def handle_event(self, event, type, pos=None):
        for child in self.children.values():
            if child.contains(pos):
                # Translate the view coordinate to the child's coordinate
                pos = QtCore.QPoint(pos.x() - child.pos().x(), pos.y() - child.pos().y())
                child.handle_event(event=event, type=type, pos=pos)

