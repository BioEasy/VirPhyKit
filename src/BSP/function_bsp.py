import os
import random
import subprocess
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel
from PyQt5.QtGui import QFont

# Global variable to store the current color scheme
current_colors = []

# Predefined color plans
COLOR_PLANS = {
    "Plan1": ["#d1b6d1", "#fcd82c", "#91c2d8", "#f7932d", "#ed3e2e"],
    "Plan2": ["#0d0887", "#501f80", "#92377a", "#d25172", "#dd8b57", "#e7c33c", "#f3fb40"],
    "Plan3": ["#ffc94a", "#f3f3f3", "#e867a7", "#86a5fe", "#ff914e", "#947ff2", "#726869"],
    "Plan4": ["#ec347c", "#00aae3", "#dc5e31", "#79bb56", "#1f4e9f"],
    "Plan5": ["#f36424", "#672e92", "#203f99", "#139ed3", "#74201e", "#bebebe", "#00008b", "#ff0000", "#ffa500",
              "#ffd700"],
    "Plan6": ["#fff2cc", "#7030a0", "#c00000", "#00b0f0", "#92d050", "#4472c4"],
    "Plan7": ["#ecefcd", "#b5cdb5", "#86aaa0", "#5c898e", "#39687d", "#2f455c", "#1f2531"],
    "Plan8": ["#d6e1e5", "#002a5f", "#fddbb2", "#b45218", "#f3d68a", "#c69d3c", "#3e4f69", "#62708b", "#005495",
              "#0975b3", "#bbe7fc", "#f57823"],
    "Plan9": ["#35608d", "#e46725", "#6ccc06", "#cd554e", "#bb3754", "#7c1d6d", "#49c06e"],
    "Plan10": ["#444577", "#c65861", "#f3dee0", "#ffa725", "#ff6b62", "#be588d", "#58538b"],
    "Plan11": ["#4292c9", "#a0c9e5", "#35a153", "#afdd8b", "#f26a11", "#fe9376", "#817cb9"],
    "Plan12": ["#cb78a6", "#d35f00", "#f7ec44", "#009d73", "#fcb93e", "#0072b2", "#979797"]
}


class ColorPreviewDialog(QDialog):
    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Color Scheme Preview")
        self.setFixedSize(400, 200)

        layout = QGridLayout()
        layout.setSpacing(10)

        for idx, color in enumerate(colors):
            color_label = QLabel()
            color_label.setFixedSize(50, 50)
            color_label.setStyleSheet(f"background-color: {color}; border: 1px solid #000;")
            layout.addWidget(color_label, idx // 2, (idx % 2) * 2)

            hex_label = QLabel(color)
            hex_label.setFont(QFont("Arial", 10))
            layout.addWidget(hex_label, idx // 2, (idx % 2) * 2 + 1)

        self.setLayout(layout)


def get_current_colors(num_colors=5):
    global current_colors
    if not current_colors:
        current_colors = switch_color_scheme(num_colors)
    return current_colors


def switch_color_scheme(num_colors=5):
    global current_colors
    selected_plan = random.choice(list(COLOR_PLANS.keys()))
    plan_colors = COLOR_PLANS[selected_plan]

    if len(plan_colors) <= num_colors:
        current_colors = plan_colors
    else:
        current_colors = random.sample(plan_colors, num_colors)

    return current_colors


def check_r_installation(r_path):
    if not r_path or not os.path.isdir(r_path):
        return False, ["tidyr", "ggplot2"]

    rscript_path = os.path.join(r_path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
    if not os.path.isfile(rscript_path) or not os.access(rscript_path, os.X_OK):
        return False, ["tidyr", "ggplot2"]

    required_packages = ["tidyr", "ggplot2"]
    try:
        result = subprocess.run(
            [rscript_path, "-e", "cat(rownames(installed.packages()))"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode != 0:
            return False, required_packages
        installed = result.stdout.strip().split()
        missing_packages = [pkg for pkg in required_packages if pkg not in installed]
        return len(missing_packages) == 0, missing_packages
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, required_packages


def generate_single_plot(tsv_file, output_file, direction, secondary_axis, plot_color, r_path):
    try:
        r_script = (
            f'Skyline = read.table("{tsv_file}", header=T)\n'
            f'# 计算动态y轴范围\n'
            f'data_min = min(c(Skyline$Lower, Skyline$Median, Skyline$Upper), na.rm=TRUE)\n'
            f'data_max = max(c(Skyline$Lower, Skyline$Median, Skyline$Upper), na.rm=TRUE)\n'
            f'log_min = log10(data_min)\n'
            f'log_max = log10(data_max)\n'
            f'log_center = (log_min + log_max) / 2\n'
            f'log_range = log_max - log_min\n'
            f'expanded_range = log_range * 1.6\n'
            f'ylim_min = 10^(log_center - expanded_range / 2)\n'
            f'ylim_max = 10^(log_center + expanded_range / 2)\n'
            f'pdf("{output_file}", width=8, height=6)\n'
            f'plot(Skyline$Median ~ Skyline$Time, type="l",\n'
            f'    log="y", {"xlim=c(1974,2016)" if direction == "Forward" else "xlim=c(2016,1974)"}, ylim=c(ylim_min,ylim_max),\n'
            f'    col="{plot_color}",\n'
            f'    ylab=expression(paste(italic("N"[e]),tau," ","(years)")),\n'
            f'    xlab="Sampling Year",\n'
            f'    main="Bayesian Skyline Plot",\n'
            f'    lwd=6)\n'
        )
        if secondary_axis:
            r_script += (
                'majorat <- seq(1975, 2015, by=5)\n'
                'majorlab <- majorat\n'
                'axis(1, at=majorat, labels=majorlab)\n'
                'minorat <- seq(1974, 2016, by=1)\n'
                'minorat <- minorat[!minorat %in% majorat]\n'
                'axis(1, at=minorat, tcl=par("tcl")*0.5, labels=FALSE, lwd=0, lwd.ticks=1)\n'
            )
        r_script += (
            f'BSP_X = c(Skyline$Time, rev(Skyline$Time))\n'
            f'BSP_Y = c(Skyline$Lower, rev(Skyline$Upper))\n'
            f'polygon(BSP_X, BSP_Y, border=NA, col="{plot_color}")\n'
            f'lines(Skyline$Median ~ Skyline$Time, type="l", lwd=4, col="black")\n'
            f'dev.off()\n'
        )

        r_script_path = "temp_skyline_plot.r"
        with open(r_script_path, "w", encoding="utf-8") as f:
            f.write(r_script)
        rscript_path = os.path.join(r_path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
        result = subprocess.run([rscript_path, r_script_path], capture_output=True, text=True)
        if os.path.exists(r_script_path):
            os.remove(r_script_path)

        return result

    except Exception as e:
        return str(e)

        r_script_path = "temp_skyline_plot.r"
        with open(r_script_path, "w", encoding="utf-8") as f:
            f.write(r_script)

        rscript_path = os.path.join(r_path, "bin", "Rscript" + (".exe" if os.name == "nt" else ""))
        result = subprocess.run([rscript_path, r_script_path], capture_output=True, text=True)

        if os.path.exists(r_script_path):
            os.remove(r_script_path)

        return result

    except Exception as e:
        return str(e)