import sys
import jase
app = jase.App()

if __name__ == "__main__":
    m = jase.Main()
    m.setGeometry(100, 100, 1200, 800)
    m.show()
    sys.exit(app.exec_())