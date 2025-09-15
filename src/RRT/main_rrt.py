import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from RRT.layout_rrt import RegionRandomizationTestPlotter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generator = RegionRandomizationTestPlotter()
        self.setWindowTitle(u'RegionRandomizationTestPlotter')
        self.setCentralWidget(self.generator)  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  
    window.show()  
    sys.exit(app.exec_())


