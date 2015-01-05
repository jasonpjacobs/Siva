from ..qt_bindings import QtCore, QtGui

from jcanvas.canvas_widget import CanvasWidget
from jcanvas.items import Ellipse, Rect, Line, Polyline, Text

def main():
    try:
        app = QtGui.QApplication([])
    except RuntimeError:
        app = QtCore.QCoreApplication.instance()

    cw = CanvasWidget(width=800, height=400)
    c = cw.canvas
    v = c._view

    for i in range(10):
        for j in range(10):
            r = Rect(x = i*20, y= j*20, width=10, height=10, color='red', radius=2)
            c.add(r)


    e = Ellipse(100,400,100,50, line="black", color="blue", line_width=1, gradient_type="radial")
    e.flip(y=True, x=True)
    e.rotate(30)
    c.add(e)

    r = Rect(400,450,200,100, color='#CAE1FC', line='blue', line_width=20, name="blue", radius=50)
    r.rotation = 30
    c.add(r)

    line = Line(0,0,20,20, color='green')
    c.add(line)

    pl = Polyline( [(0,0), (0,10), (10,0)], color='blue', width=10)
    c.add(pl)

    c.add(Text("hi", 400, 300))
    c._view.zoom_fit()
    cw.show()
    app.exec_()


#cProfile.run('main()', 'main.prof')


#p = pstats.Stats('main.prof')
#p.sort_stats('tottime')
#p.print_stats()


from test_canvas import *

#test_item_outline_fixes(helper())

#test_bounding_rects(helper())

main()

