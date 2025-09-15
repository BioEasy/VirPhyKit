from PyQt5 import QtWidgets
import sys
from Rename.layout_rename import RenameSequencesApp
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = RenameSequencesApp()
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()