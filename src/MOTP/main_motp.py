import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from layout_motp import MigrationOverTimePlotter

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Arial", 10))  # Global font
    window = MigrationOverTimePlotter()
    window.show()
    sys.exit(app.exec_())