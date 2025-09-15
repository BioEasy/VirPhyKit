import os
from sys import platform
import subprocess
from PyQt5.QtGui import QIntValidator, QFont
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QRadioButton, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QStatusBar, QSizePolicy)
from PyQt5.QtCore import Qt
from RSPP.fuction_rspp import showFileDialog, readTreeFile, plot_bar_chart, plot_pie_chart, \
    selectSaveDirectory, showBatchFileDialog, switch_color_scheme, get_current_colors

class RootStatePosteriorProbabilityGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_directory = os.getcwd()  
        self.save_directory = None
        self.set_fields = None
        self.prob_values = None
        self.batch_files = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("RSPP-Viz (Root State Posterior Probability Visualizer)")
        self.setGeometry(100, 100, 700, 600)

        # font = QFont("Arial", 10)
        # QApplication.setFont(font)

        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10) 
        main_layout.setSpacing(10)  

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_label = QLabel("RSPP-Viz (Root State Posterior Probability Visualizer)")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 8px; background-color: #ffffff; border-radius: 5px;")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  
        title_layout.addWidget(title_label)

        # Help Button
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
            'Step 1: Select the plot style you want to generate (pie or column).<br>'
            'Step 2: Select the working directory and the MCC tree (annotated with traits) or MultiTypeTree for analysis (batch processing is available in Batch mode).<br>'
            'Step 3: Select the output directory and specify the plot size.<br>'
            'Step 4: Use [Hue Harmony] to adjust color schemes, and click [Plot] to create the plot.'
            '</span>'
        )
        title_layout.addWidget(help_button)

        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel("RSPP-Viz is a specialized tool for visualizing root state posterior probabilities inferred from MCC trees (annotated with traits) or MultiTypeTree.")
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setStyleSheet("padding: 5px; border: none; color: #808080; font-size: 12px;")
        main_layout.addWidget(description_label, alignment=Qt.AlignCenter)


        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(5)  

    
        style_label = QLabel("Plot Style:")
        style_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(style_label)
        style_widget = QWidget()
        style_hbox = QHBoxLayout()
        self.pie_chart_rb = QRadioButton('Pie charts')
        self.histogram_rb = QRadioButton('Histogram')
        self.pie_chart_rb.setStyleSheet("font-size: 12px;")
        self.histogram_rb.setStyleSheet("font-size: 12px;")
        self.histogram_rb.setChecked(True)
        style_hbox.addWidget(self.pie_chart_rb)
        style_hbox.addWidget(self.histogram_rb)
        style_hbox.addStretch()
        style_widget.setLayout(style_hbox)
        settings_layout.addWidget(style_widget)

    
        tree_label = QLabel("MCC Tree File:")
        tree_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(tree_label)
        tree_widget = QWidget()
        tree_hbox = QHBoxLayout()
        self.input2 = QLineEdit()
        self.input2.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px;")
        tree_hbox.addWidget(self.input2)
        self.browseBtn2 = QPushButton("...")
        self.browseBtn2.setFixedWidth(30)
        self.browseBtn2.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        tree_hbox.addWidget(self.browseBtn2)
        self.batchBtn = QPushButton("Batch")
        self.batchBtn.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        tree_hbox.addWidget(self.batchBtn)
        tree_widget.setLayout(tree_hbox)
        settings_layout.addWidget(tree_widget)


        out_label = QLabel("Output Directory:")
        out_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(out_label)
        out_widget = QWidget()
        out_hbox = QHBoxLayout()
        self.input3 = QLineEdit()
        self.input3.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px;")
        out_hbox.addWidget(self.input3)
        self.browseBtn3 = QPushButton("...")
        self.browseBtn3.setFixedWidth(30)
        self.browseBtn3.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        out_hbox.addWidget(self.browseBtn3)
        self.viewBtn = QPushButton("View")
        self.viewBtn.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        out_hbox.addWidget(self.viewBtn)
        out_widget.setLayout(out_hbox)
        settings_layout.addWidget(out_widget)


        size_label = QLabel("Plot Size (pixels):")
        size_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(size_label)
        size_widget = QWidget()
        size_hbox = QHBoxLayout()
        self.width_input = QLineEdit("800")
        self.width_input.setValidator(QIntValidator(100, 5000))
        self.width_input.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px; width: 80px;")
        size_hbox.addWidget(QLabel("Width:", styleSheet="font-size: 12px;"))
        size_hbox.addWidget(self.width_input)
        self.height_input = QLineEdit("600")
        self.height_input.setValidator(QIntValidator(100, 5000))
        self.height_input.setStyleSheet("border: 1px solid #ddd; padding: 5px; border-radius: 5px; font-size: 12px; width: 80px;")
        size_hbox.addWidget(QLabel("Height:", styleSheet="font-size: 12px;"))
        size_hbox.addWidget(self.height_input)
        size_widget.setLayout(size_hbox)
        settings_layout.addWidget(size_widget)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)


        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QVBoxLayout()
        self.statusText = QTextEdit()
        self.statusText.setReadOnly(True)
        self.statusText.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 5px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            font-size: 12px;
        """)
        status_layout.addWidget(self.statusText)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=0)


        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.lucky_color_btn = QPushButton("Hue Harmony")
        self.lucky_color_btn.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        button_layout.addWidget(self.lucky_color_btn)
        self.generateBtn = QPushButton("Plot")
        self.generateBtn.setStyleSheet("""
            QPushButton { padding: 5px 10px; background-color: #1E90FF; color: white; border-radius: 5px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #00008B; }
        """)
        button_layout.addWidget(self.generateBtn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)


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


        self.pie_chart_rb.toggled.connect(self.update_chart_type)
        self.browseBtn2.clicked.connect(self.browse_file)
        self.batchBtn.clicked.connect(self.batch_action)
        self.browseBtn3.clicked.connect(self.select_save_directory)
        self.viewBtn.clicked.connect(self.view_directory)
        self.generateBtn.clicked.connect(self.generate_action)
        self.lucky_color_btn.clicked.connect(self.lucky_color_action)
        self.chart_type = 'Histogram'

    def update_chart_type(self):
        self.chart_type = 'Pie' if self.pie_chart_rb.isChecked() else 'Histogram'
        self.statusBar().showMessage(f"Chart type set to: {self.chart_type}", 5000)

    def update_status(self, message):
        self.statusText.append(message)
        self.statusBar().showMessage(message.split("<span")[0].strip(), 5000)

    def select_directory(self):
        self.file_directory = os.getcwd()
        self.update_status(f"Using default working directory: {self.file_directory}")

    def browse_file(self):
        file_path = showFileDialog(self, default_directory=self.file_directory)
        if file_path:
            self.input2.setText(file_path)
            self.update_status(f"Selected file path: {file_path}")
            self.batch_files = []
            self.set_fields, self.prob_values = readTreeFile(file_path)

    def batch_action(self):
        files = showBatchFileDialog(self, default_directory=self.file_directory)
        if files:
            self.batch_files = files
            self.input2.setText(f"{len(files)} files selected")
            self.set_fields = None
            self.prob_values = None
            self.update_status(f"Batch processing enabled. {len(files)} files selected.")

    def select_save_directory(self):
        self.save_directory = selectSaveDirectory(self)
        if self.save_directory:
            self.input3.setText(self.save_directory)
            self.update_status(f"Save path: {self.save_directory}")

    def lucky_color_action(self):
        new_colors = switch_color_scheme(len(self.set_fields) if self.set_fields else 5)
        self.update_status(f"new color scheme: {new_colors}")
        self.statusBar().showMessage("Lucky Color applied! Preview or generate to see the change.", 5000)
        if self.set_fields and self.prob_values:
            self.preview_action()

    def view_directory(self):
        if not self.save_directory:
            self.update_status("Please select an output directory first.")
            self.statusBar().showMessage("Error: No output directory selected", 5000)
            return
        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(self.save_directory)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", self.save_directory])
            else:  # Linux
                subprocess.run(["xdg-open", self.save_directory])
            self.statusBar().showMessage("Directory opened successfully", 5000)
        except Exception as e:
            self.update_status(f"Error opening directory: {e}")
            self.statusBar().showMessage("Error opening directory", 5000)
    def preview_action(self):
        if self.batch_files:
            self.update_status("Batch processing enabled. Please check the output directory for results.")
            return
        if not self.set_fields or not self.prob_values:
            self.update_status("Please select a tree file.")
            return
        try:
            width_px = int(self.width_input.text())
            height_px = int(self.height_input.text())
            colors = get_current_colors(len(self.set_fields)) 
            if self.chart_type == 'Histogram':
                plot_bar_chart(self.set_fields, self.prob_values, self.save_directory, width_px, height_px, preview=True, colors=colors)
            else:
                plot_pie_chart(self.set_fields, self.prob_values, self.save_directory, width_px, height_px, preview=True, colors=colors)
            self.statusBar().showMessage("Preview generated successfully", 5000)
        except ValueError:
            self.update_status("Please enter valid width and height in pixels.")
            self.statusBar().showMessage("Error: Invalid width or height", 5000)

    def generate_action(self):
        try:
            if not self.save_directory:
                self.update_status("Select a output directory before proceeding.")
                self.statusBar().showMessage("Error: Output directory not selected", 5000)
                return
            width_px = int(self.width_input.text())
            height_px = int(self.height_input.text())
            colors = get_current_colors(len(self.set_fields) if self.set_fields else 5)  

            if self.batch_files:
                for file_path in self.batch_files:
                    set_fields, prob_values = readTreeFile(file_path)
                    if not set_fields or not prob_values:
                        continue
                    colors = get_current_colors(len(set_fields))
                    base_name = os.path.basename(file_path)
                    output_name = os.path.splitext(base_name)[0] + ('.pdf' if self.chart_type == 'Histogram' else '_pie.pdf')
                    output_path = os.path.join(self.save_directory, output_name)
                    if self.chart_type == 'Histogram':
                        plot_bar_chart(set_fields, prob_values, output_path, width_px, height_px, preview=False, colors=colors)
                    else:
                        plot_pie_chart(set_fields, prob_values, output_path, width_px, height_px, preview=False, colors=colors)
                self.statusBar().showMessage("Batch generation completed", 5000)
            else:
                if not self.set_fields or not self.prob_values:
                    self.update_status("No valid tree file selected.")
                    self.statusBar().showMessage("Error: No valid tree file selected", 5000)
                    return
                file_path = self.input2.text()
                if not file_path:
                    self.update_status("No tree file selected.")
                    self.statusBar().showMessage("Error: No tree file selected", 5000)
                    return
                base_name = os.path.basename(file_path)
                output_name = os.path.splitext(base_name)[0] + ('.pdf' if self.chart_type == 'Histogram' else '_pie.pdf')
                output_path = os.path.join(self.save_directory, output_name)
                if self.chart_type == 'Histogram':
                    plot_bar_chart(self.set_fields, self.prob_values, output_path, width_px, height_px, preview=False, colors=colors)
                else:
                    plot_pie_chart(self.set_fields, self.prob_values, output_path, width_px, height_px, preview=False, colors=colors)
                self.statusBar().showMessage("Generation completed successfully", 5000)
            self.update_status("<b><span style='color: green;'>Drawing completed successfully!</span></b>")
        except ValueError:
            self.update_status("Invalid width or height.")
            self.statusBar().showMessage("Error: Invalid width or height", 5000)
        except Exception as e:
            self.update_status(f"Unexpected error: {e}")