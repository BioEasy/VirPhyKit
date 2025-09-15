import csv
import os
import sys
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QTableWidget
from PyQt5.QtCore import QThread, pyqtSignal
from Bio import SeqIO
from Bio import Entrez
from datetime import datetime
from io import StringIO
import time
from matplotlib import pyplot as plt


class DownloadWorker(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, accession_list, parent=None):
        super().__init__(parent)
        self.accession_list = accession_list
        self.batch_size = 500
        Entrez.email = "your_email@example.com"

    def run(self):
        data = []
        total = len(self.accession_list)
        total_batches = (total + self.batch_size - 1) // self.batch_size

        for batch_idx, start in enumerate(range(0, total, self.batch_size)):
            batch = self.accession_list[start:start + self.batch_size]
            batch_num = batch_idx + 1
            progress_percent = int((batch_idx + 1) * 100 / total_batches)

            for attempt in range(3, 0, -1):
                try:
                    self.progress.emit(f"Parsing information...{batch_num}/{total_batches}", progress_percent)
                    with Entrez.efetch(db="nucleotide",
                                       id=",".join(batch),
                                       rettype="gb",
                                       retmode="text",
                                       timeout=30) as handle:
                        genbank_data = handle.read()

                    if not genbank_data.strip():
                        self.progress.emit(f"No data for batch {batch_num}", progress_percent)
                        break

                    with StringIO(genbank_data) as genbank_handle:
                        records = list(SeqIO.parse(genbank_handle, "genbank"))

                    if not records:
                        self.progress.emit(f"No records parsed for batch {batch_num}", progress_percent)
                        break

                    batch_data = [parse_single_record(record) for record in records]
                    data.extend(batch_data)
                    break

                except Exception as e:
                    if attempt > 1:
                        time.sleep(5)
                    else:
                        self.error.emit(f"Failed batch {batch_num} after 3 attempts: {str(e)}")
                        break

                time.sleep(1)

        self.finished.emit(data)


def parse_single_record(record):
    entry = {
        "Isolate": "N/A",
        "ID": record.id,
        "Organism": record.annotations.get("organism", "N/A"),
        "Length": len(record.seq),
        "Host": "N/A",
        "Geo Location": "N/A",
        "Collection Date": "N/A"
    }
    for feature in record.features:
        if feature.type == "source":
            qualifiers = feature.qualifiers
            if "isolate" in qualifiers:
                entry["Isolate"] = qualifiers["isolate"][0]
            if "host" in qualifiers:
                entry["Host"] = qualifiers["host"][0]
            if "geo_loc_name" in qualifiers:
                geo_loc = qualifiers["geo_loc_name"][0]
                entry["Geo Location"] = geo_loc.split(":")[0].strip() if ":" in geo_loc else geo_loc
            elif "country" in qualifiers:
                geo_loc = qualifiers["country"][0]
                entry["Geo Location"] = geo_loc.split(":")[0].strip() if ":" in geo_loc else geo_loc
            if "collection_date" in qualifiers:
                date_str = qualifiers["collection_date"][0]
                for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%Y"):
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        entry["Collection Date"] = date_obj.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        entry["Collection Date"] = date_str
    return entry


class ProcessData:
    @staticmethod
    def select_seq_file(window):
        file_name, _ = QFileDialog.getOpenFileName(window, "Select Sequence File", "",
                                                   "GenBank Files (*.gb);;All Files (*)")
        if file_name:
            window.seq_dir_input.setText(file_name)
            window.seq_file_path = file_name
            window.accession_dir_input.clear()
            window.accession_file_path = None
            window.show_button.setEnabled(True)
            window.statusBar().showMessage(f"Loaded sequence file: {file_name}", 5000)

    @staticmethod
    def select_accession_file(window):
        file_name, _ = QFileDialog.getOpenFileName(window, "Select Accession File", "",
                                                   "Text Files (*.txt);;All Files (*)")
        if file_name:
            window.accession_dir_input.setText(file_name)
            window.accession_file_path = file_name
            window.seq_dir_input.clear()
            window.seq_file_path = None
            window.show_button.setEnabled(True)
            window.statusBar().showMessage(f"Loaded accession file: {file_name}", 5000)

    @staticmethod
    def select_region_file(window):
        file_name, _ = QFileDialog.getOpenFileName(window, "Select Grouping Table", "",
                                                   "Text Files (*.txt);;All Files (*)")
        if file_name:
            window.region_dir_input.setText(file_name)
            window.region_file_path = file_name
            window.statusBar().showMessage(f"Loaded region comparison table: {file_name}", 5000)
            window.preview_button.setEnabled(True)

    @staticmethod
    def parse_genbank(window):
        if window.seq_file_path:
            window.statusBar().showMessage("Parsing local GenBank file...", 5000)
            window.progress_bar.setVisible(True)
            window.progress_bar.setValue(0)
            data = []
            try:
                total_records = sum(1 for _ in SeqIO.parse(window.seq_file_path, "genbank"))
                with open(window.seq_file_path, 'r', encoding='utf-8') as f:
                    records = SeqIO.parse(f, "genbank")
                    for i, record in enumerate(records):
                        entry = parse_single_record(record)
                        data.append(entry)
                        progress = int((i + 1) * 100 / total_records)
                        window.progress_bar.setValue(progress)
                window.statusBar().showMessage("Local file parsed successfully.", 5000)
                window.progress_bar.setVisible(False)
                return data
            except Exception as e:
                window.statusBar().showMessage(f"Error parsing local file: {str(e)}", 10000)
                window.progress_bar.setVisible(False)
                return []
        elif window.accession_file_path:
            with open(window.accession_file_path, 'r', encoding='utf-8') as f:
                accession_list = [line.strip() for line in f if line.strip()]
            if accession_list:
                window.worker = DownloadWorker(accession_list)
                window.worker.progress.connect(
                    lambda msg, pct: window.statusBar().showMessage(msg, 5000) or window.progress_bar.setValue(pct))
                window.worker.finished.connect(lambda data: ProcessData.on_download_finished(window, data))
                window.worker.error.connect(lambda msg: window.statusBar().showMessage(msg, 10000))
                window.progress_bar.setVisible(True)
                window.show_button.setEnabled(False)
                window.worker.start()
            return None

    @staticmethod
    def on_download_finished(window, data):
        window.data = data
        ProcessData.show_table_data(window)
        window.progress_bar.setVisible(False)
        window.show_button.setEnabled(True)
        window.worker = None

    @staticmethod
    def show_table(window):
        window.data = ProcessData.parse_genbank(window)
        if window.data is not None:
            ProcessData.show_table_data(window)

    @staticmethod
    def show_table_data(window):
        if not window.data:
            window.statusBar().showMessage("No data to display.", 5000)
            return
        try:
            has_groups = any("Group" in record for record in window.data)
            column_count = 8 if has_groups else 7
            window.table.setColumnCount(column_count)
            headers = ["Isolate", "ID", "Organism", "Length", "Host", "Geo Location", "Collection Date"]
            if has_groups:
                headers.append("Group")
            window.table.setHorizontalHeaderLabels(headers)

            window.table.setRowCount(len(window.data))
            for row, record in enumerate(window.data):
                window.table.setItem(row, 0, QTableWidgetItem(str(record.get("Isolate", "N/A"))))
                window.table.setItem(row, 1, QTableWidgetItem(str(record.get("ID", "N/A"))))
                window.table.setItem(row, 2, QTableWidgetItem(str(record.get("Organism", "N/A"))))
                window.table.setItem(row, 3, QTableWidgetItem(str(record.get("Length", "0"))))
                window.table.setItem(row, 4, QTableWidgetItem(str(record.get("Host", "N/A"))))
                window.table.setItem(row, 5, QTableWidgetItem(str(record.get("Geo Location", "N/A"))))
                window.table.setItem(row, 6, QTableWidgetItem(str(record.get("Collection Date", "N/A"))))
                if has_groups:
                    group = str(record.get("Group", "N/A"))
                    window.table.setItem(row, 7, QTableWidgetItem(group))

            window.table.setColumnWidth(0, 100)
            window.table.setColumnWidth(1, 100)
            window.table.setColumnWidth(2, 150)
            window.table.setColumnWidth(3, 80)
            window.table.setColumnWidth(4, 150)
            window.table.setColumnWidth(5, 100)
            window.table.setColumnWidth(6, 100)
            if has_groups:
                window.table.setColumnWidth(7, 100)
            window.table.setEditTriggers(QTableWidget.DoubleClicked)
            window.save_button.setEnabled(True)
            window.statusBar().showMessage("Table data loaded successfully.", 5000)
        except Exception as e:
            window.statusBar().showMessage(f"Error loading table data: {str(e)}", 10000)

    @staticmethod
    def preview_groups(window, column_index=-1):
        if window.table.rowCount() == 0:
            window.statusBar().showMessage("Please load data first.", 5000)
            return
        use_mapping = window.use_mapping_checkbox.isChecked()
        print(f"Received column_index: {column_index}")
        try:
            if column_index < 0 or column_index >= window.table.columnCount():
                group_col = window.last_group_column if hasattr(window,
                                                                'last_group_column') and window.last_group_column >= 0 else 5
                column_name = window.table.horizontalHeaderItem(group_col).text() if window.table.horizontalHeaderItem(
                    group_col) else f"Column {group_col}"
            else:
                group_col = column_index
                column_name = window.table.horizontalHeaderItem(group_col).text() if window.table.horizontalHeaderItem(
                    group_col) else f"Column {group_col}"
            print(f"Grouping by column: {column_name} (index: {group_col})")
        except Exception as e:
            window.statusBar().showMessage(f"Error determining grouping column: {str(e)}", 10000)
            return
        group_map = {}
        unmatched = set()

        if use_mapping:
            region_file_path = getattr(window, 'region_file_path', None)
            print(f"region_file_path: {region_file_path}")
            try:
                if not region_file_path or not os.path.exists(region_file_path):
                    if getattr(sys, 'frozen', False):
                        base_path = sys._MEIPASS
                    else:
                        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    region_file_path = os.path.join(base_path, "Mapping.txt")
                    print(f"Default mapping file path: {region_file_path}")
                    if not os.path.exists(region_file_path):
                        window.statusBar().showMessage(f"Default Mapping file not found at: {region_file_path}", 10000)
                        return
                    window.statusBar().showMessage(f"Using default Mapping.txt from: {region_file_path}", 5000)
                else:
                    window.statusBar().showMessage(f"Using custom mapping table: {region_file_path}", 5000)
                with open(region_file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                group, value = line.strip().split('\t')
                                group_map[value.lower()] = group
                            except ValueError:
                                window.statusBar().showMessage(
                                    f"Invalid format in mapping table: each line must contain group and value separated by tab",
                                    10000)
                                return
            except Exception as e:
                window.statusBar().showMessage(f"Error reading mapping table at {region_file_path}: {str(e)}", 10000)
                return
        else:
            window.statusBar().showMessage(f"Direct grouping by {column_name} (no mapping table used)", 5000)
        group_counts = {}
        group_col_name = "Group"
        existing_group_col = 7 if window.table.columnCount() == 8 else -1

        try:
            for row in range(window.table.rowCount()):
                item = window.table.item(row, group_col)
                value = item.text() if item else "N/A"

                if use_mapping and value != "N/A":
                    val_lower = value.lower()
                    if val_lower == "united states":
                        val_lower = "usa"
                    group = group_map.get(val_lower, "Unknown")
                    if group == "Unknown":
                        unmatched.add(value)
                else:
                    group = value if value != "N/A" else "N/A"

                if row < len(window.data):
                    window.data[row][column_name] = value
                    window.data[row]["Group"] = group
                else:
                    window.data.append({
                        "Isolate": window.table.item(row, 0).text() if window.table.item(row, 0) else "N/A",
                        "ID": window.table.item(row, 1).text() if window.table.item(row, 1) else "N/A",
                        "Organism": window.table.item(row, 2).text() if window.table.item(row, 2) else "N/A",
                        "Length": window.table.item(row, 3).text() if window.table.item(row, 3) else "0",
                        "Host": window.table.item(row, 4).text() if window.table.item(row, 4) else "N/A",
                        "Geo Location": window.table.item(row, 5).text() if window.table.item(row, 5) else "N/A",
                        "Collection Date": window.table.item(row, 6).text() if window.table.item(row, 6) else "N/A",
                        "Group": group
                    })

                if existing_group_col == -1:
                    window.table.setColumnCount(8)
                    window.table.setHorizontalHeaderLabels(
                        ["Isolate", "ID", "Organism", "Length", "Host", "Geo Location", "Collection Date", "Group"]
                    )
                    window.table.setColumnWidth(7, 100)
                    existing_group_col = 7
                window.table.setItem(row, existing_group_col, QTableWidgetItem(group))

                if group != "N/A":
                    group_counts[group] = group_counts.get(group, 0) + 1
        except Exception as e:
            window.statusBar().showMessage(f"Error processing groups: {str(e)}", 10000)
            return

        if use_mapping and unmatched:
            print("Unmatched values:", unmatched)
        if not group_counts:
            window.statusBar().showMessage(f"No valid values found for {column_name} grouping.", 5000)
            return
        try:
            labels = list(group_counts.keys())
            sizes = list(group_counts.values())
            total = sum(sizes)

            def autopct_format(values):
                def my_format(pct):
                    absolute = int(round(pct * total / 100.0))
                    return f"{pct:.1f}%\n({absolute})"

                return my_format

            plt.figure(figsize=(8, 8))
            plt.pie(sizes, labels=labels, autopct=autopct_format(sizes), startangle=90, textprops={'fontsize': 10})
            plt.axis('equal')
            if use_mapping:
                plt.title(f"Group of Sequences by {column_name} (Using Mapping Table)")
            else:
                plt.title(f"Group of Sequences by {column_name} (Direct Grouping)")

            plt.show()
        except Exception as e:
            window.statusBar().showMessage(f"Error generating pie chart: {str(e)}", 10000)
            return

    @staticmethod
    def save_to_csv(window):
        if window.table.rowCount() > 0:
            file_path, _ = QFileDialog.getSaveFileName(window, "Save as CSV", "", "CSV Files (*.csv)")
            if file_path:
                try:
                    with open(file_path, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        headers = ["Isolate", "ID", "Organism", "Length", "Host", "Geo Location", "Collection Date"]
                        if window.table.columnCount() == 8:
                            headers.append("Group")
                        writer.writerow(headers)
                        for row in range(window.table.rowCount()):
                            row_data = [window.table.item(row, col).text() if window.table.item(row, col) else "N/A" for
                                        col in range(window.table.columnCount())]
                            writer.writerow(row_data)
                    window.statusBar().showMessage(f"Saved to {file_path}", 5000)
                except Exception as e:
                    window.statusBar().showMessage(f"Error saving to CSV: {str(e)}", 10000)


process_data = ProcessData()