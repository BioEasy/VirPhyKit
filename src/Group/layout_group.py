from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGroupBox, QLineEdit,
                             QTableWidget, QProgressBar, QSizePolicy, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Group.function_group import process_data

class GroupModule(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data = []
        self.worker = None
        self.seq_file_path = None
        self.accession_file_path = None
        self.region_file_path = None
        self.last_group_column = -1

    def initUI(self):
        self.setWindowTitle("SeqGrouper")
        self.setGeometry(100, 100, 800, 600)

        font = QFont("Arial", 10)
        QApplication.setFont(font)

        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Title with Question Mark
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_label = QLabel("SeqGrouper (Sequence Grouping Tool)")
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
        help_button.setToolTip("Step 1: Upload accession numbers in a text file (.txt) or upload a GenBank file (.gb).\n"
                               "Step 2: After checking 'Enabled', you can choose to use default grouping rules (by region) or upload a custom grouping table.\n"
                               "Step 3: Click ‘Show Table’ to display viral isolate information (You can double-click any information to modify it.).\n"
                               "Step 4: Select the columns that need to be grouped and click 'View' to view the group distribution. Note: The grouped columns will be added to the table.")
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel()
        description_label.setText("""
        <p style="line-height: 120%; margin: 0; padding: 0;">
        &nbsp;&nbsp;&nbsp;&nbsp;SeqGrouper is a specialized tool for grouping viral sequences into customizable categories(e.g.,geographic region,host,or user-defined criteria),
        with automated distribution reports for research and surveillance.
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

        api_key_label = QLabel("NCBI API Key (Optional):")
        api_key_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(api_key_label)
        self.api_key_input = QLineEdit()
        self.api_key_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        self.api_key_input.setPlaceholderText("Enter NCBI API key for faster requests")
        settings_layout.addWidget(self.api_key_input)

        accession_label = QLabel("Accession File (.txt):")
        accession_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(accession_label)
        accession_widget = QWidget()
        accession_hbox = QHBoxLayout()
        accession_hbox.setSpacing(5)
        self.accession_dir_input = QLineEdit()
        self.accession_dir_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        self.accession_dir_input.setToolTip(self.accession_dir_input.text())
        accession_hbox.addWidget(self.accession_dir_input)
        accession_dir_button = QPushButton("...")
        accession_dir_button.setStyleSheet("""
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
        accession_dir_button.clicked.connect(self.select_accession_file)
        accession_hbox.addWidget(accession_dir_button)
        accession_widget.setLayout(accession_hbox)
        settings_layout.addWidget(accession_widget)

        or_label = QLabel("OR")
        or_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        settings_layout.addWidget(or_label)

        seq_label = QLabel("GenBank File (.gb):")
        seq_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(seq_label)
        seq_widget = QWidget()
        seq_hbox = QHBoxLayout()
        seq_hbox.setSpacing(5)
        self.seq_dir_input = QLineEdit()
        self.seq_dir_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        self.seq_dir_input.setToolTip(self.seq_dir_input.text())
        seq_hbox.addWidget(self.seq_dir_input)
        seq_dir_button = QPushButton("...")
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

        region_label = QLabel("Category Mapping Table (.txt):")
        region_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(region_label)
        region_widget = QWidget()
        region_hbox = QHBoxLayout()
        region_hbox.setSpacing(5)
        self.region_dir_input = QLineEdit()
        self.region_dir_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        self.region_dir_input.setPlaceholderText("Built-in default mapping table (grouped by region)")
        self.region_dir_input.setToolTip("Leave blank to use the default Mapping.txt in the program directory.")
        region_hbox.addWidget(self.region_dir_input)
        region_dir_button = QPushButton("...")
        region_dir_button.setStyleSheet("""
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
        region_dir_button.clicked.connect(self.select_region_table)
        region_hbox.addWidget(region_dir_button)
        region_widget.setLayout(region_hbox)
        self.use_mapping_checkbox = QCheckBox("Enabled")
        self.use_mapping_checkbox.setStyleSheet("font-size: 12px;")
        self.use_mapping_checkbox.setChecked(True)
        settings_layout.addWidget(self.use_mapping_checkbox)
        settings_layout.addWidget(region_widget)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        table_group = QGroupBox("Sequence Information")
        table_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        table_layout = QVBoxLayout()
        table_layout.setSpacing(5)
        table_layout.setContentsMargins(10, 5, 10, 5)

        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        table_layout.addWidget(self.table)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        table_layout.addWidget(self.progress_bar)

        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group, stretch=1)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.show_button = QPushButton("Show Table")
        self.show_button.setStyleSheet("""
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
        self.show_button.clicked.connect(self.show_table)
        self.show_button.setEnabled(False)
        button_layout.addWidget(self.show_button)

        self.preview_button = QPushButton("View")
        self.preview_button.setStyleSheet("""
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
        self.preview_button.clicked.connect(self.preview_groups)
        self.preview_button.setEnabled(True)
        button_layout.addWidget(self.preview_button)

        self.save_button = QPushButton("Save as CSV")
        self.save_button.setStyleSheet("""
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
        self.save_button.clicked.connect(self.save_to_csv)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)
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
        try:
            process_data.select_seq_file(self)
        except Exception as e:
            self.statusBar().showMessage(f"Error selecting sequence file: {str(e)}", 10000)

    def select_accession_file(self):
        try:
            process_data.select_accession_file(self)
        except Exception as e:
            self.statusBar().showMessage(f"Error selecting accession file: {str(e)}", 10000)

    def select_region_table(self):
        try:
            process_data.select_region_file(self)
            self.region_file_path = self.region_dir_input.text()
            if self.region_file_path:
                self.preview_button.setEnabled(True)
        except Exception as e:
            self.statusBar().showMessage(f"Error selecting grouping table: {str(e)}", 10000)

    def preview_groups(self):
        try:
            print("Preview button clicked")
            column_name = self.table.horizontalHeaderItem(self.last_group_column).text() if self.last_group_column >= 0 and self.table.horizontalHeaderItem(self.last_group_column) else "Geo Location"
            print(f"Using last clicked column: {column_name} (index: {self.last_group_column})")
            process_data.preview_groups(self, self.last_group_column)
        except Exception as e:
            self.statusBar().showMessage(f"Error in preview: {str(e)}", 10000)

    def on_header_clicked(self, column_index):
        try:
            column_name = self.table.horizontalHeaderItem(column_index).text() if self.table.horizontalHeaderItem(column_index) else f"Column {column_index}"
            print(f"Header clicked: {column_name} (index: {column_index})")
            self.last_group_column = column_index
            process_data.preview_groups(self, column_index)
        except Exception as e:
            self.statusBar().showMessage(f"Error in header click: {str(e)}", 10000)

    def show_table(self):
        try:
            process_data.show_table(self)
        except Exception as e:
            self.statusBar().showMessage(f"Error showing table: {str(e)}", 10000)

    def save_to_csv(self):
        try:
            process_data.save_to_csv(self)
        except Exception as e:
            self.statusBar().showMessage(f"Error saving to CSV: {str(e)}", 10000)