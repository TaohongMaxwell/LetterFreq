import ctypes
import string
import tkinter as tk
from collections import Counter
from tkinter import messagebox, filedialog, ttk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class LetterFrequencyAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Letter Frequency Analyzer")
        self.root.state('zoomed')
        self.root.minsize(750, 550)
        
        self.scale_factor = self._get_scale_factor()
        
        self.colors = {
            'bg': '#f5f5f5',
            'card': '#ffffff',
            'primary': '#2c5282',
            'primary_hover': '#1a365d',
            'text': '#1a202c',
            'text_secondary': '#4a5568',
            'border': '#e2e8f0',
            'grid': '#cbd5e0',
            'bar': '#4299e1',
            'bar_edge': '#2b6cb0'
        }
        
        self.root.configure(bg=self.colors['bg'])
        self._create_styles()
        self._create_ui()
        self._init_chart()
        
        self.results_df = None
        self.characters = list(string.ascii_lowercase) + list(string.digits) + list(string.punctuation)
    
    def _get_scale_factor(self):
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            return user32.GetDpiForSystem() / 96.0
        except:
            return 1.0
    
    def _create_styles(self):
        style = ttk.Style()
        font = ('Microsoft YaHei', int(10 * self.scale_factor))
        font_bold = ('Microsoft YaHei', int(10 * self.scale_factor), 'bold')
        font_title = ('Microsoft YaHei', int(13 * self.scale_factor), 'bold')
        
        style.configure('Primary.TButton', font=font, padding=(12, 6))
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['text'], font=font)
        style.configure('Title.TLabel', background=self.colors['bg'], foreground=self.colors['text'], font=font_title)
        style.configure('Status.TLabel', background=self.colors['bg'], foreground=self.colors['text_secondary'], font=font)
    
    def _create_ui(self):
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        tk.Label(main, text="Letter Frequency Analyzer", 
                font=('Microsoft YaHei', int(15 * self.scale_factor), 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).pack(anchor='w')
        tk.Label(main, text="Analyze character frequency distribution in English text",
                font=('Microsoft YaHei', int(10 * self.scale_factor)),
                bg=self.colors['bg'], fg=self.colors['text_secondary']).pack(anchor='w', pady=(4, 12))
        
        self.paned = tk.PanedWindow(main, orient=tk.VERTICAL, bg=self.colors['bg'], sashwidth=10,
                                    sashrelief=tk.RAISED, sashcursor='sb_v_double_arrow')
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        self._create_input(self.paned)
        
        bottom_frame = tk.Frame(self.paned, bg=self.colors['bg'])
        self.paned.add(bottom_frame)
        
        self._create_controls(bottom_frame)
        self._create_results(bottom_frame)
        
        self.root.after(100, self._set_sash_position)
        self.root.after(150, self._set_results_sash)
    
    def _set_sash_position(self):
        self.paned.update_idletasks()
        total_h = self.paned.winfo_height()
        if total_h > 100:
            pos = int(total_h * 0.3)
            self.paned.sash_place(0, 0, pos)
        else:
            self.root.after(200, self._set_sash_position)
    
    def _set_results_sash(self):
        self.results_paned.update_idletasks()
        total_w = self.results_paned.winfo_width()
        if total_w > 400:
            self.results_paned.sash_place(0, 350, 0)
        else:
            self.root.after(200, self._set_results_sash)
    
    def _create_input(self, parent):
        frame = tk.Frame(parent, bg=self.colors['card'], highlightbackground=self.colors['border'], highlightthickness=1)
        parent.add(frame, minsize=150)
        
        inner = tk.Frame(frame, bg=self.colors['card'])
        inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        tk.Label(inner, text="Input Text", font=('Microsoft YaHei', int(11 * self.scale_factor), 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 8))
        
        container = tk.Frame(inner, bg=self.colors['card'])
        container.pack(fill=tk.BOTH, expand=True)
        
        self.text_input = tk.Text(container, bg='#fafafa', fg=self.colors['text'],
                                 insertbackground=self.colors['text'],
                                 selectbackground=self.colors['primary'], selectforeground='white',
                                 font=('Consolas', int(10 * self.scale_factor)),
                                 relief=tk.FLAT, padx=8, pady=8, wrap=tk.WORD,
                                 highlightbackground=self.colors['border'], highlightthickness=1)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.text_input.yview)
        self.text_input.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def _create_controls(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg'])
        frame.pack(fill=tk.X, pady=(0, 12))
        
        btn_style = {'font': ('Microsoft YaHei', int(10 * self.scale_factor)),
                    'relief': tk.FLAT, 'padx': 16, 'pady': 6, 'cursor': 'hand2'}
        
        analyze_btn = tk.Button(frame, text="Analyze", command=self.analyze_text,
                               bg=self.colors['primary'], fg='white', **btn_style)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 8))
        analyze_btn.bind('<Enter>', lambda e: analyze_btn.config(bg=self.colors['primary_hover']))
        analyze_btn.bind('<Leave>', lambda e: analyze_btn.config(bg=self.colors['primary']))
        
        export_btn = tk.Button(frame, text="Export", command=self.export_data,
                              bg=self.colors['primary'], fg='white', **btn_style)
        export_btn.pack(side=tk.LEFT, padx=(0, 8))
        export_btn.bind('<Enter>', lambda e: export_btn.config(bg=self.colors['primary_hover']))
        export_btn.bind('<Leave>', lambda e: export_btn.config(bg=self.colors['primary']))
        
        clear_btn = tk.Button(frame, text="Clear", command=self.clear_all,
                             bg='#ffffff', fg=self.colors['text'], **btn_style,
                             highlightbackground=self.colors['border'], highlightthickness=1)
        clear_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        reset_btn = tk.Button(frame, text="Reset Layout", command=self.reset_layout,
                             bg='#ffffff', fg=self.colors['text'], **btn_style,
                             highlightbackground=self.colors['border'], highlightthickness=1)
        reset_btn.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(frame, text="Ready", bg=self.colors['bg'],
                                    fg=self.colors['text_secondary'],
                                    font=('Microsoft YaHei', int(9 * self.scale_factor)))
        self.status_label.pack(side=tk.RIGHT)
    
    def _create_results(self, parent):
        self.results_paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, bg=self.colors['bg'], sashwidth=8,
                              sashrelief=tk.RAISED, sashcursor='sb_h_double_arrow')
        self.results_paned.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        
        table_frame = tk.Frame(self.results_paned, bg=self.colors['card'],
                              highlightbackground=self.colors['border'], highlightthickness=1)
        self.results_paned.add(table_frame, width=350)
        
        table_inner = tk.Frame(table_frame, bg=self.colors['card'])
        table_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        tk.Label(table_inner, text="Results", font=('Microsoft YaHei', int(11 * self.scale_factor), 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 8))
        
        self.table_output = tk.Text(table_inner, bg='#fafafa', fg=self.colors['text'],
                                   font=('Consolas', int(9 * self.scale_factor)),
                                   relief=tk.FLAT, padx=8, pady=8, wrap=tk.NONE,
                                   highlightbackground=self.colors['border'], highlightthickness=1)
        table_scroll = ttk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.table_output.yview)
        self.table_output.configure(yscrollcommand=table_scroll.set)
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.table_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        chart_frame = tk.Frame(self.results_paned, bg=self.colors['card'],
                              highlightbackground=self.colors['border'], highlightthickness=1)
        self.results_paned.add(chart_frame)
        
        chart_inner = tk.Frame(chart_frame, bg=self.colors['card'])
        chart_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        tk.Label(chart_inner, text="Distribution", font=('Microsoft YaHei', int(11 * self.scale_factor), 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(0, 8))
        
        self.chart_frame = tk.Frame(chart_inner, bg=self.colors['card'])
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
    
    def _init_chart(self):
        plt.rcParams.update({
            'font.sans-serif': ['Microsoft YaHei', 'Arial'],
            'axes.unicode_minus': False,
            'figure.facecolor': self.colors['card'],
            'axes.facecolor': '#ffffff',
            'axes.edgecolor': self.colors['border'],
            'axes.grid': True,
            'grid.color': self.colors['grid'],
            'grid.linestyle': '--',
            'grid.alpha': 0.5,
            'text.color': self.colors['text'],
            'axes.labelcolor': self.colors['text'],
            'xtick.color': self.colors['text_secondary'],
            'ytick.color': self.colors['text_secondary']
        })
        
        w = max(7, 7 * self.scale_factor)
        h = max(4, 4 * self.scale_factor)
        self.fig, self.ax = plt.subplots(figsize=(w, h))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.ax.text(0.5, 0.5, 'Enter text and click Analyze', ha='center', va='center',
                    transform=self.ax.transAxes, fontsize=max(10, int(11 * self.scale_factor)), color=self.colors['text_secondary'])
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
        self.fig.patch.set_facecolor(self.colors['card'])
        self.canvas.draw()
    
    def analyze_text(self):
        self.status_label.config(text="Analyzing...")
        self.root.update()
        
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            self.status_label.config(text="Error: Enter text")
            messagebox.showwarning("Warning", "Please enter text to analyze!")
            return
        
        all_chars = string.ascii_lowercase + string.digits + string.punctuation
        char_counts = Counter(c for c in text.lower() if c in all_chars)
        total = sum(char_counts.values())
        
        if total == 0:
            self.status_label.config(text="No valid characters")
            messagebox.showinfo("Info", "No valid letters, digits or symbols found!")
            return
        
        pct = [char_counts.get(c, 0) / total for c in self.characters]
        self.results_df = pd.DataFrame({'Character': self.characters, 'Normalized': pct})
        
        self.display_results()
        self.update_chart()
        self.status_label.config(text=f"Done | {total} characters")
    
    def display_results(self):
        self.table_output.delete(1.0, tk.END)
        header = f"{'Char':^6} | {'Value':^12}\n" + "=" * 22 + "\n"
        self.table_output.insert(tk.END, header)
        
        for i, row in self.results_df.iterrows():
            if row['Character'] == '0':
                self.table_output.insert(tk.END, "-" * 22 + "\n")
            elif row['Character'] == '!' and i > 0 and self.results_df.iloc[i-1]['Character'] == '9':
                self.table_output.insert(tk.END, "-" * 22 + "\n")
            
            if row['Normalized'] > 0:
                self.table_output.insert(tk.END, f"  {row['Character']:<4} | {row['Normalized']:.6f}\n")
    
    def update_chart(self):
        self.ax.clear()
        
        if self.results_df is None or self.results_df['Normalized'].sum() == 0:
            self.ax.text(0.5, 0.5, 'No data', ha='center', va='center',
                        transform=self.ax.transAxes, fontsize=11, color=self.colors['text_secondary'])
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.axis('off')
        else:
            chars = list(self.results_df['Character'])
            values = list(self.results_df['Normalized'])
            
            fs_label = max(6, int(8 * self.scale_factor))
            fs_title = max(8, int(11 * self.scale_factor))
            
            x = range(len(chars))
            self.ax.bar(x, values, width=1.0, color=self.colors['bar'], edgecolor=self.colors['bar_edge'], linewidth=0.3, alpha=0.7)
            
            self.ax.plot(x, values, color=self.colors['primary'], linewidth=1.5, marker='o', markersize=3, markerfacecolor=self.colors['primary'], markeredgecolor='white', markeredgewidth=0.5, zorder=5)
            
            self.ax.set_xlabel('Character', fontsize=fs_label)
            self.ax.set_ylabel('Probability (0-1)', fontsize=fs_label)
            self.ax.set_title('Character Frequency Distribution', fontsize=fs_title, fontweight='bold')
            
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(chars, fontsize=fs_label, rotation=45, ha='center')
            
            self.ax.set_xlim(-0.5, len(chars) - 0.5)
            
            for i, c in enumerate(chars):
                if c == '0':
                    self.ax.axvline(x=i - 0.5, color='#e53e3e', linewidth=2, linestyle='-', alpha=0.8)
                elif c == '!':
                    if i > 0 and chars[i-1] == '9':
                        self.ax.axvline(x=i - 0.5, color='#e53e3e', linewidth=2, linestyle='-', alpha=0.8)
            
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            
            self.ax.set_ylim(0, max(values) * 1.15 if max(values) > 0 else 1)
        
        self.fig.patch.set_facecolor(self.colors['card'])
        self.fig.tight_layout()
        self.canvas.draw()
    
    def export_data(self):
        if self.results_df is None:
            self.status_label.config(text="Analyze first")
            messagebox.showwarning("Warning", "Please analyze text first!")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV", "*.csv")], title="Save Results")
        
        if file_path:
            try:
                chars = list(self.results_df['Character'])
                values = list(self.results_df['Normalized'])
                
                df = pd.DataFrame([
                    ['Index', 'Curve'] + chars,
                    ['---', '---'] + ['---'] * len(chars),
                    ['1', 'Letter_Freq'] + [f'{v:.6f}' for v in values]
                ])
                df.to_csv(file_path, index=False, header=False, encoding='utf-8')
                
                self.status_label.config(text=f"Exported")
                messagebox.showinfo("Success", f"Saved to:\n{file_path}")
            except Exception as e:
                self.status_label.config(text="Export failed")
                messagebox.showerror("Error", f"Failed:\n{str(e)}")
    
    def clear_all(self):
        self.text_input.delete(1.0, tk.END)
        self.table_output.delete(1.0, tk.END)
        
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'Enter text and click Analyze', ha='center', va='center',
                    transform=self.ax.transAxes, fontsize=max(10, int(11 * self.scale_factor)), color=self.colors['text_secondary'])
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.axis('off')
        self.fig.patch.set_facecolor(self.colors['card'])
        self.canvas.draw()
        
        self.results_df = None
        self.status_label.config(text="Ready")
    
    def reset_layout(self):
        self.paned.update_idletasks()
        total_h = self.paned.winfo_height()
        if total_h > 100:
            pos = int(total_h * 0.3)
            self.paned.sash_place(0, 0, pos)
        
        self.results_paned.update_idletasks()
        total_w = self.results_paned.winfo_width()
        if total_w > 400:
            self.results_paned.sash_place(0, 350, 0)

if __name__ == "__main__":
    root = tk.Tk()
    app = LetterFrequencyAnalyzer(root)
    root.mainloop()
