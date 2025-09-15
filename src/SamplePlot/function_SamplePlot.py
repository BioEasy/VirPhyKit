import os
import subprocess
import pandas as pd
from PyQt5.QtWidgets import QFileDialog
class ProcessPlot:
    @staticmethod
    def upload_file(window):
        try:
            print("Opening file dialog...")
            file_name, _ = QFileDialog.getOpenFileName(
                window,
                "Select txt File",
                os.path.expanduser("~"),
                "Text Files (*.txt)"
            )
            print(f"File selected: {file_name}")
            if file_name:
                window.input_file = file_name
                window.input_file_display.setText(file_name)
        except Exception as e:
            print(f"Error in upload_file: {e}")
            window.info_text.setText(f"Error: {e}")
    @staticmethod
    def select_save_location(window):
        try:
            print("Opening directory dialog...")
            folder = QFileDialog.getExistingDirectory(
                window,
                "Select Save Directory",
                os.path.expanduser("~")
            )
            print(f"Folder selected: {folder}")
            if folder:
                window.save_path = folder
                window.output_path_display.setText(folder)
        except Exception as e:
            print(f"Error in select_save_location: {e}")
            window.info_text.setText(f"Error: {e}")
    @staticmethod
    def check_r_path(window):
        rscript_path = window.settings.value("r_path", "")
        if not rscript_path or not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
            window.info_text.setText("<b><span style='color:red'>Error: Rscript not configured or invalid. Please set it in Environment Settings.</span><b>")
            window.r_packages_ready = False
            return

        required_packages = ["ggplot2", "tidyr", "ggsci", "scales", "patchwork", "maps", "rnaturalearth", "sf"]
        try:
            result = subprocess.run(
                [rscript_path, "-e", "cat(rownames(installed.packages()))"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "Unknown error"
                window.info_text.setText(f"<b><span style='color:red'>Failed to check R packages: {error_msg}</span><b>")
                window.r_packages_ready = False
                return
            installed = result.stdout.strip().split()
            missing_packages = [pkg for pkg in required_packages if pkg not in installed]
            if missing_packages:
                window.info_text.setText(f"<b><span style='color:red'>Missing R packages: {', '.join(missing_packages)}</span><b>")
                window.r_packages_ready = False
            else:
                window.info_text.setText("<b><span style='color:green'>R environment ready</span><b>")
                window.r_packages_ready = True
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            window.info_text.setText(f"<b><span style='color:red'>Error checking R packages: {e}</span><b>")
            window.r_packages_ready = False

    @staticmethod
    def run_r_script(window):
        if not hasattr(window, 'input_file') or not window.input_file:
            window.info_text.setText("Please select an input file!")
            return
        if not hasattr(window, 'save_path') or not window.save_path:
            window.info_text.setText("Please select a save location!")
            return

        ProcessPlot.check_r_path(window)
        if not window.r_packages_ready:
            return

        rscript_path = window.settings.value("r_path", "")
        if not rscript_path or not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
            window.info_text.setText("<b><span style='color:red'>Error: Rscript not configured or invalid. Please set it in Environment Settings.</span><b>")
            return
        try:
            df = pd.read_csv(window.input_file, sep='\t')
            if window.plot_type == "date":
                required_cols = ['Year', 'Total']
                if not all(col in df.columns for col in required_cols) or len(
                        [col for col in df.columns if col not in required_cols]) < 1:
                    window.info_text.setText(
                        "<b><span style='color:red'>Error: Input file must have Year, Total, and at least one country column</span><b>")
                    return
            else:
                required_cols = ['region', 'Longitude', 'Latitude']
                if not all(col in df.columns for col in required_cols):
                    window.info_text.setText("<b><span style='color:red'>Error: Input file must have region, Longitude, and Latitude columns</span><b>")
                    return
        except Exception as e:
            window.info_text.setText(f"<b><span style='color:red'>Error reading input file: {e}</span><b>")
            return

        input_file_r = os.path.abspath(window.input_file).replace("\\", "/")
        output_file = os.path.abspath(os.path.join(window.save_path, f"{window.filename_input.text()}.pdf")).replace(
            "\\", "/")
        script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
        r_script_name = "generate_plot.R" if window.plot_type == "date" else "generate_map.R"
        r_script_path = os.path.join(script_dir, r_script_name)
        if not os.path.isfile(r_script_path):
            window.info_text.setText(f"<b><span style='color:red'>Error: R script not found at {r_script_path}</span><b>")
            return

        print(f"R script path: {r_script_path}")

        if window.plot_type == "date":
            country_cols = [col for col in df.columns if col not in ['Year', 'Total']]
            if not country_cols:
                window.info_text.setText("<b><span style='color:red'>Error: No data found in input file</span><b>")
                return
            first_country = country_cols[0]
            last_country = country_cols[-1]
            command = [rscript_path, r_script_path, input_file_r, output_file, first_country, last_country]
        else:
            command = [rscript_path, r_script_path, input_file_r, output_file]

        print("Executing command:", " ".join(command))
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            window.info_text.setText(
                f"<b><span style='color:green'>Plot saved successfully at: {window.save_path}</span><b>")
            print("R script output:", result.stdout)
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            window.info_text.setText(f"<b><span style='color:red'>Error generating plot: {error_msg}</span><b>")
            print("R script error:", error_msg)
        except Exception as e:
            window.info_text.setText(f"<b><span style='color:red'>Unexpected error: {e}</span><b>")
            print(f"Unexpected error: {e}")

process_plot = ProcessPlot()