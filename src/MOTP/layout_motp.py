import os
import pandas as pd
import tempfile
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QLineEdit, QPushButton, QTextEdit, QLabel,
                             QFileDialog, QMessageBox, QSizePolicy, QProgressBar, QTableWidget, QTableWidgetItem,
                             QCheckBox, QButtonGroup)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont
from MOTP.function_motp import check_r_path, WorkerThread

class MigrationOverTimePlotter(QMainWindow):
    def __init__(self, matrix_file=None):
        super().__init__()
        self.setWindowTitle("TempMig Plotter")
        self.setGeometry(100, 100, 800, 700)
        self.settings = QSettings("VirusPhylogeographics", "EnvironmentSettings")
        self.r_path = self.settings.value("r_install_dir", "/usr/local/bin" if os.name != "nt" else "C:\\Program Files\\R\\R-4.3.0")
        self.init_ui(matrix_file)

    def init_ui(self, matrix_file=None):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_label = QLabel("TempMig Plotter")
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
            'Step 1: Ensure R and required packages (tidyr, ggplot2) are installed.<br>'
            'Step 2: Upload a migration matrix file (output from "TempMig").<br>'
            'Step 3: Select the migration directions for visualization.<br>'
            'Step 4: Specify an output directory.<br>'
            'Step 5: Select a visualization style (Normal or Smooth).<br>'
            'Step 6: Click [Run] to generate temporal migration patterns.'                                                                                                      
            '</span>'
            )
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)
        data_group = QGroupBox("Settings")
        data_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        data_layout = QVBoxLayout()
        data_layout.setSpacing(5)
        data_layout.setContentsMargins(10, 5, 10, 5)
        # Matrix Input
        matrix_label = QLabel("Input migration matrix file:")
        matrix_label.setStyleSheet("font-size: 12px;")
        data_layout.addWidget(matrix_label)
        matrix_widget = QWidget()
        matrix_layout = QHBoxLayout()
        matrix_layout.setSpacing(5)
        matrix_layout.setContentsMargins(0, 0, 0, 0)
        self.matrix_input = QLineEdit(matrix_file if matrix_file else "Not selected")
        self.matrix_input.setReadOnly(True)
        self.matrix_input.setToolTip(self.matrix_input.text())
        self.matrix_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.matrix_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        matrix_layout.addWidget(self.matrix_input)
        matrix_browse = QPushButton("...")
        matrix_browse.setStyleSheet("""
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
        matrix_layout.addWidget(matrix_browse)
        matrix_widget.setLayout(matrix_layout)
        data_layout.addWidget(matrix_widget)
        self.migration_table = QTableWidget()
        self.migration_table.setColumnCount(5)
        self.migration_table.setHorizontalHeaderLabels(["Selected", "From", "To", "Within", ""])
        self.migration_table.setFont(QFont("Arial", 9))
        self.migration_table.horizontalHeader().setFont(QFont("Arial", 9))
        self.migration_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.migration_table.horizontalHeader().setStretchLastSection(True)
        self.migration_table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                font-size: 12px;
            }
        """)
        data_layout.addWidget(self.migration_table)
        output_label = QLabel("Output Directory:")
        output_label.setStyleSheet("font-size: 12px;")
        data_layout.addWidget(output_label)
        output_widget = QWidget()
        output_layout = QHBoxLayout()
        output_layout.setSpacing(5)
        output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_input = QLineEdit()
        self.output_input.setReadOnly(True)
        self.output_input.setToolTip(self.output_input.text())
        self.output_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.output_input.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")
        output_layout.addWidget(self.output_input)
        output_browse = QPushButton("...")
        output_browse.setStyleSheet("""
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
        output_layout.addWidget(output_browse)
        output_widget.setLayout(output_layout)
        data_layout.addWidget(output_widget)
        style_label = QLabel("Line styles:")
        style_label.setStyleSheet("font-size: 12px;")
        data_layout.addWidget(style_label)
        style_widget = QWidget()
        style_layout = QHBoxLayout()
        style_layout.setSpacing(10)
        style_layout.setContentsMargins(0, 0, 0, 0)
        self.normal_checkbox = QCheckBox("Normal")
        self.normal_checkbox.setStyleSheet("font-size: 12px;")
        self.normal_checkbox.setChecked(True)
        self.smooth_checkbox = QCheckBox("Smooth")
        self.smooth_checkbox.setStyleSheet("font-size: 12px;")
        self.style_group = QButtonGroup(self)
        self.style_group.addButton(self.normal_checkbox)
        self.style_group.addButton(self.smooth_checkbox)
        style_layout.addWidget(self.normal_checkbox)
        style_layout.addWidget(self.smooth_checkbox)
        style_layout.addStretch()
        style_widget.setLayout(style_layout)
        data_layout.addWidget(style_widget)
        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)
        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        status_layout.setContentsMargins(10, 5, 10, 5)
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("font-size: 12px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;")
        status_layout.addWidget(self.status_text)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=1)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.plot_btn = QPushButton("Plot")
        self.plot_btn.setStyleSheet("""
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
        button_layout.addWidget(self.plot_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        self.setStyleSheet("""
            QMainWindow { background-color: #ffffff; }
            QLineEdit { border: 1px solid #ddd; padding: 3px; border-radius: 5px; font-size: 12px; }
            QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
            QTableWidget { border: 1px solid #ddd; border-radius: 5px; }
            QProgressBar {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                height: 10px;
                border-radius: 5px;
            }
        """)
        self.label_mapping = {}
        matrix_browse.clicked.connect(self.browse_matrix)
        output_browse.clicked.connect(self.browse_output)
        self.plot_btn.clicked.connect(self.run_plot)
        self.check_r_path(self.r_path)
        if matrix_file and os.path.exists(matrix_file):
            self.show_migration_directions(matrix_file)

    def check_r_path(self, path):
        if not os.path.isdir(path):
            self.status_text.append(f"<b><span style='color: red;'>R: Directory {path} does not exist</span></b>")
            return
        rscript_path = os.path.join(path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
        if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
            self.status_text.append(f"<b><span style='color: red;'>R: Rscript executable not found at {path}</span></b>")
            return
        status, missing_packages = check_r_path(path)
        if status == "install":
            self.status_text.append(f"<b><span style='color: green;'>R: Installed, including required packages (tidyr, ggplot2)</span></b>")
        else:
            self.status_text.append(f"<b><span style='color: red;'>R: Missing: {', '.join(missing_packages)}</span></b>")

    def browse_matrix(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select migration matrix file", "", "(*.txt)")
        if path:
            self.matrix_input.setText(path)
            self.show_migration_directions(path)

    def browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save plot file", "", "(*.pdf)")
        if path:
            self.output_input.setText(path)

    def show_migration_directions(self, file_path):
        try:
            df = pd.read_csv(file_path, sep="\t")
            columns = df.columns[1:]
            self.migration_table.setRowCount(len(columns))
            self.label_mapping = {}
            for row, col in enumerate(columns):
                if "_to_" in col:
                    from_loc, to_loc = col.split("_to_")
                    checkbox = QTableWidgetItem()
                    checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    checkbox.setCheckState(Qt.Unchecked)
                    self.migration_table.setItem(row, 0, checkbox)
                    self.migration_table.setItem(row, 1, QTableWidgetItem(from_loc))
                    self.migration_table.setItem(row, 2, QTableWidgetItem(to_loc))
                    within_label = "Within_" + from_loc if from_loc == to_loc else ""
                    self.migration_table.setItem(row, 3, QTableWidgetItem(within_label))
                    if from_loc == to_loc:
                        self.label_mapping[col] = f"Within_{from_loc}"
                    else:
                        self.label_mapping[col] = col
                    total_events = df[col].sum()
                    event_item = QTableWidgetItem("No migration events" if total_events == 0 else "")
                    self.migration_table.setItem(row, 4, event_item)
                else:
                    self.status_text.append(f"<b><span style='color: red;'>Unrecognized format: {col}</span></b>")
            self.migration_table.resizeColumnsToContents()
        except Exception as e:
            self.status_text.clear()
            self.status_text.append(f"<b><span style='color: red;'>Error: {e}</span></b>")

    def run_plot(self):
        path = self.r_path
        if not os.path.isdir(path):
            QMessageBox.warning(self, "Error", f"R directory {path} does not exist")
            self.status_text.append(f"<b><span style='color: red;'>Error: R directory {path} does not exist</span></b>")
            return
        rscript_path = os.path.join(path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
        if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
            QMessageBox.warning(self, "Error", f"Rscript executable not found at {path}")
            self.status_text.append(f"<b><span style='color: red;'>Error: Rscript executable not found at {path}</span></b>")
            return
        status, missing_packages = check_r_path(path)
        if status != "install":
            message = "Please ensure R is installed and includes the following packages:\n- " + "\n- ".join(missing_packages)
            QMessageBox.warning(self, "Error", message)
            self.status_text.append(f"<b><span style='color: red;'>Error: Missing R packages: {', '.join(missing_packages)}</span></b>")
            return
        if self.matrix_input.text() == "Not selected":
            QMessageBox.warning(self, "Error", "Please select a migration matrix file")
            self.status_text.append(f"<b><span style='color: red;'>Error: Please select a migration matrix file</span></b>")
            return
        if not self.output_input.text():
            QMessageBox.warning(self, "Error", "Please specify an output plot path")
            self.status_text.append(f"<b><span style='color: red;'>Error: Please specify an output plot path</span></b>")
            return
        selected_directions = []
        for row in range(self.migration_table.rowCount()):
            checkbox = self.migration_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.Checked:
                from_loc = self.migration_table.item(row, 1).text()
                to_loc = self.migration_table.item(row, 2).text()
                original_label = f"{from_loc}_to_{to_loc}"
                selected_directions.append(self.label_mapping.get(original_label, original_label))
        if not selected_directions:
            QMessageBox.warning(self, "Error", "Please select at least one migration direction")
            self.status_text.append(f"<b><span style='color: red;'>Error: Please select at least one migration direction</span></b>")
            return
        try:
            df = pd.read_csv(self.matrix_input.text(), sep="\t")
            renamed_df = df.rename(columns=self.label_mapping)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                renamed_df.to_csv(temp_file.name, sep="\t", index=False)
                temp_matrix_file = temp_file.name
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process the input file: {e}")
            self.status_text.append(f"<b><span style='color: red;'>Error: Failed to process the input file: {e}</span></b>")
            return
        style = "Normal" if self.normal_checkbox.isChecked() else "Smooth"
        script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        r_script = os.path.join(script_dir,
                                "plot_migration_over_time.R" if style == "Normal" else "plot_migration_over_time_smooth.R")
        self.plot_btn.setEnabled(False)
        self.status_text.clear()
        self.progress_bar.setVisible(True)
        self.status_text.append("<b><span style='color: blue;'>Generating plot...</span></b>")
        matrix_file = temp_matrix_file
        r_path = rscript_path
        output_path = self.output_input.text()
        self.worker = WorkerThread(matrix_file, r_path, output_path, selected_directions, r_script)
        self.worker.update_status.connect(self.status_text.append)
        self.worker.finished.connect(lambda success: self.on_finished(success, temp_matrix_file))
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self, success, temp_file):
        self.progress_bar.setVisible(False)
        self.plot_btn.setEnabled(True)
        try:
            os.unlink(temp_file)
        except Exception:
            pass
        if success:
            QMessageBox.information(self, "Success", "The plot has been generated")
            self.status_text.append("<b><span style='color: green;'>The plot has been generated</span></b>")
        else:
            QMessageBox.warning(self, "Error", "Plot generation failed. Check the status log for details")
            self.status_text.append("<b><span style='color: red;'>Plot generation failed. Check the status log for details</span></b>")
        self.worker = None

    def on_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.plot_btn.setEnabled(True)
        QMessageBox.warning(self, "Error", f"Error: {error_msg}")
        self.status_text.append(f"<b><span style='color: red;'>Error: {error_msg}</span></b>")
        self.worker = None