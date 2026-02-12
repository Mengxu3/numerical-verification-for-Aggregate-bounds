# 文件名: tab_hierarchy.py
import os
import threading
import datetime # <--- 新增
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.special import comb

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.tableview import Tableview
except ImportError:
    import tkinter as ttk
    from tkinter import messagebox
    from tkinter.constants import *

import matrix_utils as utils
import theorem_texts as txt

class HierarchyTab:
    def __init__(self, notebook, output_dir):
        self.output_dir = output_dir
        self.frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Theorem 4.1: Hierarchy")
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
        lbl_desc = ttk.Label(desc_frame, text=txt.THM4_1_DESC, wraplength=850, font=("Consolas", 10))
        lbl_desc.pack(anchor=W)
        
        latex_frame = ttk.Frame(right_panel)
        latex_frame.pack(fill=X, padx=5, pady=2)
        self.fig_latex = Figure(figsize=(8, 1), dpi=100)
        try: self.fig_latex.patch.set_facecolor('#f8f9fa')
        except: pass
        ax_lat = self.fig_latex.add_subplot(111)
        ax_lat.axis('off')
        ax_lat.text(0.5, 0.5, txt.THM4_1_LATEX, fontsize=14, ha='center', va='center')
        self.canvas_latex = FigureCanvasTkAgg(self.fig_latex, master=latex_frame)
        self.canvas_latex.draw()
        self.canvas_latex.get_tk_widget().pack(fill=BOTH, expand=True)

        plot_frame = ttk.Labelframe(right_panel, text="Single Visualization", padding=5)
        plot_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.fig_plot = Figure(figsize=(5, 4), dpi=100)
        self.canvas_plot = FigureCanvasTkAgg(self.fig_plot, master=plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill=BOTH, expand=True)

        # Left
        ctrl_frame = ttk.Labelframe(left_panel, text="Single Check", padding=10)
        ctrl_frame.pack(fill=X, padx=5, pady=5)
        ttk.Label(ctrl_frame, text="Dimension (n):").pack(anchor=W)
        self.spin_n = ttk.Spinbox(ctrl_frame, from_=4, to=15)
        self.spin_n.set(6)
        self.spin_n.pack(fill=X, pady=5)
        
        ttk.Label(ctrl_frame, text="Larger Size (m):").pack(anchor=W)
        self.spin_m = ttk.Spinbox(ctrl_frame, from_=2, to=14)
        self.spin_m.set(5)
        self.spin_m.pack(fill=X, pady=5)
        
        ttk.Label(ctrl_frame, text="Smaller Size (k):").pack(anchor=W)
        self.spin_k = ttk.Spinbox(ctrl_frame, from_=1, to=13)
        self.spin_k.set(2)
        self.spin_k.pack(fill=X, pady=5)
        
        ttk.Button(ctrl_frame, text="Generate & Save Plot", bootstyle="success", 
                   command=self.run_single).pack(fill=X, pady=15)

        mass_frame = ttk.Labelframe(left_panel, text="Massive Range Scan", padding=10)
        mass_frame.pack(fill=X, padx=5, pady=20)
        
        row1 = ttk.Frame(mass_frame)
        row1.pack(fill=X, pady=2)
        ttk.Label(row1, text="Min n:", width=8).pack(side=LEFT)
        self.spin_min_n = ttk.Spinbox(row1, from_=4, to=20, width=8)
        self.spin_min_n.set(4)
        self.spin_min_n.pack(side=LEFT, padx=5)

        row2 = ttk.Frame(mass_frame)
        row2.pack(fill=X, pady=2)
        ttk.Label(row2, text="Max n:", width=8).pack(side=LEFT)
        self.spin_max_n = ttk.Spinbox(row2, from_=4, to=20, width=8)
        self.spin_max_n.set(8)
        self.spin_max_n.pack(side=LEFT, padx=5)
        
        ttk.Label(mass_frame, text="Samples per Dim:").pack(anchor=W, pady=(5,0))
        self.spin_iter = ttk.Spinbox(mass_frame, from_=100, to=10000, increment=100)
        self.spin_iter.set(500)
        self.spin_iter.pack(fill=X, pady=5)
        
        self.btn_mass = ttk.Button(mass_frame, text="Run Range Scan", bootstyle="danger-outline", 
                                   command=self.run_scan_thread)
        self.btn_mass.pack(fill=X, pady=10)
        
        self.progress = ttk.Progressbar(mass_frame, bootstyle="info-striped")
        self.progress.pack(fill=X, pady=5)
        self.lbl_result = ttk.Label(mass_frame, text="Status: Idle", font=("Consolas", 9))
        self.lbl_result.pack(fill=X)

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def run_single(self):
        try:
            n = int(self.spin_n.get())
            m = int(self.spin_m.get())
            k = int(self.spin_k.get())
            if k >= m or m >= n: return

            passed, v_left, v_right, viol = utils.check_hierarchy_theorem(n, m, k)
            
            self.fig_plot.clear()
            ax1 = self.fig_plot.add_subplot(111)
            ax1.plot(np.cumsum(v_left), label=f'Size {m}', color='#1f77b4', linewidth=2)
            ax1.plot(np.cumsum(v_right), label=f'Size {k}', color='#ff7f0e', linestyle='--', linewidth=2)
            ax1.fill_between(range(len(v_left)), np.cumsum(v_left), np.cumsum(v_right), color='green', alpha=0.1)
            ax1.set_title(f"Check n={n}, m={m}, k={k}")
            ax1.legend()
            self.fig_plot.tight_layout()
            self.canvas_plot.draw()
            
            # --- 保存逻辑 ---
            filename = f"Hierarchy_Check_n{n}_{self.get_timestamp()}.png"
            path = os.path.join(self.output_dir, filename)
            self.fig_plot.savefig(path, dpi=150)
            print(f"[Output] Plot saved to: {os.path.abspath(path)}")
            
        except Exception as e:
            print(e)

    def run_scan_thread(self):
        threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        try:
            min_n = int(self.spin_min_n.get())
            max_n = int(self.spin_max_n.get())
            samples = int(self.spin_iter.get())
            
            if min_n > max_n: return

            self.btn_mass.config(state="disabled")
            self.lbl_result.config(text="Scanning...", bootstyle="warning")
            
            report_data = []
            total_steps = (max_n - min_n + 1) * samples
            current_step = 0
            
            for n in range(min_n, max_n + 1):
                failures = 0
                max_violation = 0.0
                
                for i in range(samples):
                    if n < 3: break 
                    m = np.random.randint(2, n)
                    k = np.random.randint(1, m)
                    
                    passed, _, _, viol = utils.check_hierarchy_theorem(n, m, k)
                    
                    if not passed:
                        failures += 1
                        max_violation = max(max_violation, viol)
                    
                    current_step += 1
                    if current_step % 50 == 0:
                        progress_val = (current_step / total_steps) * 100
                        self.progress['value'] = progress_val
                        self.lbl_result.config(text=f"Testing n={n} ({i}/{samples})...")
                
                report_data.append((n, samples, failures, max_violation))

            self.progress['value'] = 100
            self.lbl_result.config(text="Scan Complete!", bootstyle="success")
            
            self.frame.after(0, lambda: self.show_report(report_data))
            
        except Exception as e:
            self.lbl_result.config(text=f"Error: {e}")
        finally:
            self.btn_mass.config(state="normal")

    def show_report(self, data):
        top = ttk.Toplevel()
        top.title("Massive Validation Report")
        top.geometry("600x400")
        
        ttk.Label(top, text="Statistical Summary", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        cols = ("Dimension (n)", "Samples", "Failures", "Max Violation")
        tree = ttk.Treeview(top, columns=cols, show="headings", height=15)
        
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor=CENTER, width=120)
            
        for row in data:
            n, total, fails, max_v = row
            tag = "fail" if fails > 0 else "pass"
            viol_str = f"{max_v:.2e}" if max_v > 0 else "0.0"
            tree.insert("", "end", values=(n, total, fails, viol_str), tags=(tag,))
        
        tree.tag_configure("fail", foreground="red")
        tree.tag_configure("pass", foreground="green")
        
        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)
        ttk.Button(top, text="Close", command=top.destroy, bootstyle="secondary").pack(pady=10)