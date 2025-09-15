from PyQt5.QtWidgets import QFileDialog
import re
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import random

matplotlib.rcParams['pdf.fonttype'] = 42  
matplotlib.rcParams['ps.fonttype'] = 42   
matplotlib.rcParams['font.family'] = 'Arial'  
matplotlib.rcParams['text.usetex'] = False  
matplotlib.rcParams['pdf.use14corefonts'] = False  
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans'] 


current_colors = []
def generate_color_scheme(num_colors=5):
    h_start = random.random()  
    colors = sns.husl_palette(
        n_colors=num_colors,
        h=h_start,           
        s=random.uniform(0.4, 0.7),  
        l=random.uniform(0.5, 0.8)   
    )
    hex_colors = [f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}" for r, g, b in colors]
    return hex_colors
def get_current_colors(num_colors=5):
    global current_colors
    if not current_colors:
        current_colors = generate_color_scheme(num_colors)
    return current_colors
def switch_color_scheme(num_colors=5):
    global current_colors
    current_colors = generate_color_scheme(num_colors)
    return current_colors
def selectDirectory(parent=None):
    options = QFileDialog.Options()
    directory = QFileDialog.getExistingDirectory(parent, "Select a working directory", "", options=options)
    if directory:
        return directory
    return None
def showFileDialog(parent=None, default_directory=None):
    options = QFileDialog.Options()
    filePath, _ = QFileDialog.getOpenFileName(parent, "Select the tree file", default_directory,
                                              "Tree Files (*.tre *.tree);;All Files (*)",
                                              options=options)
    if filePath:
        if filePath.endswith('.tre') or filePath.endswith('.tree'):
            return filePath
        else:
            parent.update_status(
                "<b><span style='color: red;'>Invalid file format. Please select a .tre or .tree file.</span></b>")
            return None
    return None
def readTreeFile(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        set_patterns = re.findall(r'set=\{([^\}]+)\}', content)
        prob_patterns = re.findall(r'set\.prob=\{([^\}]+)\}', content)
        if set_patterns and prob_patterns:
            last_set = set_patterns[-1]
            last_prob = prob_patterns[-1]
            set_fields = [field.strip('"') for field in last_set.split(',')]
            prob_values = [value.strip() for value in last_prob.split(',')]
            return set_fields, prob_values
        else:
            raise ValueError("Missing 'set=' or 'set.prob=' field in the file.")
    except Exception as e:
        print(f"Error reading tree file {file_path}: {e}")
        return [], []
def showBatchFileDialog(parent=None, default_directory=None):
    options = QFileDialog.Options()
    files, _ = QFileDialog.getOpenFileNames(parent, "Select tree files", default_directory,
                                            "Tree Files (*.tre *.tree);;All Files (*)",
                                            options=options)
    return files if files else None
def plot_bar_chart(set_fields, prob_values, output_path, width_px, height_px, preview=False, colors=None):
    if not set_fields or not prob_values:
        print("没有可绘制的数据。")
        return
    prob_values = [float(value) for value in prob_values]
    if colors is None:
        colors = get_current_colors(len(set_fields))
    if len(colors) < len(set_fields):
        colors = colors + generate_color_scheme(len(set_fields) - len(colors))
    plt.clf()
    plt.close('all')
    plt.figure(figsize=(width_px / 100, height_px / 100), dpi=100)
    bars = plt.barh(set_fields, prob_values, color=colors[:len(set_fields)])
    plt.xlabel('Root state posterior probability')
    plt.ylabel('Region')
    for bar in bars:
        plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                 f'{bar.get_width():.2f}', va='center')
    if preview:
        plt.show()  
    else:
        plt.savefig(output_path, bbox_inches='tight', dpi=100, format='pdf')
        plt.close()  
def plot_pie_chart(set_fields, prob_values, output_path, width_px, height_px, preview=False, colors=None):
    if not set_fields or not prob_values:
        print("没有可绘制的数据。")
        return
    prob_values = [float(value) for value in prob_values]
    if colors is None:
        colors = get_current_colors(len(set_fields))
    if len(colors) < len(set_fields):
        colors = colors + generate_color_scheme(len(set_fields) - len(colors))
    plt.clf()
    plt.close('all')
    plt.figure(figsize=(width_px / 100, height_px / 100), dpi=100)
    plt.pie(prob_values, labels=set_fields, autopct='%1.1f%%', colors=colors[:len(set_fields)], startangle=90)
    plt.title('Root state posterior probability')
    if preview:
        plt.show()  
    else:
        plt.savefig(output_path, bbox_inches='tight', dpi=100, format='pdf')  
        plt.close()  
def selectSaveDirectory(parent=None):
    save_directory = QFileDialog.getExistingDirectory(parent, "Select the save path")
    if save_directory:
        return save_directory
    return None