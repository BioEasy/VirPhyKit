from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QLabel, QLineEdit, QPushButton, QTextEdit,
                             QStatusBar, QFileDialog, QSizePolicy, QProgressBar)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Treetime.function_treetime import TreeTimeWorker

class TreeTimeUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fasta_file = None
        self.tree_file = None
        self.dates_file = None
        self.output_dir = None
        self.mapping_file = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("TreeTime-RTT (Root-to-tip Regression by TreeTime)")
        self.setGeometry(100, 100, 800, 600)
   
        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_label = QLabel("TreeTime-RTT (Root-to-tip Regression by TreeTime)")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 8px; background-color: #ffffff; border-radius: 5px;")
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
            'Step 1: Upload a FASTA sequence file, a Newick tree file, and a metadata file (.csv).<br>'
            'Step 2: If the third column of the metadata file is a "region" (or other trait) column and a trait mapping file is uploaded, isolates sharing the same trait will be color-coded in the plot.Otherwise, only the standard RTT regression plot will be generated.<br>'
            'Step 3: Select the traits mapping file.<br>'
            'Step 4: Click "Run" to perform the RTT analysis.'
            '</span>'
        )
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel()
        description_label.setText("""
        <p style="line-height: 120%; margin: 0; padding: 0;">
        &nbsp;&nbsp;&nbsp;&nbsp;TreeTime-RTT is a tool for assessing temporal signal (clock-like evolutionary patterns)
        through linear regression of root-to-tip distance against sampling dates in TreeTime.
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

        fasta_label = QLabel("Fasta File (Aligned):")
        fasta_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(fasta_label)
        fasta_widget = QWidget()
        fasta_hbox = QHBoxLayout()
        self.fasta_input = QLineEdit()
        self.fasta_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px; font-size: 12px;")
        fasta_hbox.addWidget(self.fasta_input)
        self.fasta_browse = QPushButton("...")
        self.fasta_browse.setFixedWidth(30)
        self.fasta_browse.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        self.fasta_browse.clicked.connect(self.browse_fasta)
        fasta_hbox.addWidget(self.fasta_browse)
        fasta_widget.setLayout(fasta_hbox)
        settings_layout.addWidget(fasta_widget)
        tree_label = QLabel("Newick Tree File:")
        tree_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(tree_label)
        tree_widget = QWidget()
        tree_hbox = QHBoxLayout()
        self.tree_input = QLineEdit()
        self.tree_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px;font-size: 12px;")
        tree_hbox.addWidget(self.tree_input)
        self.tree_browse = QPushButton("...")
        self.tree_browse.setFixedWidth(30)
        self.tree_browse.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        self.tree_browse.clicked.connect(self.browse_tree)
        tree_hbox.addWidget(self.tree_browse)
        tree_widget.setLayout(tree_hbox)
        settings_layout.addWidget(tree_widget)
  
        dates_label = QLabel("Metadata File:")
        dates_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(dates_label)
        dates_widget = QWidget()
        dates_hbox = QHBoxLayout()
        self.dates_input = QLineEdit()
        self.dates_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px;font-size: 12px;")
        dates_hbox.addWidget(self.dates_input)
        self.dates_browse = QPushButton("...")
        self.dates_browse.setFixedWidth(30)
        self.dates_browse.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        self.dates_browse.clicked.connect(self.browse_dates)
        dates_hbox.addWidget(self.dates_browse)
        dates_widget.setLayout(dates_hbox)
        settings_layout.addWidget(dates_widget)

        mapping_label = QLabel("Mapping File (Optional):")
        mapping_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(mapping_label)
        mapping_widget = QWidget()
        mapping_hbox = QHBoxLayout()
        self.mapping_input = QLineEdit()
        self.mapping_input.setPlaceholderText("Built-in default mapping table (grouped by region)")
        self.mapping_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px;font-size: 12px;")
        mapping_hbox.addWidget(self.mapping_input)
        self.mapping_browse = QPushButton("...")
        self.mapping_browse.setFixedWidth(30)
        self.mapping_browse.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        self.mapping_browse.clicked.connect(self.browse_mapping)
        mapping_hbox.addWidget(self.mapping_browse)
        mapping_widget.setLayout(mapping_hbox)
        settings_layout.addWidget(mapping_widget)
        # output directory
        output_label = QLabel("Output Directory:")
        output_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(output_label)
        output_widget = QWidget()
        output_hbox = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px;font-size: 12px;")
        output_hbox.addWidget(self.output_input)
        self.output_browse = QPushButton("...")
        self.output_browse.setFixedWidth(30)
        self.output_browse.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        self.output_browse.clicked.connect(self.browse_output)
        output_hbox.addWidget(self.output_browse)
        output_widget.setLayout(output_hbox)
        settings_layout.addWidget(output_widget)
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QVBoxLayout()
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 5px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            font-size: 12px;
        """)
        status_layout.addWidget(self.status_text)
  
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setVisible(False)  # Hidden by default
        status_layout.addWidget(self.progress_bar)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=0)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.generate_btn = QPushButton("Run")
        self.generate_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.generate_btn.clicked.connect(self.run_analysis)
        button_layout.addWidget(self.generate_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
    
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready", 5000)
        status_bar.setStyleSheet("background-color: #f0f0f0; padding: 3px; border-top: 1px solid #ddd;font-size: 12px;")
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
            QProgressBar {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                height: 10px;
            }
        """)

    def browse_fasta(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select FASTA File", "", "FASTA Files (*.fasta *.fas *.fa)")
        if file_name:
            self.fasta_input.setText(file_name)
            self.fasta_file = file_name

    def browse_tree(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Newick Tree File", "", "Newick Files (*.nwk *.tree)")
        if file_name:
            self.tree_input.setText(file_name)
            self.tree_file = file_name

    def browse_dates(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Dates CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.dates_input.setText(file_name)
            self.dates_file = file_name

    def browse_mapping(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Mapping File", "", "Text Files (*.txt)")
        if file_name:
            self.mapping_input.setText(file_name)
            self.mapping_file = file_name

    def browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_input.setText(directory)
            self.output_dir = directory

    def update_status(self, message):
        self.status_text.append(message)
        self.status_text.ensureCursorVisible()
        QApplication.processEvents()

    def analysis_finished(self):
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.status_text.append("<b><span style='color: green;'>Analysis complete!</span></b>")
        self.statusBar().showMessage("Analysis completed", 5000)
        self.worker = None

    def analysis_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.status_text.append(f"<b><span style='color: red;'>Error: {error_msg}</span></b>")
        self.statusBar().showMessage(f"Error: {error_msg}", 5000)
        self.worker = None

    def run_analysis(self):
        if not all([self.fasta_file, self.tree_file, self.dates_file, self.output_dir]):
            self.status_text.append("<b><span style='color: red;'>Error: Please select all required input files and output directory</span></b>")
            self.statusBar().showMessage("Error: Missing inputs", 5000)
            return
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_text.clear()
        self.status_text.append("<b><span style='color: blue;'>Running analysis...</span></b>")
        self.statusBar().showMessage("Running analysis...", 0)
        self.worker = TreeTimeWorker(self.fasta_file, self.tree_file, self.dates_file, self.output_dir, self.mapping_file)
        self.worker.log_signal.connect(self.update_status)
        self.worker.finished_signal.connect(self.analysis_finished)
        self.worker.error_signal.connect(self.analysis_error)
        self.worker.start()