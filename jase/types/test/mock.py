from jase.qt_bindings import QtGui


# ----------------------------------------------------------------
#    Mock object used for lightweight testing
# ----------------------------------------------------------------
from jase.types.types import Int, Str, Bool, Float, Typed
from jase.types.editors import ComboBox

pixmap = QtGui.QPixmap(100,100)
pixmap.fill(QtGui.QColor(0,0, 255))
blue_icon = QtGui.QIcon(pixmap)

pixmap = QtGui.QPixmap(100,100)
pixmap.fill(QtGui.QColor(0,0,255))
green_icon = QtGui.QIcon(pixmap)

class Mock(Typed):
    str = Str('Hello World', underline=True, font_color='blue')
    int = Int(0, bold=True)
    fixed = Int(0, editable=False, desc='A fixed integer', italic=True, bg_color='grey')
    bool = Bool(True, checkbox=True)
    float = Float()
    enum = Str('Type A', values=['Type A', 'Type B', 'Type C'], editor=ComboBox(['Type A','Type B', 'Type C']))
    status = Str(formula="'OK' if int < 3 else 'Bad'", editable=False)

    def __init__(self, str='Name', int=0, bool=True, float=0.0):
        super(Mock,self).__init__()
        self.str = str
        self.int = int
        self.bool = bool
        self.float = float
        self.fixed_int = 0
        self.type=None
        self.status = None

    def __repr__(self):
            return "Mock(%s)" % self.str


class Person(Typed):
    first_name = Str()
    last_name = Str()
    age = Int(min=0)