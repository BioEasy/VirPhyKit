from PyQt5.QtWidgets import QApplication
import sys
from layout_SamplePlot import PlotModule


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlotModule()
    ex.show()
    sys.exit(app.exec_())