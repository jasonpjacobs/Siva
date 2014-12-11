import sys
import os
os.environ['QT_API'] = 'pyqt'
import jase
app = jase.App()

if __name__ == "__main__":
    m = jase.Main()
    m.setGeometry(100, 100, 1200, 800)
    m.showMaximized()
    sys.exit(app.exec_())