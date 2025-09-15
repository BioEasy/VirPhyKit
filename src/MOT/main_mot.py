from PyQt5.QtWidgets import QApplication
import sys
from MOT.layout_mot import MigrationPlotter

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MigrationPlotter()
    window.show()
    sys.exit(app.exec_())