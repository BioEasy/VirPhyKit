import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from RSPP.layout_rspp import RootStatePosteriorProbabilityGenerator

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generator = RootStatePosteriorProbabilityGenerator()
        self.setWindowTitle(u'Root State Posterior Probability Generator')
        self.setCentralWidget(self.generator)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


