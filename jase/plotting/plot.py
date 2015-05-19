import pdb
from ..qt_bindings import QtGui, QtCore, Qt
import datetime

from .scale import Scale
from .plot_items import StyleFactory, LinePlot, StemPlot, BarPlot, StatePlot, LogicPlot
from .plot_group import PlotGroup

class Plot(QtGui.QGraphicsItemGroup):
    """
    The Plot class is responsible for rendering waveforms, axes, titles, annotations, etc.

    """

    # Place holder:  Will implement a more formal theme later on.
    default_colors = [Qt.red, Qt.blue, Qt.darkBlue, Qt.darkCyan]

    plot_styles = {
        "line" : LinePlot,
        "bar" : BarPlot,
        "stem" : StemPlot,
        "logic" : LogicPlot,
        "state" : StatePlot,
    }

    def __init__(self, parent=None, width=400, height=100, x_scale=None, y_scale=None, style_factory=None, title=None,
                 subtitle=None, view=None):
        QtGui.QGraphicsItemGroup.__init__(self, parent=parent)

        self.view = view
        self.title = title
        self.subtitle = subtitle

        # Scales are used to translate from data coordinates to scene coordinates
        if x_scale is None:
            print("Creating new x-scale for ", self)
            self.x_scale = Scale(plot=self, axis="x")
        else:
            self.x_scale = x_scale
            x_scale.plot = self

        if y_scale is None:
            self.y_scale = Scale(plot=self, axis="y")
        else:
            self.y_scale = y_scale

        # Style factories provide default styles (color, line style) for the
        # waveforms contained within.
        if style_factory is None:
            self.style_factory = StyleFactory(colors = Plot.default_colors)
        else:
            self.style_factory = style_factory

        #self.pan_start = (None, None)
        #self.pan_active = False

        # Container for the PlotItems (waveforms)
        self.plot_items = []

        self.width=width
        self.height=height

        # The plot_rect is the scene region where the waveforms should be rendered.
        # It is the size of the plot after allocating space for title, axes, and legends.
        self.set_plot_rect(QtCore.QRect(0, 0, width, height))

    @property
    def margins(self):
        margins = {"left": 40, "right": 10, "top": 20, "bottom": 20}
        return margins

    def drawBackground(self, painter, rect):
        """ Draws axis grids.  Part of the QGraphicsWidget implementation.
        """
        plot_rect = self.set_plot_rect(rect)
        if plot_rect.isEmpty():
            return

        painter.save()
        painter.translate(self.pos())
        painter.setClipRect(plot_rect)
        self.x_scale.draw_grid(painter, plot_rect)
        self.y_scale.draw_grid(painter, plot_rect)
        painter.restore()

    def drawForeground(self, painter, rect):
        """Renders axes, title, and annotations on the foreground.
        Part of the QGraphicsWidget implementation.
        """
        plot_rect = self.set_plot_rect(rect)
        if plot_rect.isEmpty():
            return

        painter.save()
        self.fill_margins(painter, rect)

        if self.title is None:
            title = self.name
        else:
            title = self.title

        if title is not None:
            title_rect = QtCore.QRect(self.margins['left'], self.pos().y(), self.width, self.margins['top'])
            self.draw_title(painter, title_rect, title)

        # Axis rendering is performed relative to the plot.
        painter.translate(self.pos())
        self.x_scale.draw_axis(painter, plot_rect, side="bottom", padding=40, plot=self, margins=self.margins)
        self.y_scale.draw_axis(painter, plot_rect, side="left", padding=100, plot=self, margins=self.margins)
        painter.restore()

    def fill_margins(self, painter, view_rect):
        """ Fills the visible portion of the plot margins with a solid color,
        so axis ticks and labels can be clearly read.
        """
        #TODO:  Parameterize the background color
        color = QtGui.QColor(Qt.yellow)

        # Find the portion of the plot area that is visible.
        bounding_rect = self.boundingRect()
        visible_rect = view_rect.intersected(bounding_rect)

        # Plot.plot_rect is relative to the plot.  Move the visible rect
        # to the plot origin
        visible_rect.moveTo(0, 0)
        pr = self.plot_rect

        painter.save()
        painter.translate(self.pos())
        # Fill in the margins.  Note, the four paint events don't correspond exactly
        # to top, left, bottom, and right.  This is to make use of the corner attributes
        # (topLeft, bottomRight) of the two rects:  visible_rect, plot_rect
        painter.fillRect(QtCore.QRectF(visible_rect.topLeft(), pr.bottomLeft()), color)
        painter.fillRect(QtCore.QRectF(visible_rect.bottomLeft(), pr.bottomRight()), color)
        painter.fillRect(QtCore.QRectF(pr.topRight(), visible_rect.bottomRight()), color)
        painter.fillRect(QtCore.QRectF(pr.topLeft(), visible_rect.topRight()), color)
        painter.drawRect(pr)
        painter.restore()

    def draw_title(self, painter, rect, title):
        """Renders the plot title and subtitle at the top of the plot area
        TODO:  Refactor this to work with updated scene position.
        """
        pixel = self.x_scale.pixel

        #TODO: Parameterize the title area
        font = QtGui.QFont('Helvetica')
        font.setPixelSize(16)
        font.setBold(True)
        painter.setFont(font)

        # I had trouble rendering text at small scene scales, so
        # I'll just scale and translate the painter before
        # drawing any text.
        painter.save()
        #painter.scale(1/pixel, 1/pixel)

        painter.drawText(rect,Qt.AlignCenter | Qt.AlignTop, title)
        painter.restore()

    def set_plot_rect(self, view_rect):
        """Determines the portion of the viewable plot area that is used for rendering plot data vs.
        margin for axes, title, and legend annotations.
        """
        # Convert to floating point
        rect_f = QtCore.QRectF(view_rect)

        # Determine how much of this plot's area is visible
        visible_rect = rect_f.intersected(QtCore.QRectF(self.pos().x(), self.pos().y(), self.width, self.height))

        y = (view_rect.top() - self.pos().y() )if view_rect.top() > self.pos().y() else 0
        x = (view_rect.left() - self.pos().x())  if view_rect.left() > self.pos().x() else 0
        visible_rect.moveTo(x, y)

        # If nothing is visible, just return an emtpy rect
        if visible_rect.isEmpty():
            self.plot_rect = visible_rect
            return visible_rect

        # Adjust for margins
        self.plot_rect = visible_rect.adjusted(self.margins['left']/self.x_scale.pixel,
                                       self.margins['top']/self.y_scale.pixel,
                                        -1*self.margins['right']/self.x_scale.pixel,
                                        -1*self.margins['bottom']/self.y_scale.pixel)

        return self.plot_rect

    @property
    def plot_rect(self):
        return self._plot_rect

    @plot_rect.setter
    def plot_rect(self, value):
        self._plot_rect = value

    def plot(self, obj=None, x=None, y=None, name=None, style="line", *args, **kwargs):
        """ Creates a PlotItem (waveform), from raw X,Y data and plot style, and adds it to this plot.
        """
        if style not in self.plot_styles:
            raise ValueError("Plot style does not exist: {}".format(style))

        item = self.plot_styles[style](obj=obj, x=x, y=y, plot=self, *args, **kwargs)
        item.name = name
        self.add_plot(item)
        item.plot = self

    def add_plot(self, plot_item, name=None):
        if name is None:
            name = "Plot_{}".format(len(self.plot_items) + 1)

        self.plot_items.append(plot_item)
        self.addToGroup(plot_item)
        plot_item.setParentItem(self)

        # Update the scales
        self.x_scale.update_range(plot_item.data[0])
        self.y_scale.update_range(plot_item.data[1])

    # --------------------------------------------------------
    #    Pan/Zoom Methods
    # --------------------------------------------------------
    def zoom_fit(self):
        """ Sets the zoom so the entire sheet fits in the view port"""
        self.x_scale.fit(self.plot_rect)
        self.y_scale.fit(self.plot_rect)

        #self.viewport().update()
        self.update()
        #self.viewChanged.emit()

    def zoom(self, x, y=None, center=None):
        """ Zooms (scales) the window by the given ratio.
        """
        if y is None:
            y = x

        # Need to get the current center of the view
        # so we can recenter the view after zooming
        if center is None:
            center = self.mapToScene(self.rect()).boundingRect().center()

        # Convert scene coords to data coords
        dx = self.x_scale.to_data(center.x())
        dy = self.y_scale.to_data(center.y())

        # Move the center to the origin
        self.pan(x=-1 * dx, y=-1 * dy, mode="absolute")

        # Now scale
        self.x_scale.zoom(x)
        self.y_scale.zoom(y)

        # Then move back
        self.pan(dx, dy)

    def pan(self, x=None, y=None, mode="absolute"):
        """Pans the Canvas by the x and y values in Scene coordinates.
        """
        if x is not None:
            self.x_scale.pan(-1 * x, mode=mode)
        if y is not None:
            self.y_scale.pan( -1 * y, mode=mode)
        #self.viewChanged.emit()


    # --------------------------------------------------------
    #    Event Handling Methods
    # --------------------------------------------------------
    def coords(self, event):
        '''Converts event (screen) coordinates to data space coordinates'''
        pos = self.mapToScene(event.pos())
        x = self.x_scale.to_data(pos.x())
        y = self.y_scale.to_data(pos.y())
        return x,y

    def mouseMoveEvent(self, event):
        end = event.pos()
        delta = self.start - end
        hsb = self.view.horizontalScrollBar()
        vsb = self.view.verticalScrollBar()
        hsb.setValue(hsb.value() + delta.x())
        vsb.setValue(vsb.value() + delta.y())

    def mousePressEvent(self, event):
        if (event.buttons() & Qt.LeftButton):
            #item = self.parent.itemAt(event.pos())
            #if item is not None:
            #    return False

            self.setCursor(Qt.ClosedHandCursor)
            self.pan_active = True
            self.start = event.pos()
            self.pan_start = self.coords(event)

            # Don't consume the mouse click, since it may have been intended
            # for items underneath the cursor
            return False
        else:
            return False

    def mouseMoveEvent(self, event):
        x, y = self.coords(event)
        if self.pan_active and (
            event.buttons() & Qt.LeftButton):
            dx = self.pan_start[0] - x
            dy = self.pan_start[1] - y
            self.pan(x=dx, y=dy, mode="absolute")
            self.pan_start = self.coords(event)
            return True
        else:
            #item = self.itemAt(event.pos())
            item = None
            if item is not None:
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.CrossCursor)
            return False

    def mouseReleaseEvent(self, event):
        if self.pan_active:
            self.pan_active = False
            self.setCursor(Qt.CrossCursor)
            return True
        else:
            return False

    def keyPressEvent(self, event):
        print('Key')
        handler = self.keypress_event_handlers.get(event.key(), None)
        if handler:
            result = handler(event)
        else:
            return False

        if result:
            event.accept()
        return result

    def wheelEvent(self, event):
        center = self.mapToScene(event.pos())
        if event.orientation() == Qt.Vertical:
            d = event.delta() / 8
            ratio = abs((d / 15.0) * 1.25)
            if d < 0:
                scale = 1 / ratio
            else:
                scale = ratio
            self.zoom(scale, center=center)
            return True

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

    # --------------------------------------------------------
    #    QGraphicsWidget Implementation
    # --------------------------------------------------------
    def boundingRect(self, *args, **kwargs):
        """Returns the bounding rectangle plot in scene coordinates"""
        return QtCore.QRectF(self.pos().x(), self.pos().y(), self.width, self.height)

    def __repr__(self):
        return "Plot({}) @ {},{}".format(id(self), int(self.pos().x()), int(self.pos().y()))

    def sizeHint(self, *args, **kwargs):
        #TODO:  Compute size hint based on plot area and margins
        return QtCore.QSizeF(self.width, self.height)


