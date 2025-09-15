import sys
from PyQt5.QtWidgets import QApplication
from MakovMJump.layout_mmj import ConfigGenerator

def main():
    app = QApplication(sys.argv)
    ex = ConfigGenerator()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()