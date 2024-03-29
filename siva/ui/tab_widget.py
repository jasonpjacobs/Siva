from ..qt_bindings import QtCore, QtGui, Qt
from ..icons import ICONS
class TabWidget(QtGui.QTabWidget):

    def __init__(self):
        super().__init__()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.create_context_menu()
        #self.customContextMenuRequested.connect(self.show_context_menu)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBar().setMovable(True)

    def create_context_menu(self):
        icons = ICONS
        menu = QtGui.QMenu()

        action = QtGui.QAction(icons[""], 'Close me', self)
        action.triggered.connect(self.close_tab)
        self.close_action = action
        menu.addAction(self.close_action)

        action = QtGui.QAction(icons[""], 'Close others', self)
        action.triggered.connect(self.close_others)
        self.close_others_action = action
        menu.addAction(self.close_others_action)

        action = QtGui.QAction(icons[""], 'Close all', self)
        action.triggered.connect(self.close_all)
        self.close_all_action = action
        menu.addAction(self.close_all_action)

        self.context_menu = menu


    def mousePressEvent(self, event):
        menu = self.context_menu
        self.chosen_index = index = self.tabBar().tabAt(event.pos())
        if index >= 0:
            menu.exec_(event.globalPos())


    def close_tab(self, index = None):
        if index is None:
            index = self.chosen_index
        widget = self.widget(index)
        widget.close()
        del(widget)
        self.removeTab(index)

    def close_others(self):
        index = self.chosen_index
        for i in reversed(range(self.count())):
            if i != index:
                self.close_tab(i)

    def close_all(self, index = None):
        self.clear()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count():
            pass
        else:
            painter = QtGui.QPainter()
            painter.begin(self)

            coords = self.rect().getCoords()[::-1]
            gradient = QtGui.QLinearGradient(*coords)
            gradient.setColorAt(1, Qt.gray)
            gradient.setColorAt(0, Qt.white)
            painter.setBrush(gradient)

            font = QtGui.QFont()
            font.setBold(True)
            font.setPixelSize(20)

            painter.setPen(QtGui.QColor("#555555"))
            painter.setFont(font)
            painter.fillRect(self.rect(), painter.brush())
            painter.drawText(self.rect(), Qt.AlignCenter, "No views are open.")





