from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QSizePolicy, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from Rename.function_rename import rename_sequences
class RenameSequencesApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle("SeqIDRenamer")
        self.setGeometry(100, 100, 800, 600)
        font = QtGui.QFont("Arial", 10)
        QtWidgets.QApplication.setFont(font)
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        main_layout = QtWidgets.QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_label = QtWidgets.QLabel("SeqIDRenamer (Sequence Identifier Renamer)")
        title_label.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        title_label.setAlignment(QtCore.Qt.AlignCenter)
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
        help_button.setToolTip("Step 1: Select a FASTA sequence file to rename.\n"
                               "Step 2: Upload a tab-delimited mapping text file('OrgName\\tNewName').\n"
                               "Step 3: Select the output directory to save the renamed file.\n"
                               "Step 4: Click the 'Run' button to start the renaming process.")
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)
        description_label = QLabel()
        description_label.setText("""
        <p style="line-height: 120%; margin: 0; padding: 0;">
        &nbsp;&nbsp;&nbsp;&nbsp;SeqIDRenamer is a tool for rapid renaming sequence identifiers in FASTA files. 
        This utility provides a simple workflow for batch processing of sequence IDs using custom naming rules.
        </p>
        """)
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignLeft)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("padding: 5px; border: none; color: #808080; font-size: 12px;")
        main_layout.addWidget(description_label)
        settings_group = QtWidgets.QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        settings_layout = QtWidgets.QVBoxLayout()
        settings_layout.setSpacing(10)
        seq_label = QtWidgets.QLabel("Sequence File:")
        seq_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(seq_label)
        seq_widget = QtWidgets.QWidget()
        seq_hbox = QtWidgets.QHBoxLayout()
        self.seq_dir_input = QtWidgets.QLineEdit()
        self.seq_dir_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        seq_hbox.addWidget(self.seq_dir_input)
        seq_dir_button = QtWidgets.QPushButton("...")
        seq_dir_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        seq_dir_button.clicked.connect(self.select_seq_file)
        seq_hbox.addWidget(seq_dir_button)
        seq_widget.setLayout(seq_hbox)
        settings_layout.addWidget(seq_widget)
        rename_label = QtWidgets.QLabel("Name Mapping File:")
        rename_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(rename_label)
        rename_widget = QtWidgets.QWidget()
        rename_hbox = QtWidgets.QHBoxLayout()
        self.rename_input = QtWidgets.QLineEdit()
        self.rename_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        rename_hbox.addWidget(self.rename_input)
        rename_button = QtWidgets.QPushButton("...")
        rename_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        rename_button.clicked.connect(self.select_rename_file)
        rename_hbox.addWidget(rename_button)
        rename_widget.setLayout(rename_hbox)
        settings_layout.addWidget(rename_widget)
        output_label = QtWidgets.QLabel("Output Directory:")
        output_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(output_label)
        output_widget = QtWidgets.QWidget()
        output_hbox = QtWidgets.QHBoxLayout()
        self.output_dir_input = QtWidgets.QLineEdit()
        self.output_dir_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        output_hbox.addWidget(self.output_dir_input)
        output_dir_button = QtWidgets.QPushButton("...")
        output_dir_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        output_dir_button.clicked.connect(self.select_output_directory)
        output_hbox.addWidget(output_dir_button)
        output_widget.setLayout(output_hbox)
        settings_layout.addWidget(output_widget)
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        status_group = QtWidgets.QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QtWidgets.QVBoxLayout()
        self.status_output = QtWidgets.QTextEdit()
        self.status_output.setReadOnly(True)
        self.status_output.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        """)
        status_layout.addWidget(self.status_output)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=1)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        self.rename_button = QtWidgets.QPushButton("Run")
        self.rename_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        self.rename_button.clicked.connect(self.rename_sequences)
        button_layout.addWidget(self.rename_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready", 5000)
        status_bar.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-top: 1px solid #ddd;")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QLineEdit {
                border: 1px solid #ddd;
            }
        """)
    def select_seq_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Sequence File", "","Text Files (*.fasta);;All Files (*)")
        if file_name:
            self.seq_dir_input.setText(file_name)
            self.statusBar().showMessage(f"Loaded sequence file: {file_name}", 5000)
    def select_rename_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Rename Mapping File", "",
                                                             "Text Files (*.txt);;All Files (*)")
        if file_name:
            self.rename_input.setText(file_name)
            self.statusBar().showMessage(f"Loaded rename mapping file: {file_name}", 5000)
    def select_output_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_input.setText(directory)
            self.statusBar().showMessage(f"Output directory set to: {directory}", 5000)
    def rename_sequences(self):
        seq_file = self.seq_dir_input.text()
        rename_file = self.rename_input.text()
        output_dir = self.output_dir_input.text()
        if not seq_file or not rename_file or not output_dir:
            self.status_output.append("<b><span style='color: red;'>Please select all required files and the output directory!</span></b>")
            self.statusBar().showMessage("Error: Missing required input", 5000)
            return
        try:
            output_file = rename_sequences(seq_file, rename_file, output_dir)
            self.status_output.append(f"<b><span style='color: green;'>Renaming completed! New file created: {output_file}</span></b>")
            self.statusBar().showMessage(f"Renaming completed! New file created: {output_file}", 5000)
        except Exception as e:
            self.status_output.append(f"<b><span style='color: red;'>Error: {str(e)}</span></b>")
            self.statusBar().showMessage(f"Error: {str(e)}", 5000)