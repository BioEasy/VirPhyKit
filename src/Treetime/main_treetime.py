import sys
from PyQt5.QtWidgets import QApplication
from layout_treetime import TreeTimeUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TreeTimeUI()
    ex.show()
    sys.exit(app.exec_())