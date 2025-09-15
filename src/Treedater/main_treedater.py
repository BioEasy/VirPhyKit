import sys
from PyQt5 import QtWidgets
from Treedater.function_treedater import TreeDaterFunctions
from Treedater.layout_treedater import TreeDaterLayout

class TreeDaterApp(QtWidgets.QMainWindow, TreeDaterFunctions, TreeDaterLayout):
    def __init__(self):
        super().__init__()
        self.tree_file = ""
        self.metadata_file = ""
        self.output_dir = ""
        self.init_ui()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = TreeDaterApp()
    window.show()
    sys.exit(app.exec_())