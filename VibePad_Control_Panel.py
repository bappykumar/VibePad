#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  VibePad Control Panel v2.3.0 - Developed by Bappy Kumar
============================================================
  Modern Utility for Managing VibePad Notes
============================================================
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

class ControlPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VibePad Control Panel v2.3.0")
        self.root.geometry("400x500")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(False, False)
        
        # Center Screen
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-400)//2}+{(sh-500)//2}")

        # Header
        header = tk.Frame(self.root, bg="#4A90E2", height=120)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="VibePad", font=("Segoe UI", 28, "bold"), bg="#4A90E2", fg="white").pack(pady=(25, 0))
        tk.Label(header, text="Control Panel v2.3.0", font=("Segoe UI", 9, "bold"), bg="#4A90E2", fg="#E3F2FD").pack()

        # Content
        body = tk.Frame(self.root, bg="#FFFFFF", padx=40, pady=30)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(body, text="Management Actions", font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#999999").pack(pady=(0, 15))

        self.create_button(body, "🚀  Launch VibePad", "#4CAF50", self.launch_app)
        self.create_button(body, "⚙️  Enable Auto-Start", "#2196F3", self.setup_auto)
        self.create_button(body, "❌  Disable Auto-Start", "#757575", self.remove_auto)
        self.create_button(body, "🗑️  Cleanup & Reset", "#FF5252", self.clean_data)

        # Help Section
        help_f = tk.Frame(body, bg="#F9F9F9", padx=15, pady=15, highlightthickness=1, highlightbackground="#EEEEEE")
        help_f.pack(fill=tk.X, pady=(20, 0))
        tk.Label(help_f, text="Need help? Check the README.md or visit the community.", 
                 font=("Segoe UI", 8), bg="#F9F9F9", fg="#666666", wraplength=280, justify="left").pack()

        # Footer
        tk.Label(self.root, text="© 2026 VibePad Project. All rights reserved.", font=("Segoe UI", 8), bg="#FFFFFF", fg="#CCCCCC").pack(pady=15)

    def create_button(self, parent, text, color, cmd):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"), bg=color, fg="white", 
                        relief="flat", pady=12, cursor="hand2", command=cmd)
        btn.pack(fill=tk.X, pady=8)
        btn.bind("<Enter>", lambda e: btn.configure(bg=self.darken(color)))
        btn.bind("<Leave>", lambda e: btn.configure(bg=color))

    def darken(self, hex_c):
        hex_c = hex_c.lstrip('#')
        rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
        return '#%02x%02x%02x' % tuple(max(0, int(c*0.8)) for c in rgb)

    def launch_app(self):
        script = "VibePad.py"
        if os.path.exists(script):
            try:
                subprocess.Popen(["pythonw", script], shell=True)
                # Keep control panel open as per user request
            except Exception as e:
                messagebox.showerror("Error", f"Could not launch VibePad: {e}")
        else:
            messagebox.showerror("Error", "VibePad.py not found!")

    def setup_auto(self):
        bat = "setup_autostart.bat"
        if os.path.exists(bat):
            try:
                subprocess.Popen([bat], shell=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not run setup: {e}")
        else:
            messagebox.showerror("Error", f"{bat} not found!")

    def clean_data(self):
        bat = "VibePad_Cleaner.bat"
        if os.path.exists(bat):
            if messagebox.askyesno("Confirm Reset", "This will close VibePad and PERMANENTLY delete all notes.\n\nAre you sure you want to proceed?"):
                try:
                    subprocess.Popen([bat], shell=True)
                    self.root.destroy() # Close control panel on Cleanup & Reset
                except Exception as e:
                    messagebox.showerror("Error", f"Could not run cleaner: {e}")
        else:
            messagebox.showerror("Error", f"{bat} not found!")

    def remove_auto(self):
        bat = "remove_autostart.bat"
        if os.path.exists(bat):
            try:
                subprocess.Popen([bat], shell=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not run removal: {e}")
        else:
            messagebox.showerror("Error", f"{bat} not found!")

if __name__ == "__main__":
    cp = ControlPanel()
    cp.root.mainloop()
