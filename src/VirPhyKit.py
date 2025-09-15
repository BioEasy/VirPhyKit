import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QPushButton, QWidget, QLineEdit, QMenu, QLabel, QTabWidget, QTextEdit, QStatusBar,
                             QListWidget, QListWidgetItem, QSizePolicy)
import os
import platform
import subprocess
from Rename.layout_rename import RenameSequencesApp
from SeqHarvester.function_SeqHarvester import VirusAnalysisApp
from RRT.layout_rrt import RegionRandomizationTestPlotter
from RSPP.layout_rspp import RootStatePosteriorProbabilityGenerator
from SamplePlot.layout_SamplePlot import PlotModule
from Subsample.layout_subsample import SubsampleApp
from Group.layout_group import GroupModule
from MOT.layout_mot import MigrationPlotter
from MOTP.layout_motp import MigrationOverTimePlotter
from About.layout_about import AboutWindow
from BSP.layout_bsp import BayesianSkylinePlotAPP
from Environment import EnvironmentWindow
from Treetime.layout_treetime import TreeTimeUI
from MakovMJump.layout_mmj import ConfigGenerator
from Treedater.main_treedater import TreeDaterApp
from Quick_guide import open_quick_guide
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VirPhyKit")
        self.resize(900, 630)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        if platform.system() == "Windows":
            original_run = subprocess.run
            def patched_run(*args, **kwargs):
                kwargs.setdefault('creationflags', subprocess.CREATE_NO_WINDOW)
                return original_run(*args, **kwargs)
            subprocess.run = patched_run
        self.function_map = {
            "SeqIDRename": self.open_rename_window,
            "SeqGrouper": self.open_group_window,
            "GeoSubsampler": self.open_subsample_window,
            "SeqHarvester": self.open_seqharvester_window,
            "RRT": self.open_rrt_window,
            "TempMig": self.open_mot_window,
            "RSPP-Viz": self.open_rspp_window,
            "VirSpaceTime": self.open_samplot_window,
            "RTT": lambda: self.add_tab("RTT"),
            "BSP-Viz": self.open_bsp_window,
            # "MOTP": self.open_motp_window,
            "TreeTime-RTT": self.open_treetime_window,
            "TreeDater-LTT": self.open_treedater_window,
            "MatrixMJump": self.open_mmj_window,
            "About": self.open_about_window,
            "Environment": self.open_environment_window,
            "Quick guide": self.open_quick_guide
        }
        self.init_ui()

    def init_ui(self):
        font = QFont("Arial", 12)
        QApplication.setFont(font)
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.setStyleSheet("QStatusBar { font-size: 12px; }")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 5, 0, 5)
        top_layout.setSpacing(3)
        button_style = """
            QPushButton { 
                background-color: transparent; 
                color: #000000; 
                border-radius: 5px; 
                padding: 6px 1px; 
                font-size: 14px; 
                font-weight: normal; 
                border: none; 
                outline: none; 
                max-width: 80px
            }
            QPushButton:hover { 
                background-color: #C0C0C0; 
                color: #FFFFFF; 
            }
            QPushButton::menu-indicator { 
                image: none; 
            }
        """

        underlined_S = "S\u0332"
        self.sample_button = QPushButton(f"{underlined_S}ample")
        self.sample_button.setStyleSheet(button_style)
        self.sample_button.setFlat(True)
        self.sample_menu = QMenu(self)
        self._style_menu(self.sample_menu)
        sample_actions = ["VirSpaceTime",
                          "SeqHarvester",
                          "SeqIDRename",
                          "SeqGrouper"]
        for action in sample_actions:
            self.sample_menu.addAction(action, self.function_map[action])
        self.sample_button.setMenu(self.sample_menu)
        top_layout.addWidget(self.sample_button)

        underlined_A = "A\u0332"
        self.analysis_button = QPushButton(f"{underlined_A}nalysis")
        self.analysis_button.setStyleSheet(button_style)
        self.analysis_button.setFlat(True)
        self.analysis_menu = QMenu(self)
        self._style_menu(self.analysis_menu)
        analysis_actions = ["RRT", "TempMig", "GeoSubsampler"]
        for action in analysis_actions:
            self.analysis_menu.addAction(action, self.function_map[action])
        self.analysis_button.setMenu(self.analysis_menu)
        top_layout.addWidget(self.analysis_button)

        underlined_P = "P\u0332"
        self.plot_button = QPushButton(f"{underlined_P}lot")
        self.plot_button.setStyleSheet(button_style)
        self.plot_button.setFlat(True)
        self.plot_menu = QMenu(self)
        self._style_menu(self.plot_menu)
        plot_actions = ["RSPP-Viz", "BSP-Viz"]
        for action in plot_actions:
            self.plot_menu.addAction(action, self.function_map[action])
        self.plot_button.setMenu(self.plot_menu)
        top_layout.addWidget(self.plot_button)

        underlined_D = "D\u0332"
        self.dating_button = QPushButton(f"{underlined_D}ating")
        self.dating_button.setStyleSheet(button_style)
        self.dating_button.setFlat(True)

        self.dating_menu = QMenu(self)
        self._style_menu(self.dating_menu)
        dating_actions = ["TreeTime-RTT", "TreeDater-LTT"]
        for action in dating_actions:
            self.dating_menu.addAction(action, self.function_map[action])
        self.dating_button.setMenu(self.dating_menu)
        top_layout.addWidget(self.dating_button)

  
        underlined_M = "M\u0332"
        self.misc_button = QPushButton(f"{underlined_M}isc")
        self.misc_button.setStyleSheet(button_style)
        self.misc_button.setFlat(True)
        self.misc_menu = QMenu(self)
        self._style_menu(self.misc_menu)
        misc_actions = ["MatrixMJump"]
        for action in misc_actions:
            self.misc_menu.addAction(action, self.function_map[action])
        self.misc_button.setMenu(self.misc_menu)
        top_layout.addWidget(self.misc_button)

    
        underlined_O = "O\u0332"
        self.option_button = QPushButton(f"{underlined_O}ption")
        self.option_button.setStyleSheet(button_style)
        self.option_button.setFlat(True)
        self.option_menu = QMenu(self)
        self._style_menu(self.option_menu)
        option_actions = ["Environment"]
        for action in option_actions:
            self.option_menu.addAction(action, self.function_map[action])
        self.option_button.setMenu(self.option_menu)
        top_layout.addWidget(self.option_button)

        underlined_H = "H\u0332"
        self.help_button = QPushButton(f"{underlined_H}elp")
        self.help_button.setStyleSheet(button_style)
        self.help_button.setFlat(True)
        self.help_menu = QMenu(self)
        self._style_menu(self.help_menu)
        help_actions = ["About", "Quick guide"]
        for action in help_actions:
            self.help_menu.addAction(action, self.function_map[action])
        self.help_button.setMenu(self.help_menu)
        top_layout.addWidget(self.help_button)
        top_layout.addStretch()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setStyleSheet("""
            padding: 3px;
            border: 1px solid #ddd;
            border-radius: 5px;
            min-width: 80px;
            font-size: 12px;
        """)

        self.search_box.textChanged.connect(self.show_search_dropdown)
        top_layout.addWidget(self.search_box) 


        self.search_button = QPushButton("➔")
        self.search_button.setStyleSheet("""
            background-color: #1E90FF;
            color: white;
            border-radius: 5px;
            padding: 3px 5px;
            font-size: 14px;
            font-weight: bold;
            border: none;
            outline: none;
        """)
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setFixedWidth(30)  
        top_layout.addWidget(self.search_button)

        self.search_dropdown = QListWidget(self)
        self.search_dropdown.setStyleSheet("""
            QListWidget { font-size: 12px; border: 1px solid #ddd; border-radius: 5px; background-color: #ffffff; }
            QListWidget::item { padding: 8px; }
            QListWidget::item:hover { background-color: #e0e0e0; }
            QListWidget::item:selected { background-color: #2196F3; color: white; }
        """)
        self.search_dropdown.hide()
        self.search_dropdown.itemClicked.connect(self.on_dropdown_item_clicked)
        self.search_dropdown.setMaximumHeight(200)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setStyleSheet("""
                QTabWidget::pane { border: none; background-color: #ffffff; }
                QTabBar::tab { 
                    background-color: #f0f0f0; 
                    padding: 8px 15px; 
                    border-radius: 5px; 
                    margin-right: 5px; 
                    font-size: 12px;
                }
                QTabBar::tab:hover { background-color: #e0e0e0; }
                QTabBar::tab:selected { background-color: #2196F3; color: white; }
            """)

        main_layout.addWidget(top_widget)
        main_layout.addWidget(self.tab_widget)

        self.setStyleSheet("QMainWindow { background-color: #ffffff; }")
        self.add_default_tab()

    def _style_menu(self, menu):
        menu.setStyleSheet("""
            QMenu { background-color: #ffffff; border: 1px solid #ddd; border-radius: 5px; padding: 5px; }
            QMenu::item { padding: 8px 20px; font-size: 12px; }
            QMenu::item:selected { background-color: #2196F3; color: white; }
        """)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S:
            self.sample_menu.popup(self.sample_button.mapToGlobal(self.sample_button.rect().bottomLeft()))
        elif event.key() == Qt.Key_A:
            self.analysis_menu.popup(self.analysis_button.mapToGlobal(self.analysis_button.rect().bottomLeft()))
        elif event.key() == Qt.Key_P:
            self.plot_menu.popup(self.plot_button.mapToGlobal(self.plot_button.rect().bottomLeft()))
        elif event.key() == Qt.Key_D:
            self.dating_menu.popup(self.dating_button.mapToGlobal(self.dating_button.rect().bottomLeft()))
        elif event.key() == Qt.Key_O:
            self.option_menu.popup(self.option_button.mapToGlobal(self.option_button.rect().bottomLeft()))
        elif event.key() == Qt.Key_H:
            self.help_menu.popup(self.help_button.mapToGlobal(self.help_button.rect().bottomLeft()))
        elif event.key() == Qt.Key_Return and self.search_box.hasFocus():
            self.perform_search()
        elif event.key() == Qt.Key_Down and self.search_box.hasFocus() and self.search_dropdown.isVisible():
            self.search_dropdown.setFocus()
            self.search_dropdown.setCurrentRow(0)
        else:
            super().keyPressEvent(event)

    def add_tab(self, name):
        for index in range(self.tab_widget.count()):
            if self.tab_widget.tabText(index) == name:
                self.tab_widget.setCurrentIndex(index)
                return
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        layout.addWidget(QLabel(f"This is the {name} tab"))
        self.tab_widget.addTab(new_tab, name)
        self.tab_widget.setCurrentWidget(new_tab)

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

    def show_search_dropdown(self, text):
        text = text.strip().lower()
        if not text:
            self.search_dropdown.hide()
            return

        matches = [name for name in self.function_map.keys() if text in name.lower()]
        if not matches:
            self.search_dropdown.hide()
            return

        self.search_dropdown.clear()
        for match in matches:
            self.search_dropdown.addItem(QListWidgetItem(match))

        pos = self.search_box.mapToGlobal(self.search_box.rect().bottomLeft())
        self.search_dropdown.move(self.mapFromGlobal(pos))
        self.search_dropdown.setFixedWidth(self.search_box.width())
        self.adjust_dropdown_size()
        self.search_dropdown.show()

    def adjust_dropdown_size(self):

        item_count = self.search_dropdown.count()
        if item_count > 0:
            item_height = self.search_dropdown.sizeHintForRow(0)
            total_height = min(item_height * item_count + 4, 200)
            self.search_dropdown.setFixedHeight(total_height)

    def on_dropdown_item_clicked(self, item):

        function_name = item.text()
        self.function_map[function_name]()
        self.search_dropdown.hide()
        self.search_box.clear()

    def perform_search(self):

        text = self.search_box.text().strip().lower()

        matches = [name for name in self.function_map.keys() if text in name.lower()]
        if matches:
            self.function_map[matches[0]]()
            self.search_box.clear()
            self.search_dropdown.hide()
            self.statusBar().showMessage(f"Opened: {matches[0]}", 2000)
        else:
            self.statusBar().showMessage(f"No matches found for '{text}'", 2000)


    def open_rename_window(self): self._open_tab("SeqIDRename", RenameSequencesApp)
    def open_seqharvester_window(self): self._open_tab("SeqHarvester", VirusAnalysisApp)
    def open_rspp_window(self): self._open_tab("RSPP-Viz", RootStatePosteriorProbabilityGenerator)
    def open_rrt_window(self): self._open_tab("RRT", RegionRandomizationTestPlotter)
    def open_mot_window(self): self._open_tab("TempMig", MigrationPlotter)
    def open_subsample_window(self): self._open_tab("GeoSubsampler", SubsampleApp)
    def open_group_window(self): self._open_tab("SeqGrouper", GroupModule)
    def open_samplot_window(self): self._open_tab("VirSpaceTime", PlotModule)
    def open_motp_window(self): self._open_tab("MOTP", MigrationOverTimePlotter)
    def open_about_window(self): self._open_tab("About", AboutWindow)
    def open_bsp_window(self):  self._open_tab("BSP-Viz", BayesianSkylinePlotAPP)
    def open_environment_window(self): self._open_tab("Environment", EnvironmentWindow)
    def open_treetime_window(self): self._open_tab("TreeTime-RTT", TreeTimeUI)
    def open_mmj_window(self): self._open_tab("MakovMJump", ConfigGenerator)
    def open_treedater_window(self): self._open_tab("TreeDater-LTT", TreeDaterApp)
    def open_quick_guide(self):
        success, message = open_quick_guide()
        self.statusBar().showMessage(message, 2000)
    def _open_tab(self, name, cls):
        for index in range(self.tab_widget.count()):
            if self.tab_widget.tabText(index) == name:
                self.tab_widget.setCurrentIndex(index)
                return
        tab = cls()
        self.tab_widget.addTab(tab, name)
        self.tab_widget.setCurrentWidget(tab)
    def add_default_tab(self):
        default_tab = QWidget()
        layout = QVBoxLayout(default_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        welcome_widget = QWidget()
        welcome_layout = QHBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(5)
        quote_widget = QWidget()
        quote_layout = QVBoxLayout(quote_widget)
        quote_layout.setContentsMargins(20, 20, 20, 20)
        quote = QTextEdit()
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "icon.ico")
        html_content = (
            f"<div style='line-height: 1.2; width: 100%;'>"
            "<div style='text-align: center; margin-bottom: 15px;'>"
            "<span style='font-size: 22px; font-weight: bold;'>VirPhyKit: an integrated toolkit for viral phylogeographic analysis 1.0</span>"
            "</div>"
            "<p style='font-size: 0.7em; text-indent: 2em; margin: 0; line-height: 1.5; display: block;'>&nbsp;&nbsp;&nbsp;&nbsp;A software suite for viral phylogeographic analysis, integrating tools for sequence curation, spatiotemporal subsampling, migration pattern reconstruction and molecular dating.<br><br></span>"
            "</div>"
            "<table style='border: none; border-collapse: collapse; width: 100%;'>"
            "<tr>"
            f"<td style='vertical-align: top; padding: 0; border: none;'><img src='{icon_path}' width='250' height='250'></td>"
            "<td style='vertical-align: top; padding-left: 20px; padding-top: 10px; border: none; font-size: 0.8em;'><strong><br><br>Home Page:</strong> <a href='https://github.com/BioEasy/VirPhyKit' target='_blank' style='color: #0066cc; text-decoration: underline;'>https://github.com/BioEasy/VirPhyKit</a><br><br><br><br><br>"
            "<strong>Citation:</strong> Yin et al., 2025. VirPhyKit: an integrated toolkit for viral phylogeographic analysis."
            "</td>"
            "</tr>"
            "</table>"
            "</div>"
        )
        quote.setHtml(html_content)
        quote.setReadOnly(True)
        quote.setStyleSheet("""
         background-color: #ffffff;
         border: 1px solid #ccc;
         border-radius: 5px;
         color: #333;
         text-align: center;
         padding: 20px;
         font-weight: normal;
         """)
        # font = QFont("Arial", 14)
        # quote.setFont(font)
        quote.setSizePolicy(quote.sizePolicy().Expanding, quote.sizePolicy().Expanding)
        quote_layout.addWidget(quote)
        quote_widget.setLayout(quote_layout)
        layout.addWidget(quote_widget, stretch=1)
        default_tab.setLayout(layout)
        self.tab_widget.addTab(default_tab, "Welcome")
        self.tab_widget.setCurrentWidget(default_tab)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())