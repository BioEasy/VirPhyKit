import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QGroupBox, QLineEdit,
                             QSizePolicy, QRadioButton, QTextEdit,
                             QProgressBar)
from PyQt5.QtCore import Qt, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from SamplePlot.function_SamplePlot import process_plot
import os
import subprocess


class Worker(QThread):
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, parent, command):
        super().__init__(parent)
        self.command = command

    def run(self):
        try:
            result = subprocess.run(
                self.command,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            self.finished.emit('green', f"Plot successfully generated at: {self.parent().save_path}")
            print("R script output:", result.stdout)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            self.error.emit(f"Error generating plot: {error_msg}")
            print("R script error:", error_msg)
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")
            print("Unexpected error:", str(e))


class PlotModule(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("VirusPhylogeographics", "EnvironmentSettings")
        self.input_file = None
        self.save_path = None
        self.r_packages_ready = False
        self.plot_type = "date"
        self.worker = None
        self.initUI()

    def initUI(self):
        # font = QFont("Arial", 10)
        # self.setFont(font)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_label = QLabel("VirSpaceTime (Viral Space-Time Visualizer)")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 10px; background-color: #ffffff; border-radius: 5px; font-size: 16px;")
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
            'Step 1: Ensure Rscript is properly configured (in "Option-Environment").<br>'
            'Step 2: Select visualization mode (spatial distribution, temporal distribution, or both).<br>'
            'Step 3: Upload a tab-delimited text file containing geographic coordinates for spatial analysis and/or population sample sizes over time for temporal analysis.<br>'
            'Step 4: Select the output directory and filename.<br>'
            'Step 5: Click [Generate] to create visualization.'
            '</span>'
        )
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel("VirSpaceTime is a tool for visualizing spatial and/or temporal distribution patterns of viral isolates.\n")
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setStyleSheet("padding: 5px; border: none; color: #808080; font-size: 12px;")
        main_layout.addWidget(description_label, alignment=Qt.AlignCenter)

        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(5)
        settings_layout.setContentsMargins(10, 10, 10, 5)

        plot_type_group = QGroupBox("Visualization mode")
        plot_type_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12px; border: none; }")
        plot_type_layout = QHBoxLayout()
        plot_type_layout.setSpacing(10)

        self.date_radio = QRadioButton("Temporal")
        self.date_radio.setFont(QFont("Arial", 12))
        self.date_radio.setChecked(True)
        self.date_radio.toggled.connect(lambda: self.set_plot_type("date"))
        self.date_radio.setStyleSheet("font-size: 12px;")
        plot_type_layout.addWidget(self.date_radio)

        self.map_radio = QRadioButton("Spatial")
        self.map_radio.setFont(QFont("Arial", 12))
        self.map_radio.toggled.connect(lambda: self.set_plot_type("map"))
        self.map_radio.setStyleSheet("font-size: 12px;")
        plot_type_layout.addWidget(self.map_radio)
        plot_type_layout.addStretch()
        plot_type_group.setLayout(plot_type_layout)
        settings_layout.addWidget(plot_type_group)

        input_label = QLabel("Input File (.txt):")
        input_label.setFont(QFont("Arial", 12))
        input_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(input_label)

        input_widget = QWidget()
        input_hbox = QHBoxLayout()
        input_hbox.setSpacing(5)
        input_hbox.setContentsMargins(0, 0, 0, 0)

        self.input_file_display = QLineEdit()
        self.input_file_display.setReadOnly(True)
        self.input_file_display.setFont(QFont("Arial", 12))
        self.input_file_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.input_file_display.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        input_hbox.addWidget(self.input_file_display)

        input_button = QPushButton("...")
        input_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008b
            }
        """)
        input_button.clicked.connect(self.upload_file)
        input_hbox.addWidget(input_button)
        input_widget.setLayout(input_hbox)
        settings_layout.addWidget(input_widget)

        output_label = QLabel("Output Directory:")
        output_label.setFont(QFont("Arial", 12))
        output_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(output_label)

        output_widget = QWidget()
        output_hbox = QHBoxLayout()
        output_hbox.setSpacing(5)
        output_hbox.setContentsMargins(0, 0, 0, 0)

        self.output_path_display = QLineEdit()
        self.output_path_display.setReadOnly(True)
        self.output_path_display.setFont(QFont("Arial", 12))
        self.output_path_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.output_path_display.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        output_hbox.addWidget(self.output_path_display)

        output_button = QPushButton("...")
        output_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008b
            }
        """)
        output_button.clicked.connect(self.select_save_location)
        output_hbox.addWidget(output_button)
        output_widget.setLayout(output_hbox)
        settings_layout.addWidget(output_widget)

        filename_label = QLabel("Output Filename:")
        filename_label.setFont(QFont("Arial", 12))
        filename_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(filename_label)

        self.filename_input = QLineEdit("output_plot")
        self.filename_input.setFont(QFont("Arial", 12))
        self.filename_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        settings_layout.addWidget(self.filename_input)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        info_group = QGroupBox("Status")
        info_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        info_layout.setContentsMargins(10, 5, 10, 5)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFont(QFont("Arial", 12))
        self.info_text.setText("Checking R environment...")
        self.info_text.setStyleSheet("font-size: 12px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;")
        self.info_text.setMinimumHeight(100)
        info_layout.addWidget(self.info_text)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        info_layout.addWidget(self.progress_bar)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group, stretch=1)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.generate_button = QPushButton("Generate")
        self.generate_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008b
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.generate_button.setFont(QFont("Arial", 12))
        self.generate_button.clicked.connect(self.run_r_script)
        button_layout.addWidget(self.generate_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.setStyleSheet("""
            QWidget { 
                background-color: #ffffff; 
            }
            QLineEdit { 
                border: 1px solid #ddd; 
                padding: 3px; 
                border-radius: 5px; 
                font-size: 12px; 
            }
            QGroupBox { 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                margin-top: 10px; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 0 3px; 
            }
            QTextEdit { 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                background-color: #f9f9f9; 
                font-size: 12px; 
            }
            QProgressBar { 
                border: 1px solid #ddd; 
                background-color: #f9f9f9; 
                height: 10px; 
                border-radius: 5px; 
            }
            QRadioButton { 
                font-size: 12px; 
            }
        """)

        self.check_r_environment()

    def check_r_executable(self, path):
        return os.path.isfile(path) and os.access(path, os.X_OK)

    def check_r_environment(self):
        r_path = self.settings.value("r_path", "")
        if not r_path or not self.check_r_executable(r_path):
            self.info_text.setText(
                "<b><span style='color:red'>Error: Rscript not configured or invalid. Please set it in Environment Settings.</span></b>")
            self.r_packages_ready = False
            return

        required_packages = ["ggplot2", "tidyr", "ggsci", "scales", "patchwork", "maps", "rnaturalearth", "sf"]
        try:
            result = subprocess.run(
                [r_path, "-e", "cat(rownames(installed.packages()))"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                self.info_text.setText(f"<b><span style='color:red'>Failed to check R packages: {error_msg}</span></b>")
                self.r_packages_ready = False
                return
            installed = result.stdout.strip().split()
            missing = [pkg for pkg in required_packages if pkg not in installed]
            if missing:
                self.info_text.setText(
                    f"<b><span style='color:red'>Missing R packages: {', '.join(missing)}</span></b>")
                self.r_packages_ready = False
            else:
                self.info_text.setText("<b><span style='color:green'>R environment ready</span></b>")
                self.r_packages_ready = True
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.info_text.setText(f"<b><span style='color:red'>Error checking R packages: {e}</span></b>")
            self.r_packages_ready = False

    def set_plot_type(self, plot_type):
        self.plot_type = plot_type

    def upload_file(self):
        process_plot.upload_file(self)

    def select_save_location(self):
        process_plot.select_save_location(self)

    def run_r_script(self):
        if not hasattr(self, 'input_file') or not self.input_file:
            self.info_text.setText("Please select an input file")
            return
        if not hasattr(self, 'save_path') or not self.save_path:
            self.info_text.setText("Please select a save location")
            return

        process_plot.check_r_path(self)
        if not self.r_packages_ready:
            return

        rscript_path = self.settings.value("r_path", "")
        if not rscript_path or not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
            self.info_text.setText(
                "<b><span style='color:red'>Error: Rscript not configured or invalid. Please set it in Environment Settings.</span></b>")
            return
        try:
            df = pd.read_csv(self.input_file, sep='\t')
            if self.plot_type == "date":
                required_cols = ['Year', 'Total']
                if not all(col in df.columns for col in required_cols) or len(
                    [col for col in df.columns if col not in required_cols]) < 1:
                    self.info_text.setText(
                        "<b><span style='color:red'>Error: Input file must contain Year, Total columns, and at least one country column</span></b>")
                    return
            else:
                required_cols = ['region', 'Longitude', 'Latitude']
                if not all(col in df.columns for col in required_cols):
                    self.info_text.setText(
                        "<b><span style='color:red'>Error: Input file must contain region, Longitude, and Latitude columns</span></b>")
                    return
        except Exception as e:
            self.info_text.setText(f"<b><span style='color:red'>Error reading input file: {e}</span></b>")
            return

        input_file_r = os.path.abspath(self.input_file).replace("\\", "/")
        output_file = os.path.abspath(os.path.join(self.save_path, f"{self.filename_input.text()}.pdf")).replace(
            "\\", "/")
        script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        r_script_name = "generate_plot.R" if self.plot_type == "date" else "generate_map.R"
        r_script_path = os.path.join(script_dir, r_script_name)
        if not os.path.isfile(r_script_path):
            self.info_text.setText(
                f"<b><span style='color:red'>Error: R script not found at {r_script_path}</span></b>")
            return

        print(f"R script path: {r_script_path}")

        if self.plot_type == "date":
            country_cols = [col for col in df.columns if col not in ['Year', 'Total']]
            if not country_cols:
                self.info_text.setText("<b><span style='color:red'>Error: No data found in input file</span></b>")
                return
            first_country = country_cols[0]
            last_country = country_cols[-1]
            command = [rscript_path, r_script_path, input_file_r, output_file, first_country, last_country]
        else:
            command = [rscript_path, r_script_path, input_file_r, output_file]

        print("Executing command:", " ".join(command))

        self.generate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.info_text.setText("Generating plot...")

        self.worker = Worker(self, command)
        self.worker.finished.connect(self.on_script_finished)
        self.worker.error.connect(self.on_script_error)
        self.worker.start()

    def on_script_finished(self, color, message):
        self.info_text.setText(f"<b><span style='color:{color}'>{message}</span></b>")
        self.generate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.worker = None

    def on_script_error(self, error_msg):
        self.info_text.setText(f"<b><span style='color:red'>{error_msg}</span></b>")
        self.generate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.worker = None