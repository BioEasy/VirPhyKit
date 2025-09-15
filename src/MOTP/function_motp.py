import os
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

def check_r_path(path):
    rscript_path = os.path.join(path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
    if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
        return "uninstall", ["tidyr", "ggplot2"]
    required_packages = ["tidyr", "ggplot2"]
    try:
        result = subprocess.run(
            [rscript_path, "-e", "cat(rownames(installed.packages()))"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode != 0:
            return "uninstall", required_packages
        installed = result.stdout.strip().split()
        missing_packages = [pkg for pkg in required_packages if pkg not in installed]
        return "install" if not missing_packages else "uninstall", missing_packages
    except (subprocess.SubprocessError, FileNotFoundError):
        return "uninstall", required_packages

class WorkerThread(QThread):
    update_status = pyqtSignal(str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, matrix_file, r_path, output_path, selected_directions, r_script):
        super().__init__()
        self.matrix_file = matrix_file
        self.r_path = r_path
        self.output_path = output_path
        self.selected_directions = selected_directions
        self.r_script = r_script

    def run(self):
        def status_callback(message):
            self.update_status.emit(message)

        status_callback(f"Input file: {self.matrix_file}")
        if not os.path.exists(self.matrix_file):
            status_callback("<b><span style='color: red;'>Error: The migration matrix file does not exist.</span></b>")
            self.finished.emit(False)
            return
        if not os.path.exists(self.r_script):
            status_callback(f"<b><span style='color: red;'>Error: {os.path.basename(self.r_script)} not found.</span></b>")
            self.finished.emit(False)
            return
        status_callback("Generating plot...")
        try:
            args = [self.r_path, self.r_script, self.matrix_file, self.output_path] + self.selected_directions
            subprocess.run(args, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            status_callback(f"<b><span style='color: green;'>Plot successfully generated!</span></b>")
            self.finished.emit(True)
        except Exception as e:
            error_msg = f"Failed to generate plot: {e}"
            status_callback(f"<b><span style='color: red;'>{error_msg}</span></b>")
            self.error.emit(error_msg)
            self.finished.emit(False)