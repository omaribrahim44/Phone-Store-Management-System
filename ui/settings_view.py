# ui/settings_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, filedialog
import config
from modules.backup_manager import create_backup, list_backups, restore_backup, delete_backup

class SettingsFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=15)
        self.frame.columnconfigure(0, weight=1)
        
        # Create notebook for different settings sections
        self.notebook = tb.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Shop Info Tab
        self.create_shop_info_tab()
        
        # Backup Tab
        self.create_backup_tab()
        
    def create_shop_info_tab(self):
        shop_frame = tb.Frame(self.notebook, padding=15)
        self.notebook.add(shop_frame, text="Shop Information")
        
        cfg = config.load_config()
        shop_info = cfg.get("shop_info", config.DEFAULT_SHOP_INFO)
        
        # Shop Name
        tb.Label(shop_frame, text="Shop Name:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.shop_name = tb.Entry(shop_frame, width=40)
        self.shop_name.insert(0, shop_info.get("name", ""))
        self.shop_name.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        
        # Address
        tb.Label(shop_frame, text="Address:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.shop_address = tb.Entry(shop_frame, width=40)
        self.shop_address.insert(0, shop_info.get("address", ""))
        self.shop_address.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        
        # Phone
        tb.Label(shop_frame, text="Phone:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.shop_phone = tb.Entry(shop_frame, width=40)
        self.shop_phone.insert(0, shop_info.get("phone", ""))
        self.shop_phone.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        
        # Tax Rate
        tb.Label(shop_frame, text="Tax Rate (%):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.tax_rate = tb.Entry(shop_frame, width=40)
        self.tax_rate.insert(0, shop_info.get("tax_rate", "0"))
        self.tax_rate.grid(row=3, column=1, sticky="ew", pady=5, padx=5)
        
        # Currency
        tb.Label(shop_frame, text="Currency:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.currency = tb.Entry(shop_frame, width=40)
        self.currency.insert(0, shop_info.get("currency", "EGP"))
        self.currency.grid(row=4, column=1, sticky="ew", pady=5, padx=5)
        
        # Theme
        tb.Label(shop_frame, text="Theme:").grid(row=5, column=0, sticky="w", pady=5, padx=5)
        self.theme = tb.Combobox(shop_frame, values=["flatly", "darkly", "cosmo", "journal", "litera", "lumen", "minty", "pulse", "sandstone", "united", "yeti"], state="readonly", width=38)
        self.theme.set(cfg.get("theme", "flatly"))
        self.theme.grid(row=5, column=1, sticky="ew", pady=5, padx=5)
        
        # Save Button
        tb.Button(shop_frame, text="Save Shop Info", bootstyle="success", command=self.save_shop_info).grid(row=6, column=1, sticky="e", pady=15, padx=5)
        
    def create_backup_tab(self):
        backup_frame = tb.Frame(self.notebook, padding=15)
        self.notebook.add(backup_frame, text="Backup & Restore")
        
        backup_frame.columnconfigure(0, weight=1)
        backup_frame.rowconfigure(2, weight=1)
        
        # --- Manual Backup Section ---
        manual_frame = tb.Labelframe(backup_frame, text="Manual Backup", padding=10)
        manual_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        tb.Label(manual_frame, text="Create a backup of your database:").pack(anchor="w", pady=5)
        tb.Button(manual_frame, text="Create Backup Now", bootstyle="primary", command=self.create_backup_now).pack(anchor="w", pady=5)
        
        # --- Auto Backup Settings ---
        auto_frame = tb.Labelframe(backup_frame, text="Automatic Backup", padding=10)
        auto_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        cfg = config.load_config()
        backup_cfg = cfg.get("backup", {})
        
        self.auto_backup_enabled = tb.BooleanVar(value=backup_cfg.get("auto_backup_enabled", True))
        tb.Checkbutton(auto_frame, text="Enable Automatic Backups", variable=self.auto_backup_enabled, bootstyle="primary").pack(anchor="w", pady=5)
        
        freq_frame = tb.Frame(auto_frame)
        freq_frame.pack(anchor="w", pady=5)
        tb.Label(freq_frame, text="Frequency:").pack(side="left", padx=(0, 5))
        self.backup_frequency = tb.Combobox(freq_frame, values=["daily", "weekly"], state="readonly", width=15)
        self.backup_frequency.set(backup_cfg.get("auto_backup_frequency", "daily"))
        self.backup_frequency.pack(side="left")
        
        last_backup = backup_cfg.get("last_backup_date", "Never")
        if last_backup and last_backup != "Never":
            last_backup = last_backup[:19]  # Truncate to readable format
        tb.Label(auto_frame, text=f"Last Backup: {last_backup}").pack(anchor="w", pady=5)
        
        tb.Button(auto_frame, text="Save Auto-Backup Settings", bootstyle="success", command=self.save_backup_settings).pack(anchor="w", pady=5)
        
        # --- Existing Backups ---
        backups_frame = tb.Labelframe(backup_frame, text="Existing Backups", padding=10)
        backups_frame.grid(row=2, column=0, sticky="nsew")
        backups_frame.columnconfigure(0, weight=1)
        backups_frame.rowconfigure(0, weight=1)
        
        # Backups table
        cols = ("filename", "size", "date")
        self.backups_tree = ttk.Treeview(backups_frame, columns=cols, show="headings", height=8)
        self.backups_tree.heading("filename", text="Filename")
        self.backups_tree.heading("size", text="Size (MB)")
        self.backups_tree.heading("date", text="Date")
        self.backups_tree.column("filename", width=250)
        self.backups_tree.column("size", width=100)
        self.backups_tree.column("date", width=150)
        self.backups_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        vsb = ttk.Scrollbar(backups_frame, orient="vertical", command=self.backups_tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.backups_tree.configure(yscrollcommand=vsb.set)
        
        # Buttons
        btn_frame = tb.Frame(backups_frame)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        tb.Button(btn_frame, text="Refresh", bootstyle="secondary", command=self.refresh_backups).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Restore Selected", bootstyle="warning", command=self.restore_selected).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Delete Selected", bootstyle="danger-outline", command=self.delete_selected).pack(side="left", padx=5)
        
        # Load backups
        self.refresh_backups()
        
    def save_shop_info(self):
        cfg = config.load_config()
        cfg["shop_info"] = {
            "name": self.shop_name.get(),
            "address": self.shop_address.get(),
            "phone": self.shop_phone.get(),
            "tax_rate": float(self.tax_rate.get() or 0),
            "currency": self.currency.get()
        }
        cfg["theme"] = self.theme.get()
        config.save_config(cfg)
        messagebox.showinfo("Success", "Shop information saved!\nRestart the app to apply theme changes.")
        
    def save_backup_settings(self):
        cfg = config.load_config()
        if "backup" not in cfg:
            cfg["backup"] = {}
        cfg["backup"]["auto_backup_enabled"] = self.auto_backup_enabled.get()
        cfg["backup"]["auto_backup_frequency"] = self.backup_frequency.get()
        config.save_config(cfg)
        messagebox.showinfo("Success", "Backup settings saved!")
        
    def create_backup_now(self):
        result = create_backup()
        if result:
            messagebox.showinfo("Success", f"Backup created:\n{result}")
            self.refresh_backups()
        else:
            messagebox.showerror("Error", "Failed to create backup!")
            
    def refresh_backups(self):
        # Clear tree
        for item in self.backups_tree.get_children():
            self.backups_tree.delete(item)
        
        # Load backups
        backups = list_backups()
        for backup in backups:
            self.backups_tree.insert("", "end", values=(backup[0], f"{backup[1]:.2f}", backup[2]))
            
    def restore_selected(self):
        sel = self.backups_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a backup to restore.")
            return
        
        item = self.backups_tree.item(sel[0])['values']
        filename = item[0]
        
        if messagebox.askyesno("Confirm Restore", 
                               f"Are you sure you want to restore from:\n{filename}\n\n"
                               "This will replace your current database!\n"
                               "A safety backup will be created first."):
            if restore_backup(filename):
                messagebox.showinfo("Success", "Database restored successfully!\nPlease restart the application.")
            else:
                messagebox.showerror("Error", "Failed to restore backup!")
                
    def delete_selected(self):
        sel = self.backups_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a backup to delete.")
            return
        
        item = self.backups_tree.item(sel[0])['values']
        filename = item[0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete backup:\n{filename}?"):
            if delete_backup(filename):
                messagebox.showinfo("Success", "Backup deleted!")
                self.refresh_backups()
            else:
                messagebox.showerror("Error", "Failed to delete backup!")
