import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QLineEdit, QPushButton, QTextEdit, QLabel,
                             QFileDialog, QMessageBox, QSizePolicy, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QFont
from MOT.function_mot import run_steps, check_python_path, check_perl_path, check_r_path


class WorkerThread(QThread):
    update_status = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, mcc_file, perl_path, r_path, output_path, python_path=None):
        super().__init__()
        self.mcc_file = mcc_file
        self.perl_path = perl_path
        self.r_path = r_path
        self.output_path = output_path
        self.python_path = python_path

    def run(self):
        print("Worker thread started")

        def status_callback(message):
            self.update_status.emit(message)

        try:
            success = run_steps(self.mcc_file, self.perl_path, self.r_path, status_callback,
                                self.output_path, python_path=self.python_path)
            print(f"Run steps completed with success: {success}")
            self.finished.emit(success)
        except Exception as e:
            self.update_status.emit(f"Unexpected error in worker thread: {str(e)}")
            self.error.emit(str(e))


class EnvironmentCheckThread(QThread):
    status_message = pyqtSignal(str)
    environment_ready = pyqtSignal(bool)

    def __init__(self, python_path, perl_path, r_path):
        super().__init__()
        self.python_path = python_path
        self.perl_path = perl_path
        self.r_path = r_path

    def run(self):
        env_issues = []

        # Check Python
        if not self.python_path or not os.path.isfile(self.python_path):
            env_issues.append("Python path not configured")
            self.status_message.emit(
                "<b><span style='color: red;'>Error: Python path not configured. Please check 'Option-Environment' settings.</span></b>")
        elif check_python_path(self.python_path) != "install":
            env_issues.append("Python environment missing ete3 or pandas")
            self.status_message.emit(
                "<b><span style='color: red;'>Error: Python environment missing ete3 or pandas. Please install required libraries.</span></b>")

        # Check Perl
        if not self.perl_path or not os.path.isfile(self.perl_path):
            env_issues.append("Perl path not configured")
            self.status_message.emit(
                "<b><span style='color: red;'>Error: Perl path not configured. Please check the settings in 'Option-Environment'.</span></b>")
        elif check_perl_path(self.perl_path) != "install":
            env_issues.append("Invalid Perl executable")
            self.status_message.emit(
                "<b><span style='color: red;'>Error: Invalid Perl executable. Please check Environment settings.</span></b>")

        # Check R
        if not self.r_path or not os.path.isdir(self.r_path):
            env_issues.append("R installation directory not configured")
            self.status_message.emit(
                "<b><span style='color: red;'>Error: R installation directory not configured. Please check the 'Option-Environment' settings.</span></b>")
        else:
            status, missing_packages = check_r_path(self.r_path)
            if status != "install":
                if not os.path.isfile(
                        os.path.join(self.r_path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))):
                    env_issues.append("Rscript executable not found")
                    self.status_message.emit(
                        f"<b><span style='color: red;'>Error: Rscript executable not found. Please configure in 'Option-Environment'</span></b>")
                else:
                    env_issues.append(f"Missing R packages: {', '.join(missing_packages)}")
                    self.status_message.emit(
                        f"<b><span style='color: red;'>Error: Missing R packages: {', '.join(missing_packages)}.</span></b>")

        # Report environment status
        if not env_issues:
            self.status_message.emit(
                "<b><span style='color: green;'>Environment check completed: All dependencies are properly configured.</span></b>")
            self.environment_ready.emit(True)
        else:
            self.status_message.emit(
                f"<b><span style='color: red;'>Environment check completed: {len(env_issues)} issue(s) found.</span></b>")
            self.environment_ready.emit(False)


class MigrationPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("VirusPhylogeographics", "EnvironmentSettings")
        self.setWindowTitle("Migration Plotter")
        self.setGeometry(100, 100, 800, 700)

        # font = QFont("Arial", 10)
        # QApplication.setFont(font)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Title with Help Button
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_label = QLabel("TempMig (Temporal Migration Tracker)")
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
            'Step 1: Ensure Python, Perl, and R installation directories are configured in the "Option-Environment" menu.<br>'
            'Step 2: Upload an MCC tree annotated with traits or a MultiTypeTree.<br>'
            'Step 3: Specify the output directory of the migration matrix.<br>'
            'Step 4: Click [Run] to process the MCC tree/MultiTypeTree and generate migration matrix.<br>'
            'Step 5: Click [Go to plot] to move to the "TempMig Plotter" tool and visualize the results using the migration matrix.'
            '</span>'
            )
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        # Add description label below title
        description_label = QLabel()
        description_label.setText("""
        <p style="line-height: 120%; margin: 0; padding: 0;">
        &nbsp;&nbsp;&nbsp;&nbsp;TempMig is a specialized tool for reconstructing and visualizing temporal migration patterns of viral pathogens.
        The utility processes the MCC tree annotated with traits or MultiTypeTree to generate time-resolved migration matrices and interactive visualizations.
        </p>
        """)
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignLeft)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("padding: 5px; border: none; color: #808080; font-size: 12px;")
        main_layout.addWidget(description_label)

        # Data Group
        data_group = QGroupBox("Settings")
        data_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        data_layout = QVBoxLayout()
        data_layout.setSpacing(5)
        data_layout.setContentsMargins(10, 5, 10, 5)

        # MCC Input
        mcc_label = QLabel("Input MCC Tree with trait:")
        mcc_label.setStyleSheet("font-size :12px;")
        data_layout.addWidget(mcc_label)
        mcc_widget = QWidget()
        mcc_layout = QHBoxLayout()
        mcc_layout.setSpacing(5)
        mcc_layout.setContentsMargins(0, 0, 0, 0)
        self.mcc_input = QLineEdit("not selected")
        self.mcc_input.setStyleSheet("font-size: 12px;")
        self.mcc_input.setReadOnly(True)
        self.mcc_input.setToolTip(self.mcc_input.text())
        self.mcc_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        mcc_layout.addWidget(self.mcc_input)
        self.mcc_browse_btn = QPushButton("...")
        self.mcc_browse_btn.setFixedWidth(40)
        self.mcc_browse_btn.setStyleSheet("""
            QPushButton {
                padding: 5px;
                background-color: #1E90FF;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        mcc_layout.addWidget(self.mcc_browse_btn)
        mcc_widget.setLayout(mcc_layout)
        data_layout.addWidget(mcc_widget)

        # Output Directory
        plot_label = QLabel("Output Directory:")
        plot_label.setStyleSheet("font-size :12px;")
        data_layout.addWidget(plot_label)
        plot_widget = QWidget()
        plot_layout = QHBoxLayout()
        plot_layout.setSpacing(5)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_input = QLineEdit()
        self.plot_input.setStyleSheet("font-size: 12px;")
        self.plot_input.setReadOnly(True)
        self.plot_input.setStyleSheet("font-size: 12px;")
        self.plot_input.setToolTip(self.plot_input.text())
        self.plot_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        plot_layout.addWidget(self.plot_input)
        plot_browse_btn = QPushButton("...")
        plot_browse_btn.setFixedWidth(40)
        plot_browse_btn.setStyleSheet("""
            QPushButton {
                padding: 5px;
                background-color: #1E90FF;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00008b;
            }
        """)
        plot_layout.addWidget(plot_browse_btn)
        plot_widget.setLayout(plot_layout)
        data_layout.addWidget(plot_widget)

        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

        # Status Group
        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        status_layout.setContentsMargins(10, 5, 10, 5)
        self.status_text = QTextEdit()
        self.status_text.setStyleSheet("font-size: 12px;")
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)  # Hidden by default
        status_layout.addWidget(self.progress_bar)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=1)

        # Run Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.run_btn = QPushButton("Run")
        self.run_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #1E90FF;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px
            }
            QPushButton:hover {
                background-color: #00008b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.run_btn)

        self.plot_btn = QPushButton("Go to Plot")
        self.plot_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px
            }
            QPushButton:hover {
                background-color: #00008b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.plot_btn.setEnabled(True)  # Enable Plot button by default
        button_layout.addWidget(self.plot_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        # Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QLineEdit {
                border: 1px solid #ddd;
                padding: 5px;
                border-radius: 5px;
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
            QProgressBar {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                height: 10px;
            }
        """)
        self.last_matrix_file = None

        # Connect signals
        self.mcc_browse_btn.clicked.connect(self.browse_mcc)
        plot_browse_btn.clicked.connect(self.browse_plot)
        self.run_btn.clicked.connect(self.run_steps)
        self.plot_btn.clicked.connect(self.show_plotter)

        # Start environment check in a separate thread
        self.check_environment()

    def check_environment(self):
        """Start environment checks in a separate thread"""
        python_path = self.settings.value("python_path", "")
        perl_path = self.settings.value("perl_path", "")
        r_path = self.settings.value("r_install_dir", "")

        self.env_check_thread = EnvironmentCheckThread(python_path, perl_path, r_path)
        self.env_check_thread.status_message.connect(self.status_text.append)
        self.env_check_thread.environment_ready.connect(self.on_env_check_finished)
        self.env_check_thread.start()

    def on_env_check_finished(self, ready):
        """Environment check finished callback"""
        pass  # We don't need to do anything special here since messages are already shown in status

    def browse_mcc(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select MCC Tree File", "", "Tree Files (*.tree *.tre)")
        if path:
            self.mcc_input.setText(path)

    def browse_plot(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Output Directory", "", "Text Files (*.txt)")
        if path:
            self.plot_input.setText(path)

    def run_steps(self):
        # Validate environments
        python_path = self.settings.value("python_path", "")
        perl_path = self.settings.value("perl_path", "")
        r_path = self.settings.value("r_install_dir", "")

        # Check Python
        if not python_path or not os.path.isfile(python_path):
            QMessageBox.warning(self, "Error", "Please select the Python executable first")
            self.status_text.append(
                "<b><span style='color: red;'>Error: Python path not configured. Please check the settings in 'Option-Environment'.</span></b>")
            return
        if check_python_path(python_path) != "install":
            QMessageBox.warning(self, "Error", "Python environment missing ete3 or pandas")
            self.status_text.append(
                "<b><span style='color: red;'>Error: Python environment missing ete3 or pandas. Please install required libraries.</span></b>")
            return

        # Check Perl
        if not perl_path or not os.path.isfile(perl_path):
            QMessageBox.warning(self, "Error", "Please select the Perl executable first")
            self.status_text.append(
                "<b><span style='color: red;'>Error: Perl path not configured. Please check 'Option-Environment' settings.</span></b>")
            return
        if check_perl_path(perl_path) != "install":
            QMessageBox.warning(self, "Error", "Invalid Perl executable")
            self.status_text.append(
                "<b><span style='color: red;'>Error: Invalid Perl executable. Please check the 'Option-Environment' settings.</span></b>")
            return

        # Check R
        if not r_path or not os.path.isdir(r_path):
            QMessageBox.warning(self, "Error", "Please select the R installation directory first")
            self.status_text.append(
                "<b><span style='color: red;'>Error: R installation directory not configured. Please check the 'Option-Environment' settings.</span></b>")
            return
        rscript_path = os.path.join(r_path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
        if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
            QMessageBox.warning(self, "Error", f"Rscript executable not found in {r_path}")
            self.status_text.append(
                f"<b><span style='color: red;'>Error: Rscript executable not found in {r_path}.</span></b>")
            return
        status, missing_packages = check_r_path(r_path)
        if status != "install":
            QMessageBox.warning(self, "Error", f"Missing R packages: {', '.join(missing_packages)}")
            self.status_text.append(
                f"<b><span style='color: red;'>Error: Missing R packages: {', '.join(missing_packages)}.</span></b>")
            return

        if self.mcc_input.text() == "not selected":
            QMessageBox.warning(self, "Error", "Please select an MCC tree file")
            self.status_text.append("<b><span style='color: red;'>Error: Please select an MCC tree file.</span></b>")
            return

        self.status_text.clear()
        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_text.append("<b><span style='color: blue;'>Running analysis...</span></b>")
        mcc_file = self.mcc_input.text()
        output_path = self.plot_input.text() if self.plot_input.text() else None
        self.worker = WorkerThread(mcc_file, perl_path, r_path, output_path, python_path)
        self.worker.update_status.connect(self.status_text.append)
        self.worker.finished.connect(self.on_run_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_run_finished(self, success):
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", "Processing completed successfully!")
            self.last_matrix_file = self.plot_input.text() if self.plot_input.text() else os.path.join(
                os.path.dirname(self.mcc_input.text()), "outfile_transposed.txt")
        else:
            QMessageBox.warning(self, "Error", "Processing failed. Check the status log for details.")
            self.status_text.append(
                "<b><span style='color: red;'>Processing failed. Check the status log for details.</span></b>")
        self.worker = None

    def on_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        QMessageBox.warning(self, "Error", f"Processing failed: {error_msg}")
        self.status_text.append(f"<b><span style='color: red;'>Error: {error_msg}</span></b>")
        self.worker = None

    def show_plotter(self):
        from MOTP.layout_motp import MigrationOverTimePlotter
        # Always open MOTP, pass last_matrix_file if available, otherwise None
        self.plotter_window = MigrationOverTimePlotter(matrix_file=self.last_matrix_file)
        self.plotter_window.show()