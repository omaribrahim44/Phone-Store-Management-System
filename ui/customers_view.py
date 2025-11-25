# ui/customers_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from modules import models

class CustomersFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=30)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)

        # --- Header Section ---
        header = tb.Frame(self.frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        header.columnconfigure(1, weight=1)
        
        # Title with icon
        title_container = tb.Frame(header)
        title_container.grid(row=0, column=0, sticky="w")
        tb.Label(title_container, text="👥", font=("Segoe UI", 36)).pack(side="left", padx=(0, 15))
        tb.Label(title_container, text="Customer Management", font=("Segoe UI", 30, "bold")).pack(side="left")
        
        # Action buttons
        actions = tb.Frame(header)
        actions.grid(row=0, column=1, sticky="e")
        
        tb.Button(actions, text="🔄 Refresh", bootstyle="primary", command=self.load_all, width=12).pack(side="right", padx=5)
        tb.Button(actions, text="📊 Export", bootstyle="info-outline", command=self.export_customers, width=12).pack(side="right", padx=5)

        # --- Filter Section with Visual Tabs ---
        filter_frame = tb.Labelframe(self.frame, text="🔍 Search & Filter", padding=20, bootstyle="primary")
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        filter_frame.columnconfigure(1, weight=1)
        
        # Search box with placeholder
        tb.Label(filter_frame, text="Search:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.phone_entry = tb.Entry(filter_frame, width=30, font=("Segoe UI", 11))
        self.phone_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        self.phone_entry.bind("<Return>", lambda e: self.search())
        
        # Add placeholder
        def add_placeholder(entry, text):
            entry.placeholder = text
            entry.insert(0, text)
            entry.config(foreground='#999999')
            
            def on_focus_in(e):
                if entry.get() == entry.placeholder:
                    entry.delete(0, 'end')
                    entry.config(foreground='#000000')
            
            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, entry.placeholder)
                    entry.config(foreground='#999999')
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        add_placeholder(self.phone_entry, "Search by name or phone...")
        
        # Filter buttons with modern styling
        tb.Button(filter_frame, text="🔍 Search", bootstyle="primary", command=self.search, width=12).grid(row=0, column=2, padx=5)
        tb.Button(filter_frame, text="📋 Show All", bootstyle="secondary", command=self.load_all, width=12).grid(row=0, column=3, padx=5)

        # --- Customer Type Filter Tabs ---
        tabs_frame = tb.Frame(self.frame)
        tabs_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        
        # Filter state
        self.filter_type = tb.StringVar(value="All")
        
        # Create visual tab buttons
        tab_container = tb.Frame(tabs_frame)
        tab_container.pack(side="left")
        
        self.tab_buttons = {}
        tabs = [
            ("All", "📊 All Customers", "info"),
            ("Sales", "🛒 Sales Only", "success"),
            ("Repairs", "🔧 Repairs Only", "primary"),
            ("Both", "🌟 Both", "warning")
        ]
        
        for tab_id, tab_text, tab_style in tabs:
            btn = tb.Button(
                tab_container,
                text=tab_text,
                bootstyle=f"{tab_style}-outline",
                command=lambda t=tab_id: self.filter_by_type(t),
                width=18
            )
            btn.pack(side="left", padx=3)
            self.tab_buttons[tab_id] = (btn, tab_style)
        
        # Statistics label
        self.info_lbl = tb.Label(tabs_frame, text="", font=("Segoe UI", 12, "bold"), bootstyle="info")
        self.info_lbl.pack(side="right", padx=20)

        # --- Customer Table with Enhanced Visualization ---
        table_frame = tb.Labelframe(self.frame, text="📋 Customer List", padding=20, bootstyle="secondary")
        table_frame.grid(row=3, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        cols = ("icon", "id", "name", "phone", "email", "type", "purchases", "repairs", "spent", "last_activity")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)

        # Column configuration with icons
        widths = {
            "icon": 50,
            "id": 60,
            "name": 200,
            "phone": 130,
            "email": 180,
            "type": 120,
            "purchases": 100,
            "repairs": 90,
            "spent": 130,
            "last_activity": 120
        }
        
        labels = {
            "icon": "👤",
            "id": "ID",
            "name": "Customer Name",
            "phone": "Phone",
            "email": "Email",
            "type": "Customer Type",
            "purchases": "Purchases",
            "repairs": "Repairs",
            "spent": "Total Spent",
            "last_activity": "Last Activity"
        }
        
        alignments = {
            "icon": "center",
            "id": "center",
            "name": "w",
            "phone": "center",
            "email": "w",
            "type": "center",
            "purchases": "center",
            "repairs": "center",
            "spent": "e",
            "last_activity": "center"
        }

        for c in cols:
            self.tree.heading(c, text=labels[c], anchor="center")
            self.tree.column(c, width=widths[c], anchor=alignments[c], stretch=False)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=hsb.set)

        # Enhanced tag styles with distinct colors and backgrounds
        self.tree.tag_configure('odd', background='#F8F9FA')
        self.tree.tag_configure('even', background='#FFFFFF')
        
        # Sales customers - Green theme
        self.tree.tag_configure('sales_only', background='#D4EDDA', foreground='#155724')
        self.tree.tag_configure('sales_only_odd', background='#C3E6CB', foreground='#155724')
        
        # Repair customers - Blue theme
        self.tree.tag_configure('repairs_only', background='#D1ECF1', foreground='#004085')
        self.tree.tag_configure('repairs_only_odd', background='#BEE5EB', foreground='#004085')
        
        # Both - Purple theme
        self.tree.tag_configure('both', background='#E2D9F3', foreground='#4A148C')
        self.tree.tag_configure('both_odd', background='#D4C4E8', foreground='#4A148C')

        # Double-click to view details
        self.tree.bind("<Double-1>", self.view_customer_details)

        # Store all customers for filtering
        self.all_customers = []

        # Load all customers initially
        self.load_all()
    
    def filter_by_type(self, customer_type):
        """Filter customers by type and update visual tabs"""
        self.filter_type.set(customer_type)
        
        # Update tab button styles
        for tab_id, (btn, style) in self.tab_buttons.items():
            if tab_id == customer_type:
                btn.configure(bootstyle=style)  # Solid style for active
            else:
                btn.configure(bootstyle=f"{style}-outline")  # Outline for inactive
        
        # Apply filter
        self.display_customers(self.all_customers)

    def load_all(self):
        """Load all customers from the database and display them in the table."""
        try:
            from modules.models import get_all_customers
            self.all_customers = get_all_customers()
            
            # Reset filter to "All"
            self.filter_type.set("All")
            for tab_id, (btn, style) in self.tab_buttons.items():
                if tab_id == "All":
                    btn.configure(bootstyle=style)
                else:
                    btn.configure(bootstyle=f"{style}-outline")
            
            self.display_customers(self.all_customers)
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
            import traceback
            traceback.print_exc()
    
    def display_customers(self, rows):
        """Display customers in the table with filtering and styling"""
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not rows:
            self.info_lbl.configure(text="No customers found", bootstyle="warning")
            return

        # Apply type filter
        filter_type = self.filter_type.get()
        if filter_type != "All":
            rows = [r for r in rows if r[5] == filter_type]

        # Calculate statistics
        total_customers = len(rows)
        sales_only = sum(1 for r in rows if r[5] == 'Sales')
        repairs_only = sum(1 for r in rows if r[5] == 'Repairs')
        both = sum(1 for r in rows if r[5] == 'Both')
        
        self.info_lbl.configure(
            text=f"Total: {total_customers} | 🛒 {sales_only} | 🔧 {repairs_only} | 🌟 {both}",
            bootstyle="info"
        )

        for idx, row in enumerate(rows):
            # row: customer_id, name, phone, email, address, customer_type,
            #      total_purchases, total_repairs, total_spent,
            #      last_purchase_date, last_repair_date, created_date
            
            customer_id = row[0]
            name = row[1]
            phone = row[2] or "N/A"
            email = row[3] or "N/A"
            customer_type = row[5]
            purchases = row[6]
            repairs = row[7]
            spent = f"EGP {row[8]:,.2f}" if row[8] else "EGP 0.00"
            
            # Determine last activity
            last_purchase = row[9]
            last_repair = row[10]
            if last_purchase and last_repair:
                last_activity = max(last_purchase, last_repair)[:10]
            elif last_purchase:
                last_activity = last_purchase[:10]
            elif last_repair:
                last_activity = last_repair[:10]
            else:
                last_activity = "Never"
            
            # Icon based on customer type
            if customer_type == "Sales":
                icon = "🛒"
            elif customer_type == "Repairs":
                icon = "🔧"
            else:  # Both
                icon = "🌟"
            
            # Tags for enhanced styling
            type_key = customer_type.lower().replace(' ', '_')
            if idx % 2 == 0:
                type_tag = f"{type_key}_odd"
            else:
                type_tag = type_key
            
            display_values = (icon, customer_id, name, phone, email, customer_type, purchases, repairs, spent, last_activity)
            self.tree.insert("", "end", values=display_values, tags=(type_tag,))

    def search(self):
        """Search customers by phone number or name (partial match)."""
        query = self.phone_entry.get().strip()
        
        # Check if it's the placeholder
        if query == "Search by name or phone..." or not query:
            self.load_all()
            return

        try:
            # Search in phone or name
            filtered = [c for c in self.all_customers if query.lower() in str(c[2]).lower() or query.lower() in str(c[1]).lower()]

            if not filtered:
                self.info_lbl.configure(text=f"❌ No results for '{query}'", bootstyle="danger")
                # Clear table
                for item in self.tree.get_children():
                    self.tree.delete(item)
                return

            self.display_customers(filtered)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def export_customers(self):
        """Export customer list to CSV"""
        try:
            from tkinter import filedialog
            import csv
            
            rows = [self.tree.item(i)['values'] for i in self.tree.get_children()]
            if not rows:
                messagebox.showwarning("No Data", "No customers to export")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile="customers_export.csv"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write headers
                writer.writerow(["Icon", "ID", "Name", "Phone", "Email", "Type", "Purchases", "Repairs", "Total Spent", "Last Activity"])
                # Write data
                for row in rows:
                    writer.writerow(row)
            
            messagebox.showinfo("Success", f"Exported {len(rows)} customers to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export: {e}")
    
    def view_customer_details(self, event=None):
        """View detailed customer information with enhanced visualization"""
        sel = self.tree.selection()
        if not sel:
            return
        
        values = self.tree.item(sel[0])['values']
        customer_id = values[1]  # ID is now at index 1 (after icon)
        
        try:
            from modules.models import get_customer_details
            customer = get_customer_details(customer_id)
            
            if not customer:
                messagebox.showerror("Error", "Customer not found")
                return
            
            # Verify customer is a tuple/list with expected structure
            if not isinstance(customer, (tuple, list)) or len(customer) < 12:
                messagebox.showerror("Error", f"Invalid customer data structure. Got: {type(customer)}")
                return
            
            # Create detail window with better size
            detail_win = tb.Toplevel(self.frame)
            detail_win.title(f"Customer Details - {customer[1]}")
            detail_win.geometry("700x650")
            detail_win.resizable(True, True)
            detail_win.minsize(650, 600)
            
            # Center window
            detail_win.update_idletasks()
            x = (detail_win.winfo_screenwidth() // 2) - (700 // 2)
            y = (detail_win.winfo_screenheight() // 2) - (650 // 2)
            detail_win.geometry(f"700x650+{x}+{y}")
            
            # Header with customer type indicator
            customer_type = customer[5]
            if customer_type == "Sales":
                header_style = "success"
                icon = "🛒"
            elif customer_type == "Repairs":
                header_style = "primary"
                icon = "🔧"
            else:
                header_style = "warning"
                icon = "🌟"
            
            header = tb.Frame(detail_win, bootstyle=header_style, padding=20)
            header.pack(fill="x")
            
            tb.Label(
                header,
                text=f"{icon} {customer[1]}",
                font=("Segoe UI", 20, "bold"),
                bootstyle=f"{header_style}-inverse"
            ).pack(anchor="w")
            
            tb.Label(
                header,
                text=f"Customer Type: {customer_type}",
                font=("Segoe UI", 12),
                bootstyle=f"{header_style}-inverse"
            ).pack(anchor="w", pady=(5, 0))
            
            # Main content
            content = tb.Frame(detail_win, padding=25)
            content.pack(fill="both", expand=True)
            
            # Contact Information
            contact_frame = tb.Labelframe(content, text="📞 Contact Information", padding=20, bootstyle="info")
            contact_frame.pack(fill="x", pady=(0, 15))
            contact_frame.columnconfigure(1, weight=1)
            
            contact_details = [
                ("Phone:", customer[2] or "N/A"),
                ("Email:", customer[3] or "N/A"),
                ("Address:", customer[4] or "N/A"),
            ]
            
            for idx, (label, value) in enumerate(contact_details):
                tb.Label(contact_frame, text=label, font=("Segoe UI", 12, "bold")).grid(row=idx, column=0, sticky="w", pady=8, padx=(0, 20))
                tb.Label(contact_frame, text=str(value), font=("Segoe UI", 12)).grid(row=idx, column=1, sticky="w", pady=8)
            
            # Statistics
            stats_frame = tb.Labelframe(content, text="📊 Customer Statistics", padding=15, bootstyle="secondary")
            stats_frame.pack(fill="x", pady=(0, 15))
            
            # Create stat cards
            stats_container = tb.Frame(stats_frame)
            stats_container.pack(fill="x")
            stats_container.columnconfigure(0, weight=1)
            stats_container.columnconfigure(1, weight=1)
            stats_container.columnconfigure(2, weight=1)
            
            # Purchases card
            purchase_card = tb.Frame(stats_container, bootstyle="success", padding=20)
            purchase_card.grid(row=0, column=0, sticky="ew", padx=8, pady=5)
            tb.Label(purchase_card, text="🛒 Purchases", font=("Segoe UI", 11, "bold"), bootstyle="success-inverse").pack(pady=(0, 8))
            tb.Label(purchase_card, text=str(customer[9] or 0), font=("Segoe UI", 28, "bold"), bootstyle="success-inverse").pack()
            
            # Repairs card
            repair_card = tb.Frame(stats_container, bootstyle="primary", padding=20)
            repair_card.grid(row=0, column=1, sticky="ew", padx=8, pady=5)
            tb.Label(repair_card, text="🔧 Repairs", font=("Segoe UI", 11, "bold"), bootstyle="primary-inverse").pack(pady=(0, 8))
            tb.Label(repair_card, text=str(customer[10] or 0), font=("Segoe UI", 28, "bold"), bootstyle="primary-inverse").pack()
            
            # Total spent card
            spent_card = tb.Frame(stats_container, bootstyle="info", padding=20)
            spent_card.grid(row=0, column=2, sticky="ew", padx=8, pady=5)
            tb.Label(spent_card, text="💰 Total Spent", font=("Segoe UI", 11, "bold"), bootstyle="info-inverse").pack(pady=(0, 8))
            # Convert to float safely
            try:
                spent_amount = float(customer[11]) if customer[11] else 0.0
                spent_text = f"EGP {spent_amount:,.0f}"
            except (ValueError, TypeError):
                spent_text = "EGP 0"
            tb.Label(spent_card, text=spent_text, font=("Segoe UI", 24, "bold"), bootstyle="info-inverse").pack()
            
            # Activity Information
            activity_frame = tb.Labelframe(content, text="📅 Activity History", padding=20, bootstyle="secondary")
            activity_frame.pack(fill="x", pady=(0, 15))
            activity_frame.columnconfigure(1, weight=1)
            
            activity_details = [
                ("Last Purchase:", customer[7][:10] if customer[7] and len(customer) > 7 else "Never"),
                ("Last Repair:", customer[8][:10] if customer[8] and len(customer) > 8 else "Never"),
                ("Customer Since:", customer[6][:10] if customer[6] and len(customer) > 6 else "N/A"),
            ]
            
            for idx, (label, value) in enumerate(activity_details):
                tb.Label(activity_frame, text=label, font=("Segoe UI", 12, "bold")).grid(row=idx, column=0, sticky="w", pady=8, padx=(0, 20))
                tb.Label(activity_frame, text=str(value), font=("Segoe UI", 12)).grid(row=idx, column=1, sticky="w", pady=8)
            
            # Close button
            tb.Button(detail_win, text="✖ Close", bootstyle="secondary", command=detail_win.destroy, width=15).pack(pady=15)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load customer details: {e}")
            import traceback
            traceback.print_exc()
