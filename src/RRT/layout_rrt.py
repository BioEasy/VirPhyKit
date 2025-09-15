from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QTextEdit, QGroupBox, QStatusBar, QSizePolicy)
from PyQt5.QtCore import Qt
from RRT.function_rrt import browse_original_data_file, browse_randomized_data_files, generate_table, \
    plot_graph_from_csv

class RegionRandomizationTestPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('RRT (Region Randomization Test)')
        self.original_data = None
        self.randomized_data = []
        self.current_df = None
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)

        font = QFont("Arial", 10)
        QApplication.setFont(font)

        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_label = QLabel("RRT (Region Randomization Test)")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
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
            'Step 1: Upload the original MCC tree and the region-random MCC tree with feature annotations.<br>'
            'Step 2: Select an output directory for the posterior probability CSV table.<br>'
            'Step 3: Click [Run] to conduct regional randomization tests. The test results will be displayed on the Status panel.<br>'
            'Step 4: Specify the output directory for saving results.'
            '</span>'
            )
        title_layout.addWidget(help_button)

        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel()
        description_label.setText("""
        <p style="line-height: 120%; margin: 0; padding: 0;">
        &nbsp;&nbsp;&nbsp;&nbsp;RRT is a statistical method that detects sampling bias in phylogeographic analyses.
        It compares ancestral root state probabilities between the original dataset and location-permuted scenarios
        to correct for systematic overestimation of viral origins in oversampled regions.
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
        settings_layout.setSpacing(10)

        orig_label = QLabel("Original MCC Tree:")
        orig_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(orig_label)
        orig_widget = QWidget()
        orig_hbox = QHBoxLayout()
        self.original_data_input = QLineEdit()
        self.original_data_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        orig_hbox.addWidget(self.original_data_input)
        self.original_data_browse = QPushButton("...")
        self.original_data_browse.setStyleSheet("""
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
        self.original_data_browse.clicked.connect(self.browse_original_data)
        orig_hbox.addWidget(self.original_data_browse)
        orig_widget.setLayout(orig_hbox)
        settings_layout.addWidget(orig_widget)

        rand_label = QLabel("Randomized MCC Trees:")
        rand_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(rand_label)
        rand_widget = QWidget()
        rand_hbox = QHBoxLayout()
        self.randomized_data_input = QLineEdit()
        self.randomized_data_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        rand_hbox.addWidget(self.randomized_data_input)
        self.randomized_data_browse = QPushButton("...")
        self.randomized_data_browse.setStyleSheet("""
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
        self.randomized_data_browse.clicked.connect(self.browse_randomized_data)
        rand_hbox.addWidget(self.randomized_data_browse)
        rand_widget.setLayout(rand_hbox)
        settings_layout.addWidget(rand_widget)

        export_label = QLabel("Export Data (CSV):")
        export_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(export_label)
        export_widget = QWidget()
        export_hbox = QHBoxLayout()
        self.export_data_input = QLineEdit()
        self.export_data_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        export_hbox.addWidget(self.export_data_input)
        self.export_data_browse = QPushButton("...")
        self.export_data_browse.setStyleSheet("""
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
        self.export_data_browse.clicked.connect(self.browse_export_data)
        export_hbox.addWidget(self.export_data_browse)
        export_widget.setLayout(export_hbox)
        settings_layout.addWidget(export_widget)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QVBoxLayout()
        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        """)
        status_layout.addWidget(self.status_box)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.run_button = QPushButton("Run")
        self.run_button.setStyleSheet("""
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
        self.run_button.clicked.connect(self.run_export)
        button_layout.addWidget(self.run_button)
        self.preview_button = QPushButton("Preview")
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
        self.preview_button.clicked.connect(self.preview_plot)
        button_layout.addWidget(self.preview_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        status_bar = QStatusBar()
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

    def browse_original_data(self):
        file_name, last_set, last_set_prob, message = browse_original_data_file()
        if file_name:
            self.original_data_input.setText(file_name)
        if last_set and last_set_prob:
            self.original_data = {"set": last_set, "set_prob": last_set_prob}
            self.status_box.append("<span style='color: black;'>Original file uploaded.</span>")
            self.statusBar().showMessage("Original file uploaded", 5000)
        if message:
            self.status_box.append(message)
            self.statusBar().showMessage(message.split("<span")[0].strip(), 5000)
        print("self.original_data:", self.original_data)

    def browse_randomized_data(self):
        file_names = browse_randomized_data_files()
        if file_names:
            paths = ', '.join([file_name[0] for file_name in file_names])
            self.randomized_data_input.setText(paths)
        self.randomized_data = []
        for _, last_set, last_set_prob in file_names:
            if last_set and last_set_prob:
                self.randomized_data.append({"set": last_set, "set_prob": last_set_prob})
                self.status_box.append("<span style='color: black;'>Randomized file uploaded.</span>")
                self.statusBar().showMessage("Randomized file uploaded", 5000)
        print("self.randomized_data:", self.randomized_data)

    def browse_export_data(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Select Path for Saving Data", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.export_data_input.setText(file_name)
            self.statusBar().showMessage(f"Export path set to: {file_name}", 5000)
    def run_export(self):
        if self.original_data and self.randomized_data:
            save_path = self.export_data_input.text()
            if save_path:
                try:
                    result, df = generate_table(self.original_data, self.randomized_data, save_path)
                    self.status_box.append(result)
                    self.current_df = df
                    self.statusBar().showMessage("Data export completed", 5000)
                    print("DataFrame generated successfully.")
                except Exception as e:
                    self.status_box.append(
                        f"<b><span style='color: red;'>Failed to generate table: {str(e)}</span></b>")
                    self.statusBar().showMessage(f"Error: {str(e)}", 5000)
            else:
                self.status_box.append("<b><span style='color: red;'>Please select the export path first.</span></b>")
                self.statusBar().showMessage("Error: Export path not selected", 5000)
        else:
            self.status_box.append(
                "<b><span style='color: red;'>Load original and randomized data before proceeding.</span></b>")
            self.statusBar().showMessage("Error: Data not loaded", 5000)
    def preview_plot(self):
        save_path = self.export_data_input.text()
        if not save_path:
            self.status_box.append("<b><span style='color: red;'>Export file not specified. Please complete the export process first.</span></b>")
            self.statusBar().showMessage("Error: Export file not specified", 5000)
            return
        try:
            self.statusBar().showMessage(f"Generating plot from {save_path}...", 5000)
            plot_graph_from_csv(save_path)
        except Exception as e:
            self.status_box.append(f"Failed to generate preview: {str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}", 5000)

