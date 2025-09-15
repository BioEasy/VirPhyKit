from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QGroupBox, QStatusBar, QTextEdit,
                             QHeaderView, QSizePolicy, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
class VirusAnalysisUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SeqHarvester")
        self.initUI()
    def initUI(self):
        self.setGeometry(100, 100, 700, 600)
        font = QFont("Arial", 10)
        QApplication.setFont(font)
        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)
        # Title with Help Button
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_label = QLabel("SeqHarvester (Sequence Metadata Harvester)")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 5px; background-color: #ffffff; border-radius: 5px;")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
            'Step 1: Enter the full name of the virus for retrieval or upload a text file containing the accession number.<br>'
            'Step 2: When retrieving by virus name, the results will display the complete metadata for all available isolates from GenBank in the "Result" panel.<br>'
            'Step 3: From the "Genome Segments" dropdown menu, select the required segment.<br>'
            'Step 4: Select a valid output directory, then click [Download] to initiate sequence retrieval.(The accession number txt file of all selected sequences will also be downloaded)'
            '</span>'
        )
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel(
            "SeqHarvester retrieves viral isolates from GenBank, displaying comprehensive metadata for filtering and download.")
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setStyleSheet("padding: 5px; border: none;color: #808080;")
        main_layout.addWidget(description_label, alignment=Qt.AlignCenter)

        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(5)
        settings_layout.setContentsMargins(5, 5, 5, 5)
  
        input_layout = QHBoxLayout()
        self.virus_label = QLabel("Virus Name:")
        self.virus_label.setStyleSheet("font-size: 12px;")
        self.virus_input = QLineEdit()
        self.virus_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;font-size: 12px;")
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("""
            QPushButton{
            padding: 5px 10px;
            background-color: #2196F3;
            color: white;
            font-size: 12px;
            border-radius: 5px;
            font-weight: bold;}
            QPushButton:hover{
            background-color: #00008b
            }
        """)
        self.search_button.setFixedWidth(100)
        input_layout.addWidget(self.virus_label)
        input_layout.addWidget(self.virus_input)
        input_layout.addWidget(self.search_button)
        settings_layout.addLayout(input_layout)
        or_label = QLabel("     OR      ")
        or_label.setStyleSheet("font-weight: bold; margin: 2px 0px;font-size: 12px;")
        or_label.setContentsMargins(0, 2, 0, 2)
        settings_layout.addWidget(or_label)
        accession_layout = QHBoxLayout()
        self.accession_label = QLabel("Accession File:")
        self.accession_label.setStyleSheet("font-size: 12px;")
        self.accession_input = QLineEdit()
        self.accession_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;font-size: 12px;")
        self.accession_browse_button = QPushButton("...")
        self.accession_browse_button.setStyleSheet("""
            QPushButton{
            padding: 5px 10px;
            background-color: #2196F3;
            color: white;
            border-radius: 5px;
            font-size: 12px;
            font-weight: bold;}
            QPushButton:hover{
            background-color: #00008b
            }
        """)
        self.accession_browse_button.setFixedWidth(100)
        accession_layout.addWidget(self.accession_label)
        accession_layout.addWidget(self.accession_input)
        accession_layout.addWidget(self.accession_browse_button)
        settings_layout.addLayout(accession_layout)
        settings_group.setLayout(settings_layout)
        settings_group.setContentsMargins(5, 5, 5, 5)
        settings_group.setFixedHeight(settings_group.sizeHint().height() + 5)
        main_layout.addWidget(settings_group)

        download_group = QGroupBox("Options")
        download_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        download_layout = QVBoxLayout()
        download_layout.setSpacing(5)
        download_layout.setContentsMargins(5, 5, 5, 5)

        path_layout = QHBoxLayout()
        self.path_label = QLabel("Output Directory:")
        self.path_label.setStyleSheet("font-size: 12px;")
        self.path_input = QLineEdit()
        self.path_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;font-size: 12px;")
        self.browse_button = QPushButton("...")
        self.browse_button.setStyleSheet("""
            QPushButton{
            padding: 5px 10px;
            background-color: #2196F3;
            color: white;
            font-size: 12px;
            border-radius: 5px;
            font-weight: bold;}
            QPushButton:hover{
            background-color: #00008b
            }
        """)
        self.browse_button.setFixedWidth(100)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        download_layout.addLayout(path_layout)

        self.combo_layout = QHBoxLayout()
        self.combo_label = QLabel("Genome Segments:")
        self.combo_label.setStyleSheet("font-size: 12px;")
        self.combo_layout.addWidget(self.combo_label)
        self.download_button = QPushButton("Download")
        self.download_button.setStyleSheet("""
            QPushButton{
            padding: 5px 10px;
            background-color: #2196F3;
            color: white;
            font-size: 12px;
            border-radius: 5px;
            font-weight: bold;}
            QPushButton:hover{
            background-color: #00008b
            }
        """)
        self.download_button.setFixedWidth(100)
        self.combo_layout.addWidget(self.download_button)
        download_layout.addLayout(self.combo_layout)
        download_group.setLayout(download_layout)
        download_group.setFixedHeight(download_group.sizeHint().height() + 20)
        main_layout.addWidget(download_group)

        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QVBoxLayout()
        self.status_label = QTextEdit()
        self.status_label.setReadOnly(True)
        self.status_label.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 3px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        """)
        self.status_label.setText("Enter the full virus name to retrieve sequences,"
                                  "or select an accession number file to download sequences directly.")
        self.status_label.setStyleSheet("font-size: 12px;")
        status_layout.addWidget(self.status_label)
        self.progress_label = QLabel("Retrieval progress: 0/0")
        self.progress_label.setStyleSheet("font-size: 12px;")
        status_layout.addWidget(self.progress_label)
        status_group.setLayout(status_layout)
        status_group.setFixedHeight(150)
        main_layout.addWidget(status_group)

        result_group = QGroupBox("Results")
        result_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        result_layout = QVBoxLayout()
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["Type", "Number", "Percentage", "Describe"])
        self.result_table.setStyleSheet("Font-size: 12px;")
        self.result_table.setSortingEnabled(True)
        self.result_table.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")
        header = self.result_table.horizontalHeader()
        for i in range(4):
            header.setDefaultAlignment(Qt.AlignLeft)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.setMinimumHeight(100)  
        self.result_table.setMaximumHeight(130) 
        self.result_table.setMinimumWidth(500)
        self.result_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.result_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.result_table.verticalHeader().setDefaultSectionSize(30)
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        result_group.setMinimumHeight(140)
        result_group.setMaximumHeight(170)
        main_layout.addWidget(result_group)
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready", 5000)
        status_bar.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-top: 1px solid #ddd;font-size: 12px;")
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