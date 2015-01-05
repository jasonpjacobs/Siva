from ...qt_bindings import QtCore, QtGui, Qt, QTest
from ..items import Circle, Ellipse, Rect, Line, Polyline, Text, Polygon
from ..canvas_widget import CanvasWidget

class CanvasTestHelper(object):
    """ A helper class to simplify sending events to a Canvas in scene coordinates

    """
    def __init__(self, delay=-1):
        if QtGui.QApplication.instance():
            app = QtGui.QApplication.instance()
        else:
            app = QtGui.QApplication([])
        self.app = app
        self.canvas_widget = CanvasWidget(width=1200, height=800)
        self.canvas = self.canvas_widget.canvas
        self.view = self.canvas._view
        self.delay = delay

    def pt(self, x, y):
        # Returns a QPoint coordinates for the desired scene coordinates, in view coordinates
        return QtCore.QPoint(x, y)

    def click(self, x, y, button=Qt.LeftButton, modifier=Qt.NoModifier, delay=-1):
        QTest.mouseClick(self.canvas_widget, Qt.LeftButton, Qt.NoModifier, self.pt(x, y), self.delay)

    def dclick(self, row, col, button=Qt.LeftButton, modifier=Qt.NoModifier, delay=-1):
        QTest.mouseDClick(self.canvas_widget, Qt.LeftButton, Qt.NoModifier, self.pt(row,col), self.delay)

    def down(self):
        QTest.keyClick(self.canvas_widget.viewport().focusWidget(), Qt.Key_Down, self.delay)

    def enter(self):
        QTest.keyClick(self.canvas_widget.viewport().focusWidget(), Qt.Key_Return, self.delay)

    def text(self, txt, enter=True):
        QTest.keyClicks(self.canvas_widget.viewport().focusWidget(), txt, self.delay)
        if enter:
            QTest.keyClick(self.canvas_widget.viewport().focusWidget(), Qt.Key_Return, self.delay)

    def snapshot(self, format="BMP", filename=None):
        """ Renders the canvas on an image"""
        try:
            size=QtCore.QSize(self.canvas_widget.canvas._view.viewport().size())
        except:
            pass
        image = QtGui.QImage(size, QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter()
        painter.begin(image)
        self.view.render(painter)
        del painter
        return image

    def hash(self):
        """Returns a cryptographic hash of the Canvas image data, used for
        simple testing
        """
        image = self.snapshot()
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QBuffer.WriteOnly)
        image.save(buffer, "BMP")
        array = buffer.data()
        buffer.close()

        # Get the hash
        hash = QtCore.QCryptographicHash(QtCore.QCryptographicHash.Sha1)
        hash.addData(array)
        result = hash.result().toHex()
        return result

    def populate(self, N=4, x0=100, y0=750):
        """Adds one of each type of item to the canvas, for further manipulation by tests"""
        c=self.canvas_widget.canvas

        items = {}
        for i in range(N):
            for j in range(7):

                y = y0 - i*100
                x = x0 + j*100

                color = 'red'
                if j == 0:
                    items[(i,j)] = Circle(x=x, y=y, r=50, line_width=i+1, color=color, line_color='black')

                if j == 1:
                    items[(i,j)] = Ellipse(x=x, y=y, width=35, height=15, line_width=i+1, color=color, line_color='black')

                if j == 2:
                    items[(i,j)] = Rect(x=x, y=y, width=50, height=25, line_width=i+1, color=color, line_color='black', radius=0)

                if j == 3:
                    items[(i,j)] = Line(x1=x, y1=y-25, x2=x+50, y2 = y + 25, width=5, color=color)

                if j == 4:
                    items[(i,j)] = Polyline( ((x,y),
                             (x+20, y),
                             (x+30, y-20),
                             (x+40, y+30),
                             (x+60, y+30)
                            ),
                            color=color, width=5)

                if j == 5:
                    items[(i,j)] = Polygon( ((x, y - 25),(x,y+25),(x + 50, y - 25)), color=color, line='black')

                if j == 6:
                    items[(i,j)] = Text("Text Item (with a long comment)\n\n\nThis is line two.", x, y)


        return items

    def components(self):
        return (self.app, self.canvas_widget, self.canvas, self.view)
