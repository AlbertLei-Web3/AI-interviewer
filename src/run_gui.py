import sys
import os

# 添加 src 目录到 Python 路径
src_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(src_path))

from src.gui.app import run_gui

if __name__ == "__main__":
    run_gui() 