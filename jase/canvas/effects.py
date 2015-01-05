# -*- coding: utf-8 -*-
"""
Copyright 2014, Jason Jacobs

A good explanation of how to create custom effects is here:
http://unafaltadecomprension.blogspot.com/2013/02/subclassing-qgraphicseffect-in-pyside.html
"""


from .qt_bindings import QtGui, QtCore, Qt
import pdb

class GlowEffect(QtGui.QGraphicsBlurEffect):
    
    def boundingRectFor(self, sourceRect):
        #return sourceRect
        return sourceRect.adjusted(-100, -100, 100, 100)
    
    def draw(self, painter):
        
        offset=QtCore.QPoint()
        pad=QtGui.QGraphicsEffect.PadToTransparentBorder
        pixmap = self.sourcePixmap(Qt.DeviceCoordinates, offset, pad)
        
        painter.setWorldTransform(QtGui.QTransform())
        rect = pixmap.rect()
        #pdb.set_trace()

        painter.save()

        gradient = QtGui.QRadialGradient()
        gradient.setColorAt(0.0, Qt.red)
        gradient.setColorAt(0.1, Qt.white)
        gradient.setColorAt(1.0,Qt.blue)
        brush = QtGui.QBrush(gradient)
        
        pen = QtGui.QPen(Qt.blue)
        pen.setWidthF(2)
        #painter.setPen(pen)
        #painter.setBrush(gradient)
        
        painter.translate(offset)
        #self.drawSource(painter)
        #painter.drawPixmap(offset, pixmap)
        
        #painter.drawPath(path)
        #r = QtGui.QGraphicsRectItem(rect)
        #painter.strokePath(r.shape(), pen)
        
        #painter.drawRect(rect)
        #painter.fillRect(rect.x(), rect.y(), rect.width(), rect.height(), gradient)

        painter.setBrush(QtGui.QBrush(Qt.red))
        #painter.setBrush(brush)
        #dx = rect.width()*0.1
        #dy = rect.height()*0.1
        #new = pixmap.scaled(rect.width() + dx, rect.height() + dy)
        #new.fill(Qt.red)
        #painter.drawPixmap(QtCore.QPoint(-0.5*dx,-0.5*dy),new)
        #painter.drawPixmap(QtCore.QPoint(0,0),pixmap)
        
        
        #painter.setCompositionMode(QtGui.QPainter.CompositionMode_DestinationOut)
        #painter.setBrush(QtGui.QBrush(Qt.transparent))
        #painter.drawPixmap(QtCore.QPoint(0,0),pixmap)
        
        
        QtGui.QGraphicsBlurEffect.draw(self, painter)
        painter.restore()
    
    def sourcePixmap(self, coords, offset, pad):
        pixmap = QtGui.QGraphicsBlurEffect.sourcePixmap(self, coords, offset, pad)
        
        return pixmap.scaled(100,1000)
    
    
class OutlineEffect(QtGui.QGraphicsEffect):
    def __init__(self, ):
        QtGui.QGraphicsEffect.__init__(self)
        
        self.line_width=0
        self.color = Qt.blue
        self.line_style = Qt.DashLine
        
    def boundingRectFor(self, sourceRect):
        #return sourceRect
        lw = self.line_width
        return sourceRect.adjusted(-0.5*lw, -0.5*lw, 0.5*lw, 0.5*lw)
    
    def draw(self, painter, ):
        offset=QtCore.QPoint()
        
        mode=QtGui.QGraphicsEffect.PadToTransparentBorder
        
        # Get the source pixmap and its location
        location=QtCore.QPoint()
        
        # This method will store the source position in the "offset" variable
        pixmap = self.sourcePixmap(Qt.DeviceCoordinates, offset, mode)
        
        # Not sure why this is needed but the implemenations in the
        # QGraphicsEffects source code do this
        painter.setWorldTransform(QtGui.QTransform())
        
        # Get the boundary, adjusted for the line
        rect = self.boundingRectFor(pixmap.rect())
        
        # Translate the painter
        # to match the source pixmap
        painter.translate(offset)
                
        # Setup the pen
        pen = QtGui.QPen(self.color)     
        pen.setWidthF(self.line_width)
        pen.setStyle(self.line_style)
        painter.setPen(pen)
        
        # Draw the bounding box
        painter.drawRect(rect)
        
        # And then the source object itself
        painter.drawPixmap(QtCore.QPoint(0,0), pixmap)  
        
if __name__ == "__main__":
    app = QtGui.QApplication([])
    from canvas import Canvas
    import items
    c = Canvas(width=800, height=400, size=(800, 400))

    circle = items.Circle(100,100,50,color='green', width=2)
    c.add(circle)
    e=GlowEffect()
    e=OutlineEffect()
    circle.setGraphicsEffect(e)
    #c.add(items.Rect(200,200,200,100, color='blue', line='blue', line_width=0, name="blue"))
    
    
    #c.add(items.Line(20,30,200,356, color='black', width=5))
    
    c.show()
    app.exec_()