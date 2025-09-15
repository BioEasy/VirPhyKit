from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QFileDialog, QLabel, QGroupBox, QTextEdit,
                             QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from MakovMJump.function_mmj import generate_config


class ConfigGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('MJRM Generator (Markov Jumps and Rewards Matrix Generator)')
        self.setGeometry(300, 300, 500, 450)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_label = QLabel("MJRM Generator (Markov Jumps and Rewards Matrix Generator)")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 10px; background-color: #ffffff; border-radius: 5px;")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_layout.addWidget(title_label)
        help_button = QPushButton("?")
        help_button.setFixedSize(20, 20)
        help_button.setStyleSheet("""
            QPushButton { 
                background-color: #2196F3; 
                color: white; 
                border-radius: 10px; 
                font-weight: bold; 
                font-size: 12px; 
            }
            QPushButton:hover { 
                background-color: #00008b; 
            }
        """)
        help_button.setToolTip(
            '<span style="font-family: Arial; font-size: 12px;">'
            'Step 1: Specify the discrete trait categories (e.g. location, host, etc.) as comma-separated values.<br>'
            'Step 2: Upload a BEAUti 1.x-generated xml file for modification.<br>'
            'Step 3: Specify the output directory and name for the new xml file.<br>'
            'Step 4: Click [Run] to automatically generate and insert the matrix module into the new xml file.<br>'
            'Step 5: If you choose not to upload the XML file, the generated Markov jump and reward matrix will be saved in txt format in the specified output directory.'
            '</span>'
        )
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)
        description_label = QLabel()
        description_label.setText("""
        <p style="line-height: 120%; margin: 0; padding: 0;">
        &nbsp;&nbsp;&nbsp;&nbsp;MJRM is a specialized tool that automatically constructs Markov jump and reward matrices from user-defined discrete traits for phylogeographic analysis.
        It seamlessly integrates these matrices into BEAST-compatible XML configuration files.
        </p>
        """)
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignLeft)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("padding: 5px; border: none; color: #808080; font-size: 12px;")
        main_layout.addWidget(description_label)
        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(5)
        settings_layout.setContentsMargins(10, 5, 10, 5)
        migr_label = QLabel("Traits parameters (comma separated):")
        migr_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(migr_label)
        self.migr_input = QLineEdit()
        self.migr_input.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px;")
        settings_layout.addWidget(self.migr_input)
        xml_label = QLabel("Input xml File (optional):")
        xml_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(xml_label)
        xml_widget = QWidget()
        xml_hbox = QHBoxLayout()
        xml_hbox.setSpacing(5)
        self.xml_input = QLineEdit()
        self.xml_input.setReadOnly(True)
        self.xml_input.setPlaceholderText('Select xml file')
        self.xml_input.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px;")
        xml_hbox.addWidget(self.xml_input)
        xml_browse_button = QPushButton("...")
        xml_browse_button.setFixedWidth(40)
        xml_browse_button.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        xml_browse_button.clicked.connect(self.browse_xml_file)
        xml_hbox.addWidget(xml_browse_button)
        xml_widget.setLayout(xml_hbox)
        settings_layout.addWidget(xml_widget)
        output_label = QLabel("Output directory:")
        output_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(output_label)
        output_widget = QWidget()
        output_hbox = QHBoxLayout()
        output_hbox.setSpacing(5)
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText('Select output directory')
        self.path_input.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px;")
        output_hbox.addWidget(self.path_input)
        browse_button = QPushButton("...")
        browse_button.setFixedWidth(40)
        browse_button.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        browse_button.clicked.connect(self.browse_folder)  # Changed to browse folder
        output_hbox.addWidget(browse_button)
        output_widget.setLayout(output_hbox)
        settings_layout.addWidget(output_widget)
        filename_label = QLabel("Output filename:")
        filename_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(filename_label)
        self.filename_input = QLineEdit("config")
        self.filename_input.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px;")
        settings_layout.addWidget(self.filename_input)
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        status_layout.setContentsMargins(10, 5, 10, 5)
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("border: 1px solid #ddd; background-color: #f9f9f9; font-size: 12px;")
        self.status_text.setMinimumHeight(100)
        self.status_text.setText("Ready")
        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=1)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.generate_button = QPushButton("Generate")
        self.generate_button.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        self.generate_button.clicked.connect(self.generate_config)
        button_layout.addWidget(self.generate_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            QLineEdit { border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px; }
            QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
        """)
    def browse_xml_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select XML File', '', 'XML Files (*.xml);;All Files (*)')
        if file_path:
            self.xml_input.setText(file_path)
            self.status_text.setPlainText('Selected XML: ' + file_path)
    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if folder_path:
            self.path_input.setText(folder_path)
            self.status_text.setPlainText('Selected Output Folder: ' + folder_path)
    def set_status_message(self, message, success=True):
        self.status_text.clear()
        color = QColor("Green") if success else QColor("Red")
        cursor = self.status_text.textCursor()
        format = cursor.charFormat()
        format.setForeground(color)
        cursor.setCharFormat(format)
        self.status_text.setTextCursor(cursor)
        self.status_text.insertPlainText(message)
    def generate_config(self):
        migr_text = self.migr_input.text().strip()
        file_path = self.path_input.text().strip()
        filename = self.filename_input.text().strip()
        xml_path = self.xml_input.text().strip() or None
        success, message = generate_config(migr_text, file_path, filename, xml_path)
        self.set_status_message(message, success)