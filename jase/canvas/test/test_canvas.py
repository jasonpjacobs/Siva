import pytest
import os

os.environ['QT_API'] = 'pyside'
print(os.environ['QT_API'])


from ..qt_bindings import QtGui, QtCore, QTest
from jcanvas.canvas_widget import CanvasWidget
from jcanvas.items import Circle, Ellipse, Rect, Line, Polyline, Text, Polygon

from jcanvas.test.canvas_test_helper import CanvasTestHelper

PALETTE = ["red","blue", "green", "cyan", "magenta", "indigo",
           "#AAAAAA", "#999999", "#777777", "#555555", "#333333"
           ]



@pytest.fixture
def widget():
    cw = CanvasWidget(width=1200, height=800)
    return cw

@pytest.fixture
def helper():
    helper = CanvasTestHelper(delay=500)
    return helper

def test_canvas_creation(helper):
    cw = helper.canvas_widget
    c = cw.canvas

    assert c is not None
    assert c.width == 1200
    assert c.height == 800


def test_zoom_fit(helper):
    cw = helper.canvas_widget
    c = helper.canvas
    v = helper.view

    # There should be no items on the Canvas.
    v.zoom_fit()
    assert len(v.items()) == 0

def test_item_creation(helper):
    cw = helper.canvas_widget
    c = cw.canvas
    v = c._view
    assert len(v.items()) == 0

    for i in range(10):
        for j in range(10):
            r = Rect(x = 100 + i*20, y= 100 + j*20, width=10, height=10, color='red', radius=0)
            c.addItem(r)

    v.zoom_fit()

    assert len(v.items()) == 100
    #assert helper.hash() == "836f6b4090bda0bd53508ed0f40eb49130d2a322"


    if False:
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()

def test_canvas_widget(helper):
    cw = helper.canvas_widget
    c = helper.canvas
    v = helper.view

    e=Ellipse(100,400,100,50, line="black", color="blue", line_width=1, gradient_type="radial")
    e.flip(y=True, x=True)
    e.rotate(30)
    c.add(e)

    r = Rect(400,450,200,100, color='#CAE1FC', line='blue', line_width=20, name="blue", radius=50)
    r.rotation = 30
    c.add(r)

    v.zoom_fit()
    if False:
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()

    #assert helper.hash() == "74f807142111d260831bb2480d07dd93e252f087"

def test_lines(helper):
    cw = helper.canvas_widget
    c = helper.canvas
    v = helper.view

    y0 = 800 - 50
    x0 = 100
    for i in range(5):
        color=PALETTE[i]
        c.add(Line(x1=x0, y1=y0 - 50*i, x2 = x0 + 100, y2 = y0 - 50 * i, color=color, line_color=color,
                   anti_alias=True, width=i))

    v.zoom_fit()

    #assert helper.hash() == "40ae914bdfbbf638d640e38b116e78de55509f1c"

    if False:
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()


def test_circles(helper):
    cw = helper.canvas_widget
    c = helper.canvas
    v = helper.view

    for i in range(5):
        for j in range(4):
            y0 = 750 - j*100
            x0 = 100 + i * 100
            color=PALETTE[i]

            c.add(Circle(x=x0, y=y0, r=20+10*i, color=color, line_color = "black", line_width=j))

    v.zoom_fit()
    #assert helper.hash() == "c5ef74b53ac7583dcd358e9d15479c296a542c74"

    if False:
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()

def test_ellipses(helper):
    c = helper.canvas
    v = helper.view

    for i in range(5):
        for j in range(4):
            y0 = 750 - j*100
            x0 = 100 + i * 100
            color=PALETTE[i]

            c.add(Ellipse(x=x0, y=y0, width=20+10*i, height=20+10*j, color=color, line_color = "black", line_width=j))

    v.zoom_fit()
    #assert helper.hash() == "c119d0b4263b10b1ac56a55767eb003870ef0ec0"

    if False:
        v.zoom_fit()
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()


def test_rects(helper):
    cw = helper.canvas_widget
    c = helper.canvas
    v = helper.view

    for i in range(8):
        for j in range(8):
            y0 = 750 - j*100
            x0 = 100 + i * 100
            color=PALETTE[i]

            c.add(Rect(x=x0, y=y0, width=20+10*i, height=20+10*j, radius = 2*(i + j) - 4,
                       color=color, line_color = "black", line_width=5-j))

    v.zoom_fit()
    #assert helper.hash() == "845a9a62504d4ac63efc2aedd79f863b8556a236"


    if False:
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()



def test_items(helper):
    cw = helper.canvas_widget
    c = helper.canvas
    v = helper.view

    from jcanvas.items import Circle, Ellipse, Rect, Line, Polyline, Text
    for i in range(4):
        y0 = 750 - i*100
        x0 = 100
        color=PALETTE[i]
        c.add(Circle(x=x0 + 0, y=y0 + i, r=50, line_width=i+1, color=color, line_color='black'))
        c.add(Ellipse(x=x0 + 100, y=y0 + i, width=35, height=15, line_width=i+1, color=color, line_color='black'))
        c.add(Rect(x=x0 + 200, y=y0 + i, width=50, height=25, line_width=i+1, color=color, line_color='black', radius=0))
        c.add(Line(x1=x0 + 300, y1=y0 - 25, x2 = x0 + 350, y2 = y0 + 25, width=5, color=color))
        c.add(Polyline( ((x0+400,y0),
                         (x0+420, y0),
                         (x0+430, y0-20),
                         (x0+440, y0+30),
                         (x0+460, y0+30)

                        ),color=color, width=5))
        c.add(Polygon( ((x0+500, y0-25),(x0+525,y0+25),(x0+550,y0-25)),color=color, line='black'))
        c.add(Text("Text Item", x0 + 600, y0))

    v.zoom_fit()
    assert helper.hash() == b'49d6e3933de6bc9ec5d287500e7949f75dddcf85'

    if False:
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()

def test_effects(helper):
    cw = helper.canvas_widget
    c = helper.canvas
    v = helper.view

    y0 = 800 - 50
    x0 = 100

    items = helper.populate(N=7)
    assert items is not None

    for key in items:
        item = items[key]
        if key[0] == 1:
            item.shadow = True

        if key[0] == 2:
            item.highlight = True

        if key[0] == 3:
            item.blur = True

        if key[0] == 4:
            item.bold = True

        if key[0] == 5:
            item.outline = True

        if key[0] == 7:
            item.glow = True

        print("Adding ({}){}".format(key, item))
        c.add(item)

    v.zoom_fit()
    assert helper.hash() == b'f4a51d7bc413450b7635a9b43280bb91df2a3120'

    if False:
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()


def test_text(helper):
    cw = helper.canvas_widget
    c = helper.canvas
    v = helper.view

    test_items = [
        Text("Normal, 8 pt", size=8),
        Text("Bold, 8 pt", bold=True, size=8),
        Text("Italic, 8 pt", italic=True, size=8),
        Text("Underline, 8 pt", underline=True, size=8),
        Text("Overline, 8 pt", overline=True, size=8),

        Text("Normal, 12 pt", size=12),
        Text("Bold, 12 pt", bold=True, size=12),
        Text("Italic, 12 pt", italic=True, size=12),
        Text("Underline, 12 pt", underline=True, size=12),
        Text("Overline, 12 pt", overline=True, size=12),

        Text("Normal, Red, 8 pt", size=8, color='red'),
        Text("Bold, Red, 8 pt", bold=True, size=8, color='red'),
        Text("Semi transparent 8 pt", italic=True, size=8,  color='red'),
        Text("Underline, red, 8 pt", underline=True, size=8,  color='red'),
        Text("Overline, red, 8 pt", overline=True, size=8,  color='red'),
    ]

    N_cols = 5
    N_rows = 3

    for i in range(N_rows):
        for j in range(N_cols):
            x = 100 + j*200
            y = 700 - i*100
            n = i*N_cols + j

            if n < len(test_items):
                item = test_items[n]
                item.setX(x)
                item.setY(y)
                c.add(item)

    v.zoom_fit()
    #assert helper.hash() == "f60420d9c5bd3393cde447365825d84d10329ec1"

    if False:
        cw.show()
        QTest.qWaitForWindowShown(cw)
        helper.app.exec_()


# ============================================================================
# Tests that demonstrate issues
# ============================================================================
def test_item_outline_fixes(helper):
    app, cw, c, v = helper.components()

    color = QtGui.QColor(255,0,0,50)
    items = [None, None, None, None, None]
    y = 700


    #items[0] = Ellipse(x=100, y=y, width=35, height=15, line_width=2, color=color, line_color='black')
    items[0] = Circle(x=100, y=y, r=35, line_width=2, color=color, line_color='black')
    items[1] = Rect(x=200, y=y, width=50, height=25, line_width=2, color=color, line_color='black', radius=0)

    x = 300
    items[2] = Polyline( ((x,y),
             (x+20, y),
             (x+30, y-20),
             (x+40, y+30),
             (x+60, y+30)
            ),
            color=color, width=5)

    x =400
    items[3] = Polygon( ((x, y - 25),(x,y+25),(x + 50, y - 25)), color=color, line='black')

    items[4] = Text("Text Item", 500, y)


    for item in items:
        item.outline = True
        c.add(item)

    v.zoom_fit()

    if False:
        cw.show()
        helper.app.exec_()


def test_bounding_rects(helper):
    app, cw, c, v = helper.components()
    items = helper.populate(2)

    color = QtGui.QColor(255,0,0,30)
    for i,j in items:
        item = items[(i,j)]
        if i == 1:
            item.outline = True
        else:
            item.outline = False

        rect = item.boundingRect()

        poly = item.mapToScene(QtCore.QRectF(rect))
        g_rect = QtGui.QGraphicsPolygonItem(poly)
        g_rect.setBrush(QtGui.QBrush(color))
        c.add(item)
        c.add(g_rect)

    v.zoom_fit()
    if False:
        cw.show()
        helper.app.exec_()


def test_shapes(helper):
    app, cw, c, v = helper.components()
    items = helper.populate(2)

    color = QtGui.QColor(255,0,0,30)
    for i,j in items:
        item = items[(i,j)]
        if i == 1:
            item.outline = True
        else:
            item.outline = False

        shape = item.shape()
        c.add(item)

    v.zoom_fit()
    if False:
        cw.show()
        helper.app.exec_()
