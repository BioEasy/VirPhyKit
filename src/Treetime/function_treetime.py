import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
from treetime import TreeTime
from treetime.utils import parse_dates
from Bio import AlignIO, Phylo
from Bio.Seq import Seq
import matplotlib
from io import StringIO
import sys
from scipy.stats import linregress


matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.sans-serif'] = ['Arial']
matplotlib.rcParams['pdf.fonttype'] = 42

if getattr(sys, 'frozen', False):
    DEFAULT_MAPPING_FILE = os.path.join(sys._MEIPASS, "Mapping.txt")
else:
    DEFAULT_MAPPING_FILE = os.path.join(os.path.dirname(__file__), "Mapping.txt")
class TreeTimeWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(object, float, float, str, str)
    error_signal = pyqtSignal(str)
    def __init__(self, fasta_file, tree_file, dates_file, output_dir, mapping_file=None):
        super().__init__()
        self.fasta_file = fasta_file
        self.tree_file = tree_file
        self.dates_file = dates_file
        self.output_dir = output_dir
        self.mapping_file = mapping_file if mapping_file else DEFAULT_MAPPING_FILE
    def load_mapping(self):
        try:
            mapping = {}
            file_path = self.mapping_file
            if not os.path.exists(file_path):
                self.log_signal.emit(f"Mapping file not found at: {file_path}")
                return {}
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        region, location = line.strip().split('\t')
                        mapping[location] = region
            self.log_signal.emit(f"Loaded mapping file: {file_path}")
            return mapping
        except Exception as e:
            self.log_signal.emit(f"Error loading mapping file: {str(e)}")
            return {}
    def capture_treetime_logs(self, func, *args, **kwargs):
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = func(*args, **kwargs)
            output = sys.stdout.getvalue()
            for line in output.split('\n'):
                if line.strip():
                    self.log_signal.emit(line.strip())
                    QThread.msleep(10)
                    QApplication.processEvents()
            beta = None
            r_squared = None
            beta_patterns = [
                r"ClockTree\.date2dist: Setting new molecular clock\. rate\s*([\d\.eE+-]+)",
                r"Clock rate estimate:\s*([\d\.eE+-]+)",
                r"rate\s*=\s*([\d\.eE+-]+)"
            ]
            r_squared_patterns = [
                r"R\^2 of root-to-tip regression:\s*([\d\.]+)",
                r"R\^2\s*=\s*([\d\.]+)"
            ]
            for pattern in beta_patterns:
                beta_match = re.search(pattern, output)
                if beta_match:
                    beta = float(beta_match.group(1))
                    break
            if beta is None:
                self.log_signal.emit("Failed to extract β from logs.")
            for pattern in r_squared_patterns:
                r_squared_match = re.search(pattern, output)
                if r_squared_match:
                    r_squared = float(r_squared_match.group(1))
                    break
            if r_squared is None:
                self.log_signal.emit("Failed to extract R² from logs.")
            return result, beta, r_squared
        finally:
            sys.stdout = old_stdout

    def validate_dates_and_tree(self, tt, dates):
        tree_tips = {clade.name for clade in tt.tree.get_terminals()}
        date_names = set(dates.keys())
        missing_in_dates = tree_tips - date_names
        missing_in_tree = date_names - tree_tips
        if missing_in_dates:
            self.log_signal.emit(f"Error: The following tree tips are missing dates: {missing_in_dates}")
            return False
        if missing_in_tree:
            self.log_signal.emit(f"Warning: The following date entries are not in the tree: {missing_in_tree}")
        return True

    def load_mapping(self):
        try:
            mapping = {}
            with open(self.mapping_file, 'r') as f:
                for line in f:
                    if line.strip():
                        region, location = line.strip().split('\t')
                        mapping[location] = region
            self.log_signal.emit(f"Loaded mapping file: {self.mapping_file}")
            return mapping
        except Exception as e:
            self.log_signal.emit(f"Error loading mapping file: {str(e)}")
            return {}

    def run(self):
        try:

            alignment = AlignIO.read(self.fasta_file, "fasta")
            for record in alignment:
                seq = str(record.seq).replace('U', 'T')
                record.seq = Seq(seq)
            self.log_signal.emit(f"Loaded {len(alignment)} sequences from {self.fasta_file}")
    
            tree = Phylo.read(self.tree_file, "newick")
            self.log_signal.emit(f"Loaded newick tree from {self.tree_file}")

            dates = parse_dates(self.dates_file)
            metadata = pd.read_csv(self.dates_file)
            has_location = 'location' in metadata.columns
            locations = dict(zip(metadata['name'], metadata['location'])) if has_location else None
            self.log_signal.emit(f"Loaded {len(dates)} dates{' and locations' if has_location else ''} from {self.dates_file}")
   
            if has_location:
                tree_tips = {clade.name for clade in tree.get_terminals()}
                missing_dates = tree_tips - set(dates.keys())
                missing_locations = tree_tips - set(locations.keys())
                if missing_dates:
                    self.log_signal.emit(f"Error: The following tree tips are missing dates: {missing_dates}")
                    self.error_signal.emit("Missing dates for tree tips")
                    return
                if missing_locations:
                    self.log_signal.emit(f"Error: The following tree tips are missing location data: {missing_locations}")
                    self.error_signal.emit("Missing location data for tree tips")
                    return

                location_to_region = self.load_mapping()
  
                region_map = {}
                unmapped_locations = []
                for name, loc in locations.items():
                    region = location_to_region.get(loc, None)
                    if region:
                        region_map[name] = region
                    else:
                        unmapped_locations.append(loc)
                        region_map[name] = "Unknown"
                if unmapped_locations:
                    self.log_signal.emit(f"The following locations were not found in the mapping file and will be labeled 'Unknown': {set(unmapped_locations)}")

            tt = TreeTime(
                aln=alignment,
                tree=tree,
                dates=dates,
                gtr='Jukes-Cantor',
                seq_len=len(alignment[0]),
                verbose=4
            )

            if not self.validate_dates_and_tree(tt, dates):
                self.error_signal.emit("Date-tree mismatch")
                return

            tt.reroot(root='least-squares')
            self.log_signal.emit("Tree rerooted using least-squares method.")

            _, beta, r_squared = self.capture_treetime_logs(
                tt.run,
                root="best",
                branch_length_mode='joint',
                infer_gtr=False,
                infer_clock=True,
                resolve_polytomies=True,
                time_marginal=True,
                max_iter=3
            )
            self.log_signal.emit("Time-tree inference completed!")

            if beta is None and hasattr(tt, 'date2dist') and hasattr(tt.date2dist, 'clock_rate'):
                beta = tt.date2dist.clock_rate
                self.log_signal.emit(f"Extracted β from tt.date2dist.clock_rate: {beta}")
            clock_rate = tt.date2dist.clock_rate if hasattr(tt, 'date2dist') and hasattr(tt.date2dist, 'clock_rate') else None
            if clock_rate:
                self.log_signal.emit(f"Clock rate (substitutions per site per year): {clock_rate}")
            else:
                self.log_signal.emit("Clock rate not available.")

            output_tree_file = os.path.join(self.output_dir, "timetree_inferred.nwk")
            Phylo.write(tt.tree, output_tree_file, "newick")
            self.log_signal.emit(f"Saved inferred time-tree to {output_tree_file}")
  
            tip_names = [clade.name for clade in tt.tree.get_terminals()]
            root_to_tip_distances = []
            sampling_dates = []
            for tip in tt.tree.get_terminals():
                path = tt.tree.get_path(tip)
                distance = sum(clade.branch_length for clade in path if clade.branch_length is not None)
                root_to_tip_distances.append(distance)
                sampling_dates.append(dates[tip.name])
            if root_to_tip_distances and sampling_dates:
                self.log_signal.emit(f"Number of tips: {len(tip_names)}")
                self.log_signal.emit(f"Sampling dates: {sampling_dates}")
                self.log_signal.emit(f"Root-to-tip distances: {root_to_tip_distances}")
                regression_result = linregress(sampling_dates, root_to_tip_distances)
                p_value = regression_result.pvalue
                p_value_display = "<1e-10" if p_value < 1e-10 else f"{p_value:.3e}"
                self.log_signal.emit(f"Regression: slope={regression_result.slope:.3e}, water: {regression_result.rvalue:.3f}, pvalue={p_value_display}")
            else:
                p_value = None
                p_value_display = "N/A"
                self.log_signal.emit("Error: Could not calculate p-value due to missing data.")

            fig1, ax1 = plt.subplots(figsize=(10, 6))
            tt.plot_root_to_tip(ax=ax1, add_internal=False, label=False)

            if ax1.get_legend():
                ax1.get_legend().remove()
            for line in ax1.get_lines():
                line.set_label('_nolegend_')
                line.set_color('#00A0E9')  

            scatter_collections = ax1.collections
            if len(scatter_collections) == 0:
                self.log_signal.emit("Error: No scatter points found in root-to-tip plot.")
                self.error_signal.emit("No scatter points in root-to-tip plot")
                return
            if has_location:
 
                scatter_collection = scatter_collections[0]
                scatter_coords = scatter_collection.get_offsets()
                if len(scatter_coords) != len(tip_names):
                    self.log_signal.emit(
                        f"Error: Number of scatter points ({len(scatter_coords)}) does not match number of tips ({len(tip_names)})")
                    self.error_signal.emit("Scatter points mismatch")
                    return
                for artist in ax1.collections:
                    artist.remove()
  
                unique_regions = list(set(region_map.values()))
                colors = plt.cm.get_cmap('tab20', len(unique_regions))
                region_colors = {region: colors(i) for i, region in enumerate(unique_regions)}

                for region in unique_regions:
                    region_coords = [(coord[0], coord[1]) for name, coord in zip(tip_names, scatter_coords) if region_map[name] == region]
                    if region_coords:
                        x_coords, y_coords = zip(*region_coords)
                        ax1.scatter(x_coords, y_coords, c=[region_colors[region]], label=region, s=50)
            else:
 
                for artist in ax1.collections:
                    artist.remove()
                tt.plot_root_to_tip(ax=ax1, add_internal=True, label=False)
                for line in ax1.get_lines():
                    line.set_color('#00A0E9')  
                    line.set_label('_nolegend_')
                for collection in ax1.collections:
                    collection.set_facecolor('orange')
                    collection.set_label('_nolegend_')
  
            ax1.set_title("Root-to-Tip Regression", fontsize=18)
            ax1.tick_params(labelsize=14)
            ax1.set_ylabel("Distance to root", fontsize=16)
            ax1.set_xlabel("Sampling date", fontsize=16)
 
            if beta is not None and r_squared is not None:
                root_date = min(dates.values())
                text_labels = [f"Root date: {root_date:.2f}", f"Rate: {beta:.3e}", f"$R^2$: {r_squared:.3f}"]
                if p_value is not None:
                    text_labels.append(f"$P$-value: {p_value_display}")
                if has_location:
                    region_handles, region_labels = ax1.get_legend_handles_labels()

                    stats_handles = [plt.Line2D([], [], marker=None, linestyle='none')] * len(text_labels)
                    stats_legend = ax1.legend(stats_handles, text_labels, loc='upper left', fontsize=12)
                    ax1.add_artist(stats_legend)
       
                    region_handles = [plt.scatter([], [], c=region_colors[region], marker='o', s=50) for region in region_labels]
                    ax1.legend(region_handles, region_labels, loc='lower right', fontsize=12)
                else:
                    final_handles = [plt.Line2D([], [], marker=None, linestyle='none')] * len(text_labels)
                    final_labels = text_labels
                    ax1.legend(final_handles, final_labels, loc='upper left', fontsize=12)

            root_to_tip_plot = os.path.join(self.output_dir, "RootToTip.pdf")
            try:
                plt.savefig(root_to_tip_plot, bbox_inches='tight', dpi=100, format='pdf')
                self.log_signal.emit(f"Saved root-to-tip plot to {root_to_tip_plot}")
            except Exception as e:
                self.log_signal.emit(f"Error saving root-to-tip plot: {str(e)}")
                self.error_signal.emit(f"Failed to save root-to-tip plot: {str(e)}")
                return
            finally:
                plt.close()

            fig2, ax2 = plt.subplots(figsize=(10, 6))

            try:
                Phylo.draw(tt.tree, axes=ax2, do_show=False, label_func=lambda clade: "",
                           branch_labels=lambda clade: "")
                ax2.set_title("Time Inference Tree", fontsize=16)
                time_tree_plot = os.path.join(self.output_dir, "TimeInference_tree.pdf")
                plt.savefig(time_tree_plot, bbox_inches='tight', dpi=100, format='pdf')
                self.log_signal.emit(f"Saved time inference tree plot to {time_tree_plot}")
            except Exception as e:
                self.log_signal.emit(f"Error saving time inference tree plot: {str(e)}")
                self.error_signal.emit(f"Failed to save time inference tree plot: {str(e)}")
                return
            finally:
                plt.close()
            self.finished_signal.emit(tt, beta, r_squared, output_tree_file, time_tree_plot)
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
            self.error_signal.emit(f"Unexpected error: {str(e)}")