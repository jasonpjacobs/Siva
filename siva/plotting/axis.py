from ..qt_bindings import QtGui, QtCore, Qt

from .view import DrawingArea
import pdb
class Axis(DrawingArea):
    def __init__(self, parent=None, w=400, h=20, axis="x", scale=None):
        super().__init__(parent=parent)
        self.scale = scale
        self.axis = axis

        policy = Qt.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(policy)
        self.setHorizontalScrollBarPolicy(policy)

        self.major_tick_length = 10
        self.minor_tick_length = 6


    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)

        painter.drawEllipse(0,0,10,10)
        painter.drawRect(0,0, 100, 10)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)


        if self.axis == "x":
            print(rect)
        # Draw the base line
        if self.axis == "x":
            baseline = rect.topLeft().y() + 2
        else:
            baseline = rect.topRight().x() - 2

        x_range, y_range = self.scale.scene_visible_range()

        # Draw the base line
        if self.axis == "x":
            sx = self.scale.to_screen(x_range)
            painter.drawLine(sx[0], baseline, sx[1], baseline)
        else:
            sy = self.scale.to_screen(y_range)
            painter.drawLine(baseline, sy[0], baseline, sy[1])

        # Draw major tick marks
        ticks = self.scale.ticks(N=10)

        # Draw labels for the major ticks
        self.draw_tick_labels(painter, ticks, baseline=baseline)

        # Draw major tick marks
        self.draw_ticks(painter, ticks, self.major_tick_length, baseline=baseline)

        # Draw minor tick marks
        ticks = self.scale.ticks(N=50)
        self.draw_ticks(painter, ticks, self.minor_tick_length, baseline=baseline)

    def draw_tick_labels(self, painter, ticks, baseline=0):
        s_ticks = [int(s) for s in self.scale.to_screen(ticks)]
        spacing = s_ticks[1] - s_ticks[0]
        for t in s_ticks:
            if self.axis == "x":
                x = t -spacing/2
                y = baseline + self.major_tick_length + 4
                w = int(spacing)
                h = 10
                txt ="{}".format(t)
                painter.drawText(int(x), int(y), w, h, Qt.AlignCenter, txt)
            else:
                w = 40
                h = 20
                y = t - h/2
                x = baseline - ((self.major_tick_length + 2) + w)
                txt ="{}".format(t)
                painter.drawText(int(x), int(y), w, h, Qt.AlignVCenter | Qt.AlignRight, txt)

    def draw_ticks(self, painter, ticks, tick_size=10, baseline=0):
        ticks = [int(s) for s in self.scale.to_screen(ticks)]
        if self.axis == "y":
            x = baseline
            tick_lines = [QtCore.QLineF(x, y, x - tick_size, y)
                for y in ticks]
        else:
            y = baseline
            tick_lines = [QtCore.QLineF(x, y, x, y + tick_size)
                for x in ticks]
        painter.drawLines(tick_lines)

    def getRange(self, rect):
        pass

    def scale_changed(self):
        print("Scale changed", self)
        range = self.scale.range
        self.update()