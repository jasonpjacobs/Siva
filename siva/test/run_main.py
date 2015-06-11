import sys
from siva.ui.main import Main
from siva.ui.app import App
app = App()

if __name__ == "__main__":
    m = Main()
    m.setGeometry(100, 100, 1200, 800)
    m.show()
    sys.exit(app.exec_())