from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QLabel, \
    QFileDialog, QMessageBox, QSizePolicy, QApplication, QTextEdit, QStatusBar, QProgressBar
from PyQt5.QtCore import Qt, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys


class InstallThread(QThread):
    status_update = pyqtSignal(str, str)  # (message, color)
    installation_complete = pyqtSignal(bool, list, list)  # (success, missing_r, missing_python)

    def __init__(self, rscript_path, missing_r, python_path, missing_python):
        super().__init__()
        self.rscript_path = rscript_path
        self.missing_r = missing_r
        self.python_path = python_path
        self.missing_python = missing_python

    def run(self):
        success = True
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []

            # Submit R package installation tasks
            if self.rscript_path and self.missing_r:
                self.status_update.emit("R: Starting package installation...", "blue")

                # Separate treedater from other packages
                regular_packages = [pkg for pkg in self.missing_r if pkg != 'treedater']
                has_treedater = 'treedater' in self.missing_r

                # Install regular packages first
                for pkg in regular_packages:
                    futures.append(executor.submit(self._install_r_package, pkg))

                # If treedater needs to be installed, handle it specially
                if has_treedater:
                    futures.append(executor.submit(self._install_treedater_package))

            # Submit Python package installation tasks
            if self.python_path and self.missing_python:
                self.status_update.emit("Python: Starting package installation...", "blue")
                for pkg in self.missing_python:
                    futures.append(executor.submit(self._install_python_package, pkg))

            # Collect results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if not result["success"]:
                        success = False
                        self.status_update.emit(
                            f"{result['type']}: Failed to install {result['package']}: {result['error']}",
                            "red"
                        )
                    else:
                        self.status_update.emit(
                            f"{result['type']}: Successfully installed {result['package']}",
                            "green"
                        )
                except Exception as e:
                    success = False
                    self.status_update.emit(f"Installation error: {e}", "red")

        self.installation_complete.emit(success, self.missing_r, self.missing_python)

    def _install_r_package(self, pkg):
        self.status_update.emit(f"R: Installing {pkg}...", "blue")
        try:
            subprocess.run(
                [self.rscript_path, "-e", f'install.packages("{pkg}", repos="https://cloud.r-project.org")'],
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            return {"success": True, "type": "R", "package": pkg}
        except subprocess.SubprocessError as e:
            return {"success": False, "type": "R", "package": pkg, "error": str(e)}

    def _install_treedater_package(self):
        self.status_update.emit("R: Installing devtools (required for treedater)...", "blue")
        try:
            subprocess.run(
                [self.rscript_path, "-e", 'install.packages("devtools", repos="https://cloud.r-project.org")'],
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            self.status_update.emit("R: Installing treedater...", "blue")
            subprocess.run(
                [self.rscript_path, "-e", 'library(devtools); install_github("emvolz/treedater")'],
                check=True,
                capture_output=True,
                text=True,
                timeout=600
            )
            return {"success": True, "type": "R", "package": "treedater"}
        except subprocess.SubprocessError as e:
            return {"success": False, "type": "R", "package": "treedater", "error": str(e)}

    def _install_python_package(self, pkg):
        self.status_update.emit(f"Python: Installing {pkg}...", "blue")
        try:
            subprocess.run(
                [self.python_path, "-m", "pip", "install", pkg],
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            return {"success": True, "type": "Python", "package": pkg}
        except subprocess.SubprocessError as e:
            return {"success": False, "type": "Python", "package": pkg, "error": str(e)}


class EnvironmentWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Environment Settings")
        self.settings = QSettings("VirusPhylogeographics", "EnvironmentSettings")
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)
        title_label = QLabel("Environment Settings")
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
            'Step 1: Select the R installation directory (must contain bin/Rscript).<br>'
            'Step 2: Select the Python installation directory.<br>'
            'Step 3: Select the Perl installation directory.<br>'
            'Step 4: Save settings.'
            '</span>'
        )
        title_layout.addWidget(help_button)
        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)
        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(10)
        r_label = QLabel("R Installation Directory:")
        r_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(r_label)
        r_widget = QWidget()
        r_hbox = QHBoxLayout()
        self.r_path_input = QLineEdit()
        r_path_from_settings = self.settings.value("r_install_dir", "Please specify the R installation directory")
        self.r_path_input.setText(r_path_from_settings)
        self.r_path_input.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 5px;font-size: 12px;")
        self.r_path_input.setReadOnly(True)
        self.r_path_input.setToolTip(self.r_path_input.text())
        r_hbox.addWidget(self.r_path_input)
        self.r_browse_btn = QPushButton("...")
        self.r_browse_btn.setFixedWidth(40)
        self.r_browse_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008B;
            }
        """)
        self.r_browse_btn.clicked.connect(self.browse_r)
        r_hbox.addWidget(self.r_browse_btn)
        r_widget.setLayout(r_hbox)
        settings_layout.addWidget(r_widget)
        python_label = QLabel("Python Installation Directory:")
        python_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(python_label)
        python_widget = QWidget()
        python_hbox = QHBoxLayout()
        self.python_path_input = QLineEdit()
        python_path_from_settings = self.settings.value("python_install_dir",
                                                        "Please specify the Python installation directory")
        self.python_path_input.setText(python_path_from_settings)
        self.python_path_input.setStyleSheet(
            "padding: 5px; border: 1px solid #ddd; border-radius: 5px;font-size: 12px;")
        self.python_path_input.setReadOnly(True)
        self.python_path_input.setToolTip(self.python_path_input.text())
        python_hbox.addWidget(self.python_path_input)
        self.python_browse_btn = QPushButton("...")
        self.python_browse_btn.setFixedWidth(40)
        self.python_browse_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008B;
            }
        """)
        self.python_browse_btn.clicked.connect(self.browse_python)
        python_hbox.addWidget(self.python_browse_btn)
        python_widget.setLayout(python_hbox)
        settings_layout.addWidget(python_widget)
        perl_label = QLabel("Perl Installation Directory:")
        perl_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(perl_label)
        perl_widget = QWidget()
        perl_hbox = QHBoxLayout()
        self.perl_path_input = QLineEdit()
        perl_path_from_settings = self.settings.value("perl_install_dir",
                                                      "Please specify the Perl installation directory")
        self.perl_path_input.setText(perl_path_from_settings)
        self.perl_path_input.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 5px;font-size: 12px;")
        self.perl_path_input.setReadOnly(True)
        self.perl_path_input.setToolTip(self.perl_path_input.text())
        perl_hbox.addWidget(self.perl_path_input)
        self.perl_browse_btn = QPushButton("...")
        self.perl_browse_btn.setFixedWidth(40)
        self.perl_browse_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008B;
            }
        """)
        self.perl_browse_btn.clicked.connect(self.browse_perl)
        perl_hbox.addWidget(self.perl_browse_btn)
        perl_widget.setLayout(perl_hbox)
        settings_layout.addWidget(perl_widget)
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
            font-size: 12px;
        """)
        status_layout.addWidget(self.status_box)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=1)
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { 
                border: 1px solid #ddd; 
                background-color: #f9f9f9; 
                height: 10px; 
                border-radius: 5px; 
            }

        """)
        main_layout.addWidget(self.progress_bar)
        # Button layout with Check button only
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_btn = QPushButton("Check")
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00008B;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(self.save_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
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
        self.check_r_path(r_path_from_settings)
        self.check_python_path(python_path_from_settings)
        self.check_perl_path(perl_path_from_settings)

    def browse_r(self):
        directory = QFileDialog.getExistingDirectory(self, "Select R Installation Directory")
        if directory:
            self.r_path_input.setText(directory)
            self.check_r_path(directory)

    def browse_python(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Python Installation Directory")
        if directory:
            self.python_path_input.setText(directory)
            self.check_python_path(directory)

    def browse_perl(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Perl Installation Directory")
        if directory:
            self.perl_path_input.setText(directory)
            self.check_perl_path(directory)

    def _check_executable(self, path):
        return os.path.isfile(path) and os.access(path, os.X_OK)

    def _check_r_packages(self, rscript_path):
        required_packages = ["tidyr", "ggplot2", "scales", "ggsci", "patchwork", "treeio", "plyr", "dplyr", "readr",
                             "rnaturalearth", "rnaturalearthdata", "treedater", "ape", "maps", "sf"]
        try:
            result = subprocess.run(
                [rscript_path, "-e", "cat(rownames(installed.packages()))"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return required_packages
            installed = result.stdout.strip().split()
            missing = [pkg for pkg in required_packages if pkg not in installed]
            return missing
        except (subprocess.SubprocessError, FileNotFoundError):
            return required_packages

    def _check_python_packages(self, python_path):
        required_packages = ["numpy", "pandas", "biopython", "ete3"]
        try:
            result = subprocess.run(
                [python_path, "-m", "pip", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return required_packages
            installed = [line.split()[0].lower() for line in result.stdout.strip().split('\n')[2:]]
            missing = [pkg for pkg in required_packages if pkg.lower() not in installed]
            return missing
        except (subprocess.SubprocessError, FileNotFoundError):
            return required_packages

    def check_r_path(self, directory):
        if directory == "Please specify the R installation directory":
            self.status_box.append(f"<b><span style='color:red'>R: No directory specified</span></b>")
            return
        rscript_path = os.path.join(directory, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
        if not self._check_executable(rscript_path):
            self.status_box.append(
                f"<b><span style='color:red'>R: Rscript executable not found in {directory}</span></b>")
            return
        missing_packages = self._check_r_packages(rscript_path)
        if not missing_packages:
            self.status_box.append(
                f"<b><span style='color:green'>R: Installed, including all required packages</span></b>")
        else:
            self.status_box.append(f"<b><span style='color:red'>R: Missing: {', '.join(missing_packages)}</span></b>")

    def check_python_path(self, directory):
        if directory == "Please specify the Python installation directory":
            self.status_box.append(f"<b><span style='color:red'>Python: No directory specified</span></b>")
            return
        possible_paths = [
            os.path.join(directory, "python" + (".exe" if os.name == "nt" else "")),
            os.path.join(directory, "python3" + (".exe" if os.name == "nt" else "")),
            os.path.join(directory, "bin", "python" + (".exe" if os.name == "nt" else "")),
            os.path.join(directory, "bin", "python3" + (".exe" if os.name == "nt" else ""))
        ]
        python_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                python_path = path
                break
        if python_path and self._check_executable(python_path):
            self.status_box.append(f"<b><span style='color:green'>Python: Installed</span></b>")
            missing_packages = self._check_python_packages(python_path)
            if not missing_packages:
                self.status_box.append(
                    f"<b><span style='color:green'>Python: All required packages installed</span></b>")
            else:
                self.status_box.append(
                    f"<b><span style='color:red'>Python: Missing: {', '.join(missing_packages)}</span></b>")
        else:
            self.status_box.append(
                f"<b><span style='color:red'>Python: executable file not found in {directory}</span></b>")

    def check_perl_path(self, directory):
        if directory == "Please specify the Perl installation directory":
            self.status_box.append(f"<b><span style='color:red'>Perl: No directory specified</span></b>")
            return
        perl_path = os.path.join(directory, "bin", "perl" + (".exe" if os.name == "nt" else ""))
        if self._check_executable(perl_path):
            self.status_box.append(f"<b><span style='color:green'>Perl: Installed</span></b>")
        else:
            self.status_box.append(
                f"<b><span style='color:red'>Perl: Perl executable not found in {directory}</span></b>")

    def save_settings(self):
        r_path = self.r_path_input.text()
        python_path = self.python_path_input.text()
        perl_path = self.perl_path_input.text()
        self.settings.setValue("r_install_dir",
                               r_path if r_path != "Please specify the R installation directory" else "")
        self.settings.setValue("python_install_dir",
                               python_path if python_path != "Please specify the Python installation directory" else "")
        self.settings.setValue("perl_install_dir",
                               perl_path if perl_path != "Please specify the Perl installation directory" else "")
        rscript_path = ""
        if r_path != "Please specify the R installation directory":
            candidate_rscript_path = os.path.join(r_path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
            if self._check_executable(candidate_rscript_path):
                rscript_path = candidate_rscript_path
        possible_python_paths = [
            os.path.join(python_path, "python" + (".exe" if os.name == "nt" else "")),
            os.path.join(python_path, "python3" + (".exe" if os.name == "nt" else "")),
            os.path.join(python_path, "bin", "python" + (".exe" if os.name == "nt" else "")),
            os.path.join(python_path, "bin", "python3" + (".exe" if os.name == "nt" else ""))
        ]
        python_exe_path = ""
        for path in possible_python_paths:
            if os.path.isfile(path):
                python_exe_path = path
                break
        perl_exe_path = os.path.join(perl_path, "bin", "perl" + (
            ".exe" if os.name == "nt" else "")) if perl_path != "Please specify the Perl installation directory" else ""
        self.settings.setValue("r_path", rscript_path)
        self.settings.setValue("python_path", python_exe_path)
        self.settings.setValue("perl_path", perl_exe_path)

        # Check for missing R and Python packages
        missing_r = []
        missing_python = []
        if rscript_path:
            missing_r = self._check_r_packages(rscript_path)
        if python_exe_path:
            missing_python = self._check_python_packages(python_exe_path)

        self.status_box.clear()
        self.check_r_path(r_path)
        self.check_python_path(python_path)
        self.check_perl_path(perl_path)

        if missing_r or missing_python:
            missing_text = "The following packages are missing and need to be installed (this may take a few minutes):\n\n"
            if missing_r:
                missing_text += f"R packages: {', '.join(missing_r)}\n"
            if missing_python:
                missing_text += f"Python packages: {', '.join(missing_python)}\n"
            missing_text += "\nWould you like to install these packages automatically?"
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Missing Packages")
            msg_box.setText(missing_text)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            msg_box.setStyleSheet("QLabel { font-size: 12px; }")
            reply = msg_box.exec_()
            if reply == QMessageBox.Yes:
                # Disable buttons and show progress bar
                self.save_btn.setText("Cancel")
                self.save_btn.clicked.disconnect()
                self.save_btn.clicked.connect(self.cancel_installation)
                self.r_browse_btn.setEnabled(False)
                self.python_browse_btn.setEnabled(False)
                self.perl_browse_btn.setEnabled(False)
                self.progress_bar.setVisible(True)
                self.status_box.clear()
                self.status_box.append(
                    "<b><span style='color:blue'>Starting package installation process...</span></b>")

                # Start installation in a separate thread
                self.install_thread = InstallThread(rscript_path, missing_r, python_exe_path, missing_python)
                self.install_thread.status_update.connect(self.update_status)
                self.install_thread.installation_complete.connect(
                    lambda success, mr, mp: self.on_installation_complete(success, mr, mp, r_path, python_path,
                                                                          perl_path)
                )
                self.install_thread.start()
            else:
                self.status_box.append(
                    "<b><span style='color:red'>Warning: Some packages are missing. The environment may not function properly.</span></b>")
                QMessageBox.warning(self, "Incomplete Setup",
                                    "Some packages are missing. Please install them to ensure proper functionality.")
        else:
            self.status_box.append("Settings saved successfully!")
            QMessageBox.information(self, "Done!", "Settings saved successfully!")

    def update_status(self, message, color):
        self.status_box.append(f"<b><span style='color:{color}'>{message}</span></b>")
        QApplication.processEvents()

    def cancel_installation(self):
        if hasattr(self, 'install_thread') and self.install_thread.isRunning():
            self.install_thread.terminate()
            self.status_box.append("<b><span style='color:red'>Installation canceled by user.</span></b>")
            self.progress_bar.setVisible(False)
            self.save_btn.setText("Check")
            self.save_btn.clicked.disconnect()
            self.save_btn.clicked.connect(self.save_settings)
            self.r_browse_btn.setEnabled(True)
            self.python_browse_btn.setEnabled(True)
            self.perl_browse_btn.setEnabled(True)
            self.check_r_path(self.r_path_input.text())
            self.check_python_path(self.python_path_input.text())
            self.check_perl_path(self.perl_path_input.text())

    def on_installation_complete(self, success, missing_r, missing_python, r_path, python_path, perl_path):
        # Hide progress bar
        self.progress_bar.setVisible(False)
        # Restore Check button
        self.save_btn.setText("Check")
        self.save_btn.clicked.disconnect()
        self.save_btn.clicked.connect(self.save_settings)
        # Re-enable buttons
        self.r_browse_btn.setEnabled(True)
        self.python_browse_btn.setEnabled(True)
        self.perl_browse_btn.setEnabled(True)
        if not success:
            QMessageBox.warning(self, "Installation Failed",
                                "Some packages failed to install. Please check the status log for details.")
        self.status_box.append("<b><span style='color:blue'>Re-checking environment...</span></b>")
        QApplication.processEvents()
        self.status_box.clear()
        self.check_r_path(r_path)
        self.check_python_path(python_path)
        self.check_perl_path(perl_path)
        self.status_box.append("Settings saved successfully!")
        QMessageBox.information(self, "Done!", "Settings saved successfully!")