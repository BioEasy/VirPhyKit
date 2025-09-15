from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QSizePolicy, QLabel, QComboBox, QRadioButton
from PyQt5.QtCore import Qt
from Subsample.fuction_subsample import run_subsampling

class SubsamplingThread(QtCore.QThread):
    finished = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    status_update = QtCore.pyqtSignal(str)

    def __init__(self, fasta_file, num_seqs, region, output_dir, equal_sampling, replicates=1):
        super().__init__()
        self.fasta_file = fasta_file
        self.num_seqs = num_seqs
        self.region = region
        self.output_dir = output_dir
        self.equal_sampling = equal_sampling
        self.replicates = replicates

    def run(self):
        try:
            if self.equal_sampling:
                for i in range(self.replicates):
                    output_file = f"extract_rep{i+1}.fas" if self.replicates > 1 else "extract.fas"
                    result = run_subsampling(
                        self.fasta_file, self.num_seqs, self.region,
                        self.output_dir, self.equal_sampling, self.status_update,
                        output_file_name=output_file
                    )
                    if i == 0:
                        self.status_update.emit(result)
                self.finished.emit(f"<b><span style='color: green;'>Done! Generated {self.replicates} bootstrap subsampling replicates. Output file: {self.output_dir}</span></b>")
            else:
                result = run_subsampling(self.fasta_file, self.num_seqs, self.region, self.output_dir, self.equal_sampling, self.status_update)
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class SubsampleApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GeoSubSampler")
        self.setGeometry(100, 100, 700, 500)

        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        main_layout = QtWidgets.QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_label = QtWidgets.QLabel("GeoSubsampler (Sequence Geographic Subsampler)")
        title_label.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("padding: 8px; background-color: #ffffff; border-radius: 5px;")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_layout.addWidget(title_label)

        help_button = QPushButton("?")
        help_button.setFixedSize(20, 20)
        help_button.setStyleSheet("""
            QPushButton { background-color: #1E90FF; color: white; border-radius: 10px; font-weight: bold; font-size: 12px;}
            QPushButton:hover { background-color: #00008B; }
        """)
        help_button.setToolTip(
            '<span style="font-family: Arial; font-size: 12px;">'
            'Step 1: Upload a FASTA sequence file to be subsampled. Ensure each sequence name includes its geographic region (marked with _region)<br>'
            'Step 2: Specify the desired sample size and/or specific region for the subset;<br>'
            'Step 3: Enable the for subsample bootstrap analysis option and set the number of replicates. This will generate multiple subsampled datasets by randomly selecting sequences—using the smallest sample size among all regions — for each region;<br>'
            'Step 4: Select an output directory to save the resulting sequences.'
            '</span>'
        )
        title_layout.addWidget(help_button)

        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel()
        description_label.setText("""
        <p style="line-height: 120%; margin: 0; padding: 0;">
        &nbsp;&nbsp;&nbsp;&nbsp;GeoSubsampler is a specialized tool for region-stratified subsampling of FASTA-formatted sequence datasets.
        It generates balanced sequence subsets by either geographic region or sample size, with integrated support for bootstrap analysis.
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
        settings_layout.setSpacing(5)

        file_label = QtWidgets.QLabel("Sequence File:")
        file_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(file_label)
        file_widget = QtWidgets.QWidget()
        file_layout = QtWidgets.QHBoxLayout()
        self.file_dir_input = QtWidgets.QLineEdit()
        self.file_dir_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px;")
        file_layout.addWidget(self.file_dir_input)
        file_button = QtWidgets.QPushButton("...")
        file_button.setFixedWidth(30)
        file_button.setStyleSheet("""
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
        file_button.clicked.connect(self.select_file_directory)
        file_layout.addWidget(file_button)
        file_widget.setLayout(file_layout)
        settings_layout.addWidget(file_widget)

        output_label = QtWidgets.QLabel("Output Directory:")
        output_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(output_label)
        output_widget = QtWidgets.QWidget()
        output_layout = QtWidgets.QHBoxLayout()
        self.output_input = QtWidgets.QLineEdit()
        self.output_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px;")
        output_layout.addWidget(self.output_input)
        output_button = QtWidgets.QPushButton("...")
        output_button.setFixedWidth(30)
        output_button.setStyleSheet("""
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
        output_button.clicked.connect(self.select_output_directory)
        output_layout.addWidget(output_button)
        output_widget.setLayout(output_layout)
        settings_layout.addWidget(output_widget)

        mode_widget = QtWidgets.QWidget()
        mode_layout = QtWidgets.QHBoxLayout()
        self.normal_radio = QRadioButton("Normal")
        self.normal_radio.setStyleSheet("font-size: 12px")
        self.bootstrap_radio = QRadioButton("Bootstrap")
        self.bootstrap_radio.setStyleSheet("font-size: 12px")
        self.normal_radio.setChecked(True)
        mode_layout.addWidget(self.normal_radio)
        mode_layout.addWidget(self.bootstrap_radio)
        mode_layout.addStretch()
        mode_widget.setLayout(mode_layout)
        settings_layout.addWidget(mode_widget)

        self.normal_radio.toggled.connect(self.toggle_input_fields)
        self.bootstrap_radio.toggled.connect(self.toggle_input_fields)

        self.bootstrap_widget = QtWidgets.QWidget()
        bootstrap_layout = QtWidgets.QHBoxLayout()
        replicates_label = QtWidgets.QLabel("Replicates:")
        replicates_label.setStyleSheet("font-size :12px;")
        bootstrap_layout.addWidget(replicates_label)
        self.replicates_combo = QComboBox()
        self.replicates_combo.addItems(['10', '20', '30'])
        self.replicates_combo.setCurrentText('10')
        self.replicates_combo.setStyleSheet("font-size: 12px; padding: 3px; border: 1px solid #ddd; border-radius: 3px;")
        bootstrap_layout.addWidget(self.replicates_combo)
        bootstrap_layout.addStretch()
        self.bootstrap_widget.setLayout(bootstrap_layout)
        settings_layout.addWidget(self.bootstrap_widget)

        num_label = QtWidgets.QLabel("Number of Sequences:")
        num_label.setStyleSheet("font-size: 12px;")
        self.num_label = num_label
        settings_layout.addWidget(num_label)
        self.num_seqs_input = QtWidgets.QLineEdit()
        self.num_seqs_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px;")
        settings_layout.addWidget(self.num_seqs_input)

        region_label = QtWidgets.QLabel("Region (Optional)")
        region_label.setStyleSheet("font-size: 12px;")
        self.region_label = region_label
        settings_layout.addWidget(region_label)
        self.region_input = QtWidgets.QLineEdit()
        self.region_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 3px;")
        settings_layout.addWidget(self.region_input)

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
            border-radius: 3px;
            padding: 5px;
            font-size: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        """)
        self.status_output.append(
            "<b><span style='color: grey;'>Warning: The original file may be overwritten in region-specific mode. Please backup before running!</span></b>")
        status_layout.addWidget(self.status_output)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=0)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        self.run_button = QtWidgets.QPushButton("Run")
        self.run_button.setStyleSheet("""
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
        self.run_button.clicked.connect(self.run_subsample)
        button_layout.addWidget(self.run_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        status_bar = QtWidgets.QStatusBar()
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
        """)

        self.toggle_input_fields()

    def select_file_directory(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Sequence File", "",
                                                             "All Files (*)")
        if file_name:
            self.file_dir_input.setText(file_name)
            self.statusBar().showMessage(f"Loaded sequence file: {file_name}", 5000)

    def select_output_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_input.setText(directory)
            self.statusBar().showMessage(f"Output directory set to: {directory}", 5000)

    def toggle_input_fields(self):
        if self.bootstrap_radio.isChecked():
            self.num_seqs_input.setEnabled(False)
            self.region_input.setEnabled(False)
            self.num_label.hide()
            self.num_seqs_input.hide()
            self.region_label.hide()
            self.region_input.hide()
            self.bootstrap_widget.show()
        else:
            self.num_seqs_input.setEnabled(True)
            self.region_input.setEnabled(True)
            self.num_label.show()
            self.num_seqs_input.show()
            self.region_label.show()
            self.region_input.show()
            self.bootstrap_widget.hide()

    def run_subsample(self):
        fasta_file = self.file_dir_input.text()
        num_seqs = self.num_seqs_input.text()
        region = self.region_input.text().strip() or None
        output_path = self.output_input.text()
        equal_sampling = self.bootstrap_radio.isChecked()
        replicates = int(self.replicates_combo.currentText()) if equal_sampling else 1

        self.statusBar().showMessage(f"Starting subsampling...", 5000)

        if not fasta_file:
            self.status_output.append("<b><span style='color: red;'>Error: Please select a sequence file!</span></b>")
            self.statusBar().showMessage("Error: Missing sequence file", 5000)
            return

        if not equal_sampling and not num_seqs:
            self.status_output.append("<b><span style='color: red;'>Error: Please specify the number of sequences!</span></b>")
            self.statusBar().showMessage("Error: Missing number of sequences", 5000)
            return

        try:
            num_seqs = int(num_seqs) if num_seqs else 0
            if not equal_sampling and num_seqs <= 0:
                self.status_output.append("<b><span style='color: red;'>Error: Number of sequences must be greater than 0!</span></b>")
                self.statusBar().showMessage("Error: Invalid number of sequences", 5000)
                return
            self.status_output.append(f"Starting subsampling with {replicates} replicate(s)...")
            self.thread = SubsamplingThread(fasta_file, num_seqs, region, output_path, equal_sampling, replicates)
            self.thread.finished.connect(lambda result: self.status_output.append(result))
            self.thread.error.connect(lambda error: self.status_output.append(error))
            self.thread.status_update.connect(lambda msg: self.status_output.append(msg))
            self.thread.finished.connect(lambda _: self.statusBar().showMessage("Subsampling completed", 5000))
            self.thread.error.connect(lambda error: self.statusBar().showMessage(error, 5000))
            self.thread.start()

        except ValueError as ve:
            self.status_output.append(f"Error: Invalid number - {str(ve)}")
            self.statusBar().showMessage(f"Error: Invalid number - {str(ve)}", 5000)

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()
        event.accept()