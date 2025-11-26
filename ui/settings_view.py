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
        # Create scrollable frame for shop info
        shop_container = tb.Frame(self.notebook)
        self.notebook.add(shop_container, text="Shop Information")
        
        # Create canvas and scrollbar
        canvas = tb.Canvas(shop_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(shop_container, orient="vertical", command=canvas.yview)
        shop_frame = tb.Frame(canvas, padding=15)
        
        shop_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=shop_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        cfg = config.load_config()
        shop_info = cfg.get("shop_info", config.DEFAULT_SHOP_INFO)
        
        shop_frame.columnconfigure(1, weight=1)
        row = 0
        
        # === BASIC INFORMATION SECTION ===
        tb.Label(shop_frame, text="BASIC INFORMATION", font=("Segoe UI", 12, "bold"), bootstyle="primary").grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1
        
        # Shop Name
        tb.Label(shop_frame, text="Shop Name:*", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.shop_name = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.shop_name.insert(0, shop_info.get("name", ""))
        self.shop_name.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Tagline
        tb.Label(shop_frame, text="Tagline/Slogan:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.shop_tagline = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.shop_tagline.insert(0, shop_info.get("tagline", ""))
        self.shop_tagline.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Address
        tb.Label(shop_frame, text="Address:*", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.shop_address = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.shop_address.insert(0, shop_info.get("address", ""))
        self.shop_address.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # === CONTACT INFORMATION SECTION ===
        ttk.Separator(shop_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        tb.Label(shop_frame, text="CONTACT INFORMATION", font=("Segoe UI", 12, "bold"), bootstyle="info").grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1
        
        # Phone
        tb.Label(shop_frame, text="Phone:*", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.shop_phone = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.shop_phone.insert(0, shop_info.get("phone", ""))
        self.shop_phone.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Email
        tb.Label(shop_frame, text="Email:*", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.shop_email = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.shop_email.insert(0, shop_info.get("email", ""))
        self.shop_email.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Website
        tb.Label(shop_frame, text="Website:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.shop_website = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.shop_website.insert(0, shop_info.get("website", ""))
        self.shop_website.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Business Hours
        tb.Label(shop_frame, text="Business Hours:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.business_hours = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.business_hours.insert(0, shop_info.get("business_hours", ""))
        self.business_hours.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # === LEGAL INFORMATION SECTION ===
        ttk.Separator(shop_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        tb.Label(shop_frame, text="LEGAL & TAX INFORMATION", font=("Segoe UI", 12, "bold"), bootstyle="warning").grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1
        
        # Tax ID
        tb.Label(shop_frame, text="Tax ID/VAT Number:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.tax_id = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.tax_id.insert(0, shop_info.get("tax_id", ""))
        self.tax_id.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Commercial Register
        tb.Label(shop_frame, text="Commercial Register:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.commercial_register = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.commercial_register.insert(0, shop_info.get("commercial_register", ""))
        self.commercial_register.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Tax Rate
        tb.Label(shop_frame, text="Tax Rate (%):*", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.tax_rate = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.tax_rate.insert(0, shop_info.get("tax_rate", "0"))
        self.tax_rate.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Currency
        tb.Label(shop_frame, text="Currency:*", font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.currency = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.currency.insert(0, shop_info.get("currency", "EGP"))
        self.currency.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # === POLICIES SECTION ===
        ttk.Separator(shop_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        tb.Label(shop_frame, text="POLICIES & WARRANTY", font=("Segoe UI", 12, "bold"), bootstyle="danger").grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1
        
        # Return Policy Days
        tb.Label(shop_frame, text="Return Policy (Days):", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.return_policy_days = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.return_policy_days.insert(0, shop_info.get("return_policy_days", "7"))
        self.return_policy_days.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Warranty Info
        tb.Label(shop_frame, text="Warranty Information:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="nw", pady=5, padx=5)
        self.warranty_info = tb.Text(shop_frame, width=50, height=3, font=("Segoe UI", 9))
        self.warranty_info.insert("1.0", shop_info.get("warranty_info", ""))
        self.warranty_info.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # === SOCIAL MEDIA SECTION ===
        ttk.Separator(shop_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        tb.Label(shop_frame, text="SOCIAL MEDIA", font=("Segoe UI", 12, "bold"), bootstyle="success").grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1
        
        # Facebook
        tb.Label(shop_frame, text="Facebook:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.social_facebook = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.social_facebook.insert(0, shop_info.get("social_facebook", ""))
        self.social_facebook.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Instagram
        tb.Label(shop_frame, text="Instagram:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.social_instagram = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.social_instagram.insert(0, shop_info.get("social_instagram", ""))
        self.social_instagram.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Twitter
        tb.Label(shop_frame, text="Twitter/X:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.social_twitter = tb.Entry(shop_frame, width=50, font=("Segoe UI", 10))
        self.social_twitter.insert(0, shop_info.get("social_twitter", ""))
        self.social_twitter.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # === APPEARANCE SECTION ===
        ttk.Separator(shop_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        tb.Label(shop_frame, text="APPEARANCE", font=("Segoe UI", 12, "bold"), bootstyle="secondary").grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 10))
        row += 1
        
        # Theme
        tb.Label(shop_frame, text="Theme:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        self.theme = tb.Combobox(shop_frame, values=["flatly", "darkly", "cosmo", "journal", "litera", "lumen", "minty", "pulse", "sandstone", "united", "yeti"], state="readonly", width=48, font=("Segoe UI", 10))
        self.theme.set(cfg.get("theme", "flatly"))
        self.theme.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        row += 1
        
        # Logo Path
        tb.Label(shop_frame, text="Logo Path:", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", pady=5, padx=5)
        logo_frame = tb.Frame(shop_frame)
        logo_frame.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.logo_path = tb.Entry(logo_frame, width=40, font=("Segoe UI", 10))
        self.logo_path.insert(0, shop_info.get("logo_path", ""))
        self.logo_path.pack(side="left", fill="x", expand=True)
        tb.Button(logo_frame, text="Browse", bootstyle="secondary-outline", command=self.browse_logo).pack(side="left", padx=(5, 0))
        row += 1
        
        # === SAVE BUTTON ===
        ttk.Separator(shop_frame, orient="horizontal").grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        button_frame = tb.Frame(shop_frame)
        button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        
        tb.Label(button_frame, text="* Required fields", font=("Segoe UI", 9, "italic"), foreground="#6c757d").pack(side="left")
        tb.Button(button_frame, text="💾 Save Shop Information", bootstyle="success", command=self.save_shop_info, padding=10).pack(side="right", padx=5)
        tb.Button(button_frame, text="🔄 Reset to Defaults", bootstyle="warning-outline", command=self.reset_to_defaults).pack(side="right")
        
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
        
        # Configure headers and columns with center alignment
        self.backups_tree.heading("filename", text="Filename", anchor="center")
        self.backups_tree.heading("size", text="Size (MB)", anchor="center")
        self.backups_tree.heading("date", text="Date", anchor="center")
        
        self.backups_tree.column("filename", width=250, anchor="center")
        self.backups_tree.column("size", width=100, anchor="center")
        self.backups_tree.column("date", width=150, anchor="center")
        
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
        
    def browse_logo(self):
        """Browse for logo file"""
        filename = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.logo_path.delete(0, "end")
            self.logo_path.insert(0, filename)
    
    def reset_to_defaults(self):
        """Reset all fields to default values"""
        if messagebox.askyesno("Reset to Defaults", "Are you sure you want to reset all shop information to default values?"):
            defaults = config.DEFAULT_SHOP_INFO
            self.shop_name.delete(0, "end")
            self.shop_name.insert(0, defaults.get("name", ""))
            self.shop_tagline.delete(0, "end")
            self.shop_tagline.insert(0, defaults.get("tagline", ""))
            self.shop_address.delete(0, "end")
            self.shop_address.insert(0, defaults.get("address", ""))
            self.shop_phone.delete(0, "end")
            self.shop_phone.insert(0, defaults.get("phone", ""))
            self.shop_email.delete(0, "end")
            self.shop_email.insert(0, defaults.get("email", ""))
            self.shop_website.delete(0, "end")
            self.shop_website.insert(0, defaults.get("website", ""))
            self.business_hours.delete(0, "end")
            self.business_hours.insert(0, defaults.get("business_hours", ""))
            self.tax_id.delete(0, "end")
            self.tax_id.insert(0, defaults.get("tax_id", ""))
            self.commercial_register.delete(0, "end")
            self.commercial_register.insert(0, defaults.get("commercial_register", ""))
            self.tax_rate.delete(0, "end")
            self.tax_rate.insert(0, defaults.get("tax_rate", "0"))
            self.currency.delete(0, "end")
            self.currency.insert(0, defaults.get("currency", "EGP"))
            self.return_policy_days.delete(0, "end")
            self.return_policy_days.insert(0, defaults.get("return_policy_days", "7"))
            self.warranty_info.delete("1.0", "end")
            self.warranty_info.insert("1.0", defaults.get("warranty_info", ""))
            self.social_facebook.delete(0, "end")
            self.social_facebook.insert(0, defaults.get("social_facebook", ""))
            self.social_instagram.delete(0, "end")
            self.social_instagram.insert(0, defaults.get("social_instagram", ""))
            self.social_twitter.delete(0, "end")
            self.social_twitter.insert(0, defaults.get("social_twitter", ""))
            self.logo_path.delete(0, "end")
            self.logo_path.insert(0, defaults.get("logo_path", ""))
    
    def save_shop_info(self):
        # Validate required fields
        if not self.shop_name.get().strip():
            messagebox.showwarning("Validation Error", "Shop Name is required!")
            return
        if not self.shop_address.get().strip():
            messagebox.showwarning("Validation Error", "Address is required!")
            return
        if not self.shop_phone.get().strip():
            messagebox.showwarning("Validation Error", "Phone is required!")
            return
        if not self.shop_email.get().strip():
            messagebox.showwarning("Validation Error", "Email is required!")
            return
        
        # Validate tax rate
        try:
            tax_rate = float(self.tax_rate.get() or 0)
            if tax_rate < 0 or tax_rate > 100:
                messagebox.showwarning("Validation Error", "Tax rate must be between 0 and 100!")
                return
        except ValueError:
            messagebox.showwarning("Validation Error", "Tax rate must be a valid number!")
            return
        
        # Validate return policy days
        try:
            return_days = int(self.return_policy_days.get() or 7)
            if return_days < 0:
                messagebox.showwarning("Validation Error", "Return policy days must be a positive number!")
                return
        except ValueError:
            messagebox.showwarning("Validation Error", "Return policy days must be a valid number!")
            return
        
        cfg = config.load_config()
        cfg["shop_info"] = {
            "name": self.shop_name.get().strip(),
            "tagline": self.shop_tagline.get().strip(),
            "address": self.shop_address.get().strip(),
            "phone": self.shop_phone.get().strip(),
            "email": self.shop_email.get().strip(),
            "website": self.shop_website.get().strip(),
            "business_hours": self.business_hours.get().strip(),
            "tax_id": self.tax_id.get().strip(),
            "commercial_register": self.commercial_register.get().strip(),
            "tax_rate": tax_rate,
            "currency": self.currency.get().strip() or "EGP",
            "return_policy_days": return_days,
            "warranty_info": self.warranty_info.get("1.0", "end").strip(),
            "social_facebook": self.social_facebook.get().strip(),
            "social_instagram": self.social_instagram.get().strip(),
            "social_twitter": self.social_twitter.get().strip(),
            "logo_path": self.logo_path.get().strip(),
        }
        cfg["theme"] = self.theme.get()
        
        if config.save_config(cfg):
            messagebox.showinfo("Success", "✅ Shop information saved successfully!\n\n"
                                          "All receipts and reports will now use the updated information.\n\n"
                                          "Note: Restart the app to apply theme changes.")
        else:
            messagebox.showerror("Error", "Failed to save shop information!")
        
    def save_backup_settings(self):
        cfg = config.load_config()
        if "backup" not in cfg:
            cfg["backup"] = {}
        cfg["backup"]["auto_backup_enabled"] = self.auto_backup_enabled.get()
        cfg["backup"]["auto_backup_frequency"] = self.backup_frequency.get()
        config.save_config(cfg)
        messagebox.showinfo("Success", "Backup settings saved!")
    
    def update_last_backup_display(self):
        """Update the last backup date display"""
        try:
            cfg = config.load_config()
            backup_cfg = cfg.get("backup", {})
            last_backup = backup_cfg.get("last_backup_date", "Never")
            if last_backup and last_backup != "Never":
                last_backup = last_backup[:19]  # Truncate to readable format
            # Find and update the label (this is a simple approach)
            # In production, you'd store a reference to the label
        except:
            pass
        
    def create_backup_now(self):
        try:
            result = create_backup()
            if result:
                messagebox.showinfo("Success", f"Backup created successfully!\n{result}")
                self.refresh_backups()
                # Update last backup display
                self.update_last_backup_display()
            else:
                messagebox.showerror("Error", "Failed to create backup!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup:\n{str(e)}")
            
    def refresh_backups(self):
        # Clear tree
        for item in self.backups_tree.get_children():
            self.backups_tree.delete(item)
        
        # Load backups
        try:
            backups = list_backups()
            for idx, backup in enumerate(backups):
                # Add alternating row colors
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.backups_tree.insert("", "end", values=(backup[0], f"{backup[1]:.2f}", backup[2]), tags=(tag,))
            
            # Configure row colors
            self.backups_tree.tag_configure("evenrow", background="#FFFFFF")
            self.backups_tree.tag_configure("oddrow", background="#F8F9FA")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load backups:\n{str(e)}")
            
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
            try:
                if restore_backup(filename):
                    messagebox.showinfo("Success", "Database restored successfully!\nPlease restart the application.")
                    self.refresh_backups()
                else:
                    messagebox.showerror("Error", "Failed to restore backup!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore backup:\n{str(e)}")
                
    def delete_selected(self):
        sel = self.backups_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a backup to delete.")
            return
        
        item = self.backups_tree.item(sel[0])['values']
        filename = item[0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete backup:\n{filename}?"):
            try:
                if delete_backup(filename):
                    messagebox.showinfo("Success", "Backup deleted successfully!")
                    self.refresh_backups()
                else:
                    messagebox.showerror("Error", "Failed to delete backup!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete backup:\n{str(e)}")
