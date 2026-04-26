#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  VibePad v2.3 - Developed by Bappy Kumar
============================================================
  Modern, Clean, and Professional Desktop Widget
============================================================
"""

import tkinter as tk
from tkinter import font as tkfont
import json
import os
import sys
import time
import re
from datetime import datetime
from pathlib import Path
import webbrowser

# Ensure UTF-8 for Windows console/environment
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except:
        pass

# ============================================================
# Theme & Config
# ============================================================

APP_NAME = "VibePad"
APP_VERSION = "2.3.0"

if sys.platform == "win32":
    DATA_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
else:
    DATA_DIR = Path.home() / ".config" / APP_NAME

DATA_DIR.mkdir(parents=True, exist_ok=True)
NOTES_FILE = DATA_DIR / "notes.json"

# Modern Harmonious Color Palette
NOTE_COLORS = {
    "Vibe Yellow":  {"bg": "#FFFDE7", "header": "#FFF59D", "border": "#FBC02D", "text": "#424242"},
    "Soft Pink":    {"bg": "#FCE4EC", "header": "#F8BBD0", "border": "#F06292", "text": "#424242"},
    "Mint Green":   {"bg": "#F1F8E9", "header": "#DCEDC8", "border": "#8BC34A", "text": "#424242"},
    "Sky Blue":     {"bg": "#E1F5FE", "header": "#B3E5FC", "border": "#29B6F6", "text": "#424242"},
    "Sweet Orange": {"bg": "#FFF3E0", "header": "#FFE0B2", "border": "#FFB74D", "text": "#424242"},
    "Pure White":   {"bg": "#FFFFFF", "header": "#F5F5F5", "border": "#E0E0E0", "text": "#424242"},
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
        self.font_name = kwargs.get("font_name", "Handwriting")
        self.font_size = kwargs.get("font_size", 11)
    
    def to_dict(self):
        return self.__dict__

class StickyNote:
    def __init__(self, app, data: NoteData):
        self.app = app
        self.data = data
        self.theme = NOTE_COLORS.get(data.color_name, NOTE_COLORS["Vibe Yellow"])
        
        # Setup Window
        self.window = tk.Toplevel()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", data.always_on_top)
        self.window.geometry(f"{data.width}x{data.height}+{data.x}+{data.y}")
        
        # Flags
        self._dragging = False
        self._resizing = False
        
        self.setup_ui()
        self.bind_events()

    def setup_ui(self):
        # Master Border
        self.root_frame = tk.Frame(self.window, bg=self.theme["border"], padx=1, pady=1)
        self.root_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main Container
        self.main_container = tk.Frame(self.root_frame, bg=self.theme["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Modern Header
        self.header = tk.Frame(self.main_container, bg=self.theme["header"], height=32)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        
        # Pin Button
        self.pin_btn = tk.Label(self.header, text="📍" if self.data.always_on_top else "📌", 
                                bg=self.theme["header"], fg=self.theme["text"], 
                                font=("Segoe UI", 11), width=2, cursor="hand2")
        self.pin_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Title
        self.title_label = tk.Label(self.header, text=self.data.title, bg=self.theme["header"], 
                                   fg=self.theme["text"], font=("Segoe UI", 9, "bold"), padx=5)
        self.title_label.pack(side=tk.LEFT)
        
        # Control Buttons
        self.controls = tk.Frame(self.header, bg=self.theme["header"])
        self.controls.pack(side=tk.RIGHT, padx=5)
        
        self.add_btn = tk.Label(self.controls, text="+", bg=self.theme["header"], fg=self.theme["text"], 
                                font=("Segoe UI", 12), width=2, cursor="hand2")
        self.add_btn.pack(side=tk.LEFT)
        
        # Editor with Handwriting Font
        font_family = AVAILABLE_FONTS.get(self.data.font_name, "Segoe Print")
        size = self.data.font_size
        self.editor = tk.Text(self.main_container, bg=self.theme["bg"], fg=self.theme["text"],
                             font=(font_family, size), wrap=tk.WORD, borderwidth=0,
                             padx=15, pady=10, highlightthickness=0, insertbackground=self.theme["text"])
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.tag_configure("strike", overstrike=True)
        self.editor.tag_configure("tick_color", foreground="#2E7D32")  # Dark Green
        self.editor.tag_configure("cross_color", foreground="#C62828") # Dark Red
        
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
                              fg=self.theme["border"], font=("Segoe UI", 10), cursor="size_nw_se")
        self.handle.place(relx=1.0, rely=1.0, anchor="se", x=-2, y=-2)
        
        self.update_colors()

    def update_colors(self):
        hover_bg = self.app.darken(self.theme["header"])
        for btn in [self.add_btn, self.pin_btn]:
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=hover_bg))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.theme["header"]))

    def bind_events(self):
        self.header.bind("<Button-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)
        self.header.bind("<ButtonRelease-1>", self.stop_move)
        self.header.bind("<Button-3>", self.show_menu)
        self.title_label.bind("<Button-3>", self.show_menu)
        self.title_label.bind("<Double-Button-1>", self.edit_title)
        
        self.handle.bind("<Button-1>", self.start_resize)
        self.handle.bind("<B1-Motion>", self.do_resize)
        
        self.pin_btn.bind("<Button-1>", self.toggle_pin)
        self.add_btn.bind("<Button-1>", self.show_plus_menu)
        self.editor.bind("<KeyRelease>", self.on_text_change)
        self.editor.bind("<<Selection>>", self.on_selection)
        self.window.bind("<Configure>", lambda e: self.hide_toolbar()) # Hide when moving/resizing
        self.editor.bind("<Button-1>", self.on_click_text, add="+")
        if self.data.is_checklist:
            self.editor.bind("<Return>", self.handle_checklist_return)
            self.editor.bind("<Button-1>", self.handle_checklist_click, add="+")

        # Keyboard Shortcuts
        self.editor.bind("<Control-n>", lambda e: self.app.new_note())
        self.editor.bind("<Control-N>", lambda e: self.app.new_note())
        self.editor.bind("<Control-d>", lambda e: self.confirm_delete())
        self.editor.bind("<Control-D>", lambda e: self.confirm_delete())
        self.editor.bind("<Control-p>", lambda e: self.toggle_pin())
        self.editor.bind("<Control-P>", lambda e: self.toggle_pin())

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
        menu = tk.Menu(self.window, tearoff=0, font=("Segoe UI", 9))
        menu.add_command(label="  New Note", command=lambda: self.app.new_note(False))
        menu.add_command(label="  New Checklist", command=lambda: self.app.new_note(True))
        menu.tk_popup(e.x_root, e.y_root)

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
        if line_content.startswith("☐ ") or line_content.startswith("☑ ") or line_content.startswith("☒ "):
            self.editor.insert("insert", "\n☐ ")
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
                return "break"

    def apply_checklist_tags(self):
        self.editor.tag_remove("strike", "1.0", tk.END)
        self.editor.tag_remove("tick_color", "1.0", tk.END)
        self.editor.tag_remove("cross_color", "1.0", tk.END)
        
        lines = self.editor.get("1.0", tk.END).splitlines()
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            end = f"{i+1}.end"
            
            if line.startswith("☑"):
                self.editor.tag_add("tick_color", line_start, end)
            elif line.startswith("☒"):
                self.editor.tag_add("cross_color", line_start, end)

    def setup_toolbar(self):
        self.toolbar = tk.Toplevel(self.window)
        self.toolbar.overrideredirect(True)
        self.toolbar.attributes("-topmost", True)
        self.toolbar.withdraw() # Start hidden
        self.toolbar.configure(bg="#333333", padx=2, pady=2)
        
        btn_style = {"bg": "#333333", "fg": "white", "font": ("Segoe UI", 9, "bold"), 
                     "relief": "flat", "padx": 8, "cursor": "hand2"}
        
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
        menu = tk.Menu(self.window, tearoff=0, font=("Segoe UI", 9))
        
        menu.add_command(label="↺ Reset Size", command=self.reset_size)
        menu.add_separator()
        
        c_menu = tk.Menu(menu, tearoff=0)
        for name in NOTE_COLORS:
            c_menu.add_command(label=f"  {name}", command=lambda n=name: self.change_theme(n))
        menu.add_cascade(label="🎨 Themes", menu=c_menu)
        
        f_menu = tk.Menu(menu, tearoff=0)
        for name in AVAILABLE_FONTS:
            f_menu.add_command(label=f"  {name}", command=lambda n=name: self.change_font(n))
        menu.add_cascade(label="🔤 Fonts", menu=f_menu)
        
        s_menu = tk.Menu(menu, tearoff=0)
        for s in [9, 10, 11, 12, 14, 16, 18, 20, 24]:
            s_menu.add_command(label=f"  {s}px", command=lambda sz=s: self.change_font_size(sz))
        menu.add_cascade(label="📏 Font Size", menu=s_menu)
        
        menu.add_separator()
        menu.add_command(label="📌 Unpin Header" if self.data.always_on_top else "📍 Pin Header", 
                        command=self.toggle_pin)
        menu.add_command(label="🗑️ Delete Note", command=self.confirm_delete)
        menu.add_separator()
        menu.add_command(label="ℹ️ About", command=self.app.show_about)
        menu.add_command(label="❌ Exit App", command=self.app.quit_app)
        
        menu.tk_popup(e.x_root, e.y_root)

    def reset_size(self):
        self.window.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        self.data.width, self.data.height = DEFAULT_WIDTH, DEFAULT_HEIGHT
        self.app.save()

    def change_theme(self, name):
        self.data.color_name = name
        self.theme = NOTE_COLORS[name]
        self.root_frame.configure(bg=self.theme["border"])
        self.main_container.configure(bg=self.theme["bg"])
        self.header.configure(bg=self.theme["header"])
        self.title_label.configure(bg=self.theme["header"], fg=self.theme["text"])
        self.controls.configure(bg=self.theme["header"])
        self.pin_btn.configure(bg=self.theme["header"], fg=self.theme["text"])
        self.add_btn.configure(bg=self.theme["header"], fg=self.theme["text"])
        self.editor.configure(bg=self.theme["bg"], fg=self.theme["text"], insertbackground=self.theme["text"])
        self.handle.configure(bg=self.theme["bg"], fg=self.theme["border"])
        self.update_colors()
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
        
        if self.data.is_checklist:
            self.apply_checklist_tags()
        else:
            self.apply_markdown_tags()
        self.app.save()

    def toggle_pin(self, event=None):
        self.data.always_on_top = not self.data.always_on_top
        self.window.attributes("-topmost", self.data.always_on_top)
        self.pin_btn.configure(text="📍" if self.data.always_on_top else "📌")
        self.app.save()

    def edit_title(self, event):
        """Allow editing the note title with an inline entry."""
        edit = tk.Entry(self.header, bg=self.theme["header"], fg=self.theme["text"],
                       font=("Segoe UI", 9, "bold"), borderwidth=0, highlightthickness=1)
        edit.insert(0, self.data.title)
        
        # Position exactly over the title label
        edit.place(x=self.title_label.winfo_x(), y=self.title_label.winfo_y(), 
                  width=self.title_label.winfo_width(), height=self.title_label.winfo_height())
        edit.focus_set()
        edit.select_range(0, tk.END)
        
        def save(e=None):
            new_title = edit.get().strip() or "Sticky Note"
            self.data.title = new_title
            self.title_label.configure(text=new_title)
            edit.destroy()
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
        confirm.geometry(f"200x120+{wx + (ww-200)//2}+{wy + (wh-120)//2}")
        confirm.attributes("-topmost", True)
        confirm.configure(bg="white", highlightthickness=1, highlightbackground="#E0E0E0")
        
        tk.Label(confirm, text="Delete Note?", font=("Segoe UI", 11, "bold"), bg="white", fg="#DD2C00").pack(pady=(15, 5))
        tk.Label(confirm, text="This action cannot be undone.", font=("Segoe UI", 8), bg="white", fg="#757575").pack()
        
        btn_f = tk.Frame(confirm, bg="white")
        btn_f.pack(pady=15)
        
        tk.Button(btn_f, text="Delete", bg="#FF5252", fg="white", font=("Segoe UI", 9, "bold"), 
                  relief="flat", padx=10, command=lambda: [confirm.destroy(), self.window.destroy(), self.app.remove_note(self.data.note_id)]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_f, text="Cancel", bg="#EEEEEE", fg="#424242", font=("Segoe UI", 9), 
                  relief="flat", padx=10, command=confirm.destroy).pack(side=tk.LEFT, padx=5)

class VibePadApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.notes = {}
        self.load()
        
        if not self.notes:
            self.create_welcome()
            
        self.root.mainloop()

    def create_welcome(self):
        content = """# Quick Tips:
- **Drag Top**: Move note
- **Right-Click**: Options
- **(+)**: New Note / List
- **Select Text**: Styling
- **Ctrl+N**: New Note
- **Ctrl+P**: Pin Note
- **Ctrl+D**: Delete Note"""
        d = NoteData(title="Welcome", content=content, x=200, y=200)
        self.add_note(d)

    def add_note(self, data):
        self.notes[data.note_id] = StickyNote(self, data)
        self.save()

    def new_note(self, is_checklist=False):
        title = "Checklist" if is_checklist else "Sticky Note"
        d = NoteData(x=300, y=300, is_checklist=is_checklist, title=title)
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

    def load(self):
        if not NOTES_FILE.exists(): return
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                for d in raw:
                    self.add_note(NoteData(**d))
        except: pass

    def darken(self, hex_c):
        hex_c = hex_c.lstrip('#')
        rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
        return '#%02x%02x%02x' % tuple(max(0, int(c*0.9)) for c in rgb)

    def show_about(self):
        # SaaS Style Premium About Window
        about = tk.Toplevel()
        about.title("About VibePad")
        about.geometry("340x450")
        about.resizable(False, False)
        about.attributes("-topmost", True)
        about.configure(bg="white")
        
        # Center Screen
        sw, sh = about.winfo_screenwidth(), about.winfo_screenheight()
        about.geometry(f"+{(sw-340)//2}+{(sh-450)//2}")
        
        # Header Section
        h_f = tk.Frame(about, bg="#4A90E2", height=120)
        h_f.pack(fill=tk.X)
        h_f.pack_propagate(False)
        
        tk.Label(h_f, text="VibePad", font=("Segoe UI", 24, "bold"), bg="#4A90E2", fg="white").pack(expand=True)
        
        # Info Section
        body = tk.Frame(about, bg="white", padx=30, pady=20)
        body.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(body, text=f"Version {APP_VERSION}", font=("Segoe UI", 9), bg="white", fg="#999999").pack(anchor="w")
        tk.Label(body, text="Experience a realistic and modern sticky note on your desktop. Designed for productivity and aesthetics.", 
                 font=("Segoe UI", 10), bg="white", fg="#424242", wraplength=280, justify="left").pack(pady=(15, 20))
        
        # Developer Card
        dev_c = tk.Frame(body, bg="#F9F9F9", padx=15, pady=10, highlightthickness=1, highlightbackground="#F0F0F0")
        dev_c.pack(fill=tk.X)
        
        tk.Label(dev_c, text="DEVELOPER", font=("Segoe UI", 7, "bold"), bg="#F9F9F9", fg="#4A90E2").pack(anchor="w")
        tk.Label(dev_c, text="Bappy Kumar", font=("Segoe UI", 11, "bold"), bg="#F9F9F9", fg="#212121").pack(anchor="w", pady=(2, 0))
        tk.Label(dev_c, text="Visualizer | Vibe Coder", font=("Segoe UI", 9), bg="#F9F9F9", fg="#616161").pack(anchor="w")
        
        # Links
        btn_g = tk.Label(body, text="📂 GitHub Repository", font=("Segoe UI", 10, "bold"), bg="white", fg="#4A90E2", cursor="hand2")
        btn_g.pack(pady=(20, 0))
        btn_g.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/bappykumar/VibePad"))

        btn_l = tk.Label(body, text="🌐 Join Community", font=("Segoe UI", 10, "bold"), bg="white", fg="#4A90E2", cursor="hand2")
        btn_l.pack(pady=(10, 0))
        btn_l.bind("<Button-1>", lambda e: webbrowser.open("https://t.me/designbd2"))
        
        # Footer
        tk.Label(about, text="© 2026 VibePad App. All rights reserved.", font=("Segoe UI", 8), bg="white", fg="#CCCCCC").pack(pady=15)

    def quit_app(self):
        self.save()
        self.root.quit()

if __name__ == "__main__":
    if sys.platform == "win32":
        import ctypes
        # Keep the mutex reference alive to prevent garbage collection
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "VibePad_SingleInstance_Mutex")
        if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
            sys.exit(0)
            
    app = VibePadApp()

