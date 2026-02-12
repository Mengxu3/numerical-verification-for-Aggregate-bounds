# 文件名: tab_weighted.py
import os
import threading
import datetime # <--- 新增时间戳
import csv      # <--- 新增CSV导出
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

class WeightedTab:
    def __init__(self, notebook, output_dir):
        self.output_dir = output_dir
        self.frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.frame, text="Main Result: Weighted Bounds")
        self.init_ui()

    def init_ui(self):
        paned = ttk.Panedwindow(self.frame, orient=HORIZONTAL)
        paned.pack(fill=BOTH, expand=True)
        
        left_panel = ttk.Frame(paned, width=380)
        paned.add(left_panel, weight=1)
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=3)

        # Right
        desc_frame = ttk.Labelframe(right_panel, text="Theorem 2.2: Weighted Projection", padding=10)
        desc_frame.pack(fill=X, padx=5, pady=5)
        lbl_desc = ttk.Label(desc_frame, text=txt.THM2_2_DESC, wraplength=850, font=("Consolas", 10))
        lbl_desc.pack(anchor=W)

        latex_frame = ttk.Frame(right_panel)
        latex_frame.pack(fill=X, padx=5, pady=2)
        self.fig_latex = Figure(figsize=(8, 1.5), dpi=100)
        try: self.fig_latex.patch.set_facecolor('#f8f9fa')
        except: pass
        ax_lat = self.fig_latex.add_subplot(111)
        ax_lat.axis('off')
        ax_lat.text(0.5, 0.5, txt.THM2_2_LATEX, fontsize=13, ha='center', va='center')
        self.canvas_latex = FigureCanvasTkAgg(self.fig_latex, master=latex_frame)
        self.canvas_latex.draw()
        self.canvas_latex.get_tk_widget().pack(fill=BOTH, expand=True)

        plot_frame = ttk.Labelframe(right_panel, text="Verification Plot", padding=5)
        plot_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.fig_plot = Figure(figsize=(5, 4), dpi=100)
        self.canvas_plot = FigureCanvasTkAgg(self.fig_plot, master=plot_frame)
        self.canvas_plot.get_tk_widget().pack(fill=BOTH, expand=True)

        # Left Controls
        ctrl_frame = ttk.Labelframe(left_panel, text="Single Check (Normal Mode)", padding=10)
        ctrl_frame.pack(fill=X, padx=5, pady=5)
        ttk.Label(ctrl_frame, text="Dimension (n):").pack(anchor=W)
        self.spin_n = ttk.Spinbox(ctrl_frame, from_=5, to=20, command=self.update_window_limits)
        self.spin_n.set(8)
        self.spin_n.pack(fill=X, pady=5)
        
        ttk.Label(ctrl_frame, text="Window Start (l):").pack(anchor=W)
        self.spin_l = ttk.Spinbox(ctrl_frame, from_=1, to=10)
        self.spin_l.set(1)
        self.spin_l.pack(fill=X, pady=5)
        
        ttk.Label(ctrl_frame, text="Window End (r):").pack(anchor=W)
        self.spin_r = ttk.Spinbox(ctrl_frame, from_=1, to=10)
        self.spin_r.set(3)
        self.spin_r.pack(fill=X, pady=5)
        
        # 按钮文案改了一下，提示会保存
        ttk.Button(ctrl_frame, text="Generate & Save Plot", bootstyle="primary", 
                   command=self.run_single).pack(fill=X, pady=10)

        mass_frame = ttk.Labelframe(left_panel, text="Stress Test (Hell Mode)", padding=10)
        mass_frame.pack(fill=X, padx=5, pady=20)
        
        row1 = ttk.Frame(mass_frame)
        row1.pack(fill=X, pady=2)
        ttk.Label(row1, text="Min n:", width=8).pack(side=LEFT)
        self.spin_min_n = ttk.Spinbox(row1, from_=4, to=30, width=8)
        self.spin_min_n.set(5)
        self.spin_min_n.pack(side=LEFT, padx=5)

        row2 = ttk.Frame(mass_frame)
        row2.pack(fill=X, pady=2)
        ttk.Label(row2, text="Max n:", width=8).pack(side=LEFT)
        self.spin_max_n = ttk.Spinbox(row2, from_=4, to=30, width=8)
        self.spin_max_n.set(10)
        self.spin_max_n.pack(side=LEFT, padx=5)

        ttk.Label(mass_frame, text="Samples per Dim:").pack(anchor=W)
        self.spin_iter = ttk.Spinbox(mass_frame, from_=100, to=10000, increment=100)
        self.spin_iter.set(500)
        self.spin_iter.pack(fill=X, pady=5)
        
        ttk.Label(mass_frame, text="*Includes Repeated Roots & Zero Weights", 
                  font=("Arial", 8, "italic"), bootstyle="secondary").pack(anchor=W)
                  
        self.btn_mass = ttk.Button(mass_frame, text="Run Audit & Export CSV", bootstyle="danger-outline", 
                                   command=self.run_audit_thread)
        self.btn_mass.pack(fill=X, pady=10)
        self.progress = ttk.Progressbar(mass_frame, bootstyle="warning-striped")
        self.progress.pack(fill=X, pady=5)
        self.lbl_result = ttk.Label(mass_frame, text="Status: Idle", font=("Consolas", 10))
        self.lbl_result.pack(fill=X)

    def update_window_limits(self):
        try:
            n = int(self.spin_n.get())
            limit = max(1, n - 1)
            self.spin_l.configure(to=limit)
            self.spin_r.configure(to=limit)
        except: pass

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def run_single(self):
        try:
            n = int(self.spin_n.get())
            l = int(self.spin_l.get()) - 1
            r = int(self.spin_r.get()) - 1
            if l > r or r >= n: return

            passed, val, lb, ub, viol = utils.check_weighted_theorem(n, l, r, stress_mode=False)
            
            self.fig_plot.clear()
            ax = self.fig_plot.add_subplot(111)
            y_pos = 1
            ax.errorbar(val, y_pos, xerr=0, fmt='o', color='#d62728', markersize=10, label=r'Actual $\sum \mu$')
            ax.plot([lb, ub], [y_pos, y_pos], '|--', color='blue', linewidth=3, markersize=15, label='Theoretical Bounds')
            
            title_text = f"Check n={n}, Window=[{l+1}, {r+1}]\nLHS={lb:.4f} <= Actual={val:.4f} <= RHS={ub:.4f}"
            ax.set_title(title_text, fontsize=11)
            ax.set_yticks([])
            ax.legend(loc='upper right')
            margin = (ub - lb) * 0.2 if ub != lb else 0.5
            ax.set_xlim(lb - margin, ub + margin)
            ax.set_ylim(0.8, 1.2)
            self.fig_plot.tight_layout()
            self.canvas_plot.draw()

            # --- 导出逻辑 ---
            # 1. 构造文件名 (带时间戳)
            filename = f"Weighted_Check_n{n}_w{l+1}-{r+1}_{self.get_timestamp()}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # 2. 保存
            self.fig_plot.savefig(filepath, dpi=150)
            
            # 3. 严格遵守你的规则：显示绝对路径
            abs_path = os.path.abspath(filepath)
            print(f"[Output] Plot saved to: {abs_path}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_audit_thread(self):
        threading.Thread(target=self.run_audit, daemon=True).start()

    def run_audit(self):
        try:
            min_n = int(self.spin_min_n.get())
            max_n = int(self.spin_max_n.get())
            samples = int(self.spin_iter.get())
            if min_n > max_n: return

            self.btn_mass.config(state="disabled")
            self.lbl_result.config(text="Running Stress Test...", bootstyle="warning")
            
            report_data = []
            total_steps = (max_n - min_n + 1) * samples
            current_step = 0
            
            for n in range(min_n, max_n + 1):
                failures = 0
                max_viol = 0.0
                
                for i in range(samples):
                    if n < 2: break
                    limit = n - 1
                    l = np.random.randint(0, limit)
                    r = np.random.randint(l, limit)
                    
                    is_pass, _, _, _, viol = utils.check_weighted_theorem(n, l, r, stress_mode=True)
                    
                    if not is_pass:
                        failures += 1
                        max_viol = max(max_viol, viol)
                    
                    current_step += 1
                    if current_step % 50 == 0:
                        self.progress['value'] = (current_step / total_steps) * 100
                        self.lbl_result.config(text=f"Stress Testing n={n}...")
                
                report_data.append((n, samples, failures, max_viol))
            
            self.progress['value'] = 100
            
            # --- 导出 CSV 逻辑 ---
            csv_filename = f"Audit_Report_{self.get_timestamp()}.csv"
            csv_path = os.path.join(self.output_dir, csv_filename)
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Dimension (n)", "Samples", "Failures", "Max Violation"])
                for row in report_data:
                    writer.writerow(row)
            
            # 打印绝对路径
            abs_csv_path = os.path.abspath(csv_path)
            print(f"[Output] Audit data saved to: {abs_csv_path}")
            
            self.lbl_result.config(text="Audit Complete & Saved!", bootstyle="success")
            self.frame.after(0, lambda: self.show_report(report_data))
            
        except Exception as e:
            self.lbl_result.config(text=f"Error: {e}")
            messagebox.showerror("Audit Error", str(e))
        finally:
            self.btn_mass.config(state="normal")

    def show_report(self, data):
        top = ttk.Toplevel()
        top.title("Stress Test Report")
        top.geometry("600x400")
        ttk.Label(top, text="Hell Mode Audit Results", font=("Helvetica", 14, "bold")).pack(pady=10)
        
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