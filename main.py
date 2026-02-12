# 文件名: main.py
import sys
import os
import matplotlib.pyplot as plt

# 设置学术风格字体
plt.rcParams['mathtext.fontset'] = 'cm' 
plt.rcParams['font.family'] = 'serif'

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    import tkinter as ttk
    from tkinter.constants import *

# 导入所有 Tab
from tab_bounds import BoundsTab
from tab_weighted import WeightedTab
from tab_hierarchy import HierarchyTab
from tab_lemma import LemmaTab # <--- 必须导入

# 高分屏适配 (Windows)
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Principal Submatrices Verification Suite")
        self.root.geometry("1280x850")
        
        # Output Path
        try: script_dir = os.path.dirname(os.path.abspath(__file__))
        except: script_dir = os.getcwd()
        self.output_dir = os.path.join(script_dir, "output")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        # Header
        header = ttk.Frame(root, padding=20, bootstyle="primary")
        header.pack(fill=X)
        
        lbl_title = ttk.Label(header, text="Numerical Verification: Aggregate Bounds on the eigenvalues of the principal submatrices of a Hermitian matrix", 
                              font=("Helvetica", 24, "bold"), bootstyle="inverse-primary")
        lbl_title.pack(side=LEFT)
        
        lbl_sub = ttk.Label(header, text="Research by Hristo Sendov & Mengxu Yuan", 
                            font=("Helvetica", 12), bootstyle="inverse-primary")
        lbl_sub.pack(side=RIGHT, anchor=S)

        # Notebook
        self.notebook = ttk.Notebook(root, bootstyle="default")
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- 这里是关键修正：必须把 4 个 Tab 都加进去 ---
        self.tab1 = BoundsTab(self.notebook, self.output_dir)
        self.tab_weighted = WeightedTab(self.notebook, self.output_dir)
        self.tab2 = HierarchyTab(self.notebook, self.output_dir)
        self.tab_lemma = LemmaTab(self.notebook, self.output_dir) # <--- 补上这一行！

        # Status Bar
        self.status = ttk.Label(root, text=f" System Ready. Output: {self.output_dir}", 
                                bootstyle="secondary", relief="sunken", anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

if __name__ == "__main__":
    app = ttk.Window(themename="cosmo") 
    MainApp(app)
    app.mainloop()