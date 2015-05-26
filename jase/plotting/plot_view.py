from ..qt_bindings import QtGui, QtCore, Qt, Signal

from .plot_group import PlotGroup
from .plot import Plot
from .scale import Scale

import datetime

class PlotView(QtGui.QGraphicsView):
    """ QGraphicsView/Scene combination that holds one or more plots (contained in a PlotGroup)
     in a set of vertical strips.  All plots within the view will share the same X-axis.
    """
    viewChanged = Signal()

    def __init__(self, parent=None, x_scale=None, width=1200, height=600):
        super().__init__(parent)


        # We'll handle our own scroll bars
        policy = Qt.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(policy)
        self.setHorizontalScrollBarPolicy(policy)

        self.scene = scene = QtGui.QGraphicsScene(parent=self)
        self.scene.setSceneRect(0, 0, width, height)
        self.setGeometry(100, 100, width, height)

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
        self.subtitle = None

        #app = QtGui.QApplication.instance()
        #app.installEventFilter(self)
        self.create_event_handers()

        self.mouse_pos = None


    def drawForeground(self, painter, rect):
        """
         TODO:  PlotView Title/Subtitle feature
        """
        if self.subtitle is None:
            subtitle = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
        else:
            subtitle = self.subtitle

        super().drawForeground(painter, rect)

    def drawBackground(self, painter, rect):
        """Responsible for rendering grid lines, axis ticks"""
        super().drawBackground(painter, rect)
        self.top.drawBackground(painter, rect)
        for item in self.items():
            if hasattr(item, 'drawForeground'):
                item.drawForeground(painter, rect)

    def resizeEvent(self, event):

        self.top.width = event.size().width()
        self.top.height = event.size().height()
        self.top.layout()
        self.update()

    def update_view(self):
        """ Slot called when scales are updated to re-render the plots"""
        self.viewport().update()

    def plot(self, *args, name=None, **kwargs):
        """ Creates a new Plot and adds it to the current PlotGroup
        """
        pg = self.current_plot_group
        # Create a new plot object
        plot = Plot(parent=pg, width=1.0*self.width(), height=self.height()*1.0, x_scale=self.x_scale, view=self)

        # Plot the data
        plot.plot(name=name, *args, **kwargs)

        # Add to the scene
        pg.add_plot(plot)

        plot.zoom_fit()


    def eventFilter(self, obj, event):
        print("Event", obj, event)
        return False

    def keyReleaseEvent(self, event):
        if self.top:
            self.top.handle_event(event=event, type='keyReleaseEvent', pos=self.mouse_pos)


    def mousePressEvent(self, event):
        self.mouse_pos = event.pos()
        if self.top:
            self.top.handle_event(event=event, type='mousePressEvent', pos=self.mouse_pos)

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        if self.top:
            self.top.handle_event(event=event, type='mouseMoveEvent', pos=self.mouse_pos)

    def keyPressEvent(self, event):
        if self.top:
            self.top.handle_event(event=event, type='keyPressEvent', pos=self.mouse_pos)

    def wheelEvent(self, event):
        if self.top:
            self.top.handle_event(event=event, type='wheelEvent', pos=self.mouse_pos)

    def create_event_handers(self):
        self.keypress_event_handlers = {
            Qt.Key_Right : self.key_pan_zoom,
            Qt.Key_Left : self.key_pan_zoom,
            Qt.Key_Up : self.key_pan_zoom,
            Qt.Key_Down : self.key_pan_zoom,
            Qt.Key_Plus : self.key_pan_zoom,
            Qt.Key_Minus : self.key_pan_zoom,
            Qt.Key_F : self.key_pan_zoom
        }

    def key_pan_zoom(self, event):
        if event.modifiers() == Qt.NoModifier:
            if event.key() == Qt.Key_Right:
                self.pan(x=0.2, mode="relative")
                return True
            elif event.key() == Qt.Key_Left:
                self.pan(x=-0.2, mode="relative")
                return True
            elif event.key() == Qt.Key_Up:
                self.pan(y=-0.2, mode="relative")
                return True
            elif event.key() == Qt.Key_Down:
                self.pan(y=0.2, mode="relative")
                return True
            elif event.key() == Qt.Key_Plus:
                self.zoom(1.2)
                return True
            elif event.key() == Qt.Key_Minus:
                self.zoom(0.8)
                return True
            elif event.key() == Qt.Key_F:
                self.zoom_fit()
                return True
        elif event.modifiers() == Qt.ShiftModifier:
            if event.key() == Qt.Key_Right:
                self.zoom(x=1.2, y=1.0)
                return True
            elif event.key() == Qt.Key_Left:
                self.zoom(x=0.8, y=1.0)
                return True
            if event.key() == Qt.Key_Up:
                self.zoom(y=1.2, x=1.0)
                return True
            elif event.key() == Qt.Key_Down:
                self.zoom(y=0.8, x=1.0)
                return True
        return False

