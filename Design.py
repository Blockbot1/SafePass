import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os


# Color palette
Background = "#2C2F3A"
Window_Background = "#421C10"
Button = "#6F732F"
TEXT_COLOR = "#F0F0F0"
SELECT_COLOR = "#78A083"

def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("Custom.TFrame", background=Background)

    style.configure("TLabel", font=("Segoe UI", 11), background=Background, foreground=TEXT_COLOR)

    style.configure("TButton",
        font=("Segoe UI", 11),
        background=Button,
        foreground="white",
        borderwidth=0,
        focuscolor=Background,
        relief="flat"
    )
    style.map("TButton",
        background=[("active", "#78A083")],
        foreground=[("active", "white")],
        highlightcolor=[("focus", Background)],
        bordercolor=[("focus", Background)]
    )

    style.configure("Treeview",
        rowheight=30,
        background=Background,
        fieldbackground=Background,
        foreground=TEXT_COLOR,
        borderwidth=0
    )

    style.configure("Treeview.Heading",
        font=("Segoe UI", 11, "bold"),
        background=Window_Background,
        foreground=TEXT_COLOR,
        relief="flat"
    )
    style.map("Treeview.Heading",
        background=[("active", Button)]
    )

    return style

# Export theme constants
__all__ = ["apply_theme", "Background", "Window_Background", "Button", "TEXT_COLOR", "SELECT_COLOR"]



def load_logo(path="Images/SafePass_Logo.png", size=(500, 500)):
    image = Image.open(path)
    image = image.resize(size)
    return ImageTk.PhotoImage(image)