from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QSizePolicy, QHBoxLayout, QWidget, QCheckBox, QLabel
from PyQt5.QtCore import Qt

class TreeDaterLayout:
    def init_ui(self):
        self.setWindowTitle("TreeDater-LTT (Lineage Through Time with Treedater)")
        self.setGeometry(100, 100, 800, 600)



        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        main_layout = QtWidgets.QVBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(5)

        title_label = QtWidgets.QLabel("TreeDater-LTT (Lineage Through Time with Treedater)")
        title_label.setFont(QtGui.QFont("Arial", 16, QtGui.QFont.Bold))
        title_label.setAlignment(QtCore.Qt.AlignCenter)
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
            'Step 1: Select a Newick tree file (.nwk).<br>'
            'Step 2: Upload the metadata file (.csv) with sampling dates.<br>'
            'Step 3: Enter sequence length and enable the ’LTT’ option to generate a lineage-through-time plot.<br>'
            'Step 4: Specify the output directory for saving results.<br>'
            'Step 5: Click the ’Run’ to perform the LTT analysis using TreeDater, and view the results in the Status panel and output images.'
            '</span>'
        )
        title_layout.addWidget(help_button)

        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget, alignment=Qt.AlignCenter)

        description_label = QLabel()
        description_label.setText("""
        <p style="line-height: 120%; margin: 0; padding: 0;">
        &nbsp;&nbsp;&nbsp;&nbsp;TreeDater-LTT is a tool for conducting a lineage-through-time (LTT) analysis using Treedater.
        Additionally, it can also infer the time to the most recent ancestor (TMRCA) and the substitution rate,
        implemented with a scalable relaxed-clock phylogenetic dating framework.
        </p>
        """)
        description_label.setFont(QFont("Arial", 10))
        description_label.setAlignment(Qt.AlignLeft)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("padding: 5px; border: none; color: #808080; font-size: 12px;")
        main_layout.addWidget(description_label)

        settings_group = QtWidgets.QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        settings_layout = QtWidgets.QVBoxLayout()
        settings_layout.setSpacing(10)

        tree_label = QtWidgets.QLabel("Tree File (.nwk):")
        tree_label.setStyleSheet("font-size: 12px;")
        settings_layout.addWidget(tree_label)
        tree_widget = QtWidgets.QWidget()
        tree_hbox = QtWidgets.QHBoxLayout()
        self.tree_input = QtWidgets.QLineEdit()
        self.tree_input.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 5px; font-size: 12px;")
        tree_hbox.addWidget(self.tree_input)
        tree_button = QtWidgets.QPushButton("...")
        tree_button.setFixedWidth(40)
        tree_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00008B;
            }
        """)
        tree_button.clicked.connect(self.select_tree_file)
        tree_hbox.addWidget(tree_button)
        tree_widget.setLayout(tree_hbox)
        settings_layout.addWidget(tree_widget)

        metadata_label = QtWidgets.QLabel("Metadata File (.csv):")
        metadata_label.setStyleSheet("font-size:12px;")
        settings_layout.addWidget(metadata_label)
        metadata_widget = QtWidgets.QWidget()
        metadata_hbox = QtWidgets.QHBoxLayout()
        self.metadata_input = QtWidgets.QLineEdit()
        self.metadata_input.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 5px; font-size: 12px;")
        metadata_hbox.addWidget(self.metadata_input)
        metadata_button = QtWidgets.QPushButton("...")
        metadata_button.setFixedWidth(40)
        metadata_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00008B;
            }
        """)
        metadata_button.clicked.connect(self.select_metadata_file)
        metadata_hbox.addWidget(metadata_button)
        metadata_widget.setLayout(metadata_hbox)
        settings_layout.addWidget(metadata_widget)

        seq_ltt_widget = QtWidgets.QWidget()
        seq_ltt_hbox = QtWidgets.QHBoxLayout()
        seq_ltt_hbox.setContentsMargins(0, 0, 0, 0)
        seq_ltt_hbox.setSpacing(10)

        seq_widget = QtWidgets.QWidget()
        seq_hbox = QtWidgets.QHBoxLayout()
        seq_hbox.setContentsMargins(0, 0, 0, 0)
        seq_hbox.setSpacing(5)
        seq_label = QtWidgets.QLabel("Sequence Length:")
        seq_label.setStyleSheet("font-size:12px;")
        seq_hbox.addWidget(seq_label)
        self.seq_input = QtWidgets.QLineEdit()
        self.seq_input.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 5px;font-size: 12px;")
        self.seq_input.setPlaceholderText("")
        self.seq_input.setFixedWidth(250)
        seq_hbox.addWidget(self.seq_input)
        seq_widget.setLayout(seq_hbox)
        seq_ltt_hbox.addWidget(seq_widget, alignment=Qt.AlignLeft)

        seq_ltt_hbox.addStretch(1)

        ltt_widget = QtWidgets.QWidget()
        ltt_hbox = QtWidgets.QHBoxLayout()
        ltt_hbox.setContentsMargins(0, 0, 0, 0)
        ltt_hbox.setSpacing(5)
        ltt_label = QtWidgets.QLabel("Plot Lineage Through Time (LTT):")
        ltt_label.setStyleSheet("font-size:12px;")
        ltt_hbox.addWidget(ltt_label)
        self.ltt_checkbox = QCheckBox()
        self.ltt_checkbox.setStyleSheet("padding: 5px;")
        ltt_hbox.addWidget(self.ltt_checkbox)
        ltt_widget.setLayout(ltt_hbox)
        seq_ltt_hbox.addWidget(ltt_widget, alignment=Qt.AlignRight)

        seq_ltt_widget.setLayout(seq_ltt_hbox)
        settings_layout.addWidget(seq_ltt_widget)

        output_dir_label = QtWidgets.QLabel("Output Directory:")
        output_dir_label.setStyleSheet("font-size:12px;")
        settings_layout.addWidget(output_dir_label)
        output_dir_widget = QtWidgets.QWidget()
        output_dir_hbox = QtWidgets.QHBoxLayout()
        self.output_dir_input = QtWidgets.QLineEdit()
        self.output_dir_input.setStyleSheet("padding: 5px; border: 1px solid #ddd; border-radius: 5px;font-size: 12px;")
        output_dir_hbox.addWidget(self.output_dir_input)
        output_dir_button = QtWidgets.QPushButton("...")
        output_dir_button.setFixedWidth(40)
        output_dir_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00008B;
            }
        """)
        output_dir_button.clicked.connect(self.select_output_dir)
        output_dir_hbox.addWidget(output_dir_button)
        output_dir_widget.setLayout(output_dir_hbox)
        settings_layout.addWidget(output_dir_widget)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        status_group = QtWidgets.QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        status_layout = QtWidgets.QVBoxLayout()
        self.status_output = QtWidgets.QTextEdit()
        self.status_output.setReadOnly(True)
        self.status_output.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            font-size: 12px;
        """)
        status_layout.addWidget(self.status_output)
        # Add progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setVisible(False)  # Hidden by default
        status_layout.addWidget(self.progress_bar)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group, stretch=1)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        self.run_button = QtWidgets.QPushButton("Run")
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
                background-color: #00008B;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.run_button.clicked.connect(self.run_analysis)
        button_layout.addWidget(self.run_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        status_bar = QtWidgets.QStatusBar()
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
            QProgressBar {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                height: 10px;
            }
        """)