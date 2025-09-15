from PyQt5.QtWidgets import QApplication
import sys
from Group.layout_group import GroupModule

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GroupModule()
    ex.show()
    sys.exit(app.exec_())