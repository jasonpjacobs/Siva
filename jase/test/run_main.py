import sys
from jase.ui.main import Main
from jase.ui.app import App
app = App()

if __name__ == "__main__":
    m = Main()
    m.setGeometry(100, 100, 1200, 800)
    m.show()
    sys.exit(app.exec_())