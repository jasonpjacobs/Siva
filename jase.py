import sys
import os
os.environ['QT_API'] = 'pyqt'
import siva
app = siva.App()

if __name__ == "__main__":
    m = siva.Main(app=app)
    m.setGeometry(100, 100, 1200, 800)
    m.showMaximized()
    sys.exit(app.exec_())