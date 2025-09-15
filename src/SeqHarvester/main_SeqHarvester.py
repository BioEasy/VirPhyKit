from PyQt5.QtWidgets import QApplication
import sys
from SeqHarvester.function_SeqHarvester import VirusAnalysisApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirusAnalysisApp()
    window.show()
    sys.exit(app.exec_())