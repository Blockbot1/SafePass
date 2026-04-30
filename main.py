import tkinter as tk
from tkinter import ttk, messagebox
import storage
from pathlib import Path
from vault import Vault, PasswordEntry
from Design import apply_theme, Background
import client

class SafePassApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SafePass")
        self.root.state('zoomed')
        self.current_user = ""
        self.master_password = ""
        self.vault = None
        apply_theme(self.root)
        self.show_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def show_login_screen(self):
        self.clear_screen()
        self.root.configure(bg=Background)  # Fixes the "white background" issue

        # Main container that fills the whole screen
        self.main_frame = ttk.Frame(self.root, style="Custom.TFrame")
        self.main_frame.pack(expand=True, fill="both")

        # Center login box
        login_box = ttk.Frame(self.main_frame, padding=40, style="Custom.TFrame")
        login_box.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(login_box, text="SafePass Login", font=("Segoe UI", 24, "bold")).pack(pady=20)

        ttk.Label(login_box, text="Username").pack(anchor="w")
        u_ent = ttk.Entry(login_box, width=30)
        u_ent.pack(pady=(0, 15))

        ttk.Label(login_box, text="Master Password").pack(anchor="w")
        p_ent = ttk.Entry(login_box, show="*", width=30)
        p_ent.pack(pady=(0, 20))

        def do_login():
            user = u_ent.get()
            pwd = p_ent.get()
            if not user or not pwd:
                messagebox.showwarning("Input Error", "Please fill in all fields")
                return

            # 1. Ask server if credentials are correct
            res = client.server_request("login", user, pwd)
            if res == "SUCCESS":
                self.current_user = user
                self.master_password = pwd

                # 2. Download the vault blob
                data = client.server_request("download", user)
                if data:
                    storage.save_vault_raw(user, data)

                # 3. Try to load the vault locally
                try:
                    self.vault = storage.load_vault(user, pwd)
                    self.show_vault_screen()
                except Exception as e:
                    messagebox.showerror("Vault Error", f"Could not decrypt vault: {e}")
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

        def do_register():
            user = u_ent.get()
            pwd = p_ent.get()
            if not user or not pwd:
                messagebox.showwarning("Input Error", "Please fill in all fields")
                return

            res = client.server_request("register", user, pwd)
            if res == "SUCCESS":
                messagebox.showinfo("Success", "Account created! You can now login.")
            elif res == "EXISTS":
                messagebox.showerror("Error", "Username already exists.")
            else:
                messagebox.showerror("Error", "Could not connect to server.")

        ttk.Button(login_box, text="Login", width=20, command=do_login).pack(pady=5)
        ttk.Button(login_box, text="Register", width=20, command=do_register).pack(pady=5)

    def show_vault_screen(self):
        self.clear_screen()
        self.root.configure(bg=Background)

        # UI for the vault
        frame = ttk.Frame(self.root, padding=20, style="Custom.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Welcome, {self.current_user}", font=("Segoe UI", 14)).pack(pady=10)

        # The Table
        columns = ("Site", "User")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        self.tree.heading("Site", text="Website / Service")
        self.tree.heading("User", text="Username")
        self.tree.pack(fill="both", expand=True, pady=20)

        # Binding double-click to view password
        self.tree.bind("<Double-1>", lambda e: self.show_password_detail())

        btn_frame = ttk.Frame(frame, style="Custom.TFrame")
        btn_frame.pack(fill="x")
        # Add this line along with your other buttons in show_vault_screen
        ttk.Button(btn_frame, text="🗑 Delete Entry", command=self.delete_entry).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="+ Add Entry", command=self.add_entry_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="👁 Show Password", command=self.show_password_detail).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 Sync to Cloud", command=self.sync_vault).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📥 Pull Changes", command=self.refresh_vault).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Logout", command=self.show_login_screen).pack(side="right", padx=5)


        self.refresh_tree()

    def delete_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an entry to delete.")
            return

        # Ask for confirmation
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?"):
            return

        # Get index and remove from vault object
        idx = self.tree.index(selected[0])
        self.vault.remove_entry(idx)

        # Save the change locally
        storage.save_vault(self.current_user, self.master_password, self.vault)

        # Refresh the UI
        self.refresh_tree()
        messagebox.showinfo("Success", "Entry deleted locally. Sync to update the cloud!")
    def refresh_tree(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for entry in self.vault.get_all_entries():
            self.tree.insert("", "end", values=(entry.site, entry.username))

    def show_password_detail(self):
        selected = self.tree.selection()
        if not selected: return
        idx = self.tree.index(selected[0])
        entry = self.vault.get_all_entries()[idx]
        messagebox.showinfo("Details", f"Site: {entry.site}\nUser: {entry.username}\nPass: {entry.password}\nNotes: {entry.notes}")

    # בתוך הקובץ שבו נמצא ה-GUI (למשל Design.py)

    def sync_button_clicked(self):
        try:
            # שלב א': תקשורת מול השרת
            # כאן אנחנו פונים למחלקת התקשורת שתבצע את העלאת/הורדת הקובץ
            status = self.network_client.sync_vault_with_server()

            if status:
                # שלב ב': טעינה מחדש של הנתונים מהדיסק לזיכרון
                # לאחר שהקובץ החדש ירד מהשרת, צריך "לקרוא" אותו שוב
                self.vault_manager.load_vault()

                # שלב ג': רענון הטבלה בממשק הגרפי
                # זו הפונקציה שמוחקת את השורות הישנות ומציגה את החדשות
                self.refresh_table()

                print("Sync complete: Local vault is now up to date.")
            else:
                print("Sync failed: Could not reach the server.")

        except Exception as e:
            print(f"Error during sync: {e}")

    def sync_vault(self):
        """Uploads the current local state to the server."""
        try:
            # 1. Save current memory state to local disk first
            storage.save_vault(self.current_user, self.master_password, self.vault)

            # 2. Read those bytes and upload
            user_path = Path(f"{self.current_user}.vault")
            if user_path.exists():
                res = client.server_request("upload", self.current_user, self.master_password,
                                            data=user_path.read_bytes())
                if res == "OK":
                    messagebox.showinfo("Sync", "Vault uploaded to cloud successfully!")
                else:
                    messagebox.showerror("Sync Error", "Server failed to save the vault.")
        except Exception as e:
            messagebox.showerror("Sync Error", f"Failed to upload: {e}")

    def refresh_vault(self):
        """Downloads the latest version from server and RE-LOADS the UI."""
        try:
            # 1. Download the latest blob from server
            data = client.server_request("download", self.current_user)
            if data:
                # 2. Overwrite the local file with the server's version
                storage.save_vault_raw(self.current_user, data)

                # 3. CRITICAL: Re-load the vault object from the new file into memory
                self.vault = storage.load_vault(self.current_user, self.master_password)

                # 4. Update the UI table
                self.refresh_tree()
                messagebox.showinfo("Refresh", "Vault updated from cloud!")
            else:
                messagebox.showwarning("Refresh", "No data found on server.")
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Could not sync from server: {e}")

    def add_entry_window(self):
        # Implementation similar to your old code, but calling self.vault.add_entry
        # and then storage.save_vault(self.current_user, ...)
        pass # (Omitted for brevity, but use your original add_win logic)

    def add_entry_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Add New Entry")
        add_win.geometry("400x500")
        add_win.configure(bg=Background)

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

            new_entry = PasswordEntry(
                site=site,
                username=user_ent.get(),
                password=pass_ent.get(),
                notes=notes_ent.get()
            )

            self.vault.add_entry(new_entry)
            # Save to local file using the new storage logic
            storage.save_vault(self.current_user, self.master_password, self.vault)
            self.refresh_tree()
            add_win.destroy()
            messagebox.showinfo("Success", f"Entry for {site} added locally. Don't forget to Sync!")

        ttk.Button(add_win, text="Save Entry", command=save_new_entry).pack(pady=20)
        ttk.Button(add_win, text="Cancel", command=add_win.destroy).pack()
if __name__ == "__main__":
    root = tk.Tk()
    app = SafePassApp(root)
    root.mainloop()