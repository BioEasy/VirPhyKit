import os
import subprocess
import re
import pandas as pd
def check_python_path(path):
    try:
        result = subprocess.run([path, "-c", "import ete3; import pandas"],
                                capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return "install"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "uninstall"
def check_perl_path(path):
    try:
        result = subprocess.run([path, "-v"], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        version_line = [line for line in result.stdout.splitlines() if "This is perl" in line]
        return "install" if version_line else "uninstall"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "uninstall"
def check_r_path(path):
    if not path or not os.path.isdir(path):
        return "uninstall", ["ggplot2", "tidyr", "ggsci", "scales", "patchwork"]
    rscript_path = os.path.join(path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
    if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
        return "uninstall", ["ggplot2", "tidyr", "ggsci", "scales", "patchwork"]
    required_packages = ["ggplot2", "tidyr", "ggsci", "scales", "patchwork"]
    try:
        result = subprocess.run(
            [rscript_path, "-e", "cat(rownames(installed.packages()))"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode != 0:
            return "uninstall", required_packages
        installed = result.stdout.strip().split()
        missing_packages = [pkg for pkg in required_packages if pkg not in installed]
        return "install" if not missing_packages else "uninstall", missing_packages
    except (subprocess.SubprocessError, FileNotFoundError):
        return "uninstall", required_packages
def run_steps(mcc_file, perl_path, r_path, status_callback, output_path=None, python_path=None):
    mcc_dir = os.path.dirname(mcc_file)
    status_callback(f"Selected a MCC tree annotated with traits/MultiTypeTree: {mcc_file}")

    if not os.path.exists(mcc_file):
        status_callback(f"<b><span style='color: red;'>Error: MCC tree does not exist.</span></b>")
        return False
    try:
        test_file = os.path.join(mcc_dir, "test_write.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        status_callback(f"<b><span style='color: red;'>Error: Cannot write to MCC directory: {e}</span></b>")
        status_callback("Falling back to current working directory.")
        mcc_dir = os.getcwd()
    ins_file = os.path.join(mcc_dir, "Test_ins.tree")
    ins_out_file = os.path.join(mcc_dir, "Test_ins.out.tree")
    tree_data_file = os.path.join(mcc_dir, "Treedata.csv")
    outfile = os.path.join(mcc_dir, "outfile.csv")
    if output_path and os.path.isdir(os.path.dirname(output_path)):
        transposed_outfile = output_path
    else:
        transposed_outfile = os.path.join(mcc_dir, "outfile_transposed.txt")
    if not python_path or not os.path.isfile(python_path):
        status_callback("<b><span style='color: red;'>Error: Invalid or missing Python executable path. Please configure in Environment settings.</span></b>")
        return False
    if check_python_path(python_path) != "install":
        status_callback("<b><span style='color: red;'>Error: Python environment missing required libraries (ete3, pandas).</span></b>")
        return False
    if not perl_path or not os.path.isfile(perl_path):
        status_callback("<b><span style='color: red;'>Error: Invalid or missing Perl executable path. Please configure in Environment settings.</span></b>")
        return False
    if check_perl_path(perl_path) != "install":
        status_callback("<b><span style='color: red;'>Error: Invalid Perl executable.</span></b>")
        return False
    if not r_path or not os.path.isdir(r_path):
        status_callback("<b><span style='color: red;'>Error: Invalid or missing R installation directory. Please configure in Environment settings.</span></b>")
        return False
    rscript_path = os.path.join(r_path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
    if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
        status_callback(f"<b><span style='color: red;'>Error: Rscript executable not found in {r_path}.</span></b>")
        return False
    status, missing_packages = check_r_path(r_path)
    if status != "install":
        status_callback(f"<b><span style='color: red;'>Error: Missing R packages: {', '.join(missing_packages)}.</span></b>")
        return False
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
    insert_script = os.path.join(script_dir, "Insert_node_numbers.py")
    afterphylo_script = os.path.join(script_dir, "AfterPhylo.pl")
    r_script = os.path.join(script_dir, "process_tree.R")
    migration_script = os.path.join(script_dir, "Get_migration_matrix_general_number_of_categories.py")

    for script in [insert_script, afterphylo_script, r_script, migration_script]:
        if not os.path.exists(script):
            status_callback(f"<b><span style='color: red;'>Error: {os.path.basename(script)} not found at {script_dir}.</span></b>")
            return False
    status_callback("Inserting node numbers into MCC tree/MultiTypeTree...")
    try:
        subprocess.run([python_path, insert_script, mcc_file, ins_file], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        status_callback(f"<b><span style='color: red;'>Error: Insert node numbers failed with exit code {e.returncode}: {e.stderr}</span></b>")
        return False

    if not os.path.exists(ins_file):
        status_callback(f"<b><span style='color: red;'>Error: Test_ins.tree was not generated.</span></b>")
        return False
    status_callback("Converting to Newick format...")
    try:
        subprocess.run([perl_path, afterphylo_script, "-format=newick", ins_file], capture_output=True, text=True,
                       check=True)
    except subprocess.CalledProcessError as e:
        status_callback(f"<b><span style='color: red;'>Error: Convert to Newick failed with exit code {e.returncode}: {e.stderr}</span></b>")
        return False

    if not os.path.exists(ins_out_file):
        status_callback(f"<b><span style='color: red;'>Error: Test_ins.out.tree was not generated.</span></b>")
        return False
    status_callback("Processing tree data with R script...")
    trait = None
    try:
        with open(ins_file, 'r') as f:
            content = f.read()
            match = re.search(r'(\w+)\.set\.prob', content)
            if match:
                trait = match.group(1)
            else:
                status_callback("<b><span style='color: red;'>Error: Could not find .set.prob field in Test_ins.tree</span></b>")
                return False
    except Exception as e:
        status_callback(f"<b><span style='color: red;'>Error reading Test_ins.tree for trait extraction: {e}</span></b>")
        return False
    original_dir = os.getcwd()
    os.chdir(mcc_dir)
    try:
        subprocess.run([rscript_path, r_script, trait], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        status_callback(f"<b><span style='color: red;'>Error: R script failed with exit code {e.returncode}: {e.stderr}</span></b>")
        os.chdir(original_dir)
        return False

    if not os.path.exists(tree_data_file):
        status_callback(f"<b><span style='color: red;'>Error: Treedata.csv was not generated.</span></b>")
        os.chdir(original_dir)
        return False
    status_callback("Generating migration matrix...")
    try:
        subprocess.run([python_path, migration_script, ins_out_file, tree_data_file, outfile], capture_output=True,
                       text=True, check=True)
    except subprocess.CalledProcessError as e:
        status_callback(f"<b><span style='color: red;'>Error: Generate migration matrix failed with exit code {e.returncode}: {e.stderr}</span></b>")
        os.chdir(original_dir)
        return False

    if not os.path.exists(outfile):
        status_callback(f"<b><span style='color: red;'>Error: outfile.csv was not generated.</span></b>")
        os.chdir(original_dir)
        return False
    status_callback("Saving the migration matrix...")
    try:
        df = pd.read_csv(outfile, skip_blank_lines=True)
        df = df.dropna(how='all')
        df.columns = ['Migration_Direction'] + df.columns[1:].tolist()
        df = df.set_index('Migration_Direction')
        df_transposed = df.transpose()
        df_transposed = df_transposed.reset_index()
        df_transposed = df_transposed.rename(columns={'index': 'Year'})
        df_transposed.to_csv(transposed_outfile, sep="\t", index=False)
    except Exception as e:
        status_callback(f"<b><span style='color: red;'>Error: Save migration matrix failed with unexpected error: {e}</span></b>")
        os.chdir(original_dir)
        return False

    if not os.path.exists(transposed_outfile):
        status_callback(f"<b><span style='color: red;'>Error: outfile_transposed.txt was not generated.</span></b>")
        os.chdir(original_dir)
        return False

    for temp_file in [ins_file, ins_out_file, tree_data_file, outfile]:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                status_callback(f"<b><span style='color: red;'>Warning: Could not delete {os.path.basename(temp_file)}: {e}</span></b>")

    os.chdir(original_dir)
    status_callback(f"<b><span style='color: green;'>Done! Results are available at: {transposed_outfile}\n</span></b>."
                    f"\nPlease click 'Go to plot' to visualize the output.")
    return True