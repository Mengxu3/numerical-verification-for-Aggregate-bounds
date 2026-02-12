# 文件名: tab_bounds.py
import os
import threading
import datetime # <--- 新增
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    import tkinter as ttk
    from tkinter import messagebox
    from tkinter.constants import *

import matrix_utils as utils
import theorem_texts as txt

class BoundsTab:
    def __init__(self, notebook, output_dir):
        self.output_dir = output_dir
        self.frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Theorem 1.4: Bounds")
        self.init_ui()

    def init_ui(self):
        paned = ttk.Panedwindow(self.frame, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=True)
        
        left_panel = ttk.Frame(paned, width=380)
        paned.add(left_panel, weight=1)
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=3)

        # Right
        desc_frame = ttk.Labelframe(right_panel, text="Theorem Description & Legend", padding=10)
        desc_frame.pack(fill=X, padx=5, pady=5)
        lbl_desc = ttk.Label(desc_frame, text=txt.THM1_4_DESC, wraplength=850, font=("Consolas", 10))
        lbl_desc.pack(anchor=W)

        latex_frame = ttk.Frame(right_panel)
        latex_frame.pack(fill=X, padx=5, pady=2)
        self.fig_latex = Figure(figsize=(8, 1), dpi=100)
        try: self.fig_latex.patch.set_facecolor('#f8f9fa') 
        except: pass
        ax_lat = self.fig_latex.add_subplot(111)
        ax_lat.axis('off')
        ax_lat.text(0.5, 0.5, txt.THM1_4_LATEX, fontsize=13, ha='center', va='center')
        self.canvas_latex = FigureCanvasTkAgg(self.fig_latex, master=latex_frame)
        self.canvas_latex.draw()
        self.canvas_latex.get_tk_widget().pack(fill=BOTH, expand=True)

        plot_frame = ttk.Labelframe(right_panel, text="Visualization Result", padding=5)
        plot_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.fig_plot = Figure(figsize=(5, 4), dpi=100)
        self.canvas_plot = FigureCanvasTkAgg(self.fig_plot, master=plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill=BOTH, expand=True)

        # Left
        ctrl_frame = ttk.Labelframe(left_panel, text="Single Check", padding=10)
        ctrl_frame.pack(fill=X, padx=5, pady=5)
        ttk.Label(ctrl_frame, text="Matrix Dimension (n):").pack(anchor=W)
        self.spin_n = ttk.Spinbox(ctrl_frame, from_=3, to=15)
        self.spin_n.set(6)
        self.spin_n.pack(fill=X, pady=5)
        
        # 按钮文案更新
        ttk.Button(ctrl_frame, text="Generate & Save Plot", bootstyle="primary", 
                   command=self.run_single).pack(fill=X, pady=10)

        mass_frame = ttk.Labelframe(left_panel, text="Massive Validation", padding=10)
        mass_frame.pack(fill=X, padx=5, pady=20)
        ttk.Label(mass_frame, text="Iterations (N):").pack(anchor=W)
        self.spin_iter = ttk.Spinbox(mass_frame, from_=100, to=100000, increment=100)
        self.spin_iter.set(1000)
        self.spin_iter.pack(fill=X, pady=5)
        self.btn_mass = ttk.Button(mass_frame, text="Run Massive Test", bootstyle="danger-outline", 
                                   command=self.run_massive_thread)
        self.btn_mass.pack(fill=X, pady=10)
        self.progress = ttk.Progressbar(mass_frame, bootstyle="success-striped")
        self.progress.pack(fill=X, pady=5)
        self.lbl_result = ttk.Label(mass_frame, text="Status: Idle", font=("Consolas", 10))
        self.lbl_result.pack(fill=X)

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def run_single(self):
        try:
            n = int(self.spin_n.get())
            passed, sub_sum, lb, ub = utils.check_bounds_theorem(n, 1, n-2) 
            # 注意：上面的 utils.check_bounds_theorem 返回值比较简单
            # 为了画出你之前那个漂亮的“所有窗口”图，我们需要在本地重写一下逻辑，或者只画一个窗口
            # 鉴于 Tab 1 之前的逻辑是画所有窗口，我们保持原样：

            A = utils.generate_hermitian(n)
            lambdas = np.linalg.eigvalsh(A)[::-1]
            sub_eigs = []
            idx_list = list(range(n))
            for k in range(n):
                keep = [i for i in idx_list if i != k]
                sub_eigs.append(np.linalg.eigvalsh(A[np.ix_(keep, keep)])[::-1])
            sub_eigs = np.array(sub_eigs)

            windows = [(l, r) for l in range(n-1) for r in range(l, n-1)][::max(1, (n*n)//12)]
            
            self.fig_plot.clear()
            ax = self.fig_plot.add_subplot(111)
            
            for i, (l_idx, r_idx) in enumerate(windows):
                l, r = l_idx + 1, r_idx + 1
                actual = np.sum(sub_eigs[:, l_idx:r_idx+1])
                term_lam = np.sum(lambdas[l_idx : r_idx+1])
                term_lam_next = np.sum(lambdas[l_idx+1 : r_idx+2])
                
                lb = (r - l + 1) * lambdas[l_idx] + (n - 1) * term_lam_next
                ub = (n - 1) * term_lam + (r - l + 1) * lambdas[r_idx+1]
                
                ax.vlines(i, lb, ub, colors='gray', alpha=0.5, linewidth=2)
                ax.plot(i, ub, '_', color='blue', markeredgewidth=2, markersize=10)
                ax.plot(i, lb, '_', color='blue', markeredgewidth=2, markersize=10)
                ax.plot(i, actual, 'o', color='#d62728', markersize=6, zorder=3)

            ax.set_xticks(range(len(windows)))
            ax.set_xticklabels([f"[{l+1},{r+1}]" for l,r in windows], rotation=45, fontsize=8)
            ax.set_title(f"Bounds Verification (n={n})")
            ax.set_ylabel("Sum")
            self.fig_plot.tight_layout()
            self.canvas_plot.draw()
            
            # --- 保存逻辑 ---
            filename = f"Bounds_Check_n{n}_{self.get_timestamp()}.png"
            path = os.path.join(self.output_dir, filename)
            self.fig_plot.savefig(path, dpi=150)
            print(f"[Output] Plot saved to: {os.path.abspath(path)}")
            
        except Exception as e:
            print(e)

    def run_massive_thread(self):
        threading.Thread(target=self.run_massive, daemon=True).start()

    def run_massive(self):
        try:
            N = int(self.spin_iter.get())
            n = int(self.spin_n.get())
            self.btn_mass.config(state="disabled")
            self.lbl_result.config(text="Running...", bootstyle="warning")
            self.progress['value'] = 0
            
            passed_count = 0
            for i in range(N):
                l = np.random.randint(1, n)
                r = np.random.randint(l, n)
                is_pass, _, _, _ = utils.check_bounds_theorem(n, l, r)
                if is_pass: passed_count += 1
                if i % 10 == 0: self.progress['value'] = i
            
            self.progress['value'] = N
            res = f"Passed: {passed_count}/{N}"
            self.lbl_result.config(text=res, bootstyle="success" if passed_count==N else "danger")
        except Exception as e:
            self.lbl_result.config(text=str(e))
        finally:
            self.btn_mass.config(state="normal")