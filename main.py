import tkinter as tk
from tkinter import ttk, messagebox
from storage import load_vault, save_vault
from vault import Vault, PasswordEntry
from Design import apply_theme, Background, TEXT_COLOR, load_logo
from client import upload_vault, download_vault


class SafePassApp:
    """
    The Main Application Class.
    Encapsulates the entire UI logic and state (Vault and Password).
    This fulfills the 'User-Defined Class' and 'Encapsulation' requirements.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("SafePass")
        self.root.attributes('-fullscreen', True)
        self.root.state('zoomed')

        self.vault = None
        self.master_password = ""

        # Apply the theme from Design.py
        self.style = apply_theme(self.root)

        # Start with the unlock screen
        self.show_unlock_screen()

    def clear_screen(self):
        """Helper to remove all widgets when switching screens."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_unlock_screen(self):
        self.clear_screen()
        self.root.configure(bg=Background)

        frame = ttk.Frame(self.root, padding=20, style="Custom.TFrame")
        frame.pack(expand=True)

        # Logo
        try:
            self.logo_photo = load_logo()
            ttk.Label(frame, image=self.logo_photo, background=Background).pack(pady=10)
        except:
            ttk.Label(frame, text="SafePass", font=("Segoe UI", 24, "bold")).pack(pady=10)

        ttk.Label(frame, text="Enter Master Password:").pack(pady=5)

        pass_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=pass_var, show="*", width=30)
        entry.pack(pady=5)
        entry.focus()

        status_label = ttk.Label(frame, text="")
        status_label.pack(pady=5)

        def handle_unlock():
            pwd = pass_var.get()
            try:
                self.vault = load_vault(pwd)
                self.master_password = pwd
                self.show_vault_screen()
            except Exception:
                status_label.config(text="Invalid Password", foreground="red")

        ttk.Button(frame, text="Unlock Vault", command=handle_unlock).pack(pady=10)
        ttk.Button(frame, text="Exit", command=self.root.quit).pack(pady=5)

    def show_vault_screen(self):
        self.clear_screen()

        frame = ttk.Frame(self.root, padding=20, style="Custom.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Your Vault", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Table (Treeview)
        columns = ("Site", "Username")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack(fill="both", expand=True)

        self.refresh_tree()

        # Buttons
        btn_frame = ttk.Frame(frame, style="Custom.TFrame")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Add Entry", command=self.add_entry_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Sync (Upload)", command=lambda: upload_vault("user1")).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Lock", command=self.show_unlock_screen).pack(side="left", padx=5)

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in self.vault.get_all_entries():
            # Polymorphism: using the method defined in our vault classes
            self.tree.insert("", "end", values=(entry.site, getattr(entry, 'username', 'N/A')))

    def add_entry_window(self):
        """Opens a top-level window to create a new PasswordEntry."""
        add_win = tk.Toplevel(self.root)
        add_win.title("Add New Entry")
        add_win.geometry("400x500")
        add_win.configure(bg=Background)

        # Helper to create labels and entries
        def create_field(label_text):
            ttk.Label(add_win, text=label_text).pack(pady=(10, 0))
            entry = ttk.Entry(add_win, width=35)
            entry.pack(pady=5)
            return entry

        site_ent = create_field("Website/Service Name:")
        user_ent = create_field("Username:")
        pass_ent = create_field("Password:")
        notes_ent = create_field("Notes (Optional):")

        def save_new_entry():
            site = site_ent.get()
            if not site:
                messagebox.showerror("Error", "Site name is required!")
                return

            # Create the object using our new Inheritance-based class
            new_entry = PasswordEntry(
                site=site,
                username=user_ent.get(),
                password=pass_ent.get(),
                notes=notes_ent.get()
            )

            self.vault.add_entry(new_entry)
            save_vault(self.master_password, self.vault)  # Save to local file
            self.refresh_tree()  # Update the UI table
            add_win.destroy()
            messagebox.showinfo("Success", f"Entry for {site} added!")

        ttk.Button(add_win, text="Save Entry", command=save_new_entry).pack(pady=20)
        ttk.Button(add_win, text="Cancel", command=add_win.destroy).pack()
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected: return
        index = self.tree.index(selected[0])
        self.vault.remove_entry(index)
        save_vault(self.master_password, self.vault)
        self.refresh_tree()


if __name__ == "__main__":
    root = tk.Tk()
    app = SafePassApp(root)
    root.mainloop()