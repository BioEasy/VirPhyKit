import os
from PyQt5.QtWidgets import (QTableWidgetItem, QMessageBox, QFileDialog, QComboBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from Bio import Entrez, SeqIO
import io
import re
from SeqHarvester.layout_SeqHarvester import VirusAnalysisUI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
Entrez.email = "your.email@example.com"

class CheckableComboBox(QComboBox):
    def __init__(self):
        super().__init__()
        self.setModel(QStandardItemModel(self))
        self.view().pressed.connect(self.handle_item_pressed)
        self._changed = False
        self.setEditable(False)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.view().setFont(font)
        self.setStyleSheet("""
            QComboBox {
                padding: 3px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f5f5f5;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #2196F3;
                selection-color: white;
            }
        """)

    def addItem(self, text, normalized_text=None):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        if normalized_text:
            item.setData(normalized_text, Qt.UserRole)
        font = QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.model().appendRow(item)

    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self._changed = True
        selected = self.selected_items()
        if selected:
            display_text = ", ".join([self.model().item(i).text() for i in range(self.model().rowCount()) if
                                      self.model().item(i).checkState() == Qt.Checked])
            self.setCurrentText(display_text)
            font = QFont()
            font.setPointSize(10)
            self.setFont(font)
        else:
            self.setCurrentText("Select types...")
            font = QFont()
            font.setPointSize(10)
            self.setFont(font)

    def selected_items(self):
        selected = []
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.checkState() == Qt.Checked:
                normalized_typ = item.data(Qt.UserRole) or item.text().strip().lower()
                selected.append(normalized_typ)
        return selected


class DownloadWorker(QThread):
    progress_update = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    def __init__(self, selected_types=None, type_to_ids=None, accession_ids=None, save_path=None):
        super().__init__()
        self.selected_types = [typ.strip().lower() for typ in (selected_types or [])]  # Normalize selected types
        self.type_to_ids = type_to_ids or {}
        self.accession_ids = accession_ids
        self.save_path = save_path
    def run(self):
        try:
            if self.accession_ids:
                self.progress_update.emit(f"Downloading {len(self.accession_ids)} sequences...")
                # Fetch sequences
                handle = Entrez.efetch(db="nucleotide", id=",".join(self.accession_ids), rettype="fasta",
                                       retmode="text")
                sequences = list(SeqIO.parse(handle, "fasta"))
                # Save sequences to FASTA file
                with open(os.path.join(self.save_path, "accession_sequences.fasta"), "w") as f:
                    SeqIO.write(sequences, f, "fasta")
                # Save accession IDs to text file
                accession_ids = [seq.id.split('.')[0] for seq in sequences]  # Extract accession IDs without version
                with open(os.path.join(self.save_path, "accession_ids.txt"), "w") as f:
                    f.write("\n".join(sorted(set(accession_ids))))
                self.progress_update.emit("Accession IDs saved to accession_ids.txt")
            else:
                logging.info(f"Selected types for download: {self.selected_types}")
                logging.info(f"Available type_to_ids keys: {list(self.type_to_ids.keys())}")
        
                all_selected_ids = []
                for typ in self.selected_types:
                    ids = self.type_to_ids.get(typ, [])
                    if not ids:
                        self.progress_update.emit(f"Skipping {typ}: No sequences found.")
                        logging.warning(f"No sequences found for type '{typ}'")
                        continue
                    self.progress_update.emit(f"Downloading {typ} ({len(ids)} sequences)...")
       
                    handle = Entrez.efetch(db="nucleotide", id=",".join(ids), rettype="fasta", retmode="text")
                    sequences = list(SeqIO.parse(handle, "fasta"))
                    with open(os.path.join(self.save_path, f"{typ}.fasta"), "w") as f:
                        SeqIO.write(sequences, f, "fasta")
            
                    type_accession_ids = [seq.id.split('.')[0] for seq in
                                          sequences] 
                    all_selected_ids.extend(type_accession_ids)
                    self.progress_update.emit(f"Saved {len(type_accession_ids)} accession IDs for {typ}")
   
                if all_selected_ids:
                    with open(os.path.join(self.save_path, "accession_numbers.txt"), "w") as f:
                        f.write("\n".join(sorted(set(all_selected_ids))))
                    self.progress_update.emit("Accession IDs for selected types saved to accession_numbers.txt")

            self.progress_update.emit("<span style='color: green'>All downloads completed successfully.</span>")
            self.finished.emit()
        except Exception as e:
            logging.error(f"Download failed: {str(e)}")
            self.error.emit(f"Download failed: {str(e)}")


class AnalysisWorker(QThread):
    progress_update = pyqtSignal(int, int)
    table_update = pyqtSignal(tuple)
    status_update = pyqtSignal(str)

    def __init__(self, virus_name):
        super().__init__()
        self.virus_name = virus_name
        self.sequence_ids = []
        self.type_to_ids = {}

    def run(self):
        self.status_update.emit("Querying...")

        taxon_id, _ = self.get_taxon_info()
        if not taxon_id:
            self.status_update.emit("<span style='color: red;'>Taxonomy query failed</span>")
            return

        self.sequence_ids = self.search_sequences()
        if not self.sequence_ids:
            self.status_update.emit("<span style='color: red;'>No related sequences found</span>")
            self.table_update.emit(([["no data", 0, "0%", "Unavailable sequence"]], {}, {}))
            return

        total = len(self.sequence_ids)
        records = self.fetch_records(total)
        table_data, similar_groups = self.parse_records(records)
        self.table_update.emit((table_data, similar_groups, self.type_to_ids))

        missing_count = next((item[1] for item in table_data if item[0] == "missing"), 0)
        self.status_update.emit(
            f"Data retrieval completed, {missing_count} sequences found to have missing information.")

    def get_taxon_info(self):
        try:
            handle = Entrez.esearch(db="taxonomy", term=self.virus_name)
            record = Entrez.read(handle)
            taxon_id = record["IdList"][0] if record["IdList"] else None
            return taxon_id, None
        except Exception as e:
            logging.error(f"Taxonomy query failed: {str(e)}")
            self.status_update.emit(f"<span style='color: red;'>Taxonomy query failed: {str(e)}</span>")
            return None, None

    def search_sequences(self):
        try:
            ids = []
            retmax = 10000
            retstart = 0
            while True:
                handle = Entrez.esearch(db="nucleotide",
                                        term=f"{self.virus_name}[Organism] OR {self.virus_name}[Title]",
                                        retmax=retmax, retstart=retstart)
                record = Entrez.read(handle)
                ids.extend(record["IdList"])
                retstart += retmax
                if retstart >= int(record["Count"]):
                    break
            logging.info(f"Total number of sequences retrieved: {len(ids)}")
            return ids
        except Exception as e:
            logging.error(f"Sequence retrieval failure: {str(e)}")
            self.status_update.emit(f"<span style='color: red;'>Sequence retrieval failure: {str(e)}</span>")
            return []

    def fetch_records(self, total):
        records = []
        batch_size = 500
        for i in range(0, total, batch_size):
            batch_ids = self.sequence_ids[i:i + batch_size]
            try:
                handle = Entrez.efetch(db="nucleotide", id=",".join(batch_ids),
                                       rettype="gb", retmode="text")
                batch_records = handle.read().split("\n//\n")
                records.extend(batch_records)
                self.progress_update.emit(min(i + batch_size, total), total)
            except Exception as e:
                logging.error(f"Batch search failure: {str(e)}")
                self.status_update.emit(f"<span style='color: red;'>Batch search failure: {str(e)}</span>")
        return [r + "\n//\n" if not r.endswith("\n//\n") else r for r in records if r.strip()]

    def normalize_name(self, name):
        if not name:
            return None
        name = name.lower().strip()
        name = re.sub(r'\([^()]*\)', '', name).strip()
        name = re.sub(r'\b(protein|viral|genome-linked|with|activity|gene)\b', '', name).strip()
        match = re.match(r'^(?:[a-z]+-)?[a-z0-9]+', name)
        if match:
            return match.group(0).title()
        words = name.split()
        return words[0].title() if words else name.title()

    def extract_from_definition(self, definition):
        definition = definition.lower()
        match = re.search(r'(\w+(?:-\w+)?)\s+gene', definition)
        if match:
            gene_name = match.group(1)
            return self.normalize_name(gene_name)
        return None

    def parse_records(self, records):
        stats = {"Complete genome": 0, "missing": 0, "CP gene": 0}
        cp_keywords = ["capsid protein", "coat protein", "cp protein", "cp", "CP", "Cp", "coat protein-like"]
        descriptions = {}
        similar_groups = {}
        self.type_to_ids = {}

        for idx, record_str in enumerate(records):
            try:
                record = SeqIO.read(io.StringIO(record_str), "genbank")
                definition = record.description.lower()
                cds_features = [f for f in record.features if f.type == "CDS"]
                cds_count = len(cds_features)
                seq_id = self.sequence_ids[idx]

                def_key = self.extract_from_definition(definition) or "unknown"

                is_complete = ("complete genome" in definition or
                               "complete sequence" in definition or
                               "whole genome" in definition) and "partial" not in definition
                if is_complete:
                    stats["Complete genome"] += 1
                    descriptions["Complete genome"] = definition
                    self.type_to_ids.setdefault("Complete genome".lower(), []).append(seq_id)
                    continue

                if cds_count == 0:
                    stats["missing"] += 1
                    descriptions["missing"] = definition
                    self.type_to_ids.setdefault("missing".lower(), []).append(seq_id)
                    continue

                found_segment = False
                for feature in cds_features:
                    gene = feature.qualifiers.get("gene", [""])[0]
                    product = feature.qualifiers.get("product", [""])[0]
                    if gene:
                        key = self.normalize_name(gene)
                    else:
                        key = self.normalize_name(product)

                    if not key:
                        key = def_key

                    found_segment = True
                    desc = product or gene or definition

                    is_cp_in_def = any(kw in definition for kw in cp_keywords) or def_key.lower() == "cp"
                    is_cp_in_cds = any(kw in product.lower() for kw in cp_keywords) or key.lower() == "cp"
                    if is_cp_in_def and is_cp_in_cds:
                        stats["CP gene"] += 1
                        descriptions["CP gene"] = desc
                        self.type_to_ids.setdefault("CP gene".lower(), []).append(seq_id)
                    else:
                        stats[key] = stats.get(key, 0) + 1
                        descriptions[key] = desc
                        self.type_to_ids.setdefault(key.lower(), []).append(seq_id)

                        desc_key = desc.lower()
                        if desc_key not in similar_groups:
                            similar_groups[desc_key] = []
                        similar_groups[desc_key].append(key)

                if not found_segment:
                    key = def_key
                    desc = definition
                    is_cp_in_def = any(kw in definition for kw in cp_keywords) or key.lower() == "cp"
                    if is_cp_in_def:
                        stats["CP gene"] += 1
                        descriptions["CP gene"] = desc
                        self.type_to_ids.setdefault("CP gene".lower(), []).append(seq_id)
                    else:
                        stats[key] = stats.get(key, 0) + 1
                        descriptions[key] = desc
                        self.type_to_ids.setdefault(key.lower(), []).append(seq_id)

                        desc_key = desc.lower()
                        if desc_key not in similar_groups:
                            similar_groups[desc_key] = []
                        similar_groups[desc_key].append(key)

            except Exception as e:
                logging.error(f"Parsing record failure: {str(e)}")
                self.status_update.emit(f"<span style='color: red;'>Parsing record failure: {str(e)}</span>")

        total = sum(stats.values())
        if total == 0:
            return [["no data", 0, "0%", "Unavailable sequence"]], {}
        table_data = [
            [k, v, f"{v / total * 100:.1f}%", descriptions.get(k, k)]
            for k, v in stats.items() if v > 0
        ]
        return sorted(table_data, key=lambda x: x[1], reverse=True), similar_groups


class VirusAnalysisApp(VirusAnalysisUI):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.type_to_ids = {}
        self.accession_ids = []
        self.is_updating_table = False  


        self.download_combo = CheckableComboBox()
        self.combo_layout.insertWidget(1, self.download_combo)
        self.download_combo.setFixedWidth(600)
        self.download_combo.setStyleSheet("padding: 3px; border: 1px solid #ddd; border-radius: 5px;")


        self.result_table.setStyleSheet("QTableWidget { font-size: 12px; } QHeaderView::section { font-size: 12px; }")

        self.setup_connections()

    def normalize_type_name(self, name):
        if not name:
            return ""
        return name.strip().lower()  

    def setup_connections(self):
        self.search_button.clicked.connect(self.start_analysis)
        self.download_button.clicked.connect(self.download_sequences)
        self.browse_button.clicked.connect(self.browse_save_path)
        self.accession_browse_button.clicked.connect(self.browse_accession_file)
        self.result_table.itemChanged.connect(self.handle_table_item_changed)

    def browse_accession_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Accession Numbers File", "", "Text Files (*.txt)")
        if file_path:
            self.accession_input.setText(file_path)
            try:
                with open(file_path, 'r') as f:
                    self.accession_ids = [line.strip() for line in f if line.strip()]
                if not self.accession_ids:
                    self.status_label.append("<span style='color: red;'>Status: Accession file is empty</span>")
                    self.statusBar().showMessage("Error: Accession file is empty", 5000)
                    self.accession_input.clear()
                    self.accession_ids = []
                else:
                    self.status_label.append(f"Status: Loaded {len(self.accession_ids)} accession numbers")
                    self.statusBar().showMessage("Accession file loaded", 5000)
            except Exception as e:
                logging.error(f"Failed to read accession file: {str(e)}")
                self.status_label.append(
                    f"<span style='color: red;'>Status: Failed to read accession file: {str(e)}</span>")
                self.statusBar().showMessage("Error: Failed to read accession file", 5000)
                self.accession_input.clear()
                self.accession_ids = []

    def update_progress(self, current, total):
        self.status_label.append(f"Retrieval progress: {current}/{total}")
        self.progress_label.setText(f"Retrieval progress: {current}/{total}")

    def handle_table_update(self, data_and_similar):
        try:
            table_data, similar_groups, self.type_to_ids = data_and_similar
        except ValueError as e:
            logging.error(f"Unpacking data_and_similar failed: {str(e)}")
            self.status_label.append(f"<span style='color: red;'>Error: Data format error {str(e)}</span>")
            return

        should_merge = False
        similar_count = sum(1 for keys in similar_groups.values() if len(keys) > 1)
        if similar_count > 0:
            try:
                msg_box = QMessageBox()
                msg_box.setWindowTitle('Similar fragments found')
                msg_box.setText(f"Found {similar_count} similar fragments. Combine all into a single type?")
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg_box.setDefaultButton(QMessageBox.No)
                msg_box.setStyleSheet("QMessageBox { font-size: 12px; } QPushButton { font-size: 12px; }")
                reply = msg_box.exec_()
                should_merge = (reply == QMessageBox.Yes)
                logging.info(f"User option: Merge all similar fragments: {should_merge}")
            except Exception as e:
                logging.error(f"Popup processing failed: {str(e)}")
                self.status_label.append(f"<span style='color: red;'>Error: Popup processing failed. {str(e)}</span>")
                return

        if should_merge:
            try:
                new_table_data = []
                processed_keys = set()
                new_type_to_ids = {}
                for row in table_data:
                    typ, num, perc, desc = row
                    base_key = re.sub(r'(k|kda)$', '', typ.lower())
                    if base_key in similar_groups and len(similar_groups[base_key]) > 1:
                        if base_key not in processed_keys:
                            total_num = sum(
                                r[1] for r in table_data if re.sub(r'(k|kda)$', '', r[0].lower()) == base_key)
                            total_perc = f"{total_num / sum(r[1] for r in table_data) * 100:.1f}%"
                            new_table_data.append([base_key, total_num, total_perc, desc])
                            ids = []
                            for k in similar_groups[base_key]:
                                ids.extend(self.type_to_ids.get(k.lower(), []))
                            new_type_to_ids[base_key] = ids
                            processed_keys.add(base_key)
                    elif base_key not in processed_keys:
                        new_table_data.append(row)
                        new_type_to_ids[typ.lower()] = self.type_to_ids.get(typ.lower(), [])
                        processed_keys.add(base_key)
                table_data = new_table_data
                self.type_to_ids = new_type_to_ids
            except Exception as e:
                logging.error(f"Failed to merge table data: {str(e)}")
                self.status_label.append(
                    f"<span style='color: red;'>Error: Failed to merge table data. {str(e)}</span>")
                return

        try:
            self.is_updating_table = True
            self.result_table.setRowCount(len(table_data))
            for row, (typ, num, perc, desc) in enumerate(table_data):
                type_item = QTableWidgetItem(str(typ))
                type_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                self.result_table.setItem(row, 0, type_item)
                number_item = QTableWidgetItem(str(num))
                number_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.result_table.setItem(row, 1, number_item)
                perc_item = QTableWidgetItem(str(perc))
                perc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.result_table.setItem(row, 2, perc_item)
                desc_item = QTableWidgetItem(str(desc))
                desc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.result_table.setItem(row, 3, desc_item)

            self.update_download_combo(table_data)
        except Exception as e:
            logging.error(f"Failed to update table: {str(e)}")
            self.status_label.append(f"<span style='color: red;'>Error: Failed to update table. {str(e)}</span>")
        finally:
            self.is_updating_table = False

    def update_download_combo(self, table_data):
        try:
            self.download_combo.clear()
            if not table_data:
                self.download_combo.addItem("No types available")
                self.download_combo.model().item(0).setEnabled(False)
            else:
                for typ, _, _, _ in table_data:
                    self.download_combo.addItem(typ, self.normalize_type_name(typ))
                logging.info(f"Updated download combo with types: {[typ for typ, _, _, _ in table_data]}")
        except Exception as e:
            logging.error(f"Failed to update download combo: {str(e)}")
            self.status_label.append(
                f"<span style='color: red;'>Error: Failed to update download combo. {str(e)}</span>")

    def handle_table_item_changed(self, item):
        if self.is_updating_table or item.column() != 0:
            return

        try:
            logging.info(f"Table item changed: row={item.row()}, new_text='{item.text()}'")
            new_type = item.text().strip()
            normalized_new_type = self.normalize_type_name(new_type)
            if not new_type:
                logging.warning("Empty type entered")
                self.status_label.append("<span style='color: red'>Error: Type cannot be empty</span>")
                self.statusBar().showMessage("Error: Type cannot be empty", 5000)
                item.setText("")  # Clear invalid input
                return

         
            self.result_table.itemChanged.disconnect()

    
            table_data = []
            old_type = None
            for r in range(self.result_table.rowCount()):
                typ = self.result_table.item(r, 0).text()
                num = int(self.result_table.item(r, 1).text())
                perc = self.result_table.item(r, 2).text()
                desc = self.result_table.item(r, 3).text()
                if r == item.row():
                    old_type = typ
                    typ = new_type
                table_data.append([typ, num, perc, desc])
            logging.info(f"Collected table data: {table_data}")

  
            normalized_old_type = self.normalize_type_name(old_type)
            if old_type and normalized_old_type != normalized_new_type:
                logging.info(
                    f"Updating type_to_ids: moving IDs from '{normalized_old_type}' to '{normalized_new_type}'")
                ids = self.type_to_ids.pop(normalized_old_type, [])
                self.type_to_ids[normalized_new_type] = self.type_to_ids.get(normalized_new_type, []) + ids

            merged_data = {}
            for typ, num, _, desc in table_data:
                normalized_typ = self.normalize_type_name(typ)
                if normalized_typ in merged_data:
                    merged_data[normalized_typ][1] += num
                    # Merge IDs for this type
                    existing_ids = self.type_to_ids.get(normalized_typ, [])
                    merged_data[normalized_typ][3] = desc  # Update with latest description
                    self.type_to_ids[normalized_typ] = list(
                        set(existing_ids + self.type_to_ids.get(normalized_typ, [])))
                else:
                    merged_data[normalized_typ] = [typ, num, "", desc]  # Store original typ for display
                    self.type_to_ids[normalized_typ] = self.type_to_ids.get(normalized_typ, [])
            logging.info(f"Merged data: {merged_data}")
            logging.info(f"Updated type_to_ids: {self.type_to_ids}")

            # Recalculate percentages
            total = sum(item[1] for item in merged_data.values())
            for item in merged_data.values():
                item[2] = f"{item[1] / total * 100:.1f}%"

            # Update table
            new_table_data = sorted(merged_data.values(), key=lambda x: x[1], reverse=True)
            logging.info(f"New table data: {new_table_data}")
            self.is_updating_table = True
            self.result_table.setRowCount(len(new_table_data))
            for r, (typ, num, perc, desc) in enumerate(new_table_data):
                type_item = QTableWidgetItem(str(typ))  # Use original typ for display
                type_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
                self.result_table.setItem(r, 0, type_item)
                number_item = QTableWidgetItem(str(num))
                number_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.result_table.setItem(r, 1, number_item)
                perc_item = QTableWidgetItem(str(perc))
                perc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.result_table.setItem(r, 2, perc_item)
                desc_item = QTableWidgetItem(str(desc))
                desc_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.result_table.setItem(r, 3, desc_item)

            # Update download combo
            self.update_download_combo(new_table_data)
            logging.info("Download combo updated")

        except Exception as e:
            logging.error(f"Failed to handle table item change: {str(e)}")
            self.status_label.append(f"<span style='color: red'>Error: Failed to update table. {str(e)}</span>")
            self.statusBar().showMessage("Error: Failed to update table", 5000)
        finally:
            self.is_updating_table = False
            self.result_table.itemChanged.connect(self.handle_table_item_changed)

    def update_status(self, status):
        self.status_label.append(status)
        self.statusBar().showMessage(status.split("<span")[0].strip(), 5000)

    def on_worker_finished(self):
        self.status_label.append("<span style='color: green'>Status: Task completed</span>")
        self.statusBar().showMessage("Task completed", 5000)

    def browse_save_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if path:
            self.path_input.setText(path)

    def download_sequences(self):
        save_path = self.path_input.text()
        if not save_path or not os.path.isdir(save_path):
            self.status_label.append("<span style='color: red'>Status: Please select a valid save path</span>")
            self.statusBar().showMessage("Error: Invalid save path", 5000)
            return

        if self.accession_ids:
            self.status_label.append(f"Status: Downloading {len(self.accession_ids)} accession sequences")
            self.statusBar().showMessage("Downloading accession sequences", 5000)

            self.download_worker = DownloadWorker(accession_ids=self.accession_ids, save_path=save_path)
            self.download_worker.progress_update.connect(self.status_label.append)
            self.download_worker.finished.connect(self.on_download_finished)
            self.download_worker.error.connect(self.handle_download_error)
            self.download_worker.start()
        else:
            if not self.worker or not self.worker.sequence_ids:
                self.status_label.append("<span style='color: red'>Status: Please retrieve the sequence first</span>")
                self.statusBar().showMessage("Error: Please retrieve sequences first", 5000)
                return

            selected_types = self.download_combo.selected_items()
            if not selected_types:
                self.status_label.append("<span style='color: red'>Status: Please select at least one type</span>")
                self.statusBar().showMessage("Error: No type selected", 5000)
                return

            self.status_label.append(f"Status: Downloading {', '.join(selected_types)}")
            self.statusBar().showMessage(f"Downloading {', '.join(selected_types)}", 5000)

            self.download_worker = DownloadWorker(selected_types=selected_types, type_to_ids=self.type_to_ids,
                                                  save_path=save_path)
            self.download_worker.progress_update.connect(self.status_label.append)
            self.download_worker.finished.connect(self.on_download_finished)
            self.download_worker.error.connect(self.handle_download_error)
            self.download_worker.start()

    def on_download_finished(self):
        self.status_label.append("Status: Download completed")
        self.statusBar().showMessage("Download completed", 5000)

    def handle_download_error(self, error):
        self.status_label.append(f"<span style='color: red'>Error: {error}</span>")
        self.statusBar().showMessage("Error: Download failed", 5000)

    def start_analysis(self):
        virus_name = self.virus_input.text()
        if not virus_name:
            self.status_label.append(
                "<span style='color: red'>Status: Please enter the full name of the virus or upload a txt file containing the accession numbers</span>")
            self.statusBar().showMessage("Error: No virus name entered", 5000)
            return

        self.status_label.append("Status: Initializing...")
        self.statusBar().showMessage("Initializing...", 5000)
        self.worker = AnalysisWorker(virus_name)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.table_update.connect(self.handle_table_update)
        self.worker.status_update.connect(self.update_status)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()