import os
import subprocess
import tempfile
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

# Embedded R script content from treedater.R
R_SCRIPT_CONTENT = """
require(treedater)
require(ape)
require(ggplot2)


args <- commandArgs(trailingOnly = TRUE)
tree_file <- args[1]
metadata_file <- args[2]
seqlen <- as.numeric(args[3])
output_dir <- args[4]
plot_ltt <- as.logical(args[5])


tre <- read.tree(tree_file)


Times <- read.csv(metadata_file, header = TRUE)
sts <- setNames(Times[,2], Times[,1])


dtr <- dater(tre, sts, seqlen, clock = "uncorrelated")


pdf(file.path(output_dir, "Phylogeny.pdf"), width = 10, height = 8)
plot(dtr, no.mar = TRUE, cex = 0.5)
dev.off()


if (plot_ltt) {
  pb <- parboot(dtr, ncpu = 1)
  g <- plot(pb, ggplot = TRUE)
  ggsave(file.path(output_dir, "LTT.pdf"), plot = g, width = 10, height = 8)
}


cat(capture.output(print(dtr)), sep = "\\n")
"""

class Worker(QtCore.QThread):
    """Worker thread to run R script without blocking the UI"""
    finished = pyqtSignal(dict)  # Signal for completion (result data)
    error = pyqtSignal(str)      # Signal for errors

    def __init__(self, parent, tree_file, metadata_file, seq_len, output_dir, plot_ltt):
        super().__init__(parent)
        self.tree_file = tree_file
        self.metadata_file = metadata_file
        self.seq_len = seq_len
        self.output_dir = output_dir
        self.plot_ltt = plot_ltt

    def run(self):
        try:
            # Create a temporary file for the R script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as temp_r_file:
                temp_r_file.write(R_SCRIPT_CONTENT)
                temp_r_script_path = temp_r_file.name

            # Ensure the temporary file has executable permissions (for Linux/macOS)
            if os.name != 'nt':
                os.chmod(temp_r_script_path, 0o755)

            # Run the R script
            cmd = [
                "Rscript",
                temp_r_script_path,
                self.tree_file,
                self.metadata_file,
                str(self.seq_len),
                self.output_dir,
                self.plot_ltt
            ]
            print(f"Executing command: {' '.join(cmd)}")  # Debug output
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Clean up the temporary file
            os.unlink(temp_r_script_path)

            output = result.stdout.strip()
            result_data = {
                'output': output,
                'saved_files': f"Saved Phylogeny.pdf{' and LTT.pdf' if self.plot_ltt == 'TRUE' else ''} to: {self.output_dir}"
            }
            self.finished.emit(result_data)

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            self.error.emit(f"R script failed: {error_msg}")
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")

class TreeDaterFunctions:
    def select_tree_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Tree File", "",
                                                             ".nwk files (*.nwk);;All Files (*)")
        if file_name:
            self.tree_file = file_name
            self.tree_input.setText(file_name)
            self.status_output.append(f"<b><span style='color: green;'>Loaded tree file: {file_name}</span></b>")
            self.statusBar().showMessage(f"Loaded tree file: {file_name}", 5000)

    def select_metadata_file(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Metadata File", "",
                                                             ".csv Files (*.csv);;All Files (*)")
        if file_name:
            self.metadata_file = file_name
            self.metadata_input.setText(file_name)
            self.status_output.append(f"<b><span style='color: green;'>Loaded metadata file: {file_name}</span></b>")
            self.statusBar().showMessage(f"Loaded metadata file: {file_name}", 5000)

    def select_output_dir(self):
        dir_name = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_name:
            self.output_dir = dir_name
            self.output_dir_input.setText(dir_name)
            self.status_output.append(
                f"<b><span style='color: green;'>Selected output directory: {dir_name}</span></b>")
            self.statusBar().showMessage(f"Selected output directory: {dir_name}", 5000)

    def run_analysis(self):
        seq_len = self.seq_input.text().strip()
        plot_ltt = "TRUE" if self.ltt_checkbox.isChecked() else "FALSE"

        # Input validation
        if not self.tree_file:
            self.status_output.append("<b><span style='color: red;'>Please select a tree file!</span></b>")
            self.statusBar().showMessage("Error: Missing tree file", 5000)
            return
        if not self.metadata_file:
            self.status_output.append("<b><span style='color: red;'>Please select a metadata file!</span></b>")
            self.statusBar().showMessage("Error: Missing metadata file", 5000)
            return
        if not seq_len:
            self.status_output.append("<b><span style='color: red;'>Please enter the sequence length!</span></b>")
            self.statusBar().showMessage("Error: Missing sequence length", 5000)
            return
        if not self.output_dir:
            self.status_output.append("<b><span style='color: red;'>Please select an output directory!</span></b>")
            self.statusBar().showMessage("Error: Missing output directory", 5000)
            return

        try:
            seq_len = int(seq_len)
        except ValueError:
            self.status_output.append("<b><span style='color: red;'>Sequence length must be a number!</span></b>")
            self.statusBar().showMessage("Error: Invalid sequence length", 5000)
            return

        # Disable Run button and show progress bar
        self.run_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_output.append("<b><span style='color: blue;'>Running analysis...</span></b>")
        self.statusBar().showMessage("Running analysis...", 0)

        # Start worker thread
        self.worker = Worker(self, self.tree_file, self.metadata_file, seq_len, self.output_dir, plot_ltt)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_finished(self, result):
        """Handle analysis completion"""
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.worker = None

        output = result['output']
        saved_files = result['saved_files']

        if output:
            lines = output.split("\n")
            bold_fields = [
                "Tip labels:",
                "Node labels:",
                "Time of common ancestor",
                "Time to common ancestor (before most recent sample)",
                "Weighted mean substitution rate (adjusted by branch lengths)",
                "Unadjusted mean substitution rate",
                "Clock model",
                "Coefficient of variation of rates"
            ]
            self.status_output.append(
                f"<b><span style='color: green;'>Analysis complete! {saved_files}</span></b>")
            for line in lines:
                line = line.strip()
                should_bold = any(field in line for field in bold_fields)
                if should_bold:
                    self.status_output.append(f"<b>{line}</b>")
                else:
                    self.status_output.append(line)
            self.statusBar().showMessage("Analysis complete!", 5000)
        else:
            self.status_output.append(
                "<b><span style='color: red;'>Analysis complete, but no output returned!</span></b>")
            self.statusBar().showMessage("Warning: No output returned", 5000)

    def on_analysis_error(self, error_msg):
        """Handle analysis errors"""
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.worker = None
        self.status_output.append(f"<b><span style='color: red;'>Error: {error_msg}</span></b>")
        self.statusBar().showMessage(f"Error: {error_msg}", 5000)