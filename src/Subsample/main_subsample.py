import sys
from PyQt5 import QtWidgets
from Subsample.layout_subsample import SubsampleApp

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SubsampleApp()
    window.show()
    sys.exit(app.exec_())

