import sys
import os
import webbrowser


def open_quick_guide():
    # 获取基路径，支持 PyInstaller 打包环境
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(base_path, "Quick_Guide.pdf")
    if os.path.exists(pdf_path):
        webbrowser.open(f"file://{os.path.abspath(pdf_path)}")
        return True, "Quick Guide PDF opened successfully"
    else:
        return False, "Quick Guide PDF not found"
if __name__ == "__main__":
    success, message = open_quick_guide()
    print(message)