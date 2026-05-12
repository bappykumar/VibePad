#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  VibePad v3.0.0 - Developed by Bappy Kumar
============================================================
  Modern, Clean, and Professional Desktop Widget
============================================================
  License: MIT
  Copyright (c) 2026 Bappy Kumar
============================================================
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog
import json
import os
import sys
import time
import re
import subprocess
from datetime import datetime, timedelta
import calendar
from pathlib import Path
import webbrowser
from tkinter import messagebox
import threading
try:
    import winsound
except ImportError:
    winsound = None
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    import pystray
except ImportError:
    pystray = None
    ImageTk = None
    ImageFont = None

# High DPI Awareness & UTF-8 for Windows
if sys.platform == "win32":
    try:
        import ctypes
        # Set DPI Awareness
        ctypes.windll.shcore.SetProcessDpiAwareness(1) # PROCESS_SYSTEM_DPI_AWARE
        # Set Console UTF-8
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

# ============================================================
# Theme & Config
# ============================================================

APP_NAME = "VibePad"
APP_VERSION = "3.0.0"

if sys.platform == "win32":
    DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
else:
    DATA_DIR = Path.home() / ".config" / APP_NAME

DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_FILE = DATA_DIR / "notes.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Nostalgic-modern UI system
UI = {
    "ink": "#2F2A24",
    "muted": "#766F66",
    "paper": "#FFFCF3",
    "panel": "#FFF8E6",
    "line": "#D8C9A8",
    "accent": "#4979A9",
    "accent_dark": "#2F5F8F",
    "danger": "#B64236",
    "danger_soft": "#F8E7E3",
    "shadow": "#B9AD91",
    "menu_bg": "#FFF9EA",
    "menu_hover": "#E8D8B7",
}

# Modern Harmonious Color Palette
NOTE_COLORS = {
    "Vibe Yellow":  {"bg": "#FFF7BF", "header": "#F5D86A", "border": "#B99223", "text": UI["ink"]},
    "Soft Pink":    {"bg": "#FFE5EC", "header": "#F2AFC0", "border": "#B65C76", "text": UI["ink"]},
    "Mint Green":   {"bg": "#E8F3D1", "header": "#BFD991", "border": "#6B8D3F", "text": UI["ink"]},
    "Sky Blue":     {"bg": "#E2F0F6", "header": "#A8CDDD", "border": "#4B86A1", "text": UI["ink"]},
    "Sweet Orange": {"bg": "#FFE3BC", "header": "#F1B76E", "border": "#A86721", "text": UI["ink"]},
    "Pure White":   {"bg": "#FFFDF6", "header": "#E9DFC8", "border": "#A99B82", "text": UI["ink"]},
}

DEFAULT_WIDTH = 280
DEFAULT_HEIGHT = 300

AVAILABLE_FONTS = {
    "Handwriting": "Segoe Print",
    "Artistic":    "Segoe Script",
    "Modern":      "Segoe UI",
    "Clean":       "Calibri",
    "Code":        "Consolas",
    "Classic":     "Arial",
    "Bengali":     "Li Ador Noirrit",
}

FONT_UI = ("Segoe UI", 9)
FONT_UI_MEDIUM = ("Segoe UI Semibold", 9)
FONT_TITLE = ("Segoe UI Semibold", 9)
FONT_TIMER = ("Segoe UI Semibold", 30)
FONT_ICON = ("Segoe MDL2 Assets", 11)

ICONS = {
    "add": "\ue710",
    "check": "\ue73e",
    "close": "\ue711",
    "delete": "\ue74d",
    "info": "\ue946",
    "settings": "\ue713",
    "pin": "\ue718",
    "unpin": "\ue840",
    "reset": "\ue72c",
    "palette": "\ue790",
    "font": "\ue8d2",
    "size": "\ue8e8",
    "bell": "\ue7f4",
    "power": "\ue7e8",
    "clock": "\ue916",
    "note": "\ue70b",
    "calendar": "\ue787",
    "back": "\ue72b",
    "next": "\ue76c",
    "chevron": "\ue76c",
    "up": "\ue70e",
    "down": "\ue70d",
}

def icon(name):
    return ICONS.get(name, "")

def monitor_rect_for(widget):
    """Return the monitor work area that owns a Tk window."""
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", wintypes.LONG),
                    ("top", wintypes.LONG),
                    ("right", wintypes.LONG),
                    ("bottom", wintypes.LONG),
                ]

            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", RECT),
                    ("rcWork", RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            hwnd = widget.winfo_id()
            monitor = ctypes.windll.user32.MonitorFromWindow(hwnd, 2)  # MONITOR_DEFAULTTONEAREST
            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(MONITORINFO)
            ctypes.windll.user32.GetMonitorInfoW(monitor, ctypes.byref(info))
            return (info.rcWork.left, info.rcWork.top, info.rcWork.right, info.rcWork.bottom)
        except Exception:
            pass

    x = widget.winfo_rootx()
    y = widget.winfo_rooty()
    return (x, y, x + widget.winfo_screenwidth(), y + widget.winfo_screenheight())

def clamp_point_to_rect(x, y, width, height, rect, margin=8):
    left, top, right, bottom = rect
    return (
        min(max(left + margin, x), max(left + margin, right - width - margin)),
        min(max(top + margin, y), max(top + margin, bottom - height - margin)),
    )

# ============================================================
# Core Logic
# ============================================================

class NoteData:
    def __init__(self, **kwargs):
        self.note_id = kwargs.get("note_id") or f"note_{int(time.time()*1000)}"
        self.title = kwargs.get("title", "Sticky Note")
        self.content = kwargs.get("content", "")
        self.color_name = kwargs.get("color_name", "Vibe Yellow")
        self.x = kwargs.get("x", 100)
        self.y = kwargs.get("y", 100)
        self.width = kwargs.get("width", DEFAULT_WIDTH)
        self.height = kwargs.get("height", DEFAULT_HEIGHT)
        self.always_on_top = kwargs.get("always_on_top", True)
        self.is_checklist = kwargs.get("is_checklist", False)
        self.is_timer = kwargs.get("is_timer", False)
        self.font_name = kwargs.get("font_name", "Handwriting")
        self.font_size = kwargs.get("font_size", 11)
        self.reminder = kwargs.get("reminder") # Format: "YYYY-MM-DD HH:MM"
    
    def to_dict(self):
        return self.__dict__

class ModernMenu:
    def __init__(self, parent, x, y, bg=UI["menu_bg"], fg=UI["ink"], accent=UI["menu_hover"], border=UI["line"]):
        self.parent = parent
        self.bg = bg
        self.fg = fg
        self.accent = accent
        self.border = border
        self.requested_x = x + 2
        self.requested_y = y + 2
        
        self.root = tk.Toplevel(parent)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.0) 
        self.root.configure(bg=UI["shadow"], highlightthickness=0)
        
        # Premium Positioning
        self.root.geometry(f"+{self.requested_x}+{self.requested_y}")
        
        self.panel = tk.Frame(self.root, bg=bg, highlightthickness=1, highlightbackground=border)
        self.panel.pack(padx=(0, 3), pady=(0, 3))
        self.frame = tk.Frame(self.panel, bg=bg, padx=4, pady=7)
        self.frame.pack()
        
        self.sub_menu = None
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.focus_set()
        self.fade_in()

    def fade_in(self):
        try:
            curr = float(self.root.attributes("-alpha"))
            if curr < 0.98:
                self.root.attributes("-alpha", min(0.98, curr + 0.16))
                self.root.after(12, self.fade_in)
        except tk.TclError:
            pass

    def clamp_to_screen(self):
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        x, y = clamp_point_to_rect(self.requested_x, self.requested_y, w, h, monitor_rect_for(self.parent))
        self.root.geometry(f"+{x}+{y}")

    def on_focus_out(self, e):
        self.root.after(150, self._check_focus)

    def _check_focus(self):
        try:
            focus = self.root.focus_get()
            if self.sub_menu and self.sub_menu.root.winfo_exists():
                if focus == self.sub_menu.root: return
            if focus == self.root: return
            self.root.destroy()
        except: pass

    def add_item(self, label, command=None, icon="", cascade_data=None, danger=False):
        item_f = tk.Frame(self.frame, bg=self.bg, cursor="hand2")
        item_f.pack(fill=tk.X)
        
        item_f.grid_columnconfigure(1, weight=1, minsize=142)

        icon_text = icon
        icon_fg = UI["accent_dark"]
        icon_font = FONT_ICON
        label_font = FONT_UI
        if isinstance(icon, dict):
            icon_text = icon.get("text", "")
            icon_fg = icon.get("fg", icon_fg)
            icon_font = icon.get("font", icon_font)
            label_font = icon.get("label_font", label_font)
        
        # Icon Column (Fixed Width for Perfect Alignment)
        icon_lbl = tk.Label(item_f, text=icon_text, bg=self.bg, fg=icon_fg, 
                           font=icon_font, width=3, anchor="center")
        icon_lbl.grid(row=0, column=0, sticky="nsew", padx=(8, 4), pady=1)
        
        lbl = tk.Label(item_f, text=label, bg=self.bg, fg=self.fg, 
                       font=label_font, anchor="w", padx=6, pady=8)
        lbl.grid(row=0, column=1, sticky="nsew")
        
        arrow = None
        if cascade_data:
            arrow = tk.Label(item_f, text=ICONS["chevron"], bg=self.bg, fg=UI["muted"], font=FONT_ICON, width=2)
            arrow.grid(row=0, column=2, sticky="nsew", padx=(4, 8))

        def on_enter(e):
            # Only trigger if moving to a NEW item to avoid flickering
            if getattr(self, '_last_hovered', None) == item_f:
                return
            self._last_hovered = item_f

            # CLEANUP: Cancel pending open timers for OTHER items
            for item in self.frame.winfo_children():
                if item != item_f and hasattr(item, '_cascade_id') and item._cascade_id:
                    self.root.after_cancel(item._cascade_id)
                    item._cascade_id = None

            # Cancel this item's own leave timer
            if hasattr(item_f, '_leave_id') and item_f._leave_id:
                self.root.after_cancel(item_f._leave_id)
                item_f._leave_id = None

            # SET NEW STATE
            h_bg = UI["danger"] if danger else self.accent
            h_fg = "white" if danger else UI["ink"]
            item_f.configure(bg=h_bg)
            lbl.configure(bg=h_bg, fg=h_fg)
            icon_lbl.configure(bg=h_bg, fg="white" if danger else icon_fg)
            if arrow: arrow.configure(bg=h_bg, fg=h_fg)
            
            if self.sub_menu and self.sub_menu.root.winfo_exists():
                if getattr(self, '_active_item', None) != item_f:
                    self.sub_menu.root.destroy()
                    self.sub_menu = None

            if cascade_data:
                if getattr(self, '_active_item', None) != item_f:
                    self._active_item = item_f
                    item_f._cascade_id = self.root.after(100, lambda: self.show_cascade(item_f, cascade_data))
            
        def on_leave(e):
            # Cancel any pending open timer if we leave the item
            if cascade_data and hasattr(item_f, '_cascade_id') and item_f._cascade_id:
                self.root.after_cancel(item_f._cascade_id)
                item_f._cascade_id = None

            def do_leave():
                # Real-time pointer tracking for expert accuracy
                px, py = self.root.winfo_pointerxy()
                focus = self.root.winfo_containing(px, py)
                
                in_sub = False
                if self.sub_menu and self.sub_menu.root.winfo_exists():
                    sm = self.sub_menu.root
                    sx, sy = sm.winfo_rootx(), sm.winfo_rooty()
                    sw, sh = sm.winfo_width(), sm.winfo_height()
                    if sx <= px <= sx + sw and sy <= py <= sy + sh:
                        in_sub = True
                
                if focus not in [item_f, lbl, icon_lbl, arrow] and not in_sub:
                    self._last_hovered = None
                    item_f.configure(bg=self.bg)
                    lbl.configure(bg=self.bg, fg=self.fg)
                    icon_lbl.configure(bg=self.bg, fg=icon_fg)
                    if arrow: arrow.configure(bg=self.bg, fg=UI["muted"])
            
            item_f._leave_id = self.root.after(100, do_leave)

        targets = [item_f, lbl, icon_lbl]
        if arrow: targets.append(arrow)
        
        for widget in targets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            if command:
                widget.bind("<Button-1>", lambda e: self.execute(command))

    def show_cascade(self, parent_item, data):
        if self.sub_menu and self.sub_menu.root.winfo_exists():
            return 
        self.root.update_idletasks()
        
        # Default: open to the right
        x_right = self.root.winfo_rootx() + self.root.winfo_width() - 2
        y = parent_item.winfo_rooty() - 7
        
        self.sub_menu = ModernMenu(self.parent, x_right, y, bg=self.bg, fg=self.fg, accent=self.accent, border=self.border)
        for label, cmd, icon in data:
            if label == "---": self.sub_menu.add_separator()
            else: self.sub_menu.add_item(label, command=cmd, icon=icon)
            
        # Smart Edge Detection: flip to the left if it overflows the right monitor edge
        self.sub_menu.root.update_idletasks()
        sm_w = self.sub_menu.root.winfo_reqwidth()
        
        mon_rect = monitor_rect_for(self.parent)
        if mon_rect:
            left, top, right, bottom = mon_rect
            if x_right + sm_w > right - 8:
                x_left = self.root.winfo_rootx() - sm_w + 2
                self.sub_menu.requested_x = x_left
                
        self.sub_menu.clamp_to_screen()

    def add_separator(self):
        sep_f = tk.Frame(self.frame, bg=self.bg, height=1)
        sep_f.pack(fill=tk.X, pady=7)
        tk.Frame(sep_f, bg=self.border, height=1).pack(fill=tk.X, padx=10)

    def execute(self, command):
        try:
            if self.sub_menu: self.sub_menu.root.destroy()
            self.root.destroy()
            command()
        except Exception as e:
            print(f"Menu action error: {e}")

    def show(self):
        self.clamp_to_screen()
        self.root.lift()
        self.root.focus_set()



class StickyNote:
    def __init__(self, app, data: NoteData):
        self.app = app
        self.data = data
        self.theme = NOTE_COLORS.get(data.color_name, NOTE_COLORS["Vibe Yellow"])
        
        # Setup Window
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        if sys.platform == "win32":
            try:
                self.window.attributes("-toolwindow", True)
            except tk.TclError:
                pass
        self.window.attributes("-topmost", data.always_on_top)
        self.window.geometry(f"{data.width}x{data.height}+{data.x}+{data.y}")
        
        # Flags
        self._dragging = False
        self._resizing = False
        
        # Timer State
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_triggered = False
        self.reminder_triggered = False
        
        try:
            self.setup_ui()
            self.bind_events()
        except Exception as e:
            print(f"UI Error in note {data.note_id}: {e}")
            # Ensure the window is at least visible or destroyed safely
            if hasattr(self, 'window') and self.window.winfo_exists():
                self.window.destroy()

    def pin_visual(self):
        return ICONS["unpin"] if self.data.always_on_top else ICONS["pin"]
        
    def pin_color(self):
        return UI["accent_dark"] if self.data.always_on_top else self.theme["text"]

    def setup_ui(self):
        # Master Border
        self.root_frame = tk.Frame(self.window, bg=self.theme["border"], padx=1, pady=1)
        self.root_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main Container
        self.main_container = tk.Frame(self.root_frame, bg=self.theme["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Modern Header (Nostalgic System Style)
        self.header = tk.Frame(self.main_container, bg=self.theme["header"], height=34)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        # Pin Button
        self.pin_btn = tk.Label(self.header, text=self.pin_visual(), bg=self.theme["header"], 
                                fg=self.pin_color(), font=FONT_ICON, width=3, cursor="hand2")
        self.pin_btn.pack(side=tk.LEFT, padx=(6, 2), pady=2, fill=tk.Y)

        # Control Buttons (PACKED FIRST to ensure they never get pushed out)
        self.controls = tk.Frame(self.header, bg=self.theme["header"])
        self.controls.pack(side=tk.RIGHT, padx=(0, 8), pady=2, fill=tk.Y)
        
        self.add_btn = tk.Label(self.controls, text=ICONS["add"], bg=self.theme["header"], fg=self.theme["text"], 
                                font=FONT_ICON, width=3, cursor="hand2")
        self.add_btn.pack(side=tk.LEFT)

        # Title & Countdown Container (Expert Layout - Takes remaining space)
        self.title_f = tk.Frame(self.header, bg=self.theme["header"])
        self.title_f.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)
        
        # Countdown packed RIGHT inside title_f so it's always visible
        self.countdown_lbl = tk.Label(self.title_f, text="", bg=self.theme["header"], 
                                     fg=self.theme["text"], font=("Segoe UI Semibold", 9)) 
        self.countdown_lbl.pack(side=tk.RIGHT, padx=(12, 10))
        
        # Title takes remaining flexible space
        self.title_label = tk.Label(self.title_f, text=self.data.title, bg=self.theme["header"], 
                                   fg=self.theme["text"], font=FONT_TITLE, padx=0, anchor="w")
        self.title_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 5))
        
        # Smart Ellipsis & Tooltip Logic
        def update_title_ellipsis(event=None):
            if not hasattr(self, 'title_label') or not self.title_label.winfo_exists():
                return
            
            # Calculate available width (total minus countdown)
            cd_w = self.countdown_lbl.winfo_reqwidth() if self.countdown_lbl.cget("text") else 0
            max_w = self.title_f.winfo_width() - cd_w - 15
            if max_w < 20: return

            full_text = self.data.title
            font_obj = tk.font.Font(font=FONT_TITLE)
            
            if font_obj.measure(full_text) <= max_w:
                self.title_label.configure(text=full_text)
            else:
                ellipsis = "..."
                ell_w = font_obj.measure(ellipsis)
                truncated = full_text
                while len(truncated) > 1 and font_obj.measure(truncated) + ell_w > max_w:
                    truncated = truncated[:-1]
                self.title_label.configure(text=truncated + ellipsis)

        self.title_f.bind("<Configure>", update_title_ellipsis)
        self.update_title_ellipsis = update_title_ellipsis
        
        def show_title_tooltip(e):
            if self.title_label.cget("text") != self.data.title:
                self.tooltip = tk.Toplevel(self.window)
                self.tooltip.overrideredirect(True)
                self.tooltip.attributes("-topmost", True)
                x = e.x_root + 15
                y = e.y_root + 15
                self.tooltip.geometry(f"+{x}+{y}")
                lbl = tk.Label(self.tooltip, text=self.data.title, bg="#202020", fg="white", 
                               font=("Segoe UI", 9), padx=6, pady=4, relief="flat")
                lbl.pack()

        def hide_title_tooltip(e):
            if hasattr(self, 'tooltip') and self.tooltip.winfo_exists():
                self.tooltip.destroy()
                
        self.title_label.bind("<Enter>", show_title_tooltip, add="+")
        self.title_label.bind("<Leave>", hide_title_tooltip, add="+")
        self.title_label.bind("<Button-1>", hide_title_tooltip, add="+")

        
        
        # Font Configuration (Unified for all types)
        font_family = AVAILABLE_FONTS.get(self.data.font_name, "Segoe Print")
        size = self.data.font_size

        if self.data.is_timer:
            self.setup_timer_ui()
        else:
            # Standard Editor
            self.editor = tk.Text(self.main_container, bg=self.theme["bg"], fg=self.theme["text"],
                                 font=(font_family, size), wrap=tk.WORD, borderwidth=0,
                                 padx=16, pady=12, highlightthickness=0, insertbackground=self.theme["text"],
                                 selectbackground="#D8C7A1", selectforeground=self.theme["text"])
            self.editor.pack(fill=tk.BOTH, expand=True)
            self.editor.tag_configure("strike", overstrike=True)
            
        self.editor.tag_configure("tick_color", foreground="#2E7D32")
        self.editor.tag_configure("cross_color", foreground="#C62828")
        self.editor.tag_configure("strike_faded", overstrike=True, foreground=UI["muted"])
        self.editor.tag_configure("checklist_line", lmargin1=10, lmargin2=34, spacing1=6, spacing2=2, spacing3=6, tabs=(34,))
        
        # Markdown Tags
        self.editor.tag_configure("bold", font=(font_family, size, "bold"))
        self.editor.tag_configure("italic", font=(font_family, size, "italic"))
        self.editor.tag_configure("header", font=(font_family, size + 2, "bold"), foreground=self.theme["border"])
        self.editor.tag_configure("hidden", elide=True)
        self.editor.tag_configure("md_star", elide=True) # Dedicated tag for italic stars
        self.editor.tag_raise("hidden")
        self.editor.tag_raise("md_star")
        self.editor.tag_raise("hidden") # Ensure hidden is always higher priority
        
        # Initial content or checklist template
        content = self.data.content
        if not content and self.data.is_checklist:
            content = "☐ "
        self.editor.insert("1.0", content)
        
        if self.data.is_checklist:
            self.apply_checklist_tags()
        else:
            self.apply_markdown_tags()

        # Contextual Toolbar (Floating)
        self.setup_toolbar()

        # Resize Handle (Modern Triangle)
        self.handle = tk.Label(self.main_container, text="◢", bg=self.theme["bg"], 
                              fg=self.theme["border"], font=("Segoe UI", 11), cursor="size_nw_se")
        self.handle.place(relx=1.0, rely=1.0, anchor="se", x=-1, y=-1)
        
        self.update_colors()
        self.update_countdown()

    def update_colors(self):
        """Total UI Harmonization Pass: Ensuring no color bleed or mismatched blocks."""
        hover_bg = self.app.darken(self.theme["header"])
        
        # 1. Update backgrounds for all layout frames to prevent 'accent blocks'
        for frame in [self.header, self.title_f, self.controls]:
            frame.configure(bg=self.theme["header"])
            
        # 2. Update labels and buttons
        self.title_label.configure(bg=self.theme["header"], fg=self.theme["text"])
        self.countdown_lbl.configure(bg=self.theme["header"])
        self.add_btn.configure(bg=self.theme["header"], fg=self.theme["text"])
        self.pin_btn.configure(bg=self.theme["header"])

        # 3. Timer Interface Theme Sync
        if self.data.is_timer and hasattr(self, 'timer_main_f'):
            # Harmonize main containers
            for f in [self.timer_main_f, self.adjust_f, self.preset_f, self.action_f]:
                f.configure(bg=self.theme["bg"])
            
            # Sync pills and controls
            for pill in [self.min_pill, self.preset_pill]:
                pill.configure(bg=UI["panel"])
                
            self.time_display.configure(bg=self.theme["bg"], fg=self.theme["text"])
            self.timer_sep.configure(bg=self.theme["border"])
            
            # Action buttons
            self.start_btn.configure(bg=self.theme["border"])
            self.reset_btn.configure(bg=self.theme["bg"], fg=UI["muted"])
            
            # Collection sync for adjust/preset buttons
            for btn in getattr(self, 'timer_adj_btns', []) + getattr(self, 'timer_preset_btns', []):
                btn.configure(bg=UI["panel"], fg=UI["ink"], activebackground=self.theme["header"])

    def _on_btn_enter(self, btn):
        hover_bg = self.app.darken(self.theme["header"])
        btn.configure(bg=hover_bg)

    def _on_btn_leave(self, btn):
        btn.configure(bg=self.theme["header"])

    def _on_btn_press(self, btn):
        btn.configure(bg=self.theme["border"], fg="white")

    def _on_btn_release(self, btn):
        hover_bg = self.app.darken(self.theme["header"])
        btn.configure(bg=hover_bg, fg=self.theme["text"])

    def bind_events(self):
        """Expert-grade event orchestration."""
        # Header Interaction
        for w in [self.header, self.title_f, self.title_label, self.countdown_lbl]:
            w.bind("<Button-1>", self.start_move)
            w.bind("<B1-Motion>", self.do_move)
            w.bind("<ButtonRelease-1>", self.stop_move)
            w.bind("<Button-3>", self.show_menu)
        
        # Button Hover & Feedback (Clean, leak-free bindings)
        for btn in [self.add_btn, self.pin_btn]:
            btn.bind("<Enter>", lambda e, b=btn: self._on_btn_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self._on_btn_leave(b))
            btn.bind("<ButtonPress-1>", lambda e, b=btn: self._on_btn_press(b), add="+")
            btn.bind("<ButtonRelease-1>", lambda e, b=btn: self._on_btn_release(b), add="+")

        # Functional Bindings (The 'Logic' part)
        self.title_label.bind("<Double-Button-1>", self.edit_title, add="+")
        self.handle.bind("<Button-1>", self.start_resize, add="+")
        self.handle.bind("<B1-Motion>", self.do_resize, add="+")
        self.add_btn.bind("<Button-1>", self.show_plus_menu, add="+")
        self.pin_btn.bind("<Button-1>", self.toggle_pin, add="+")
        if hasattr(self, 'editor'):
            self.editor.bind("<Button-3>", self.show_menu)
            self.editor.bind("<KeyRelease>", self.on_text_change)
            self.editor.bind("<<Selection>>", self.on_selection)
            self.editor.bind("<Button-1>", self.on_click_text, add="+")
            
            if self.data.is_checklist:
                self.editor.bind("<Return>", self.handle_checklist_return)
                self.editor.bind("<Button-1>", self.handle_checklist_click, add="+")
            elif self.data.is_timer:
                pass # Timer note uses standard editor bindings above

            # Keyboard Shortcuts
            self.editor.bind("<Control-n>", lambda e: self.app.new_note())
            self.editor.bind("<Control-N>", lambda e: self.app.new_note())
            self.editor.bind("<Control-d>", lambda e: self.confirm_delete())
            self.editor.bind("<Control-D>", lambda e: self.confirm_delete())
            self.editor.bind("<Control-p>", lambda e: self.toggle_pin())
            self.editor.bind("<Control-P>", lambda e: self.toggle_pin())
        
        self.window.bind("<Configure>", lambda e: self.hide_toolbar()) # Hide when moving/resizing

    def start_move(self, e):
        self.x, self.y = e.x, e.y
        self.window.configure(cursor="fleur")

    def do_move(self, e):
        nx = self.window.winfo_x() + e.x - self.x
        ny = self.window.winfo_y() + e.y - self.y
        self.window.geometry(f"+{nx}+{ny}")
        self.hide_toolbar()

    def stop_move(self, e):
        self.window.configure(cursor="")
        self.data.x, self.data.y = self.window.winfo_x(), self.window.winfo_y()
        self.app.save()

    def start_resize(self, e):
        self.rw, self.rh = self.window.winfo_width(), self.window.winfo_height()
        self.rx, self.ry = e.x_root, e.y_root
        self.hide_toolbar()

    def do_resize(self, e):
        nw = max(200, self.rw + e.x_root - self.rx)
        nh = max(150, self.rh + e.y_root - self.ry)
        self.window.geometry(f"{nw}x{nh}")
        self.data.width, self.data.height = nw, nh
        self.app.save()

    def show_plus_menu(self, e):
        menu = ModernMenu(self.window, e.x_root, e.y_root)
        menu.add_item("New Note", lambda: self.app.new_note(False), ICONS["note"])
        menu.add_item("New Checklist", lambda: self.app.new_note(is_checklist=True), ICONS["check"])
        menu.add_item("New Timer", lambda: self.app.new_note(is_timer=True), ICONS["clock"])
        menu.show()


    def setup_timer_ui(self):
        """Universal Timer & Note Interface - Professional Unified Style"""
        self.main_container.configure(bg=self.theme["bg"])
        self.last_timer_seconds = getattr(self, 'last_timer_seconds', 0)
        
        # Main Timer Panel (Saved as reference for update_colors)
        self.timer_main_f = tk.Frame(self.main_container, bg=self.theme["bg"], pady=4)
        self.timer_main_f.pack(fill=tk.X, padx=12)
        
        def set_preset(mins):
            if not getattr(self, 'timer_running', False):
                self.timer_seconds = mins * 60
                self.last_timer_seconds = self.timer_seconds
                self.update_timer_display()
                self.start_btn.configure(text="START", bg=self.theme["border"])

        def adj(m=0):
            if not getattr(self, 'timer_running', False):
                self.timer_seconds = max(0, self.timer_seconds + (m*60))
                self.last_timer_seconds = self.timer_seconds
                self.update_timer_display()
                self.start_btn.configure(text="START", bg=self.theme["border"])

        # 1. Top Section: Large Countdown Display
        self.time_display = tk.Label(self.timer_main_f, text="00:00", font=("Segoe UI Semibold", 42), 
                                    bg=self.theme["bg"], fg=self.theme["text"], cursor="hand2")
        self.time_display.pack(pady=(0, 4))
        
        def on_scroll(e):
            if not getattr(self, 'timer_running', False):
                delta = 1 if e.delta > 0 else -1
                self.timer_seconds = max(0, self.timer_seconds + (delta * 60))
                self.last_timer_seconds = self.timer_seconds
                self.update_timer_display()
                self.start_btn.configure(text="START", bg=self.theme["border"])
                
        self.time_display.bind("<MouseWheel>", on_scroll)
        
        # 2. Middle Section: Minute Adjustment Controls (Centered Pill)
        self.adjust_f = tk.Frame(self.timer_main_f, bg=self.theme["bg"])
        self.adjust_f.pack(pady=(0, 6))
        
        self.min_pill = tk.Frame(self.adjust_f, bg=UI["panel"], padx=2, pady=2)
        self.min_pill.pack()
        
        btn_adj_style = {"bg": UI["panel"], "fg": UI["ink"], "relief": "flat", 
                        "font": ("Segoe UI Semibold", 9), "cursor": "hand2", 
                        "activebackground": self.theme["header"], "width": 4}
        
        self.timer_adj_btns = []
        def create_adj_btn(parent, text, m):
            btn = tk.Button(parent, text=text, **btn_adj_style, command=lambda: adj(m))
            btn.pack(side=tk.LEFT, padx=1)
            self.timer_adj_btns.append(btn)
            
            # Continuous adjustment on hold
            def start_hold(e):
                btn._job = self.window.after(350, hold_loop)
            def hold_loop():
                adj(m)
                btn._job = self.window.after(100, hold_loop)
            def stop_hold(e):
                if hasattr(btn, '_job'):
                    self.window.after_cancel(btn._job)
            btn.bind("<ButtonPress-1>", start_hold, add="+")
            btn.bind("<ButtonRelease-1>", stop_hold, add="+")
            return btn

        create_adj_btn(self.min_pill, "-5m", -5)
        create_adj_btn(self.min_pill, "-1m", -1)
        create_adj_btn(self.min_pill, "+1m", 1)
        create_adj_btn(self.min_pill, "+5m", 5)

        # 3. Preset Section: Quick Presets (Refined List)
        self.preset_f = tk.Frame(self.timer_main_f, bg=self.theme["bg"])
        self.preset_f.pack(pady=(0, 8))
        
        self.preset_pill = tk.Frame(self.preset_f, bg=UI["panel"], padx=1, pady=1)
        self.preset_pill.pack()
        
        self.timer_preset_btns = []
        btn_preset_style = {"bg": UI["panel"], "fg": UI["ink"], "relief": "flat", 
                           "font": ("Segoe UI Semibold", 8), "cursor": "hand2", "width": 4, "pady": 1}
        
        for p in [10, 25, 45, 60]:
            btn = tk.Button(self.preset_pill, text=f"{p}m", **btn_preset_style, command=lambda m=p: set_preset(m))
            btn.pack(side=tk.LEFT, padx=1)
            btn.bind("<Double-Button-1>", lambda e, m=p: [set_preset(m), self.toggle_timer()])
            self.timer_preset_btns.append(btn)

        # 4. Bottom Section: Main Actions
        self.action_f = tk.Frame(self.timer_main_f, bg=self.theme["bg"])
        self.action_f.pack(pady=(2, 0))
        
        self.start_btn = tk.Button(self.action_f, text="START", bg=self.theme["border"], fg="white", 
                                   font=("Segoe UI Semibold", 9, "bold"), relief="flat", padx=32, pady=6, 
                                   cursor="hand2", activebackground=UI["accent_dark"], activeforeground="white", command=self.toggle_timer)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reset_btn = tk.Button(self.action_f, text="RESET", bg=self.theme["bg"], fg=UI["muted"], 
                                  font=("Segoe UI Semibold", 8), relief="flat", padx=10, pady=6, 
                                  activebackground=UI["menu_hover"], activeforeground=UI["ink"],
                                  cursor="hand2", command=self.reset_timer)
        self.reset_btn.pack(side=tk.LEFT)

        # Separator Line
        self.timer_sep = tk.Frame(self.main_container, bg=self.theme["border"], height=1)
        self.timer_sep.pack(fill=tk.X, padx=16)

        # Bottom Section: Full Editor
        font_family = AVAILABLE_FONTS.get(self.data.font_name, "Segoe UI")
        size = self.data.font_size
        self.editor = tk.Text(self.main_container, bg=self.theme["bg"], fg=self.theme["text"],
                             font=(font_family, size), wrap=tk.WORD, borderwidth=0,
                             padx=16, pady=10, highlightthickness=0, insertbackground=self.theme["text"],
                             selectbackground="#D8C7A1", selectforeground=self.theme["text"])
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.insert("1.0", self.data.content)
        
        # Apply Tags
        self.editor.tag_configure("strike", overstrike=True)
        self.editor.tag_configure("bold", font=(font_family, size, "bold"))
        self.editor.tag_configure("header", font=(font_family, size + 2, "bold"), foreground=self.theme["border"])

    def set_timer(self, seconds):
        self.timer_seconds = seconds
        self.last_timer_seconds = seconds
        self.timer_running = False
        self.update_timer_display()
        self.start_btn.configure(text="START", bg=self.theme["border"])

    def toggle_timer(self):
        if self.timer_seconds <= 0 and not self.timer_running:
            if getattr(self, 'last_timer_seconds', 0) > 0:
                self.timer_seconds = self.last_timer_seconds
                self.update_timer_display()
                self.timer_running = True
                self.start_btn.configure(text="PAUSE", bg=UI["ink"])
                self.run_timer()
            return

        self.timer_running = not self.timer_running
        if self.timer_running:
            self.start_btn.configure(text="PAUSE", bg=UI["ink"])
            self.run_timer()
        else:
            self.start_btn.configure(text="RESUME", bg=self.theme["border"])

    def reset_timer(self):
        self.timer_running = False
        self.timer_seconds = 0
        self.update_timer_display()
        self.start_btn.configure(text="START", bg=self.theme["border"])

    def run_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_display()
            self.window.after(1000, self.run_timer)
        elif self.timer_seconds <= 0:
            self.timer_running = False
            self.start_btn.configure(text="RESTART", bg="#2E7D32")
            if not getattr(self, 'timer_triggered', False):
                self.timer_triggered = True
                self.trigger_alert("Timer Finished", "Your session is complete.")

    def update_timer_display(self):
        if getattr(self, 'timer_seconds', 0) > 0:
            self.timer_triggered = False
        hrs = self.timer_seconds // 3600
        mins = (self.timer_seconds % 3600) // 60
        secs = self.timer_seconds % 60
        if hrs > 0:
            self.time_display.configure(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
        else:
            self.time_display.configure(text=f"{mins:02d}:{secs:02d}")

    def trigger_alert(self, title, message):
        """Premium High-Visibility Attention & Notification System - Production Grade"""
        
        # 1. State Locking: Prevent duplicate alert cycles
        if getattr(self, '_alert_active', False): return
        self._alert_active = True

        # 2. Attention Focus: Restore, Bring to Front, and Focus
        if self.window.state() == 'iconic':
            self.window.deiconify()
        
        # Temporarily force to top, then restore user's preferred AOT state
        self.window.attributes("-topmost", True)
        self.window.lift()
        self.window.focus_force()
        self.window.after(6000, lambda: self.window.winfo_exists() and self.window.attributes("-topmost", self.data.always_on_top))

        # 3. Sound System: Professional Productivity Chime
        def play_alert_sequence():
            if winsound:
                try:
                    for _ in range(3): # 3-5 second total duration
                        # A soft, ascending melodic sequence (C5, E5, G5, C6)
                        for freq in [523, 659, 784, 1046]:
                            winsound.Beep(freq, 120)
                        time.sleep(0.6)
                except: pass
        
        threading.Thread(target=play_alert_sequence, daemon=True).start()

        # 4. Full-Board Visual Attention Effect (Recursive Pulse)
        orig_border = self.theme["border"]
        orig_bg = self.theme["bg"]
        orig_header = self.theme["header"]
        
        # High-visibility pulse colors
        glow_col = "#FFD700" if "Timer" in title else UI["accent"] # Gold for Timer, Accent for Reminder
        pulse_bg = self.app.darken(orig_bg)
        
        def set_full_board_glow(active):
            if not self.window.winfo_exists(): return
            b_col = glow_col if active else orig_border
            bg_col = orig_bg # Preserve original background for premium feel
            h_col = glow_col if active else orig_header
            
            # Root frames
            self.root_frame.configure(bg=b_col)
            self.main_container.configure(bg=bg_col)
            self.header.configure(bg=h_col)
            
            # Update nested widgets while preserving body background
            def update_widgets(parent, bg, is_header=False):
                for child in parent.winfo_children():
                    try:
                        # Labels and frames in header/border pulse
                        if is_header or child.winfo_class() == "Frame":
                            child.configure(bg=bg)
                        
                        if child.winfo_class() == "Label":
                            child.configure(bg=bg)
                            
                        if child.winfo_children():
                            update_widgets(child, bg, is_header)
                    except: pass

            update_widgets(self.header, h_col, is_header=True)
            # We don't recursively update the main_container bg to preserve theme consistency
            
            # Special handling for text display if present
            if hasattr(self, 'time_display'):
                self.time_display.configure(fg=glow_col if not active else self.theme["text"])

        for i in range(10): # 10 steps of 500ms = 5 seconds
            self.window.after(i * 500, lambda i=i: set_full_board_glow(i % 2 == 0))

        # Reset alert lock after cycle completes
        self.window.after(5500, lambda: setattr(self, '_alert_active', False))

        # 5. Desktop Notification (Premium Toast)
        self.show_toast(title, message)

        # 6. Final State Cleanup
        if "Reminder" in title:
            self.data.reminder = None
            self.app.save()

    def show_toast(self, title, message):
        """Monitor-aware premium desktop toast notification"""
        toast = tk.Toplevel(self.window)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(bg="#202020", highlightthickness=1, highlightbackground=UI["accent"])
        
        # Position: Bottom-Right of the note's current monitor
        mon = monitor_rect_for(self.window)
        mx1, my1, mx2, my2 = mon
        tw, th = 320, 90
        tx = mx2 - tw - 24
        ty = my2 - th - 24
        toast.geometry(f"{tw}x{th}+{tx}+{ty}")
        
        # Content Layout
        toast_f = tk.Frame(toast, bg="#202020", padx=16, pady=12)
        toast_f.pack(fill=tk.BOTH, expand=True)
        
        icon_lbl = tk.Label(toast_f, text=ICONS["bell"], font=(FONT_ICON[0], 20), bg="#202020", fg=UI["accent"])
        icon_lbl.pack(side=tk.LEFT, padx=(0, 16))
        
        txt_f = tk.Frame(toast_f, bg="#202020")
        txt_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(txt_f, text=title.upper(), font=("Segoe UI", 9, "bold"), bg="#202020", fg="white", anchor="w").pack(fill=tk.X)
        tk.Label(txt_f, text=message, font=("Segoe UI", 9), bg="#202020", fg="#B0B0B0", anchor="w", wraplength=220).pack(fill=tk.X, pady=(2, 0))

        # Interaction: Click to focus note and close toast
        def on_click(e):
            if self.window.winfo_exists():
                self.window.deiconify()
                self.window.lift()
                self.window.focus_force()
            toast.destroy()
        
        for w in [toast, toast_f, icon_lbl, txt_f]:
            w.bind("<Button-1>", on_click)

        # Smooth Fade Animation
        toast.attributes("-alpha", 0.0)
        def fade_in(alpha=0.0):
            if not toast.winfo_exists(): return
            if alpha < 0.98:
                toast.attributes("-alpha", alpha)
                toast.after(16, lambda: fade_in(alpha + 0.1))
        fade_in()
        
        def fade_out(alpha=0.98):
            if not toast.winfo_exists(): return
            if alpha > 0.0:
                toast.attributes("-alpha", alpha)
                toast.after(16, lambda: fade_out(alpha - 0.1))
            else:
                toast.destroy()
        
        toast.after(6000, fade_out)

        # 5. State Cleanup: Ensure reminder is only triggered once
        if "Reminder" in title:
            self.data.reminder = None
            self.app.save()

    def flash_completion(self):
        orig = self.header.cget("bg")
        self.header.configure(bg="#BFD991")
        self.title_f.configure(bg="#BFD991")
        self.title_label.configure(bg="#BFD991")
        self.countdown_lbl.configure(bg="#BFD991")
        self.controls.configure(bg="#BFD991")
        self.pin_btn.configure(bg="#BFD991")
        self.add_btn.configure(bg="#BFD991")
        self.window.after(180, lambda: [
            self.header.configure(bg=orig),
            self.title_f.configure(bg=orig),
            self.title_label.configure(bg=orig),
            self.countdown_lbl.configure(bg=orig),
            self.controls.configure(bg=orig),
            self.pin_btn.configure(bg=orig),
            self.add_btn.configure(bg=orig)
        ])

    def on_text_change(self, e=None):
        content = self.editor.get("1.0", tk.END)
        
        # Auto-detect Bengali: [\u0980-\u09FF] is the Unicode range for Bengali
        if re.search(r"[\u0980-\u09FF]", content):
            if self.data.font_name != "Bengali":
                self.change_font("Bengali", save=False)

        if self.data.is_checklist:
            self.apply_checklist_tags()
        else:
            self.apply_markdown_tags()
        self.app.save()

    def handle_checklist_return(self, e):
        line_content = self.editor.get("insert linestart", "insert lineend")
        if any(line_content.startswith(c) for c in ["☐", "☑", "☒"]):
            self.editor.insert("insert", "\n☐\t")
            return "break"

    def handle_checklist_click(self, e):
        # Precise click detection: only toggle if clicking the first 2 characters (the box)
        index = self.editor.index(f"@{e.x},{e.y}")
        col = int(index.split('.')[1])
        
        if col < 2:  # Only allow toggling if clicking near the checkbox
            line_start = self.editor.index(f"{index} linestart")
            char = self.editor.get(line_start, f"{line_start} + 1 chars")
            
            if char in ["☐", "☑", "☒"]:
                # Rotate: Empty -> Tick -> Cross -> Empty
                if char == "☐": new_char = "☑"
                elif char == "☑": new_char = "☒"
                else: new_char = "☐"
                
                self.editor.delete(line_start)
                self.editor.insert(line_start, new_char)
                self.on_text_change()
                if new_char == "☑":
                    self.flash_completion()
                return "break"

    def apply_checklist_tags(self):
        self.editor.tag_remove("strike_faded", "1.0", tk.END)
        self.editor.tag_remove("tick_color", "1.0", tk.END)
        self.editor.tag_remove("cross_color", "1.0", tk.END)
        self.editor.tag_remove("checklist_line", "1.0", tk.END)
        
        lines = self.editor.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            end = f"{i+1}.end"
            
            # Auto-fix legacy spaces to tabs for perfect alignment
            if any(line.startswith(c + " ") for c in ["☐", "☑", "☒"]):
                self.editor.delete(f"{line_start}+1c", f"{line_start}+2c")
                self.editor.insert(f"{line_start}+1c", "\t")
                line = self.editor.get(line_start, end)

            # Apply layout formatting
            self.editor.tag_add("checklist_line", line_start, end)
            
            if line.startswith("☑"):
                self.editor.tag_add("tick_color", line_start, f"{line_start}+1c")
                # Strike starts after the checkbox and tab
                self.editor.tag_add("strike_faded", f"{line_start}+2c", end)
            elif line.startswith("☒"):
                self.editor.tag_add("cross_color", line_start, f"{line_start}+1c")
                self.editor.tag_add("strike_faded", f"{line_start}+2c", end)

    def setup_toolbar(self):
        self.toolbar = tk.Toplevel(self.window)
        self.toolbar.overrideredirect(True)
        self.toolbar.attributes("-topmost", True)
        self.toolbar.withdraw() # Start hidden
        self.toolbar.configure(bg=UI["ink"], padx=3, pady=3)
        
        btn_style = {"bg": UI["ink"], "fg": "#FFF8E6", "font": ("Segoe UI", 9, "bold"), 
                     "relief": "flat", "padx": 8, "pady": 2, "cursor": "hand2",
                     "activebackground": UI["accent_dark"], "activeforeground": "white"}
        
        tk.Button(self.toolbar, text="B", **btn_style, command=lambda: self.format_markdown("**")).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="I", **btn_style, command=lambda: self.format_markdown("*")).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="H", **btn_style, command=lambda: self.format_markdown("# ")).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="∅", **btn_style, command=self.clear_formatting).pack(side=tk.LEFT)

    def clear_formatting(self):
        try:
            sel_first = self.editor.index("sel.first")
            sel_last = self.editor.index("sel.last")
            text = self.editor.get(sel_first, sel_last)
            # Remove all markdown markers
            new_text = re.sub(r"[\*#]", "", text)
            self.editor.delete(sel_first, sel_last)
            self.editor.insert(sel_first, new_text)
            self.on_text_change()
            self.hide_toolbar()
        except: pass

    def update_countdown(self, schedule=True):
        """Expert Header Countdown Logic with Recovery Safety"""
        try:
            if not self.window.winfo_exists(): return
            
            if self.data.reminder:
                try:
                    dt = datetime.strptime(self.data.reminder, "%Y-%m-%d %H:%M")
                    diff = dt - datetime.now()
                    if diff.total_seconds() > 0:
                        self.reminder_triggered = False
                        seconds = int(diff.total_seconds())
                        days = seconds // 86400
                        hrs = (seconds % 86400) // 3600
                        mins = (seconds % 3600) // 60
                        scs = seconds % 60
                        
                        if days > 0: ts = f"{days}d {hrs:02d}:{mins:02d}:{scs:02d}"
                        else: ts = f"{hrs:02d}:{mins:02d}:{scs:02d}"
                        
                        # Use theme color for visibility
                        self.countdown_lbl.configure(text=ts, fg=self.theme["text"])
                    else:
                        self.countdown_lbl.configure(text="TIME'S UP!", fg=UI["danger"])
                        if not getattr(self, 'reminder_triggered', False):
                            self.reminder_triggered = True
                            self.trigger_alert("Reminder Completed", f"'{self.data.title}' is due!")
                except: 
                    self.countdown_lbl.configure(text="")
            else:
                self.countdown_lbl.configure(text="")
                self.reminder_triggered = False
                
            if hasattr(self, 'update_title_ellipsis'):
                self.update_title_ellipsis()
        except: pass
            
        if schedule and self.window.winfo_exists():
            self.window.after(1000, self.update_countdown)

    def on_selection(self, event=None):
        if self.data.is_checklist: return
        try:
            sel_range = self.editor.tag_ranges("sel")
            if not sel_range:
                self.hide_toolbar()
                return
            
            # Position above selection
            bbox = self.editor.bbox("sel.first")
            if bbox:
                x, y, w, h = bbox
                root_x = self.window.winfo_rootx() + x
                root_y = self.window.winfo_rooty() + y - 35
                self.toolbar.geometry(f"+{root_x}+{root_y}")
                self.toolbar.deiconify()
        except:
            self.hide_toolbar()

    def on_click_text(self, event):
        # Hide toolbar if clicking away from selection
        self.window.after(100, self.check_selection_and_hide)

    def check_selection_and_hide(self):
        if not self.editor.tag_ranges("sel"):
            self.hide_toolbar()

    def hide_toolbar(self):
        if hasattr(self, 'toolbar'):
            self.toolbar.withdraw()

    def format_markdown(self, marker):
        try:
            sel_first = self.editor.index("sel.first")
            sel_last = self.editor.index("sel.last")
            text = self.editor.get(sel_first, sel_last)
            
            if marker == "# ":
                # For headers, prepend to current line
                line_start = self.editor.index("sel.first linestart")
                self.editor.insert(line_start, marker)
            else:
                # Toggle wrapping
                if text.startswith(marker) and text.endswith(marker):
                    # Remove markers
                    new_text = text[len(marker):-len(marker)]
                    self.editor.delete(sel_first, sel_last)
                    self.editor.insert(sel_first, new_text)
                else:
                    # Add markers
                    self.editor.delete(sel_first, sel_last)
                    self.editor.insert(sel_first, f"{marker}{text}{marker}")
            
            self.on_text_change()
            self.hide_toolbar()
        except: pass

    def apply_markdown_tags(self):
        # Clear existing tags
        for t in ["bold", "italic", "header", "hidden", "md_star"]:
            self.editor.tag_remove(t, "1.0", tk.END)
            
        # 1. Headers: # Title
        curr = "1.0"
        while True:
            curr = self.editor.search("# ", curr, stopindex=tk.END, regexp=False)
            if not curr: break
            # Only if it's at start of line
            if curr.endswith(".0"):
                line_end = self.editor.index(f"{curr} lineend")
                self.editor.tag_add("header", curr, line_end)
                self.editor.tag_add("hidden", curr, f"{curr}+2c")
            curr = f"{curr}+1c"

        # 2. Bold: **text**
        curr = "1.0"
        while True:
            start = self.editor.search("**", curr, stopindex=tk.END, regexp=False)
            if not start: break
            end = self.editor.search("**", f"{start}+2c", stopindex=tk.END, regexp=False)
            if not end:
                curr = f"{start}+2c"
                continue
            
            self.editor.tag_add("bold", start, f"{end}+2c")
            self.editor.tag_add("hidden", start, f"{start}+2c")
            self.editor.tag_add("hidden", end, f"{end}+2c")
            curr = f"{end}+2c"

        # 3. Italic: *text* (Only if not already hidden by bold)
        curr = "1.0"
        while True:
            start = self.editor.search("*", curr, stopindex=tk.END, regexp=False)
            if not start: break
            
            # If this '*' is already tagged as hidden, it's part of a bold marker
            if "hidden" in self.editor.tag_names(start):
                curr = f"{start}+1c"
                continue
                
            end = self.editor.search("*", f"{start}+1c", stopindex=tk.END, regexp=False)
            if not end or "hidden" in self.editor.tag_names(end):
                curr = f"{start}+1c"
                continue
                
            self.editor.tag_add("italic", start, f"{end}+1c")
            self.editor.tag_add("hidden", start, f"{start}+1c")
            self.editor.tag_add("hidden", end, f"{end}+1c")
            curr = f"{end}+1c"

    def show_menu(self, e):
        # Clean Minimal Menu (Fixed subtle colors)
        menu = ModernMenu(self.window, e.x_root, e.y_root)
        
        # Section 1: Appearance
        menu.add_item("Reset Window Size", self.reset_size, ICONS["reset"])
        
        # Themes Cascade
        themes_data = []
        for name, theme in NOTE_COLORS.items():
            themes_data.append((name, lambda n=name: self.change_theme(n), {
                "text": "●",
                "fg": theme["border"],
                "font": ("Segoe UI", 12, "bold")
            }))
        menu.add_item("Themes", icon=ICONS["palette"], cascade_data=themes_data)
        
        # Fonts Cascade
        fonts_data = []
        for name in AVAILABLE_FONTS:
            family = AVAILABLE_FONTS.get(name, "Segoe UI")
            fonts_data.append((name, lambda n=name: self.change_font(n), {
                "text": "Aa",
                "fg": UI["accent_dark"],
                "font": (family, 9),
                "label_font": (family, 9)
            }))
        menu.add_item("Typography", icon=ICONS["font"], cascade_data=fonts_data)
        
        # Size Cascade
        size_data = []
        for s in [9, 10, 11, 12, 14, 16, 18, 20, 24]:
            size_data.append((f"{s}px", lambda sz=s: self.change_font_size(sz), {
                "text": "A",
                "fg": UI["accent_dark"],
                "font": ("Segoe UI", min(14, max(8, s)))
            }))
        menu.add_item("Font Size", icon=ICONS["size"], cascade_data=size_data)
        
        menu.add_separator()
        
        # Section 2: Functionality
        reminder_label = "Edit Reminder" if self.data.reminder else "Start Reminder"
        menu.add_item(reminder_label, self.show_reminder_panel, ICONS["bell"])
        if self.data.reminder:
            menu.add_item("Remove Reminder", self.clear_reminder, ICONS["delete"])
        
        pin_label = "Unpin Header" if self.data.always_on_top else "Pin Header"
        pin_icon = ICONS["unpin"] if self.data.always_on_top else ICONS["pin"]
        menu.add_item(pin_label, self.toggle_pin, pin_icon)
        
        menu.add_item("Export as PNG", self.export_as_png, ICONS["note"])
        menu.add_separator()
        menu.add_item("Delete Note", self.confirm_delete, ICONS["delete"], danger=True)
        menu.add_item("Exit Application", self.app.quit_app, ICONS["power"])
        menu.add_separator()
        menu.add_item("About VibePad", self.app.show_about, ICONS["info"])
        
        menu.show()

    def clear_reminder(self):
        self.data.reminder = None
        self.countdown_lbl.configure(text="")
        self.app.save()

    def export_as_png(self):
        if ImageFont is None:
            messagebox.showerror("Export Error", "PNG export needs Pillow support.")
            return

        default_name = re.sub(r"[^A-Za-z0-9_-]+", "_", self.data.title).strip("_") or "VibePad_Note"
        path = filedialog.asksaveasfilename(
            title="Export as PNG",
            defaultextension=".png",
            initialfile=f"{default_name}.png",
            filetypes=[("PNG Image", "*.png")]
        )
        if not path:
            return

        try:
            scale = 2
            width = max(360, int(self.window.winfo_width())) * scale
            pad = 24 * scale
            header_h = 44 * scale
            body_font = self.load_export_font(self.data.font_name, self.data.font_size * scale)
            title_font = self.load_export_font("Modern", 11 * scale, bold=True)
            small_font = self.load_export_font("Modern", 8 * scale)
            content = self.editor.get("1.0", tk.END).strip()
            if self.data.is_timer:
                timer_line = f"Timer: {self.time_display.cget('text')}"
                content = f"{timer_line}\n\n{content}" if content else timer_line

            scratch = Image.new("RGB", (width, 2000), self.theme["bg"])
            dc = ImageDraw.Draw(scratch)
            max_text_w = width - pad * 2
            lines = self.wrap_export_lines(dc, content, body_font, max_text_w)
            line_h = int((self.data.font_size * scale) * 1.65)
            height = max(220 * scale, header_h + pad + (len(lines) * line_h) + pad)

            image = Image.new("RGB", (width, height), self.theme["bg"])
            dc = ImageDraw.Draw(image)
            dc.rectangle((0, 0, width - 1, height - 1), outline=self.theme["border"], width=3 * scale)
            dc.rectangle((3 * scale, 3 * scale, width - 3 * scale, header_h), fill=self.theme["header"])
            dc.text((pad, 13 * scale), self.data.title, fill=self.theme["text"], font=title_font)
            if self.data.reminder:
                dc.text((width - pad - 150 * scale, 15 * scale), "Reminder set", fill=UI["danger"], font=small_font)

            y = header_h + 18 * scale
            for raw_line in lines:
                line = raw_line
                checkbox = None
                if line.startswith(("☐ ", "☑ ", "☒ ")):
                    checkbox = line[:1]
                    line = line[2:]
                    box = (pad, y + 4 * scale, pad + 11 * scale, y + 15 * scale)
                    dc.rectangle(box, outline=self.theme["border"], width=2)
                    if checkbox == "☑":
                        dc.line((box[0] + 3 * scale, box[1] + 6 * scale, box[0] + 5 * scale, box[3] - 3 * scale, box[2] - 2 * scale, box[1] + 2 * scale), fill="#2E7D32", width=2 * scale)
                    elif checkbox == "☒":
                        dc.line((box[0] + 3 * scale, box[1] + 3 * scale, box[2] - 3 * scale, box[3] - 3 * scale), fill=UI["danger"], width=2 * scale)
                        dc.line((box[2] - 3 * scale, box[1] + 3 * scale, box[0] + 3 * scale, box[3] - 3 * scale), fill=UI["danger"], width=2 * scale)
                    dc.text((pad + 18 * scale, y), line, fill=self.theme["text"], font=body_font)
                else:
                    dc.text((pad, y), self.clean_export_text(line), fill=self.theme["text"], font=body_font)
                y += line_h

            image.save(path, "PNG", optimize=True)
            messagebox.showinfo("Export Complete", "Your note was exported as a high-quality PNG.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export PNG: {e}")

    def load_export_font(self, name, size, bold=False):
        family = AVAILABLE_FONTS.get(name, "Segoe UI")
        font_file = {
            "Segoe UI": "seguisb.ttf" if bold else "segoeui.ttf",
            "Segoe Print": "segoeprb.ttf" if bold else "segoepr.ttf",
            "Segoe Script": "segoescb.ttf" if bold else "segoesc.ttf",
            "Calibri": "calibrib.ttf" if bold else "calibri.ttf",
            "Consolas": "consolab.ttf" if bold else "consola.ttf",
            "Arial": "arialbd.ttf" if bold else "arial.ttf",
            "Li Ador Noirrit": "NirmalaB.ttf" if bold else "Nirmala.ttf",
        }.get(family, "segoeui.ttf")
        font_path = Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts" / font_file
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception:
            return ImageFont.load_default()

    def clean_export_text(self, text):
        text = re.sub(r"^#\s+", "", text)
        text = text.replace("**", "").replace("*", "")
        return text

    def wrap_export_lines(self, dc, content, font, max_width):
        result = []
        for paragraph in content.splitlines() or [""]:
            prefix = ""
            text = paragraph
            if paragraph.startswith(("☐ ", "☑ ", "☒ ")):
                prefix = paragraph[:2]
                text = paragraph[2:]
            text = self.clean_export_text(text)
            words = text.split(" ")
            current = ""
            for word in words:
                trial = word if not current else f"{current} {word}"
                if dc.textbbox((0, 0), trial, font=font)[2] <= max_width:
                    current = trial
                else:
                    if current:
                        result.append(prefix + current)
                        current = word
                    else:
                        result.append(prefix + word)
                        current = ""
                    prefix = "  " if prefix else ""
            if current:
                result.append(prefix + current)
            elif not words:
                result.append("")
        return result


    def reset_size(self):
        target_height = 230 if self.data.is_timer else DEFAULT_HEIGHT
        self.window.geometry(f"{DEFAULT_WIDTH}x{target_height}")
        self.data.width, self.data.height = DEFAULT_WIDTH, target_height
        self.app.save()

    def change_theme(self, name):
        """Senior Theme Transition System: Total UI harmonization."""
        self.data.color_name = name
        self.theme = NOTE_COLORS[name]
        
        # 1. Update Core Components
        self.root_frame.configure(bg=self.theme["border"])
        self.main_container.configure(bg=self.theme["bg"])
        self.header.configure(bg=self.theme["header"])
        self.title_f.configure(bg=self.theme["header"])
        self.title_label.configure(bg=self.theme["header"], fg=self.theme["text"])
        self.countdown_lbl.configure(bg=self.theme["header"])
        self.controls.configure(bg=self.theme["header"])
        
        # 2. Update Icons
        self.pin_btn.configure(text=self.pin_visual(), bg=self.theme["header"], fg=self.pin_color())
            
        self.add_btn.configure(bg=self.theme["header"], fg=self.theme["text"])
        
        # 3. Update Editor (Include selection harmony)
        self.editor.configure(
            bg=self.theme["bg"], 
            fg=self.theme["text"], 
            insertbackground=self.theme["text"],
            selectbackground=self.app.darken(self.theme["bg"]) # Smooth semantic selection
        )
        
        if hasattr(self, 'handle'):
            self.handle.configure(bg=self.theme["bg"], fg=self.theme["border"])
            
        # 4. Refresh State & Interaction
        self.update_colors()
        self.app.app_settings["last_color_name"] = name
        self.app.save_settings()
        self.app.save()

    def change_font(self, name, save=True):
        self.data.font_name = name
        font_family = AVAILABLE_FONTS.get(name, "Segoe Print")
        size = self.data.font_size
        self.editor.configure(font=(font_family, size))
        
        # Update tags
        self.editor.tag_configure("bold", font=(font_family, size, "bold"))
        self.editor.tag_configure("italic", font=(font_family, size, "italic"))
        self.editor.tag_configure("header", font=(font_family, size + 2, "bold"))
        
        if save:
            self.app.app_settings["last_font_name"] = name
            self.app.save_settings()
            if self.data.is_checklist:
                self.apply_checklist_tags()
            else:
                self.apply_markdown_tags()
            self.app.save()

    def change_font_size(self, size):
        self.data.font_size = size
        font_family = AVAILABLE_FONTS.get(self.data.font_name, "Segoe Print")
        self.editor.configure(font=(font_family, size))
        
        # Update tags
        self.editor.tag_configure("bold", font=(font_family, size, "bold"))
        self.editor.tag_configure("italic", font=(font_family, size, "italic"))
        self.editor.tag_configure("header", font=(font_family, size + 2, "bold"))
        
        self.app.app_settings["last_font_size"] = size
        self.app.save_settings()
        if self.data.is_checklist:
            self.apply_checklist_tags()
        else:
            self.apply_markdown_tags()
        self.app.save()

    def toggle_pin(self, event=None):
        self.data.always_on_top = not self.data.always_on_top
        self.window.attributes("-topmost", self.data.always_on_top)
        self.pin_btn.configure(text=self.pin_visual(), fg=self.pin_color())
        self.app.save()

    def edit_title(self, event):
        """Allow editing the note title with an inline entry. Controlled temporary expansion."""
        edit = tk.Entry(self.title_f, bg=self.theme["bg"], fg=self.theme["text"],
                       font=("Segoe UI", 9, "bold"), borderwidth=0, highlightthickness=1,
                       highlightbackground=UI["accent_dark"])
        edit.insert(0, self.data.title)
        
        # Use the entire flexible title area for comfortable editing
        max_w = self.title_f.winfo_width()
        edit.place(x=0, y=0, width=max_w, height=self.title_f.winfo_height())
        edit.focus_set()
        edit.select_range(0, tk.END)
        
        def save(e=None):
            new_title = edit.get().strip() or "Sticky Note"
            self.data.title = new_title
            edit.destroy()
            self.update_title_ellipsis()
            self.app.save()
            
        edit.bind("<Return>", save)
        edit.bind("<FocusOut>", save)
        edit.bind("<Escape>", lambda e: edit.destroy())

    def confirm_delete(self):
        # Premium Custom Dialog
        confirm = tk.Toplevel(self.window)
        confirm.overrideredirect(True)
        # Position centered on note
        wx, wy = self.window.winfo_x(), self.window.winfo_y()
        ww, wh = self.window.winfo_width(), self.window.winfo_height()
        x, y = clamp_point_to_rect(wx + (ww-200)//2, wy + (wh-120)//2, 200, 120, monitor_rect_for(self.window))
        confirm.geometry(f"200x120+{x}+{y}")
        confirm.attributes("-topmost", True)
        confirm.configure(bg=UI["paper"], highlightthickness=1, highlightbackground=UI["line"])
        
        tk.Label(confirm, text="Delete Note?", font=("Segoe UI", 11, "bold"), bg=UI["paper"], fg=UI["danger"]).pack(pady=(15, 5))
        tk.Label(confirm, text="This action cannot be undone.", font=("Segoe UI", 8), bg=UI["paper"], fg=UI["muted"]).pack()
        
        btn_f = tk.Frame(confirm, bg=UI["paper"])
        btn_f.pack(pady=15)
        
        tk.Button(btn_f, text="Delete", bg=UI["danger"], fg="white", font=("Segoe UI", 9, "bold"), 
                  relief="flat", padx=10, command=lambda: [confirm.destroy(), self.window.destroy(), self.app.remove_note(self.data.note_id)]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_f, text="Cancel", bg=UI["panel"], fg=UI["ink"], font=("Segoe UI", 9), 
                  relief="flat", padx=10, command=confirm.destroy).pack(side=tk.LEFT, padx=5)

    def show_reminder_panel(self, event=None):
        """Compact Minimal Reminder Picker - Premium Design Hierarchy"""
        if hasattr(self, 'rem_win') and self.rem_win.winfo_exists():
            self.rem_win.destroy()

        self.rem_win = tk.Toplevel(self.window)
        self.rem_win.overrideredirect(True)
        
        # Expert Compact Dimensions (Tightened for no dead space)
        ww, wh = self.window.winfo_width(), self.window.winfo_height()
        wx, wy = self.window.winfo_rootx(), self.window.winfo_rooty()
        MW, MH = 320, 500 # Optimized height to eliminate the middle gap
        x, y = clamp_point_to_rect(wx + (ww-MW)//2, wy + (wh-MH)//2, MW, MH, monitor_rect_for(self.window))
        self.rem_win.geometry(f"{MW}x{MH}+{x}+{y}")
        self.rem_win.attributes("-topmost", True)
        
        panel_bg = UI["paper"]
        accent = self.theme["border"]
        self.rem_win.configure(bg=panel_bg, highlightthickness=1, highlightbackground=UI["line"])

        # State Initialization
        now = datetime.now()
        if self.data.reminder:
            try: self.sel_dt = datetime.strptime(self.data.reminder, "%Y-%m-%d %H:%M")
            except: self.sel_dt = now + timedelta(hours=1)
        else:
            self.sel_dt = now + timedelta(hours=1)
            
        self.view_month = self.sel_dt.month
        self.view_year = self.sel_dt.year

        # Helper Logic
        def update_preview():
            diff = self.sel_dt - datetime.now()
            if diff.total_seconds() < 0:
                preview_lbl.configure(text="Time is in the past", fg="#E57373")
                if hasattr(self, 'save_btn'): self.save_btn.configure(state="disabled", bg=UI["panel"])
            else:
                preview_lbl.configure(text=f"Triggering in {str(diff).split('.')[0]}", fg=UI["muted"])
                if hasattr(self, 'save_btn'): self.save_btn.configure(state="normal", bg=accent)

        def select_day(day):
            self.sel_dt = self.sel_dt.replace(year=self.view_year, month=self.view_month, day=day)
            draw_calendar()
            update_preview()

        def change_month(delta):
            self.view_month += delta
            if self.view_month > 12: self.view_month = 1; self.view_year += 1
            elif self.view_month < 1: self.view_month = 12; self.view_year -= 1
            draw_calendar()

        def draw_calendar():
            for widget in cal_grid_container.winfo_children(): widget.destroy()
            
            nav_f = tk.Frame(cal_grid_container, bg=panel_bg)
            nav_f.pack(fill=tk.X, pady=(0, 10))
            
            tk.Button(nav_f, text=ICONS["back"], bg=panel_bg, fg=accent, relief="flat", font=("Segoe MDL2 Assets", 9),
                      activebackground=UI["panel"], cursor="hand2", command=lambda: change_month(-1)).pack(side=tk.LEFT)
            
            month_name = f"{calendar.month_name[self.view_month]} {self.view_year}"
            tk.Label(nav_f, text=month_name, bg=panel_bg, fg=UI["ink"], 
                     font=("Segoe UI Semibold", 9)).pack(side=tk.LEFT, expand=True)
            
            tk.Button(nav_f, text=ICONS["next"], bg=panel_bg, fg=accent, relief="flat", font=("Segoe MDL2 Assets", 9),
                      activebackground=UI["panel"], cursor="hand2", command=lambda: change_month(1)).pack(side=tk.RIGHT)
            
            days_f = tk.Frame(cal_grid_container, bg=panel_bg)
            days_f.pack()

            for i, d in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
                tk.Label(days_f, text=d, font=("Segoe UI Semibold", 8), bg=panel_bg, fg=UI["muted"], width=4).grid(row=0, column=i, pady=(0, 4))
            
            month_days = calendar.monthcalendar(self.view_year, self.view_month)
            for r, week in enumerate(month_days):
                for c, d in enumerate(week):
                    if d == 0: continue
                    is_today = (d == now.day and self.view_month == now.month and self.view_year == now.year)
                    is_sel = (d == self.sel_dt.day and self.view_month == self.sel_dt.month and self.view_year == self.sel_dt.year)
                    
                    bg = UI["panel"] if is_sel else panel_bg
                    fg = UI["accent"] if is_sel else UI["ink"]
                    if is_today and not is_sel: fg = UI["accent"]
                    
                    btn = tk.Button(days_f, text=str(d), bg=bg, fg=fg, relief="flat", 
                                   width=3, height=1, font=("Segoe UI", 8), cursor="hand2",
                                   command=lambda d=d: select_day(d))
                    btn.grid(row=r+1, column=c, padx=1, pady=1)
                    if is_sel: btn.configure(font=("Segoe UI Bold", 8))

        # --- UI Construction (Tightened Compact) ---
        
        # 1. Header
        tk.Label(self.rem_win, text="Reminder Settings", font=("Segoe UI Semibold", 12), bg=panel_bg, fg=UI["ink"]).pack(pady=(20, 2))
        tk.Label(self.rem_win, text=self.data.title, font=("Segoe UI", 9), bg=panel_bg, fg=UI["muted"]).pack(pady=(0, 16))
        
        # 2. Calendar Core
        cal_grid_container = tk.Frame(self.rem_win, bg=panel_bg, padx=24)
        cal_grid_container.pack(fill=tk.X)
        draw_calendar()

        # 3. Time Selector
        time_section = tk.Frame(self.rem_win, bg=panel_bg)
        time_section.pack(pady=(16, 0))
        
        def change_time(h=0, m=0):
            self.sel_dt = self.sel_dt + timedelta(hours=h, minutes=m)
            update_time_ui(); update_preview()

        def toggle_ampm():
            new_h = (self.sel_dt.hour + 12) % 24
            self.sel_dt = self.sel_dt.replace(hour=new_h)
            update_time_ui(); update_preview()

        def update_time_ui():
            h_ent.delete(0, tk.END); h_ent.insert(0, self.sel_dt.strftime("%I"))
            m_ent.delete(0, tk.END); m_ent.insert(0, self.sel_dt.strftime("%M"))
            ampm_btn.configure(text=self.sel_dt.strftime("%p"))

        time_f = tk.Frame(time_section, bg=panel_bg)
        time_f.pack()

        def create_col(parent, up, down):
            col = tk.Frame(parent, bg=panel_bg)
            col.pack(side=tk.LEFT, padx=4)
            tk.Button(col, text=ICONS["up"], bg=panel_bg, fg=UI["muted"], relief="flat", font=("Segoe MDL2 Assets", 10), command=up).pack()
            ent = tk.Entry(col, font=("Segoe UI Semibold", 22), bg=panel_bg, fg=UI["ink"], width=2, relief="flat", justify="center")
            ent.pack(pady=1)
            tk.Button(col, text=ICONS["down"], bg=panel_bg, fg=UI["muted"], relief="flat", font=("Segoe MDL2 Assets", 10), command=down).pack()
            return ent

        h_ent = create_col(time_f, lambda: change_time(1, 0), lambda: change_time(-1, 0))
        tk.Label(time_f, text=":", font=("Segoe UI Semibold", 22), bg=panel_bg, fg=accent).pack(side=tk.LEFT, padx=0, pady=(0, 4))
        m_ent = create_col(time_f, lambda: change_time(0, 1), lambda: change_time(0, -1))
        
        ampm_btn = tk.Button(time_f, text="", font=("Segoe UI Bold", 8), bg=UI["panel"], fg=accent, 
                            relief="flat", width=5, pady=8, cursor="hand2", command=toggle_ampm)
        ampm_btn.pack(side=tk.LEFT, padx=(12, 0))
        update_time_ui()

        # 4. Preview
        preview_lbl = tk.Label(self.rem_win, text="", font=("Segoe UI", 8, "italic"), bg=panel_bg, fg=UI["muted"])
        preview_lbl.pack(pady=(8, 0))
        update_preview()

        # 5. Centered Action Row (Eliminated Middle Gap)
        footer_f = tk.Frame(self.rem_win, bg=panel_bg)
        footer_f.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 20))

        def save_final():
            self.data.reminder = self.sel_dt.strftime("%Y-%m-%d %H:%M")
            self.app.save(); self.update_countdown(schedule=False); self.rem_win.destroy()

        def clear_final():
            self.data.reminder = None
            self.app.save(); self.update_countdown(schedule=False); self.rem_win.destroy()

        primary_text = "Save Reminder" if self.data.reminder else "Start Reminder"
        
        btn_center = tk.Frame(footer_f, bg=panel_bg)
        btn_center.pack(expand=True)
        
        tk.Button(btn_center, text="Cancel", bg=UI["panel"], fg=UI["ink"], font=("Segoe UI Semibold", 9),
                  relief="flat", width=12, pady=10, cursor="hand2", command=self.rem_win.destroy).pack(side=tk.LEFT, padx=4)
                  
        self.save_btn = tk.Button(btn_center, text=primary_text, bg=accent, fg="white", font=("Segoe UI Bold", 9), 
                  relief="flat", width=14, pady=10, cursor="hand2", command=save_final)
        self.save_btn.pack(side=tk.LEFT, padx=4)
        
        if self.data.reminder:
            tk.Button(self.rem_win, text="Remove Reminder", font=("Segoe UI", 8, "underline"), bg=panel_bg, fg=UI["danger"],
                      relief="flat", cursor="hand2", command=clear_final).pack(side=tk.BOTTOM, pady=(0, 4))

        # Close Icon
        tk.Button(self.rem_win, text=ICONS["close"], bg=panel_bg, fg=UI["muted"], font=("Segoe MDL2 Assets", 10), 
                  relief="flat", cursor="hand2", command=self.rem_win.destroy).place(relx=1.0, x=-10, y=10, anchor="ne")
    
    def setup_auto(self):
        """Native Windows Startup Registration"""
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath("VibePad.py")
            if not getattr(sys, 'frozen', False):
                # If running as script, we need to call python
                cmd = f'pythonw "{exe_path}"'
            else:
                cmd = f'"{exe_path}"'
                
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "VibePad", 0, winreg.REG_SZ, cmd)
            winreg.CloseKey(key)
            messagebox.showinfo("Success", "VibePad will now start automatically with Windows.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not set up Auto-Start: {e}")

    def remove_auto(self):
        """Remove from Windows Startup"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, "VibePad")
                messagebox.showinfo("Success", "Auto-Start has been disabled.")
            except FileNotFoundError:
                messagebox.showinfo("Info", "Auto-Start was already disabled.")
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Error", f"Could not remove Auto-Start: {e}")

    def clean_data(self):
        """Deep Data Cleanup & Reset"""
        if messagebox.askyesno("Confirm Reset", "This will close VibePad and PERMANENTLY delete all notes and settings.\n\nAre you sure?"):
            try:
                # 1. Clear memory
                self.notes = {}
                # 2. Delete files
                if NOTES_FILE.exists(): NOTES_FILE.unlink()
                if SETTINGS_FILE.exists(): SETTINGS_FILE.unlink()
                # 3. Clear AppData folder if empty
                try: 
                    for item in DATA_DIR.iterdir():
                        if item.is_file(): item.unlink()
                    DATA_DIR.rmdir()
                except: pass
                
                messagebox.showinfo("Reset Complete", "VibePad has been reset. The application will now close.")
                os._exit(0)
            except Exception as e:
                messagebox.showerror("Error", f"Reset failed: {e}")

class VibePadApp:
    def __init__(self, show_only_cp=False):
        self.root = tk.Tk()
        self.root.withdraw()
        self.notes = {}
        self.app_settings = {
            "last_color_name": "Vibe Yellow",
            "last_font_name": "Handwriting",
            "last_font_size": 11
        }
        self.load_settings()
        self.cp = None
        self.is_standalone = show_only_cp

        if show_only_cp:
            # Note: CP logic was removed as requested, launching full
            self.launch_full()
        else:
            self.launch_full()
            
        # Initialize System Tray
        self.setup_system_tray()
        
        # Self-Installation Logic (UX: One-Click Setup)
        self.root.after(1000, self.self_install)

        self.root.mainloop()

    def self_install(self):
        """Silently handles Desktop shortcut and Startup registration on first run"""
        try:
            import winreg
            cmd = self.get_startup_command()
            exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

            # 1. Register for Startup
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "VibePad", 0, winreg.REG_SZ, cmd)
            winreg.CloseKey(key)

            # 2. Create Desktop Shortcut (Only if running as EXE)
            if getattr(sys, 'frozen', False):
                desktop = Path(os.environ["USERPROFILE"]) / "Desktop" / "VibePad.lnk"
                if not desktop.exists():
                    powershell_cmd = f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{desktop}');$s.TargetPath='{exe_path}';$s.WorkingDirectory='{os.path.dirname(exe_path)}';$s.Save()"
                    subprocess.Popen(["powershell", "-Command", powershell_cmd], shell=True)
        except: pass

    def get_startup_command(self):
        """Return the command Windows should run at login."""
        if getattr(sys, 'frozen', False):
            return f'"{sys.executable}"'
        script_path = os.path.abspath(__file__)
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        runner = pythonw if pythonw.exists() else Path(sys.executable)
        return f'"{runner}" "{script_path}"'

    def setup_auto(self):
        """Native Windows Startup Registration"""
        if sys.platform != "win32":
            messagebox.showinfo("Auto-Start", "Auto-Start setup is only available on Windows.")
            return

        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "VibePad", 0, winreg.REG_SZ, self.get_startup_command())
            winreg.CloseKey(key)
            messagebox.showinfo("Success", "VibePad will now start automatically with Windows.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not set up Auto-Start: {e}")

    def remove_auto(self):
        """Remove from Windows Startup"""
        if sys.platform != "win32":
            messagebox.showinfo("Auto-Start", "Auto-Start setup is only available on Windows.")
            return

        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            try:
                winreg.DeleteValue(key, "VibePad")
                messagebox.showinfo("Success", "Auto-Start has been disabled.")
            except FileNotFoundError:
                messagebox.showinfo("Info", "Auto-Start was already disabled.")
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("Error", f"Could not remove Auto-Start: {e}")

    def clean_data(self):
        """Deep Data Cleanup & Reset"""
        if not messagebox.askyesno(
            "Confirm Reset",
            "This will close VibePad and PERMANENTLY delete all notes and settings.\n\nAre you sure?"
        ):
            return

        try:
            for note in list(self.notes.values()):
                try:
                    note.window.destroy()
                except tk.TclError:
                    pass
            self.notes = {}

            if NOTES_FILE.exists():
                NOTES_FILE.unlink()
            if SETTINGS_FILE.exists():
                SETTINGS_FILE.unlink()

            messagebox.showinfo("Reset Complete", "VibePad has been reset. The application will now close.")
            self._is_resetting = True
            self.quit_app()
        except Exception as e:
            messagebox.showerror("Error", f"Reset failed: {e}")

    def open_settings(self):
        """Small tray settings window for background-app controls."""
        if hasattr(self, "_settings_win") and self._settings_win.winfo_exists():
            self._settings_win.deiconify()
            self._settings_win.lift()
            self._settings_win.focus_force()
            return
            
        settings = tk.Toplevel()
        self._settings_win = settings
        settings.title("VibePad Settings")
        settings.geometry("360x300")
        settings.resizable(False, False)
        if sys.platform == "win32":
            try:
                settings.attributes("-toolwindow", True)
            except tk.TclError:
                pass
        settings.attributes("-topmost", True)
        settings.configure(bg=UI["paper"], highlightthickness=1, highlightbackground=UI["line"])

        sw, sh = settings.winfo_screenwidth(), settings.winfo_screenheight()
        settings.geometry(f"+{(sw-360)//2}+{(sh-300)//2}")

        tk.Label(settings, text="VibePad", font=("Segoe UI", 21, "bold"), bg=UI["paper"], fg=UI["ink"]).pack(pady=(24, 2))
        tk.Label(settings, text="Background controls", font=("Segoe UI", 9), bg=UI["paper"], fg=UI["muted"]).pack(pady=(0, 18))

        btn_frame = tk.Frame(settings, bg=UI["paper"])
        btn_frame.pack(fill=tk.X, padx=32)

        primary = {"font": ("Segoe UI", 10, "bold"), "relief": "flat", "padx": 12, "pady": 9, "cursor": "hand2"}
        secondary = {"font": ("Segoe UI", 10), "relief": "flat", "padx": 12, "pady": 9, "cursor": "hand2", "bg": UI["panel"], "fg": UI["ink"], "activebackground": "#EADDBF"}
        tk.Button(btn_frame, text="+  New Note", bg=UI["accent"], fg="white", activebackground=UI["accent_dark"], activeforeground="white", command=self.new_note, **primary).pack(fill=tk.X, pady=4)
        tk.Button(btn_frame, text="Enable Auto-Start", command=self.setup_auto, **secondary).pack(fill=tk.X, pady=4)
        tk.Button(btn_frame, text="Disable Auto-Start", command=self.remove_auto, **secondary).pack(fill=tk.X, pady=4)
        tk.Button(btn_frame, text="Reset / Clean Data", bg=UI["danger_soft"], fg=UI["danger"], activebackground="#F0D2CC", activeforeground=UI["danger"], command=self.clean_data, **primary).pack(fill=tk.X, pady=4)

    def _run_on_ui(self, callback, *args, **kwargs):
        self.root.after(0, lambda: callback(*args, **kwargs))

    def _setup_ipc(self):
        """Sets up a local socket server to listen for signals from duplicate instances."""
        import socket
        import threading
        self.ipc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipc_socket.bind(("127.0.0.1", 0))
        self.ipc_socket.listen(1)
        port = self.ipc_socket.getsockname()[1]
        try:
            (DATA_DIR / "port.lock").write_text(str(port))
        except Exception:
            pass
        threading.Thread(target=self._ipc_listener, daemon=True).start()

    def _ipc_listener(self):
        while True:
            try:
                conn, _ = self.ipc_socket.accept()
                data = conn.recv(1024)
                if data == b"FOCUS":
                    self._run_on_ui(self.focus_app)
                conn.close()
            except Exception:
                pass

    def focus_app(self):
        """Brings all existing notes to front or opens settings if none exist."""
        has_visible = False
        for note in self.notes.values():
            try:
                if note.window.winfo_exists():
                    note.window.deiconify()
                    note.window.lift()
                    note.window.focus_force()
                    has_visible = True
            except Exception:
                pass
        
        if not has_visible:
            self.open_settings()

    def setup_system_tray(self):
        """Creates a background tray icon for persistent control"""
        if pystray is None: return

        def create_image():
            # Create a simple clean icon (Blue circle with 'V')
            image = Image.new('RGB', (64, 64), color='#FFFFFF')
            dc = ImageDraw.Draw(image)
            dc.ellipse((8, 8, 56, 56), fill='#4A90E2')
            dc.text((22, 12), "V", fill="white", font=None) # Simple text fallback
            return image

        def tray_call(callback, stop_icon=False):
            def wrapped(icon=None, item=None):
                if stop_icon and icon:
                    icon.stop()
                self._run_on_ui(callback)
            return wrapped

        menu = pystray.Menu(
            pystray.MenuItem("New Note", tray_call(self.new_note)),
            pystray.MenuItem("Settings", tray_call(self.open_settings)),
            pystray.MenuItem("Reset / Clean Data", tray_call(self.clean_data)),
            pystray.MenuItem("About", tray_call(self.show_about)),
            pystray.MenuItem("Exit Application", tray_call(self.quit_app, stop_icon=True))
        )
        
        self.tray_icon = pystray.Icon("VibePad", create_image(), "VibePad", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def launch_full(self):
        """Initializes the full app state with safety protection"""
        self.is_standalone = False
        try:
            self._setup_ipc()
            self.load()
            if not self.notes:
                self.create_welcome()
        except Exception as e:
            print(f"Subsystem initialization error: {e}")
            # Ensure at least a welcome note exists if loading fails critically
            if not getattr(self, 'notes', {}):
                self.create_welcome()

    def show_control_panel(self):
        if self.cp and self.cp.root.winfo_exists():
            self.cp.root.lift()
        else:
            self.cp = ControlPanel(self)

        # No more global check_reminders loop to prevent duplicate triggers.
        # Every StickyNote instance now handles its own real-time alert logic via update_countdown.

    def create_welcome(self):
        content = """# Quick Tips:
- **Drag Top**: Move note
- **Right-Click**: Options
- **(+)**: New Note / List
- **Select Text**: Styling
- **Ctrl+N**: New Note
- **Ctrl+P**: Pin Note
- **Ctrl+D**: Delete Note
- **(🔔)**: Set Reminder"""
        d = NoteData(title="Welcome", content=content, x=200, y=200)
        self.add_note(d)

    def add_note(self, data, save=True):
        # Multi-window safety check: destroy existing instance window if replacing
        if data.note_id in self.notes:
            try:
                self.notes[data.note_id].window.destroy()
            except: pass
        
        self.notes[data.note_id] = StickyNote(self, data)
        if save:
            self.save()

    def new_note(self, is_checklist=False, is_timer=False):
        title = "Checklist" if is_checklist else "Timer" if is_timer else "Sticky Note"
        d = NoteData(
            x=300, y=300, 
            height=230 if is_timer else DEFAULT_HEIGHT,
            is_checklist=is_checklist, 
            is_timer=is_timer,
            title=title,
            color_name=self.app_settings.get("last_color_name", "Vibe Yellow"),
            font_name=self.app_settings.get("last_font_name", "Handwriting"),
            font_size=self.app_settings.get("last_font_size", 11)
        )
        self.add_note(d)

    def remove_note(self, nid):
        if nid in self.notes:
            del self.notes[nid]
            self.save()

    def save(self):
        data = []
        for n in self.notes.values():
            n.data.content = n.editor.get("1.0", tk.END).strip()
            data.append(n.data.to_dict())
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_settings(self):
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self.app_settings.update(json.load(f))
            except Exception as e:
                print(f"Settings load error: {e}")

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.app_settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Settings save error: {e}")

    def load(self):
        if not NOTES_FILE.exists(): return
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                if not isinstance(raw, list): return
                for d in raw:
                    # Load without triggering a save for every note
                    self.add_note(NoteData(**d), save=False)
        except Exception as e:
            print(f"Load error: {e}")

    def darken(self, hex_c):
        hex_c = hex_c.lstrip('#')
        rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
        return '#%02x%02x%02x' % tuple(max(0, int(c*0.9)) for c in rgb)

    def show_about(self):
        # Premium Minimal About Window
        about = tk.Toplevel()
        about.title("About VibePad")
        about.geometry("400x540")
        about.resizable(False, False)
        if sys.platform == "win32":
            try:
                about.attributes("-toolwindow", True)
            except tk.TclError:
                pass
        about.attributes("-topmost", True)
        about.configure(bg=UI["paper"], highlightthickness=1, highlightbackground=UI["line"])
        
        # Center Screen
        sw, sh = about.winfo_screenwidth(), about.winfo_screenheight()
        about.geometry(f"+{(sw-400)//2}+{(sh-540)//2}")
        
        # Header Section
        h_f = tk.Frame(about, bg=UI["paper"], height=150)
        h_f.pack(fill=tk.X)
        h_f.pack_propagate(False)
        
        logo = tk.Frame(h_f, bg=UI["accent"], width=46, height=46, highlightthickness=1, highlightbackground=UI["accent_dark"])
        logo.pack(pady=(24, 8))
        logo.pack_propagate(False)
        tk.Label(logo, text="V", font=("Segoe UI", 20, "bold"), bg=UI["accent"], fg="white").pack(expand=True)
        tk.Label(h_f, text="VibePad", font=("Segoe UI", 26, "bold"), 
                 bg=UI["paper"], fg=UI["ink"]).pack()
        tk.Label(h_f, text=f"Version {APP_VERSION}  |  Desktop productivity notes", font=("Segoe UI", 8), 
                 bg=UI["paper"], fg=UI["muted"]).pack(pady=(2, 0))
        
        # Separator
        tk.Frame(about, bg=UI["line"], height=1).pack(fill=tk.X, padx=40)

        # Info Section
        body = tk.Frame(about, bg=UI["paper"], padx=34, pady=22)
        body.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(body, text="A lightweight sticky-note workspace with reminders, checklists, timers, and calm desktop presence.", 
                 font=("Segoe UI", 10), bg=UI["paper"], fg=UI["muted"], wraplength=320, justify="center").pack(pady=(0, 18))
        
        meta = tk.Frame(body, bg=UI["paper"])
        meta.pack(fill=tk.X, pady=(0, 18))
        for label, value in [("Mode", "Tray-first background app"), ("Data", str(DATA_DIR)), ("Startup", "Windows user login")]:
            row = tk.Frame(meta, bg=UI["paper"])
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, font=("Segoe UI", 8, "bold"), bg=UI["paper"], fg=UI["accent"], width=8, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Segoe UI", 8), bg=UI["paper"], fg=UI["muted"], anchor="w", wraplength=250).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Developer Card
        dev_c = tk.Frame(body, bg=UI["panel"], padx=18, pady=14, highlightthickness=1, highlightbackground=UI["line"])
        dev_c.pack(fill=tk.X)
        
        tk.Label(dev_c, text="DEVELOPER", font=("Segoe UI", 7, "bold"), bg=UI["panel"], fg=UI["accent"]).pack(anchor="w")
        tk.Label(dev_c, text="Bappy Kumar", font=("Segoe UI", 11, "bold"), bg=UI["panel"], fg=UI["ink"]).pack(anchor="w", pady=(2, 0))
        tk.Label(dev_c, text="Visualizer | Vibe Coder", font=("Segoe UI", 9), bg=UI["panel"], fg=UI["muted"]).pack(anchor="w")
        
        # Links
        links_f = tk.Frame(body, bg=UI["paper"])
        links_f.pack(pady=(20, 0))

        def create_link(parent, text, url):
            lbl = tk.Label(parent, text=text, font=("Segoe UI Semibold", 9), bg=UI["paper"], fg=UI["accent"], cursor="hand2")
            lbl.pack(pady=5)
            lbl.bind("<Button-1>", lambda e: webbrowser.open(url))
            lbl.bind("<Enter>", lambda e: lbl.configure(fg=UI["accent_dark"]))
            lbl.bind("<Leave>", lambda e: lbl.configure(fg=UI["accent"]))

        create_link(links_f, "GitHub Repository", "https://github.com/bappykumar/VibePad")
        create_link(links_f, "Support Community", "https://t.me/designbd2")
        
        # Footer
        tk.Label(about, text="Copyright 2026 VibePad App. All rights reserved.", font=("Segoe UI", 8), bg=UI["paper"], fg="#B9AD91").pack(pady=16)

    def quit_app(self):
        if not getattr(self, "_is_resetting", False):
            self.save()
        tray_icon = getattr(self, "tray_icon", None)
        if tray_icon:
            try:
                tray_icon.stop()
            except Exception:
                pass
        self.root.quit()

if __name__ == "__main__":
    show_only_cp = "--control-panel" in sys.argv

    # Prevent multiple instances using a named mutex
    if sys.platform == "win32" and not show_only_cp:
        import ctypes
        from tkinter import messagebox
        
        mutex_name = "Global\\VibePad_SingleInstance_Mutex"
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        
        h_mutex = kernel32.CreateMutexW(None, False, mutex_name)
        last_err = ctypes.get_last_error()
        
        if last_err == 183: # ERROR_ALREADY_EXISTS
            try:
                import socket
                lock_file = DATA_DIR / "port.lock"
                if lock_file.exists():
                    port = int(lock_file.read_text().strip())
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2.0)
                    s.connect(("127.0.0.1", port))
                    s.sendall(b"FOCUS")
                    s.close()
            except Exception:
                # If IPC fails, we fall back to a simple message or just exit cleanly
                pass
            sys.exit(0)
            
    app = VibePadApp(show_only_cp=show_only_cp)
