import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


# Color palette
PRIMARY_BG = "#2C2F3A"
PANEL_BG = "#3C3F4A"
ACCENT = "#5DA399"
TEXT_COLOR = "#F0F0F0"
SELECT_COLOR = "#78A083"

def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("Custom.TFrame", background=PRIMARY_BG)

    style.configure("TLabel", font=("Segoe UI", 11), background=PRIMARY_BG, foreground=TEXT_COLOR)

    style.configure("TButton",
        font=("Segoe UI", 11),
        background=ACCENT,
        foreground="white",
        borderwidth=0,
        focuscolor=PRIMARY_BG,
        relief="flat"
    )
    style.map("TButton",
        background=[("active", "#78A083")],
        foreground=[("active", "white")],
        highlightcolor=[("focus", PRIMARY_BG)],
        bordercolor=[("focus", PRIMARY_BG)]
    )

    style.configure("Treeview",
        rowheight=30,
        background=PRIMARY_BG,
        fieldbackground=PRIMARY_BG,
        foreground=TEXT_COLOR,
        borderwidth=0
    )

    style.configure("Treeview.Heading",
        font=("Segoe UI", 11, "bold"),
        background=PANEL_BG,
        foreground=TEXT_COLOR,
        relief="flat"
    )
    style.map("Treeview.Heading",
        background=[("active", ACCENT)]
    )

    return style

# Export theme constants
__all__ = ["apply_theme", "PRIMARY_BG", "PANEL_BG", "ACCENT", "TEXT_COLOR", "SELECT_COLOR"]



def load_logo(path="Images/SafePass_Logo.png", size=(500, 500)):
    image = Image.open(path)
    image = image.resize(size)
    return ImageTk.PhotoImage(image)