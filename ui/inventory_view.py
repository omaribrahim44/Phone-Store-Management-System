# ui/inventory_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, filedialog
from controllers.inventory_controller import InventoryController
import csv

class InventoryFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=30)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
        
        # --- Header Section ---
        header_frame = tb.Frame(self.frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        header_frame.columnconfigure(1, weight=1)
        
        # Title with icon
        title_container = tb.Frame(header_frame)
        title_container.grid(row=0, column=0, sticky="w")
        tb.Label(title_container, text="📦", font=("Segoe UI", 36)).pack(side="left", padx=(0, 15))
        tb.Label(title_container, text="Inventory Management", font=("Segoe UI", 30, "bold")).pack(side="left")
        
        # Action buttons on the right
        actions = tb.Frame(header_frame)
        actions.grid(row=0, column=2, sticky="e")
        
        tb.Button(
            actions, 
            text="➕ Add Item", 
            bootstyle="success", 
            command=self.add_item_dialog,
            width=14
        ).pack(side="right", padx=5)
        
        tb.Button(
            actions, 
            text="🗑️ Delete", 
            bootstyle="danger", 
            command=self.delete_selected_item,
            width=12
        ).pack(side="right", padx=5)
        
        tb.Button(
            actions, 
            text="🔄 Refresh", 
            bootstyle="primary", 
            command=self.refresh,
            width=12
        ).pack(side="right", padx=5)
        
        tb.Button(
            actions, 
            text="📤 Export", 
            bootstyle="info-outline", 
            command=self.export_csv,
            width=12
        ).pack(side="right", padx=5)
        
        # --- Search & Filter Bar ---
        filter_frame = tb.Labelframe(self.frame, text="🔍 Search & Filter", padding=20, bootstyle="primary")
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        filter_frame.columnconfigure(1, weight=1)
        
        # Search box with placeholder
        tb.Label(filter_frame, text="Search:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.search_var = tb.StringVar()
        self.search_var.trace("w", self.filter_items)
        search_entry = tb.Entry(filter_frame, textvariable=self.search_var, font=("Segoe UI", 11))
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        
        # Add placeholder functionality
        def add_placeholder(entry, placeholder_text):
            entry.placeholder = placeholder_text
            entry.placeholder_color = '#999999'
            entry.default_color = entry.cget('foreground')
            
            def on_focus_in(event):
                if entry.get() == entry.placeholder:
                    entry.delete(0, 'end')
                    entry.config(foreground=entry.default_color)
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, entry.placeholder)
                    entry.config(foreground=entry.placeholder_color)
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
            
            # Set initial placeholder
            entry.insert(0, entry.placeholder)
            entry.config(foreground=entry.placeholder_color)
        
        add_placeholder(search_entry, "Search by SKU, name, category...")
        
        # Low stock filter
        self.low_stock_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            filter_frame, 
            text="⚠️ Low Stock Only (< 5)", 
            variable=self.low_stock_var, 
            bootstyle="warning-round-toggle",
            command=self.filter_items
        ).grid(row=0, column=2, sticky="w", padx=10)
        
        # Item count label
        self.count_label = tb.Label(filter_frame, text="Items: 0", font=("Segoe UI", 11, "bold"), bootstyle="info")
        self.count_label.grid(row=0, column=3, sticky="e", padx=(20, 0))

        # --- Inventory Table ---
        table_frame = tb.Labelframe(self.frame, text="📋 Inventory Items", padding=20, bootstyle="secondary")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview with enhanced styling
        cols = ("id", "sku", "name", "category", "qty", "buy", "sell", "value")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
        
        # Configure tree style with larger, clearer fonts
        style = ttk.Style()
        style.configure("Treeview", 
                       font=("Segoe UI", 11),  # Increased from 10
                       rowheight=32,  # Increased from 28
                       background="#FFFFFF",
                       fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading",
                       font=("Segoe UI", 12, "bold"),  # Increased from 11
                       padding=10,  # Increased from 8
                       background="#E8E8E8")
        style.map("Treeview", background=[("selected", "#0078D7")])
        
        # Column headers with better labels
        headers = {
            "id": "ID",
            "sku": "SKU",
            "name": "Item Name",
            "category": "Category",
            "qty": "Stock",
            "buy": "Buy Price ",
            "sell": "Sell Price ",
            "value": "Total Value "
        }
        
        # Column widths - proportional to fill full width
        widths = {
            "id": 70,
            "sku": 150,
            "name": 350,
            "category": 160,
            "qty": 100,
            "buy": 160,
            "sell": 160,
            "value": 180
        }
        
        # Column alignments
        alignments = {
            "id": "center",
            "sku": "w",
            "name": "w",
            "category": "center",
            "qty": "center",
            "buy": "e",
            "sell": "e",
            "value": "e"
        }
        
        # Configure columns with matching header and data alignment
        for c in cols:
            # Headers and data use the SAME alignment for proper column alignment
            self.tree.heading(c, text=headers[c], anchor=alignments[c])
            # Data uses specific alignment based on content type
            # Allow stretching for better full-width coverage
            stretch_col = True if c in ["name", "category"] else False
            self.tree.column(c, width=widths[c], anchor=alignments[c], minwidth=50, stretch=stretch_col)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Alternating row colors and low stock highlighting
        self.tree.tag_configure('odd', background='#F8F9FA')
        self.tree.tag_configure('even', background='#FFFFFF')
        self.tree.tag_configure('low_stock', background='#FFF3CD', foreground='#856404')
        self.tree.tag_configure('out_of_stock', background='#F8D7DA', foreground='#721C24')
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Total Value Summary
        summary_frame = tb.Frame(table_frame, padding=15)
        summary_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        summary_frame.columnconfigure(0, weight=1)
        
        # Total value label
        self.total_value_label = tb.Label(
            summary_frame,
            text="Total Inventory Value:  0.00",
            font=("Segoe UI", 14, "bold"),
            bootstyle="success"
        )
        self.total_value_label.pack(side="right", padx=20)

        self.all_items = []
        self.refresh()

    def refresh(self):
        try:
            self.all_items = InventoryController.get_all_items()
            self.filter_items()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load inventory: {e}")

    def filter_items(self, *args):
        # Get search query, handling placeholder
        query = self.search_var.get().lower()
        # Skip filtering if it's the placeholder text
        if query == "search by sku, name, category...":
            query = ""
        low_stock = self.low_stock_var.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        displayed_count = 0
        total_inventory_value = 0.0
        
        for idx, row in enumerate(self.all_items):
            # row: id, sku, name, category, qty, buy, sell
            # Filter by text
            if query:
                combined = " ".join([str(x) for x in row]).lower()
                if query not in combined:
                    continue
            
            # Get quantity for filtering and styling
            try:
                qty = int(row[4])  # qty is at index 4
            except:
                qty = 0
            
            # Filter by low stock (< 5)
            if low_stock and qty >= 5:
                continue
            
            # Calculate total value (qty * buy price)
            try:
                buy_price = float(row[5])  # buy price at index 5
                total_value = qty * buy_price
                total_inventory_value += total_value
            except:
                total_value = 0.0
            
            # Add total value to row
            display_row = list(row) + [f"EGP {total_value:,.2f}"]
            
            # Determine row styling
            tags = []
            if qty == 0:
                tags.append('out_of_stock')
            elif qty < 5:
                tags.append('low_stock')
            else:
                tags.append('odd' if displayed_count % 2 == 0 else 'even')
            
            self.tree.insert("", "end", values=display_row, tags=tuple(tags))
            displayed_count += 1
        
        # Update count label
        self.count_label.configure(text=f"Items: {displayed_count} / {len(self.all_items)}")
        
        # Update total value label
        self.total_value_label.configure(text=f"Total Inventory Value: EGP {total_inventory_value:,.2f}")

    def add_item_dialog(self):
        """Professional add item dialog with validation and better UX"""
        win = tb.Toplevel(self.frame)
        win.title("Add New Inventory Item")
        win.geometry("620x650")
        win.resizable(True, True)
        win.minsize(600, 600)
        
        # Center the window
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (620 // 2)
        y = (win.winfo_screenheight() // 2) - (650 // 2)
        win.geometry(f"620x650+{x}+{y}")
        
        # Header
        header = tb.Frame(win, bootstyle="primary", padding=20)
        header.pack(fill="x")
        tb.Label(
            header, 
            text="➕ Add New Item", 
            font=("Segoe UI", 20, "bold"),
            bootstyle="primary-inverse"
        ).pack(anchor="w")
        tb.Label(
            header, 
            text="Fill in the details below to add a new item to inventory",
            font=("Segoe UI", 10),
            bootstyle="primary-inverse"
        ).pack(anchor="w", pady=(5, 0))
        
        # Scrollable form container
        canvas_frame = tb.Frame(win)
        canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        canvas = tb.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        form_container = tb.Frame(canvas, padding=20)
        
        form_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=form_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form fields with better styling
        def create_field(parent, label_text, is_required=False, field_type="entry", options=None):
            field_frame = tb.Frame(parent)
            field_frame.pack(fill="x", pady=(0, 18))
            
            # Label with required indicator
            label_container = tb.Frame(field_frame)
            label_container.pack(fill="x", pady=(0, 6))
            
            label = tb.Label(
                label_container, 
                text=label_text, 
                font=("Segoe UI", 11, "bold")
            )
            label.pack(side="left")
            
            if is_required:
                tb.Label(
                    label_container, 
                    text="*", 
                    font=("Segoe UI", 11, "bold"),
                    bootstyle="danger"
                ).pack(side="left", padx=(3, 0))
            
            # Input field
            if field_type == "entry":
                widget = tb.Entry(field_frame, font=("Segoe UI", 11))
                widget.pack(fill="x")
            elif field_type == "combobox":
                widget = tb.Combobox(
                    field_frame, 
                    values=options, 
                    state="readonly",
                    font=("Segoe UI", 11)
                )
                widget.pack(fill="x")
                if options:
                    widget.set(options[0])
            elif field_type == "text":
                widget = tb.Text(field_frame, height=3, font=("Segoe UI", 11))
                widget.pack(fill="x")
            
            return widget
        
        # Placeholder helper function
        def add_placeholder(entry, placeholder_text):
            """Add modern placeholder to entry widget"""
            entry.placeholder = placeholder_text
            entry.placeholder_color = '#999999'
            entry.default_color = '#000000'
            entry.has_placeholder = True
            
            def on_focus_in(event):
                if entry.has_placeholder and entry.get() == entry.placeholder:
                    entry.delete(0, 'end')
                    entry.config(foreground=entry.default_color)
                    entry.has_placeholder = False
            
            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, entry.placeholder)
                    entry.config(foreground=entry.placeholder_color)
                    entry.has_placeholder = True
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
            
            # Set initial placeholder
            entry.insert(0, entry.placeholder)
            entry.config(foreground=entry.placeholder_color)
        
        # Form fields with placeholders
        e_sku = create_field(form_container, "SKU (Stock Keeping Unit)", is_required=True)
        add_placeholder(e_sku, "e.g., IP14-BLK-128")
        
        e_name = create_field(form_container, "Item Name", is_required=True)
        add_placeholder(e_name, "e.g., iPhone 14 Pro Max")
        
        # Category with better options
        categories = [
            "Mobile Phones",
            "Phone Cases & Covers", 
            "Chargers & Cables",
            "AirPods & Earphones",
            "Screen Protectors",
            "Phone Accessories",
            "Repair Parts",
            "Other"
        ]
        e_category = create_field(form_container, "Category", is_required=True, field_type="combobox", options=categories)
        
        # Quantity and prices in a grid
        grid_frame = tb.Frame(form_container)
        grid_frame.pack(fill="x", pady=(0, 18))
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)
        
        # Quantity
        qty_frame = tb.Frame(grid_frame)
        qty_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tb.Label(qty_frame, text="Quantity *", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        e_qty = tb.Entry(qty_frame, font=("Segoe UI", 11))
        e_qty.pack(fill="x")
        add_placeholder(e_qty, "0")
        
        # Buy Price
        buy_frame = tb.Frame(grid_frame)
        buy_frame.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        tb.Label(buy_frame, text="Buy Price (EGP) *", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        e_buy = tb.Entry(buy_frame, font=("Segoe UI", 11))
        e_buy.pack(fill="x")
        add_placeholder(e_buy, "0.00")
        
        # Sell Price
        sell_frame = tb.Frame(grid_frame)
        sell_frame.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        tb.Label(sell_frame, text="Sell Price (EGP) *", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        e_sell = tb.Entry(sell_frame, font=("Segoe UI", 11))
        e_sell.pack(fill="x")
        add_placeholder(e_sell, "0.00")
        
        # Profit margin indicator
        margin_label = tb.Label(form_container, text="", font=("Segoe UI", 10, "italic"))
        margin_label.pack(anchor="w", pady=(0, 18))
        
        def update_margin(*args):
            try:
                # Get values, handling placeholders
                buy_str = e_buy.get().strip()
                sell_str = e_sell.get().strip()
                
                # Skip if placeholder is showing
                if (hasattr(e_buy, 'has_placeholder') and e_buy.has_placeholder) or \
                   (hasattr(e_sell, 'has_placeholder') and e_sell.has_placeholder):
                    margin_label.configure(text="")
                    return
                
                buy = float(buy_str) if buy_str else 0.0
                sell = float(sell_str) if sell_str else 0.0
                
                if buy > 0:
                    margin = ((sell - buy) / buy) * 100
                    profit = sell - buy
                    margin_label.configure(
                        text=f"💰 Profit: EGP {profit:.2f} | Margin: {margin:.1f}%",
                        bootstyle="success" if profit > 0 else "danger"
                    )
                else:
                    margin_label.configure(text="")
            except:
                margin_label.configure(text="")
        
        e_buy.bind("<KeyRelease>", update_margin)
        e_sell.bind("<KeyRelease>", update_margin)
        
        # Description
        e_desc = create_field(form_container, "Description (Optional)", field_type="text")
        
        # Validation message
        validation_label = tb.Label(form_container, text="", font=("Segoe UI", 10))
        validation_label.pack(pady=(10, 0))
        
        # Buttons
        button_frame = tb.Frame(win, padding=20)
        button_frame.pack(fill="x", side="bottom")
        
        def validate_and_save():
            # Clear previous validation message
            validation_label.configure(text="")
            
            # Get values (handle placeholders)
            sku = e_sku.get().strip() if not (hasattr(e_sku, 'has_placeholder') and e_sku.has_placeholder) else ""
            name = e_name.get().strip() if not (hasattr(e_name, 'has_placeholder') and e_name.has_placeholder) else ""
            category = e_category.get()
            desc = e_desc.get("1.0", "end").strip()
            
            # Validate required fields
            if not sku:
                validation_label.configure(text="❌ SKU is required", bootstyle="danger")
                e_sku.focus()
                return
            
            if not name:
                validation_label.configure(text="❌ Item name is required", bootstyle="danger")
                e_name.focus()
                return
            
            # Validate numbers (handle placeholders)
            try:
                qty_str = e_qty.get().strip()
                if hasattr(e_qty, 'has_placeholder') and e_qty.has_placeholder:
                    qty_str = "0"
                qty = int(qty_str)
                if qty < 0:
                    raise ValueError("Quantity cannot be negative")
            except ValueError as e:
                validation_label.configure(text=f"❌ Invalid quantity: {e}", bootstyle="danger")
                e_qty.focus()
                return
            
            try:
                buy_str = e_buy.get().strip()
                if hasattr(e_buy, 'has_placeholder') and e_buy.has_placeholder:
                    buy_str = "0.00"
                buy = float(buy_str)
                if buy < 0:
                    raise ValueError("Buy price cannot be negative")
            except ValueError as e:
                validation_label.configure(text=f"❌ Invalid buy price: {e}", bootstyle="danger")
                e_buy.focus()
                return
            
            try:
                sell_str = e_sell.get().strip()
                if hasattr(e_sell, 'has_placeholder') and e_sell.has_placeholder:
                    sell_str = "0.00"
                sell = float(sell_str)
                if sell < 0:
                    raise ValueError("Sell price cannot be negative")
            except ValueError as e:
                validation_label.configure(text=f"❌ Invalid sell price: {e}", bootstyle="danger")
                e_sell.focus()
                return
            
            # Warn if sell price is lower than buy price
            if sell < buy:
                response = messagebox.askyesno(
                    "Price Warning",
                    f"Sell price (EGP {sell:.2f}) is lower than buy price (EGP {buy:.2f}).\n\n"
                    "This will result in a loss. Do you want to continue?"
                )
                if not response:
                    return
            
            # Save item
            if InventoryController.add_item(sku, name, qty, buy, sell, category, desc):
                messagebox.showinfo("✓ Success", f"Item '{name}' has been added to inventory!")
                win.destroy()
                self.refresh()
            else:
                validation_label.configure(
                    text="❌ Could not add item. SKU might already exist.",
                    bootstyle="danger"
                )
        
        def cancel():
            win.destroy()
        
        tb.Button(
            button_frame, 
            text="💾 Save Item", 
            bootstyle="success",
            command=validate_and_save,
            width=20
        ).pack(side="right", padx=5)
        
        tb.Button(
            button_frame, 
            text="✖ Cancel", 
            bootstyle="secondary",
            command=cancel,
            width=15
        ).pack(side="right", padx=5)
        
        # Focus on first field
        e_sku.focus()

    def delete_selected_item(self):
        """Delete the selected inventory item with confirmation"""
        # Get selected item
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to delete")
            return
        
        # Get item details
        item_values = self.tree.item(selection[0])['values']
        item_id = item_values[0]
        sku = item_values[1]
        name = item_values[2]
        qty = item_values[4]
        
        # Confirmation dialog with details
        confirm = messagebox.askyesno(
            "⚠️ Confirm Deletion",
            f"Are you sure you want to delete this item?\n\n"
            f"ID: {item_id}\n"
            f"SKU: {sku}\n"
            f"Name: {name}\n"
            f"Current Stock: {qty}\n\n"
            f"⚠️ This action cannot be undone!",
            icon='warning'
        )
        
        if not confirm:
            return
        
        # Delete the item
        try:
            if InventoryController.delete_item(item_id, name, sku):
                messagebox.showinfo("✓ Success", f"Item '{name}' has been deleted from inventory")
                self.refresh()
            else:
                messagebox.showerror("Error", "Could not delete item. Check logs for details.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {e}")
    
    def export_csv(self):
        rows = [self.tree.item(i)['values'] for i in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("No data", "No rows to export.")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], initialfile="inventory_export.csv")
        if not fn:
            return
        with open(fn, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.tree["columns"])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo("Exported", f"Exported {len(rows)} rows to {fn}")
