from ..qt_bindings import QtGui, QtCore, Qt, Signal
from PySide.QtCore import Qt

from .plot_group import PlotGroup
from .plot import Plot
from .scale import Scale

class PlotView(QtGui.QGraphicsView):
    """ QGraphicsView/Scene combination that holds one or more plots in a set of vertical strips.

    All plots within the view will share the same X-axis.
    """
    viewChanged = Signal()

    def __init__(self, parent=None, x_scale=None, width=1200, height=600):
        super().__init__(parent)

        policy = Qt.ScrollBarAlwaysOff

        # We'll handle our own scroll bars
        self.setVerticalScrollBarPolicy(policy)
        self.setHorizontalScrollBarPolicy(policy)

        self.scene = scene = QtGui.QGraphicsScene(parent=self)
        #scene.setSceneRect(0, 0, width, height)
        self.setGeometry(0, 0, width, height)

        self.setScene(scene)
        if x_scale is None:
            x_scale = Scale(plot=self, axis="x")
        self.x_scale = x_scale
        self.x_scale.value_changed.connect(self.update_view)

        # Plots are stored hierarchically via PlotGroups.
        # The PlotView just keeps a reference to the top-level plot group.
        self.top = PlotGroup(expanded=True, view=self, width=self.width())
        self.top.setPos(QtCore.QPoint(0,0))
        self.scene.addItem(self.top)
        self.current_plot_group = self.top

        # View configuration
        self.setAlignment(Qt.AlignCenter)
        self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setMouseTracking(True)

    def drawForeground(self, painter, rect):
        """
         TODO:  PlotView Title/Subtitle feature

        if self.subtitle is None:
            subtitle = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
        else:
            subtitle = self.subtitle
        """

        self.top.drawForeground(painter, rect)
        pass

    def drawBackground(self, painter, rect):
        """Responsible for rendering grid lines, axis ticks"""
        self.top.drawBackground(painter, rect)

    def resizeEvent(self, *args, **kwargs):
        self.top.width = self.width()
        self.update()

    def update_view(self):
        """ Slot called when scales are updated to re-render the plots"""
        self.viewport().update()

    def plot(self, *args, name=None, **kwargs):
        """ Creates a new Plot and adds it to the current PlotGroup
        """
        pg = self.current_plot_group

        plot = Plot(parent=pg, width=pg.width, x_scale=self.x_scale, view=self)
        plot.plot(name=name, *args, **kwargs)
        pg.add_plot(plot)

        plot.zoom_fit()

