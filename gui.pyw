#!pythonw
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行GUI
from gui import MusicDecryptorGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicDecryptorGUI(root)
    root.mainloop()