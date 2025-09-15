import os
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, \
    QPushButton, QGroupBox, QLineEdit, QStatusBar, QTextEdit, QFileDialog, QComboBox, QCheckBox, QApplication, QMessageBox
from BSP.function_bsp import ColorPreviewDialog, get_current_colors, switch_color_scheme, check_r_installation, \
    generate_single_plot

class BayesianSkylinePlotAPP(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("VirusPhylogeographics", "EnvironmentSettings")
        self.r_path = ""
        self.batch_mode = False
        self.batch_files = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("BSP-Viz (Bayesian Skyline Plot Visualizer)")
        self.setGeometry(100, 100, 800, 700)

        font = QFont("Arial", 10)
        QApplication.setFont(font)

        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_label = QLabel("BSP-Viz (Bayesian Skyline Plot Visualizer)")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 10px; background-color: #ffffff; border-radius: 5px")
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
        help_button.setToolTip("\n"
                               "\n"
                               "\n"
                               "")
        help_button.setToolTip(
            '<span style="font-family: Arial; font-size: 12px;">'
            'Step 1: After ensuring that the R environment is configured correctly, select the table file (you can click the [Batch] button to draw in batches later).<br>'
            'Step 2: Select the time axis direction and whether to add a secondary axis.<br>'
            'Step 3: Specify the output directory and click [Hue Harmony] to adjust color schemes.<br>'
            'Step 4: Click [Plot] to generate.'
            '</span>'
        )
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel("BSP-Viz is a specifized tool for visualizing Bayesian Skyline Plots (BSP), supporting both single-file or batch processing modes. ")
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setStyleSheet("padding: 5px; border: none; color: #808080; font-size: 12px;")
        main_layout.addWidget(description_label, alignment=Qt.AlignCenter)


        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(10)
        settings_layout.setContentsMargins(10, 10, 10, 10)

        tsv_label = QLabel(".tsv File(s):")
        tsv_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(tsv_label)
        tsv_widget = QWidget()
        tsv_hbox = QHBoxLayout()
        tsv_hbox.setSpacing(5)
        self.tsv_dir_input = QLineEdit()
        self.tsv_dir_input.setToolTip("Enter or select the path to the .tsv file(s)")
        self.tsv_dir_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.tsv_dir_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        tsv_hbox.addWidget(self.tsv_dir_input)

        self.browseBtn1 = QPushButton("...")
        self.browseBtn1.setStyleSheet("""
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
        self.browseBtn1.clicked.connect(self.browse_tsv)
        tsv_hbox.addWidget(self.browseBtn1)

        self.batchBtn = QPushButton("Batch")
        self.batchBtn.setStyleSheet("""
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
        self.batchBtn.clicked.connect(self.browse_batch_tsv)
        tsv_hbox.addWidget(self.batchBtn)

        tsv_widget.setLayout(tsv_hbox)
        settings_layout.addWidget(tsv_widget)

        axis_options_widget = QWidget()
        axis_options_hbox = QHBoxLayout()
        axis_options_hbox.setSpacing(20)

        direction_label = QLabel("Time Axis Direction:")
        direction_label.setStyleSheet("font-size: 12px;")
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Forward", "Reverse"])
        self.direction_combo.setToolTip("Select whether the time axis should be forward or reverse")
        self.direction_combo.setStyleSheet("font-size: 12px;")
        axis_options_hbox.addWidget(direction_label)
        axis_options_hbox.addWidget(self.direction_combo)

        self.secondary_check = QCheckBox("Include Secondary X-Axis")
        self.secondary_check.setToolTip("Check to include secondary x-axis ticks")
        self.secondary_check.setStyleSheet("font-size: 12px;")
        axis_options_hbox.addWidget(self.secondary_check)
        axis_options_hbox.addStretch()

        axis_options_widget.setLayout(axis_options_hbox)
        settings_layout.addWidget(axis_options_widget)

        output_label = QLabel("Output Directory:")
        output_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(output_label)
        output_widget = QWidget()
        output_hbox = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setToolTip("Enter or select the output directory (batch mode) or PDF file (single mode)")
        self.output_dir_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.output_dir_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        output_hbox.addWidget(self.output_dir_input)
        self.browseBtn2 = QPushButton("...")
        self.browseBtn2.setStyleSheet("""
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
        self.browseBtn2.clicked.connect(self.browse_output)
        output_hbox.addWidget(self.browseBtn2)
        output_widget.setLayout(output_hbox)
        settings_layout.addWidget(output_widget)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QVBoxLayout()
        self.statusText = QTextEdit()
        self.statusText.setReadOnly(True)
        self.statusText.setStyleSheet("""
            background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 3px; padding: 5px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            font-size: 12px;
        """)
        self.statusText.setFixedHeight(100)
        status_layout.addWidget(self.statusText)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=0)

        button_widget = QWidget()
        button_hbox = QHBoxLayout()
        button_hbox.setSpacing(10)
        button_hbox.setAlignment(Qt.AlignCenter)

        self.hue_harmony_button = QPushButton("Hue Harmony")
        self.hue_harmony_button.setStyleSheet("""
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
        self.hue_harmony_button.clicked.connect(self.hue_harmony_action)
        button_hbox.addWidget(self.hue_harmony_button)

        self.plot_button = QPushButton("Plot")
        self.plot_button.setStyleSheet("""
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
        self.plot_button.clicked.connect(self.generate_plot)
        button_hbox.addWidget(self.plot_button)

        button_widget.setLayout(button_hbox)
        main_layout.addWidget(button_widget)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready", 5000)
        status_bar.setStyleSheet("background-color: #f0f0f0; padding: 3px; border-top: 1px solid #ddd; font-size: 12px;")

        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            QLineEdit { border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px; }
            QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
        """)

        r_path_saved = self.settings.value("r_install_dir", "Please specify the R installation directory")
        self.r_path = r_path_saved
        if r_path_saved != "Please specify the R installation directory":
            self.check_r_path(r_path_saved)

    def check_r_path(self, path):
        if not os.path.isdir(path):
            self.statusText.append(f"R: Directory {path} does not exist")
            return
        rscript_path = os.path.join(path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
        if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
            self.statusText.append(f"R: Rscript executable not found in {path}")
            return
        status, missing_packages = check_r_installation(path)
        if status:
            self.statusText.append(f"<b><span style='color:green;'>R: Installed with required packages (tidyr, ggplot2)</span></b>")
        else:
            self.statusText.append(f"<b><span style='color:red;'>R: Missing packages: {', '.join(missing_packages)}</span></b>")

    def browse_r_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select R Installation Directory")
        if directory:
            self.r_path = directory
            self.check_r_path(directory)

    def hue_harmony_action(self):
        new_colors = switch_color_scheme(num_colors=5)
        self.statusText.append(f"New color scheme generated: {new_colors}")
        self.statusBar().showMessage("Hue Harmony applied! Preview shown.", 5000)

        preview_dialog = ColorPreviewDialog(new_colors, self)
        preview_dialog.exec_()

    def browse_tsv(self):
        self.batch_mode = False
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "tsv Files (*.tsv *.csv)")
        if file_path:
            self.tsv_dir_input.setText(file_path)
            self.statusText.append(f"Selected tsv file: {file_path}")

    def browse_batch_tsv(self):
        self.batch_mode = True
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "tsv Files (*.tsv *.csv)")
        if files:
            self.batch_files = files
            self.tsv_dir_input.setText(f"{len(files)} files selected")
            self.statusText.append(f"Selected {len(files)} tsv files for batch processing")

    def browse_output(self):
        if self.batch_mode:
            directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if directory:
                self.output_dir_input.setText(directory)
                self.statusText.append(f"Selected output directory: {directory}")
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF Files (*.pdf)")
            if file_path:
                self.output_dir_input.setText(file_path)
                self.statusText.append(f"Selected output path: {file_path}")

    def generate_plot(self):
        output_path = self.output_dir_input.text()
        direction = self.direction_combo.currentText()
        secondary_axis = self.secondary_check.isChecked()

        if not self.r_path or not os.path.isdir(self.r_path):
            QMessageBox.warning(self, "Error", "R installation directory not specified or invalid")
            self.statusText.append("Error: R installation directory not specified or invalid")
            return

        rscript_path = os.path.join(self.r_path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
        if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
            QMessageBox.warning(self, "Error", "Rscript executable not found")
            self.statusText.append(f"Error: Rscript executable not found in {self.r_path}")
            return

        status, missing_packages = check_r_installation(self.r_path)
        if not status:
            QMessageBox.warning(self, "Error", "Missing required R packages")
            self.statusText.append(f"Error: Missing R packages: {', '.join(missing_packages)}")
            return

        if self.batch_mode:
            if not self.batch_files:
                self.statusText.append("Error: Please select .tsv files for batch processing")
                return
            if not output_path or not os.path.isdir(output_path):
                self.statusText.append("Error: Please specify a valid output directory for batch processing")
                return

            colors = get_current_colors(num_colors=len(self.batch_files))

            for idx, tsv_file in enumerate(self.batch_files):
                if not os.path.exists(tsv_file):
                    self.statusText.append(f"Error: File not found: {tsv_file}")
                    continue

                tsv_filename = os.path.basename(tsv_file)
                pdf_filename = os.path.splitext(tsv_filename)[0] + ".pdf"
                output_file = os.path.join(output_path, pdf_filename).replace("\\", "/")
                tsv_file = tsv_file.replace("\\", "/")
                plot_color = colors[idx % len(colors)] if colors else "light blue"
                result = generate_single_plot(tsv_file, output_file, direction, secondary_axis, plot_color, self.r_path)
                if isinstance(result, str):
                    self.statusText.append(f"Error processing {tsv_file}: {result}")
                elif result.returncode == 0:
                    self.statusText.append(f"<b><span style='color:green'>Plot successfully generated at: {output_file}</span><b>")
                else:
                    self.statusText.append(f"Error in R script execution for {tsv_file}:\n{result.stderr}")

        else:
            tsv_file = self.tsv_dir_input.text()
            if not tsv_file or not os.path.exists(tsv_file):
                self.statusText.append("Error: Please select a valid .tsv file")
                return
            if not output_path:
                self.statusText.append("Error: Please specify an output PDF file")
                return

            tsv_file = tsv_file.replace("\\", "/")
            output_file = output_path.replace("\\", "/")
            result = generate_single_plot(tsv_file, output_file, direction, secondary_axis, "light blue", self.r_path)
            if isinstance(result, str):
                self.statusText.append(f"Error processing {tsv_file}: {result}")
            elif result.returncode == 0:
                self.statusText.append(f"<b><span style='color:green'>Plot successfully generated at: {output_file}</span><b>")
            else:
                self.statusText.append(f"Error in R script execution for {tsv_file}:\n{result.stderr}")