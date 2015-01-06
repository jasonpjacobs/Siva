from ..qt_bindings import QtGui, QtCore, Qt
from .tree import Tree, Node

import pdb

class PlotGroup(Node, QtGui.QGraphicsWidget):
    """ A Tree node structure to store groups of plots.
    """
    def __init__(self, view=None, expanded=True, height=200, width=800):
        QtGui.QGraphicsWidget.__init__(self)
        Node.__init__(self)

        self.view = view
        self.plot_axes = []
        self.expanded = expanded

        self.width = width

        # Plots are stored in a set of vertical strips
        self.layout = QtGui.QGraphicsLinearLayout(Qt.Vertical)
        self.setLayout(self.layout)
        self.spacing = 10


    def add_plot(self, item, name=None):
        if name is None:
            name = "plot_{}".format(len(self.children) + 1)
            item.name = name

        self.layout.addItem(item)
        self.children[name] = item


    @property
    def height(self):
        """The height of the plot group, in screen coordinates
        """
        if self.children and self.expanded:
            h= sum([c.height for c in self.children])
        else:
            # Empty plot
            h = 100
        return h

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

    """
    def paint(self, painter, option, widget):
        for plot in self.children.values():
            painter.save()
            #painter.translate(plot.pos()*-1)

            ### Debug
            painter.setPen(QtGui.QPen('blue'))
            brush = QtGui.QBrush(QtGui.QColor(0,0,100,20))
            #painter.fillRect(plot.plot_rect, brush)
            #plot.paint(painter, option, widget)
            painter.restore()
        """

    def drawForeground(self, painter, rect):
        for child in self.children.values():
            child.set_plot_rect(rect)
            child.drawForeground(painter, rect)

    def drawBackground(self, painter, rect):
        for child in self.children.values():
            child.set_plot_rect(rect)
            child.drawBackground(painter, rect)

    def boundingRect(self):
        rect = QtCore.QRectF()
        for plot in self.children.values():
            item_rect = plot.boundingRect()
            rect = rect.unite(item_rect)
        return rect

