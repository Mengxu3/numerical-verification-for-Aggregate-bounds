# 文件名: tab_lemma.py
import os
import threading
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    import tkinter as ttk
    from tkinter.constants import *
from tkinter import messagebox 

import matrix_utils as utils
import theorem_texts as txt

class LemmaTab:
    def __init__(self, notebook, output_dir):
        self.output_dir = output_dir
        self.frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Lemma 3.1: Polynomial")
        self.init_ui()

    def init_ui(self):
        paned = ttk.Panedwindow(self.frame, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=True)
        
        left_panel = ttk.Frame(paned, width=380)
        paned.add(left_panel, weight=1)
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=3)

        # Right: Description
        desc_frame = ttk.Labelframe(right_panel, text="Lemma 3.1: Roots Representation", padding=10)
        desc_frame.pack(fill=X, padx=5, pady=5)
        ttk.Label(desc_frame, text=txt.LEMMA3_1_DESC, wraplength=850, font=("Consolas", 10)).pack(anchor=W)

        # LaTeX
        latex_frame = ttk.Frame(right_panel)
        latex_frame.pack(fill=X, padx=5, pady=2)
        self.fig_latex = Figure(figsize=(8, 1), dpi=100)
        try: self.fig_latex.patch.set_facecolor('#f8f9fa')
        except: pass
        ax_lat = self.fig_latex.add_subplot(111)
        ax_lat.axis('off')
        ax_lat.text(0.5, 0.5, txt.LEMMA3_1_LATEX, fontsize=14, ha='center', va='center')
        self.canvas_latex = FigureCanvasTkAgg(self.fig_latex, master=latex_frame)
        self.canvas_latex.draw()
        self.canvas_latex.get_tk_widget().pack(fill=BOTH, expand=True)

        # Plot
        plot_frame = ttk.Labelframe(right_panel, text="Polynomial Roots Visualization", padding=5)
        plot_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.fig_plot = Figure(figsize=(5, 4), dpi=100)
        self.canvas_plot = FigureCanvasTkAgg(self.fig_plot, master=plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill=BOTH, expand=True)

        # Left: Controls
        ctrl_frame = ttk.Labelframe(left_panel, text="Visualization", padding=10)
        ctrl_frame.pack(fill=X, padx=5, pady=5)
        
        ttk.Label(ctrl_frame, text="Dimension (n):").pack(anchor=W)
        self.spin_n = ttk.Spinbox(ctrl_frame, from_=3, to=8) # 多项式画图不宜过高维，否则震荡太大
        self.spin_n.set(5)
        self.spin_n.pack(fill=X, pady=5)
        
        ttk.Button(ctrl_frame, text="Generate & Plot", bootstyle="info", 
                   command=self.run_single).pack(fill=X, pady=10)

        # Audit
        mass_frame = ttk.Labelframe(left_panel, text="Hell Mode Audit", padding=10)
        mass_frame.pack(fill=X, padx=5, pady=20)
        
        ttk.Label(mass_frame, text="Samples:").pack(anchor=W)
        self.spin_iter = ttk.Spinbox(mass_frame, from_=100, to=10000, increment=100)
        self.spin_iter.set(1000)
        self.spin_iter.pack(fill=X, pady=5)
        
        ttk.Button(mass_frame, text="Run Audit", bootstyle="danger-outline", 
                   command=self.run_audit_thread).pack(fill=X, pady=10)
        
        self.progress = ttk.Progressbar(mass_frame, bootstyle="info-striped")
        self.progress.pack(fill=X, pady=5)
        self.lbl_result = ttk.Label(mass_frame, text="Status: Idle", font=("Consolas", 10))
        self.lbl_result.pack(fill=X)

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def run_single(self):
        try:
            n = int(self.spin_n.get())
            passed, lambdas, mus, poly_func, x_rng, _ = utils.check_lemma_polynomial(n, stress_mode=False)
            
            self.fig_plot.clear()
            ax = self.fig_plot.add_subplot(111)
            
            # 画多项式曲线
            x_vals = np.linspace(x_rng[0], x_rng[1], 400)
            y_vals = poly_func(x_vals)
            ax.plot(x_vals, y_vals, label=r'$P(x)$', color='black', linewidth=1.5)
            
            # 画零轴
            ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
            
            # 标记原特征值 lambda (极点/间隔点)
            ax.plot(lambdas, np.zeros_like(lambdas), 'x', color='blue', markersize=8, label=r'$\lambda$ (Original)')
            
            # 标记几何特征值 mu (应该在零点)
            ax.plot(mus, np.zeros_like(mus), 'o', color='red', markersize=8, label=r'$\mu$ (Projected)')
            
            ax.set_title(f"Lemma 3.1 Check (n={n})")
            ax.legend()
            ax.grid(alpha=0.3)
            
            self.fig_plot.tight_layout()
            self.canvas_plot.draw()
            
            # 保存
            filename = f"Lemma31_Check_n{n}_{self.get_timestamp()}.png"
            path = os.path.join(self.output_dir, filename)
            self.fig_plot.savefig(path, dpi=150)
            print(f"[Output] Lemma Plot saved to: {os.path.abspath(path)}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_audit_thread(self):
        threading.Thread(target=self.run_audit, daemon=True).start()

    def run_audit(self):
        try:
            N = int(self.spin_iter.get())
            self.lbl_result.config(text="Auditing...", bootstyle="warning")
            self.progress['value'] = 0
            
            passed_cnt = 0
            max_global_res = 0.0
            
            for i in range(N):
                # 随机 n
                n = np.random.randint(3, 10)
                is_pass, _, _, _, _, res = utils.check_lemma_polynomial(n, stress_mode=True)
                if is_pass: passed_cnt += 1
                max_global_res = max(max_global_res, res)
                
                if i % 50 == 0: self.progress['value'] = (i/N)*100
            
            self.progress['value'] = 100
            res_str = f"Pass: {passed_cnt}/{N}\nMax Res: {max_global_res:.2e}"
            self.lbl_result.config(text=res_str, bootstyle="success" if passed_cnt==N else "danger")
            
        except Exception as e:
            self.lbl_result.config(text=str(e))