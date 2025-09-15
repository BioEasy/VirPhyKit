import pandas as pd
from PyQt5.QtWidgets import QFileDialog
import re
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
from matplotlib import font_manager

def showFileDialog(parent=None):
    options = QFileDialog.Options()
    filePath, _ = QFileDialog.getOpenFileName(parent, "Select a file.", "", "All Files (*);;Text Files (*.txt)", options=options)
    if filePath:
        return filePath
    return None

def showFileDialog1(parent=None):
    options = QFileDialog.Options()
    filePath, _ = QFileDialog.getOpenFileName(parent, "Select a file", "", "All Files (*);;Text Files (*.txt)", options=options)
    if filePath:
        return filePath
    return None

def browse_original_data_file():
    file_name, _ = QFileDialog.getOpenFileName(None, "Select an MCC tree from the original data.", "", "Tree Files (*.tree *.tre);;All Files (*)")
    if file_name:
        with open(file_name, 'r') as file:
            content = file.read()
        # 改进后的正则表达式
        set_matches = re.findall(r'\b\w+\.set=\{\s*([^}]*)\s*\}', content)
        prob_matches = re.findall(r'\b\w+\.set\.prob=\{\s*([^}]*)\s*\}', content)
        last_set = set_matches[-1] if set_matches else None
        last_set_prob = prob_matches[-1] if prob_matches else None
        # 清洗 set 数据，去掉多余引号
        if last_set:
            last_set = ','.join([country.strip().strip('"') for country in last_set.split(',')])
        if last_set_prob:
            # 将set.prob解析为浮点数列表
            prob_values = [float(prob.strip()) for prob in last_set_prob.split(',')]
            # 检查是否所有相邻值差异小于0.01
            if all(abs(prob_values[i] - prob_values[i + 1]) < 0.01 for i in range(len(prob_values) - 1)):
                # 返回绿色信息
                return file_name, last_set, last_set_prob, \
                       "<b><span style='color: green;'>The posterior probability of the original file is too small and no detection is needed.</span></b>"
        return file_name, last_set, last_set_prob, None
    return None, None, None, None

def browse_randomized_data_files():
    file_names, _ = QFileDialog.getOpenFileNames(None, "Select MCC trees from the region-randomized data.", "", "Tree Files (*.tree *.tre);;All Files (*)")
    results = []
    for file_name in file_names:
        with open(file_name, 'r') as file:
            content = file.read()
        set_matches = re.findall(r'\b\w+\.set=\{\s*([^}]*)\s*\}', content)
        prob_matches = re.findall(r'\b\w+\.set\.prob=\{\s*([^}]*)\s*\}', content)
        last_set = set_matches[-1] if set_matches else None
        last_set_prob = prob_matches[-1] if prob_matches else None
        if last_set:
            last_set = ','.join([country.strip().strip('"') for country in last_set.split(',')])
        results.append((file_name, last_set, last_set_prob))
    return results

def generate_table(original_data, randomized_data, save_path):
    all_data = []
    if original_data:
        real_data = {"Replicates": "Real"}
        countries = original_data["set"].split(',')
        probs = original_data["set_prob"].split(',')
        for country, prob in zip(countries, probs):
            real_data[country.strip()] = float(prob.strip())
        max_prob = max([float(prob.strip()) for prob in probs])
        max_prob_index = [float(prob.strip()) for prob in probs].index(max_prob)
        target_country = countries[max_prob_index].strip()
    for i, data_item in enumerate(randomized_data, start=1):
        data = {"Replicates": f"Random{i}"}
        countries = data_item["set"].split(',')
        probs = data_item["set_prob"].split(',')
        for country, prob in zip(countries, probs):
            data[country.strip()] = float(prob.strip())
        all_data.append(data)
    df = pd.DataFrame(all_data)
    empty_row = pd.DataFrame([[""] + [""] * (df.shape[1] - 1)], columns=df.columns)
    df = pd.concat([df, empty_row], ignore_index=True)
    real_row = pd.DataFrame([real_data], columns=df.columns)
    df = pd.concat([df, real_row], ignore_index=True)
    min_values = df.iloc[:-2, 1:].min()
    max_values = df.iloc[:-2, 1:].max()
    min_row = pd.DataFrame([["Min"] + list(min_values)], columns=df.columns)
    max_row = pd.DataFrame([["Max"] + list(max_values)], columns=df.columns)
    df = pd.concat([df, min_row, max_row], ignore_index=True)
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"Data has been saved to {save_path}")
    random_target_probs = [data.get(target_country, 0.0) for data in all_data]
    max_random_target_prob = max(random_target_probs) if random_target_probs else 0.0
    if max_prob > max_random_target_prob:
        return "<b><span style='color: green;'>RRT SUCCESSFULLY PASSED!Click 'Preview' to view the results.</span></b>", df
    else:
        return "<b><span style='color: red;'>RRT FAILED!Click 'Preview' to view the results.</span></b>", df

def plot_graph_from_csv(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise Exception(f"Failed to read the CSV file: {str(e)}")
    required_rows = ['Real', 'Min', 'Max']
    existing_rows = df['Replicates'].unique()
    if not all(row in existing_rows for row in required_rows):
        raise ValueError("Required rows (Real, Min, Max) not found in the CSV file.")
    real_values = df[df["Replicates"] == "Real"].iloc[0, 1:]
    min_values = df[df["Replicates"] == "Min"].iloc[0, 1:]
    max_values = df[df["Replicates"] == "Max"].iloc[0, 1:]
    columns = df.columns[1:]  
    plt.rcParams['pdf.fonttype'] = 42  
    plt.rcParams['font.family'] = 'Arial' 
    plt.figure(figsize=(10, 6))
    plt.plot(columns, real_values, label="Real", marker='o', color=(0.357, 0.831, 0.847))  
    plt.plot(columns, min_values, label="Min", marker='o', color=(1.0, 0.855, 0.776), linestyle='--')  
    plt.plot(columns, max_values, label="Max", marker='o', color=(0.996, 0.412, 0.149), linestyle='--')  
    plt.title("Region Randomization Test Plot")
    plt.xlabel("Region/Country")
    plt.ylabel("Probability")
    plt.legend()
    plt.grid(True)  
    pdf_path = file_path.replace('.csv', '.pdf')
    with matplotlib.backends.backend_pdf.PdfPages(pdf_path) as pdf:
        pdf.savefig()
    plt.show()
    print(f"Plot has been saved as {pdf_path}")