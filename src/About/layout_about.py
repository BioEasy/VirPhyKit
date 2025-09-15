import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QVBoxLayout, QLabel, QSizePolicy, QTextEdit, QHBoxLayout, QPushButton, QMainWindow


class AboutWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("About")
        self.setGeometry(100, 100, 400, 350)  # Smaller size for pop-up

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Title widget
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_label = QLabel("About")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            padding: 8px;
            background-color: #e0e0e0; 
            border-radius: 5px; 
            max-width: 150px;
            margin-left: auto;
            margin-right: auto;
        """)
        title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        title_layout.addWidget(title_label)

        # Info widget
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(20, 20, 20, 20)

        # HTML content with image and bolded text
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "About", "icon.ico")
        html_content = (
            f"<div style='text-align: center;'>"
            f"<img src='{icon_path}' width='250' height='250'><br><br>"
            "<b>VirPhyKit: an integrated toolkit for viral phylogeographic analysis 1.0</b><br><br>"
            "<span style='font-size: 14px;'>Copyright©️2025 Yin Y. and Gao F.<br><br>"
            "Presented by Yuqi Yin and Fangluan Gao.<br><br>"
            "Email: archieyin@163.com, raindy@fafu.edu.cn</span>"
            "</div>"
        )

        info_text_edit = QTextEdit()
        info_text_edit.setHtml(html_content)
        info_text_edit.setReadOnly(True)
        info_text_edit.setStyleSheet("""
            background-color: #ffffff;
            border: 1px solid #ccc;
            border-radius: 5px;
            color: #333;
            padding: 20px;
        """)
        info_font = QFont("Arial", 14)
        info_text_edit.setFont(info_font)
        info_text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        info_layout.addWidget(info_text_edit)

        # Add widgets to main layout
        main_layout.addWidget(title_widget)
        main_layout.addWidget(info_widget, stretch=1)
        # Removed main_layout.addStretch() to allow info_widget to fill the space

        # Set main widget as the dialog's layout
        self.setLayout(main_layout)


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Main Application")
        self.setGeometry(100, 100, 800, 600)

        # Create a button to open the About dialog
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        button = QPushButton("Open About Window")
        button.clicked.connect(self.showAboutDialog)
        main_layout.addWidget(button)
        self.setCentralWidget(main_widget)

    def showAboutDialog(self):
        about_dialog = AboutWindow(self)
        about_dialog.exec_()  # Show as modal dialog


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec_())