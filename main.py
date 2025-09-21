import tkinter as tk
from tkinter import ttk
from storage import load_vault, save_vault
from vault import Vault, VaultEntry
from PIL import Image, ImageTk
import os
from Design import apply_theme, Background, Window_Background, Button, TEXT_COLOR, SELECT_COLOR, load_logo



# Global state
vault: Vault = None
master_password: str = ""

# Create main window
root = tk.Tk()
root.title("SafePass")
root.geometry("1000x750")
root.state('zoomed')
root.resizable(False, False)

style = apply_theme(root)


def show_unlock_screen():
    def on_unlock():
        password = password_var.get()
        if not password:
            status_label.config(text="Please enter your master password.", foreground="red")
            return
        try:
            global vault, master_password
            vault = load_vault(password)
            master_password = password
            show_vault_screen()
        except Exception as e:
            print("Error:", e)
            status_label.config(text="Incorrect password or corrupted vault.", foreground="red")

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=Background)
    frame = ttk.Frame(root, padding=20, style="Custom.TFrame")
    frame.pack(expand=True)

    logo_photo = load_logo()
    ttk.Label(frame, image=logo_photo).pack(pady=(0, 20))
    frame.logo_ref = logo_photo
    ttk.Label(frame, text="Enter your master password:").pack()

    password_var = tk.StringVar()
    password_entry = ttk.Entry(frame, textvariable=password_var, show="*")
    password_entry.pack(pady=8, ipadx=5)
    password_entry.focus()
    password_entry.bind("<Return>", lambda event: on_unlock())
    ttk.Button(frame, text="Unlock", command=on_unlock).pack(pady=10)

    global status_label
    status_label = ttk.Label(frame, text="", foreground="red")
    status_label.pack(pady=(10, 0))

def show_vault_screen():
    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for i, entry in enumerate(vault.get_all_entries()):
            tree.insert("", "end", iid=i, values=(entry.site, entry.username))

    def on_add_click():
        def on_save():
            site = site_var.get().strip()
            user = user_var.get().strip()
            pwd = pwd_var.get().strip()
            notes = notes_var.get().strip()

            if not site or not user or not pwd:
                status_label.config(text="All fields except notes are required.", foreground="red")
                return

            vault.add_entry(VaultEntry(site, user, pwd, notes))
            save_vault(master_password, vault)
            refresh_table()
            status_label.config(text="Entry added.", foreground=SELECT_COLOR)
            add_win.destroy()

        add_win = tk.Toplevel(root)
        add_win.title("Add Entry")
        add_win.geometry("320x280")
        add_win.configure(bg=Window_Background)
        add_win.grab_set()

        def lbl(text):
            ttk.Label(add_win, text=text, background=Window_Background, foreground=TEXT_COLOR).pack(anchor="w", padx=10, pady=(8, 0))

        site_var = tk.StringVar()
        user_var = tk.StringVar()
        pwd_var = tk.StringVar()
        notes_var = tk.StringVar()

        lbl("Site:")
        ttk.Entry(add_win, textvariable=site_var).pack(fill="x", padx=10)

        lbl("Username:")
        ttk.Entry(add_win, textvariable=user_var).pack(fill="x", padx=10)

        lbl("Password:")
        ttk.Entry(add_win, textvariable=pwd_var, show="*").pack(fill="x", padx=10)

        lbl("Notes:")
        ttk.Entry(add_win, textvariable=notes_var).pack(fill="x", padx=10)

        ttk.Button(add_win, text="💾 Save", command=on_save).pack(pady=15)

    def on_delete_click():
        selected = tree.focus()
        if not selected:
            status_label.config(text="Select an entry to delete.", foreground="red")
            return
        idx = int(selected)
        vault.entries.pop(idx)
        save_vault(master_password, vault)
        refresh_table()
        status_label.config(text="Entry deleted.", foreground=SELECT_COLOR)

    def on_edit_click():
        selected = tree.focus()
        if not selected:
            status_label.config(text="Select an entry to edit.", foreground="red")
            return

        entry = vault.get_all_entries()[int(selected)]

        edit_win = tk.Toplevel(root)
        edit_win.title("Edit Entry")
        edit_win.geometry("320x280")
        edit_win.configure(bg=Window_Background)
        edit_win.grab_set()

        def lbl(text):
            ttk.Label(edit_win, text=text, background=Window_Background, foreground=TEXT_COLOR).pack(anchor="w", padx=10, pady=(8, 0))

        site_var = tk.StringVar(value=entry.site)
        user_var = tk.StringVar(value=entry.username)
        pwd_var = tk.StringVar(value=entry.password)
        notes_var = tk.StringVar(value=entry.notes)

        lbl("Site:")
        ttk.Entry(edit_win, textvariable=site_var).pack(fill="x", padx=10)

        lbl("Username:")
        ttk.Entry(edit_win, textvariable=user_var).pack(fill="x", padx=10)

        lbl("Password:")
        ttk.Entry(edit_win, textvariable=pwd_var, show="*").pack(fill="x", padx=10)

        lbl("Notes:")
        ttk.Entry(edit_win, textvariable=notes_var).pack(fill="x", padx=10)

        def on_save_edit():
            entry.site = site_var.get().strip()
            entry.username = user_var.get().strip()
            entry.password = pwd_var.get().strip()
            entry.notes = notes_var.get().strip()
            save_vault(master_password, vault)
            refresh_table()
            status_label.config(text="Entry updated.", foreground=SELECT_COLOR)
            edit_win.destroy()

        ttk.Button(edit_win, text="✅ Save Changes", command=on_save_edit).pack(pady=15)

    def on_view_entry(event=None):
        selected = tree.focus()
        if not selected:
            return

        entry = vault.get_all_entries()[int(selected)]

        view_win = tk.Toplevel(root)
        view_win.title("View Entry")
        view_win.geometry("700x520")
        view_win.configure(bg=Window_Background)
        view_win.grab_set()

        def lbl(text):
            ttk.Label(view_win, text=text, background=Window_Background, foreground=TEXT_COLOR, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        lbl("Site:")
        ttk.Label(view_win, text=entry.site, background=Window_Background, foreground=TEXT_COLOR).pack(anchor="w", padx=10)

        lbl("Username:")
        ttk.Label(view_win, text=entry.username, background=Window_Background, foreground=TEXT_COLOR).pack(anchor="w", padx=10)

        lbl("Password:")
        password_var = tk.StringVar(value="*" * len(entry.password))
        password_label = ttk.Label(view_win, textvariable=password_var, background=Window_Background, foreground=TEXT_COLOR)
        password_label.pack(anchor="w", padx=10)

        def toggle_password():
            if password_var.get().startswith("*"):
                password_var.set(entry.password)
                toggle_btn.config(text="Hide")
            else:
                password_var.set("*" * len(entry.password))
                toggle_btn.config(text="Show")

        toggle_btn = ttk.Button(view_win, text="Show", command=toggle_password)
        toggle_btn.pack(padx=10, pady=5, anchor="w")

        lbl("Notes:")
        notes_text = tk.Text(view_win, height=4, wrap="word", background="#444", foreground="white")
        notes_text.insert("1.0", entry.notes)
        notes_text.configure(state="disabled")
        notes_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=Background)

    frame = ttk.Frame(root, padding=20, style="Custom.TFrame")
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Your Vault", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))
    columns = ("Site", "Username")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=260, anchor="w")
    tree.pack(fill="both", expand=True)
    tree.bind("<Double-1>", on_view_entry)

    btn_row = ttk.Frame(frame, style="Custom.TFrame")
    btn_row.pack(pady=10)
    ttk.Button(btn_row, text="➕ Add Entry", command=on_add_click).pack(side="left", padx=5)
    ttk.Button(btn_row, text="🗑 Delete Entry", command=on_delete_click).pack(side="left", padx=5)
    ttk.Button(btn_row, text="✏ Edit Entry", command=on_edit_click).pack(side="left", padx=5)

    status_label = ttk.Label(frame, text="", foreground=SELECT_COLOR)
    status_label.pack()

    refresh_table()

# Run the app
show_unlock_screen()
root.mainloop()
