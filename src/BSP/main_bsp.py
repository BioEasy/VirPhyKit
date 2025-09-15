import sys
from PyQt5.QtWidgets import QApplication
from layout_bsp import BayesianSkylinePlotAPP

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BayesianSkylinePlotAPP()
    ex.show()
    sys.exit(app.exec_())