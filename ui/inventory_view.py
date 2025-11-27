# -*- coding: utf-8 -*-
# ui/inventory_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, filedialog, simpledialog
from controllers.inventory_controller import InventoryController
import csv

class InventoryFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=30)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
        
        # Callback for when inventory changes (to notify other views)
        self.on_inventory_change = None
        
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
        
        # Quick quantity adjustment buttons
        tb.Button(
            actions, 
            text="➕ Add Stock", 
            bootstyle="success-outline", 
            command=self.quick_add_stock,
            width=13
        ).pack(side="right", padx=5)
        
        tb.Button(
            actions, 
            text="➖ Remove Stock", 
            bootstyle="warning-outline", 
            command=self.quick_remove_stock,
            width=15
        ).pack(side="right", padx=5)
        
        # Print Labels button
        tb.Button(
            actions, 
            text="🖨️ Print Labels", 
            bootstyle="info-outline", 
            command=self.print_labels_dialog,
            width=18
        ).pack(side="right", padx=5)
        
        tb.Button(
            actions, 
            text="➕ Add Item", 
            bootstyle="success", 
            command=self.add_item_dialog,
            width=12
        ).pack(side="right", padx=5)
        
        tb.Button(
            actions, 
            text="🗑️ Delete", 
            bootstyle="danger-outline", 
            command=self.delete_selected_item,
            width=12
        ).pack(side="right", padx=5)
        
        tb.Button(
            actions, 
            text="🔄 Refresh", 
            bootstyle="primary", 
            command=self.refresh,
            width=10
        ).pack(side="right", padx=5)
        
        tb.Button(
            actions, 
            text="📤 Export", 
            bootstyle="info-outline", 
            command=self.export_csv,
            width=10
        ).pack(side="right", padx=5)
        
        # --- Search & Filter Bar ---
        filter_frame = tb.Labelframe(self.frame, text="🔍 Search & Filter", padding=20, bootstyle="primary")
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        filter_frame.columnconfigure(1, weight=1)  # Search entry expands
        filter_frame.columnconfigure(3, weight=0)  # Category combo fixed width
        
        # Initialize variables first to avoid AttributeError
        self.search_var = tb.StringVar()
        self.low_stock_var = tb.BooleanVar(value=False)
        
        # Search box with placeholder
        tb.Label(filter_frame, text="Search:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.search_var.trace("w", self.filter_items)
        search_entry = tb.Entry(filter_frame, textvariable=self.search_var, font=("Segoe UI", 11))
        search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        
        # Category filter dropdown
        tb.Label(filter_frame, text="Category:", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, sticky="w", padx=(20, 10))
        self.category_var = tb.StringVar(value="All")
        self.category_combo = tb.Combobox(
            filter_frame, 
            textvariable=self.category_var, 
            font=("Segoe UI", 11),
            state="readonly",
            width=15
        )
        self.category_combo.grid(row=0, column=3, sticky="w", padx=(0, 20))
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_items())
        
        # Load categories
        self.load_categories()
        
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
        
        # Low stock filter (variable already initialized above)
        tb.Checkbutton(
            filter_frame, 
            text="⚠️ Low Stock Only (< 5)", 
            variable=self.low_stock_var, 
            bootstyle="warning-round-toggle",
            command=self.filter_items
        ).grid(row=0, column=4, sticky="w", padx=(20, 10))
        
        # Item count label
        self.count_label = tb.Label(filter_frame, text="Items: 0 / 0", font=("Segoe UI", 11, "bold"), bootstyle="info")
        self.count_label.grid(row=0, column=5, sticky="e", padx=(20, 0))

        # --- Inventory Table ---
        table_frame = tb.Labelframe(self.frame, text="📋 Inventory Items", padding=20, bootstyle="secondary")
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview with enhanced styling
        cols = ("id", "sku", "name", "category", "specs", "qty", "buy", "sell", "value")
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
            "specs": "Specifications",
            "qty": "Stock",
            "buy": "Buy Price ",
            "sell": "Sell Price ",
            "value": "Total Value "
        }
        
        # Column widths - proportional to fill full width
        widths = {
            "id": 70,
            "sku": 150,
            "name": 300,  # Reduced from 350 to make room for specs
            "category": 140,  # Reduced from 160
            "specs": 180,  # New specs column
            "qty": 100,
            "buy": 140,  # Reduced from 160
            "sell": 140,  # Reduced from 160
            "value": 150  # Reduced from 180
        }
        
        # Column alignments
        alignments = {
            "id": "center",
            "sku": "center",
            "name": "center",
            "category": "center",
            "specs": "center",
            "qty": "center",
            "buy": "center",
            "sell": "center",
            "value": "center"
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
        
        # Configure table tags with enhanced stock level color coding
        from ui.styles import configure_table_tags, STOCK_COLORS
        configure_table_tags(self.tree, table_type="stock")
        
        # Additional alternating row colors
        self.tree.tag_configure('evenrow', background='#FFFFFF')
        self.tree.tag_configure('oddrow', background='#F8F9FA')
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Right-click context menu for quick actions
        self.context_menu = tb.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="➕ Add 1 to Stock", command=lambda: self.adjust_stock(1))
        self.context_menu.add_command(label="➕ Add 5 to Stock", command=lambda: self.adjust_stock(5))
        self.context_menu.add_command(label="➕ Add 10 to Stock", command=lambda: self.adjust_stock(10))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="➖ Remove 1 from Stock", command=lambda: self.adjust_stock(-1))
        self.context_menu.add_command(label="➖ Remove 5 from Stock", command=lambda: self.adjust_stock(-5))
        self.context_menu.add_command(label="➖ Remove 10 from Stock", command=lambda: self.adjust_stock(-10))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✏️ Edit Item", command=self.edit_selected_item)
        self.context_menu.add_command(label="🗑️ Delete Item", command=self.delete_selected_item)
        
        def show_context_menu(event):
            # Select the item under cursor
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        
        self.tree.bind("<Button-3>", show_context_menu)  # Right-click
        
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

    def load_categories(self):
        """Load unique categories from inventory"""
        try:
            items = InventoryController.get_all_items()
            categories = set()
            for item in items:
                if item[3]:  # category is at index 3
                    categories.add(str(item[3]))
            
            # Update combobox values
            category_list = ["All"] + sorted(list(categories))
            self.category_combo['values'] = category_list
            self.category_var.set("All")
        except Exception as e:
            print(f"Error loading categories: {e}")

    def refresh(self):
        try:
            self.all_items = InventoryController.get_all_items()
            self.load_categories()  # Reload categories when refreshing
            self.filter_items()
            # Notify ALL views that inventory was refreshed
            from modules.event_manager import event_manager
            event_manager.notify('inventory_changed', {'action': 'refresh'})
        except Exception as e:
            messagebox.showerror("Error", f"Could not load inventory: {e}")

    def filter_items(self, *args):
        # Safety check - ensure initialization is complete
        if not hasattr(self, 'low_stock_var') or not hasattr(self, 'tree'):
            return
            
        # Get search query, handling placeholder
        query = self.search_var.get().lower()
        # Skip filtering if it's the placeholder text
        if query == "search by sku, name, category...":
            query = ""
        low_stock = self.low_stock_var.get()
        
        # Get category filter
        selected_category = self.category_var.get() if hasattr(self, 'category_var') else "All"
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        displayed_count = 0
        total_inventory_value = 0.0
        
        for idx, row in enumerate(self.all_items):
            # row: id, sku, name, category, qty, buy_price, sell_price, storage, ram, color, condition, brand, model, warranty_months
            # Filter by category
            if selected_category != "All":
                item_category = str(row[3])  # category is at index 3
                if item_category != selected_category:
                    continue
            
            # Filter by text (including specs)
            if query:
                combined = " ".join([str(x) if x else "" for x in row]).lower()
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
            
            # Get prices
            try:
                buy_price = float(row[5])  # buy price at index 5
                sell_price = float(row[6])  # sell price at index 6
            except:
                buy_price = 0.0
                sell_price = 0.0
            
            # Calculate total value (qty * buy price)
            total_value = qty * buy_price
            total_inventory_value += total_value
            
            # Format mobile specifications
            from modules.mobile_spec_manager import MobileSpecManager
            storage = row[7] if len(row) > 7 else None
            ram = row[8] if len(row) > 8 else None
            color = row[9] if len(row) > 9 else None
            specs_display = MobileSpecManager.format_specs_display(storage, ram, color)
            
            # Format display row with formatted prices and specs
            display_row = [
                row[0],  # id
                row[1],  # sku
                row[2],  # name
                row[3],  # category
                specs_display,  # formatted specs
                row[4],  # qty
                f"{buy_price:,.2f}",  # buy price (unit price, not total)
                f"{sell_price:,.2f}",  # sell price (unit price, not total)
                f"EGP {total_value:,.2f}"  # total value (qty * buy_price)
            ]
            
            # Determine row styling with enhanced stock level color coding
            from ui.styles import get_stock_tag
            tags = []
            
            # Add stock level tag (green/yellow/red/gray based on quantity)
            stock_tag = get_stock_tag(qty)
            tags.append(stock_tag)
            
            # Add alternating row color for better readability
            if displayed_count % 2 == 0:
                tags.append('evenrow')
            else:
                tags.append('oddrow')
            
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
        win.geometry("800x700")  # Increased width from 620 to 800
        win.resizable(True, True)
        win.minsize(750, 650)  # Increased minimum width
        
        # Center the window
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (800 // 2)  # Updated for new width
        y = (win.winfo_screenheight() // 2) - (700 // 2)  # Updated for new height
        win.geometry(f"800x700+{x}+{y}")
        
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
        
        canvas_window = canvas.create_window((0, 0), window=form_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make the canvas window expand to fill the canvas width
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling functions (defined early, bound later after widgets are created)
        def on_mousewheel(event):
            # Windows and MacOS
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            # Linux
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        # Recursively bind mousewheel to all widgets
        def bind_to_mousewheel(widget):
            try:
                widget.bind("<MouseWheel>", on_mousewheel)  # Windows/MacOS
                widget.bind("<Button-4>", on_mousewheel)    # Linux scroll up
                widget.bind("<Button-5>", on_mousewheel)    # Linux scroll down
            except:
                pass  # Some widgets may not support binding
            
            # Recursively bind to all children
            for child in widget.winfo_children():
                bind_to_mousewheel(child)
        
        def unbind_from_mousewheel(widget):
            try:
                widget.unbind("<MouseWheel>")
                widget.unbind("<Button-4>")
                widget.unbind("<Button-5>")
            except:
                pass
            
            # Recursively unbind from all children
            for child in widget.winfo_children():
                unbind_from_mousewheel(child)
        
        # Clean up on window destroy
        def on_destroy():
            unbind_from_mousewheel(win)
            win.destroy()
        
        win.protocol("WM_DELETE_WINDOW", on_destroy)
        
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
        
        # Enhanced Barcode Scanner Field (at the top for easy scanning)
        barcode_frame = tb.Labelframe(form_container, text="📷 Barcode Scanner", padding=20, bootstyle="info")
        barcode_frame.pack(fill="x", pady=(0, 25))
        
        # Instructions with icon
        instruction_frame = tb.Frame(barcode_frame)
        instruction_frame.pack(fill="x", pady=(0, 12))
        
        tb.Label(
            instruction_frame, 
            text="🔍", 
            font=("Segoe UI", 20)
        ).pack(side="left", padx=(0, 10))
        
        instruction_text = tb.Frame(instruction_frame)
        instruction_text.pack(side="left", fill="x", expand=True)
        
        tb.Label(
            instruction_text, 
            text="Scan barcode with your scanner device",
            font=("Segoe UI", 11, "bold"),
            foreground="#2C5282"
        ).pack(anchor="w")
        
        tb.Label(
            instruction_text, 
            text="The scanned code will automatically fill the SKU field below",
            font=("Segoe UI", 9, "italic"),
            foreground="#6c757d"
        ).pack(anchor="w")
        
        # Barcode input with enhanced styling
        barcode_input_frame = tb.Frame(barcode_frame)
        barcode_input_frame.pack(fill="x")
        
        tb.Label(
            barcode_input_frame, 
            text="Scan Here:", 
            font=("Segoe UI", 11, "bold")
        ).pack(side="left", padx=(0, 10))
        
        barcode_entry = tb.Entry(
            barcode_input_frame, 
            font=("Segoe UI", 14, "bold"),
            bootstyle="info"
        )
        barcode_entry.pack(side="left", fill="x", expand=True)
        barcode_entry.focus()  # Auto-focus for immediate scanning
        
        # Status indicator
        scan_status = tb.Label(
            barcode_frame, 
            text="⏳ Ready to scan...", 
            font=("Segoe UI", 9, "italic"),
            foreground="#6c757d"
        )
        scan_status.pack(anchor="w", pady=(8, 0))
        
        # Form fields with placeholders
        e_sku = create_field(form_container, "SKU (Stock Keeping Unit)", is_required=True)
        add_placeholder(e_sku, "e.g., IP14-BLK-128 or scan barcode above")
        
        # Enhanced barcode scan handler - when Enter is pressed, copy to SKU
        def on_barcode_scan(event):
            scanned_code = barcode_entry.get().strip()
            if scanned_code:
                # Clear placeholder if present
                if hasattr(e_sku, 'has_placeholder') and e_sku.has_placeholder:
                    e_sku.delete(0, 'end')
                    e_sku.config(foreground=e_sku.default_color)
                    e_sku.has_placeholder = False
                else:
                    e_sku.delete(0, 'end')
                
                # Set the scanned barcode as SKU
                e_sku.insert(0, scanned_code)
                
                # Show success feedback
                barcode_entry.config(bootstyle="success")
                scan_status.configure(
                    text=f"✅ Scanned: {scanned_code}", 
                    foreground="#28a745",
                    font=("Segoe UI", 10, "bold")
                )
                
                # Clear barcode field after a short delay
                def clear_and_reset():
                    barcode_entry.delete(0, 'end')
                    barcode_entry.config(bootstyle="info")
                    scan_status.configure(
                        text="⏳ Ready to scan...", 
                        foreground="#6c757d",
                        font=("Segoe UI", 9, "italic")
                    )
                    # Check if category is mobile and focus on storage field
                    try:
                        from modules.mobile_spec_manager import MobileSpecManager
                        category = e_category.get()
                        if MobileSpecManager.is_mobile_category(category):
                            # Focus on storage field for mobile products
                            e_storage.focus()
                        else:
                            # Move focus to name field for non-mobile products
                            e_name.focus()
                    except:
                        # Fallback to name field if anything goes wrong
                        try:
                            e_name.focus()
                        except:
                            pass
                
                win.after(800, clear_and_reset)  # Clear after 800ms
                
                return "break"  # Prevent default Enter behavior
                win.after(500, lambda: barcode_entry.config(bootstyle=""))
        
        barcode_entry.bind("<Return>", on_barcode_scan)
        
        e_name = create_field(form_container, "Item Name", is_required=True)
        add_placeholder(e_name, "e.g., iPhone 14 Pro Max")
        
        # Category with better options - Import from constants
        from modules.constants import PRODUCT_CATEGORIES
        e_category = create_field(form_container, "Category", is_required=True, field_type="combobox", options=PRODUCT_CATEGORIES)
        
        # Category change handler (will be defined after spec fields are created)
        def on_category_change(event=None):
            """Show/hide mobile specification fields based on category"""
            from modules.mobile_spec_manager import MobileSpecManager
            from modules.spec_preference_manager import SpecPreferenceManager
            
            category = e_category.get()
            if MobileSpecManager.is_mobile_category(category):
                # Show spec frame
                spec_frame.pack(fill="x", pady=(0, 18), before=auto_print_frame)
                
                # Load last-used values if fields are empty
                if not e_storage.get() or not e_ram.get() or not e_color.get():
                    pref_mgr = SpecPreferenceManager()
                    if not e_storage.get():
                        e_storage.set(pref_mgr.get_last_storage())
                    if not e_ram.get():
                        e_ram.set(pref_mgr.get_last_ram())
                    if not e_color.get():
                        e_color.set(pref_mgr.get_last_color())
            else:
                # Hide spec frame
                spec_frame.pack_forget()
                # Clear spec fields
                e_storage.set("")
                e_ram.set("")
                e_color.set("")
        
        # Bind category change event
        e_category.bind("<<ComboboxSelected>>", on_category_change)
        
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
        
        # Mobile Specifications Section
        from modules.mobile_spec_manager import MobileSpecManager
        
        spec_frame = tb.Labelframe(form_container, text="📱 Mobile Specifications", padding=20, bootstyle="info")
        # Initially hidden - will show when mobile category is selected
        
        # Create specification fields
        spec_grid = tb.Frame(spec_frame)
        spec_grid.pack(fill="x")
        spec_grid.columnconfigure(0, weight=1)
        spec_grid.columnconfigure(1, weight=1)
        spec_grid.columnconfigure(2, weight=1)
        
        # Storage field
        storage_frame = tb.Frame(spec_grid)
        storage_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        storage_label_container = tb.Frame(storage_frame)
        storage_label_container.pack(fill="x", pady=(0, 6))
        tb.Label(storage_label_container, text="Storage", font=("Segoe UI", 11, "bold")).pack(side="left")
        tb.Label(storage_label_container, text="*", font=("Segoe UI", 11, "bold"), bootstyle="danger").pack(side="left", padx=(3, 0))
        e_storage = tb.Combobox(
            storage_frame,
            values=MobileSpecManager.get_storage_options(),
            state="normal",  # Allow custom values
            font=("Segoe UI", 11)
        )
        e_storage.pack(fill="x")
        
        # RAM field
        ram_frame = tb.Frame(spec_grid)
        ram_frame.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        ram_label_container = tb.Frame(ram_frame)
        ram_label_container.pack(fill="x", pady=(0, 6))
        tb.Label(ram_label_container, text="RAM", font=("Segoe UI", 11, "bold")).pack(side="left")
        tb.Label(ram_label_container, text="*", font=("Segoe UI", 11, "bold"), bootstyle="danger").pack(side="left", padx=(3, 0))
        e_ram = tb.Combobox(
            ram_frame,
            values=MobileSpecManager.get_ram_options(),
            state="normal",  # Allow custom values
            font=("Segoe UI", 11)
        )
        e_ram.pack(fill="x")
        
        # Color field
        color_frame = tb.Frame(spec_grid)
        color_frame.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        color_label_container = tb.Frame(color_frame)
        color_label_container.pack(fill="x", pady=(0, 6))
        tb.Label(color_label_container, text="Color", font=("Segoe UI", 11, "bold")).pack(side="left")
        tb.Label(color_label_container, text="*", font=("Segoe UI", 11, "bold"), bootstyle="danger").pack(side="left", padx=(3, 0))
        e_color = tb.Combobox(
            color_frame,
            values=MobileSpecManager.get_color_options(),
            state="normal",  # Allow custom values
            font=("Segoe UI", 11)
        )
        e_color.pack(fill="x")
        
        # Helper text
        tb.Label(
            spec_frame,
            text="Required for mobile phones and smartphones",
            font=("Segoe UI", 9, "italic"),
            foreground="#6c757d"
        ).pack(anchor="w", pady=(10, 0))
        
        # Enter key navigation for spec fields
        def on_storage_enter(event):
            e_ram.focus()
            return "break"
        
        def on_ram_enter(event):
            e_color.focus()
            return "break"
        
        def on_color_enter(event):
            # Move to description field
            e_desc.focus()
            return "break"
        
        e_storage.bind("<Return>", on_storage_enter)
        e_ram.bind("<Return>", on_ram_enter)
        e_color.bind("<Return>", on_color_enter)
        
        # Auto-print labels option
        from modules.label_preferences import LabelPreferences
        prefs = LabelPreferences()
        
        auto_print_frame = tb.Frame(form_container)
        auto_print_frame.pack(fill="x", pady=(10, 0))
        
        auto_print_var = tb.BooleanVar(value=prefs.get('auto_print_new_products', False))
        
        auto_print_check = tb.Checkbutton(
            auto_print_frame,
            text="🖨️ Print labels after adding this item",
            variable=auto_print_var,
            bootstyle="info-round-toggle"
        )
        auto_print_check.pack(anchor="w")
        
        tb.Label(
            auto_print_frame,
            text="Automatically open the Print Labels dialog after saving",
            font=("Segoe UI", 8),
            foreground="#666"
        ).pack(anchor="w", padx=(30, 0))
        
        # Save auto-print preference when changed
        def on_auto_print_change():
            prefs.set('auto_print_new_products', auto_print_var.get())
        
        auto_print_var.trace_add("write", lambda *args: on_auto_print_change())
        
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
            
            # Validate mobile specifications if category is mobile
            from modules.mobile_spec_manager import MobileSpecManager
            storage = e_storage.get().strip()
            ram = e_ram.get().strip()
            color = e_color.get().strip()
            
            is_valid, error_msg = MobileSpecManager.validate_specs(storage, ram, color, category)
            if not is_valid:
                validation_label.configure(text=f"❌ {error_msg.split(chr(10))[0]}", bootstyle="danger")
                messagebox.showerror("Missing Specifications", error_msg)
                # Focus on first empty field
                if not storage:
                    e_storage.focus()
                elif not ram:
                    e_ram.focus()
                elif not color:
                    e_color.focus()
                return
            
            # Save item
            if InventoryController.add_item(sku, name, qty, buy, sell, category, desc, storage, ram, color):
                # Save last-used specs if this was a mobile product
                if MobileSpecManager.is_mobile_category(category) and storage and ram and color:
                    from modules.spec_preference_manager import SpecPreferenceManager
                    pref_mgr = SpecPreferenceManager()
                    pref_mgr.save_last_specs(storage, ram, color)
                
                messagebox.showinfo("✓ Success", f"Item '{name}' has been added to inventory!")
                unbind_mousewheel(None)  # Clean up mouse wheel bindings
                win.destroy()
                self.refresh()
                # Notify ALL views that inventory changed
                from modules.event_manager import event_manager
                event_manager.notify('inventory_changed', {'action': 'add', 'item': name})
                
                # Check auto-print preference
                from modules.label_preferences import LabelPreferences
                prefs = LabelPreferences()
                if prefs.get('auto_print_new_products', False):
                    # Get the newly added item ID
                    from modules.db import get_conn
                    conn = get_conn()
                    c = conn.cursor()
                    c.execute("SELECT item_id FROM inventory WHERE sku = ?", (sku,))
                    result = c.fetchone()
                    conn.close()
                    
                    if result:
                        # Select the new item in the tree and open print dialog
                        item_id = result[0]
                        # Find and select the item in the tree
                        for tree_item in self.tree.get_children():
                            if self.tree.item(tree_item)['values'][0] == item_id:
                                self.tree.selection_set(tree_item)
                                self.tree.see(tree_item)
                                # Open print labels dialog
                                self.frame.after(100, self.print_labels_dialog)
                                break
            else:
                validation_label.configure(
                    text="❌ Could not add item. SKU might already exist.",
                    bootstyle="danger"
                )
        
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
            command=on_destroy,
            width=15
        ).pack(side="right", padx=5)
        
        # Bind mouse wheel scrolling to all widgets in the dialog (after all widgets are created)
        bind_to_mousewheel(win)
        
        # Focus on first field
        barcode_entry.focus()

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
                # Notify ALL views that inventory changed
                from modules.event_manager import event_manager
                event_manager.notify('inventory_changed', {'action': 'delete', 'item': name})
            else:
                messagebox.showerror("Error", "Could not delete item. Check logs for details.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {e}")
    
    def export_csv(self):
        if not self.all_items:
            messagebox.showwarning("No data", "No items to export.")
            return
        
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], initialfile="inventory_export.csv")
        if not fn:
            return
        
        try:
            with open(fn, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write header with separate storage, RAM, color columns
                writer.writerow(["ID", "SKU", "Name", "Category", "Quantity", "Buy Price", "Sell Price", "Storage", "RAM", "Color"])
                
                # Write data rows
                for row in self.all_items:
                    # row: id, sku, name, category, qty, buy_price, sell_price, storage, ram, color, condition, brand, model, warranty_months
                    export_row = [
                        row[0],  # id
                        row[1],  # sku
                        row[2],  # name
                        row[3],  # category
                        row[4],  # qty
                        row[5],  # buy_price
                        row[6],  # sell_price
                        row[7] if len(row) > 7 and row[7] else "",  # storage
                        row[8] if len(row) > 8 and row[8] else "",  # ram
                        row[9] if len(row) > 9 and row[9] else ""   # color
                    ]
                    writer.writerow(export_row)
            
            messagebox.showinfo("Exported", f"Exported {len(self.all_items)} items to {fn}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")
    
    def quick_add_stock(self):
        """Quick add stock to selected item"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to add stock")
            return
        
        # Ask for quantity to add
        qty = simpledialog.askinteger(
            "Add Stock",
            "How many units to add?",
            initialvalue=1,
            minvalue=1,
            maxvalue=1000
        )
        
        if qty:
            self.adjust_stock(qty)
    
    def quick_remove_stock(self):
        """Quick remove stock from selected item"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to remove stock")
            return
        
        # Ask for quantity to remove
        qty = simpledialog.askinteger(
            "Remove Stock",
            "How many units to remove?",
            initialvalue=1,
            minvalue=1,
            maxvalue=1000
        )
        
        if qty:
            self.adjust_stock(-qty)
    
    def adjust_stock(self, adjustment):
        """Adjust stock quantity for selected item"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item")
            return
        
        # Get item details
        item_values = self.tree.item(selection[0])['values']
        item_id = item_values[0]
        sku = item_values[1]
        name = item_values[2]
        current_qty = int(item_values[4])
        
        # Calculate new quantity
        new_qty = current_qty + adjustment
        
        # Validate
        if new_qty < 0:
            messagebox.showwarning(
                "Invalid Quantity",
                f"Cannot remove {abs(adjustment)} units.\nCurrent stock: {current_qty}"
            )
            return
        
        # Update in database
        try:
            from controllers.inventory_controller import InventoryController
            
            # Get full item data
            item_data = None
            for row in self.all_items:
                if row[0] == item_id:
                    item_data = row
                    break
            
            if not item_data:
                messagebox.showerror("Error", "Item not found")
                return
            
            # Update quantity (keeping other fields the same)
            # row: id, sku, name, category, qty, buy_price, sell_price
            success = InventoryController.update_item(
                item_id=item_id,
                sku=sku,
                name=name,
                category=item_data[3],
                qty=new_qty,
                buy_price=item_data[5],
                sell_price=item_data[6],
                description=None
            )
            
            if success:
                action = "Added" if adjustment > 0 else "Removed"
                messagebox.showinfo(
                    "✓ Success",
                    f"{action} {abs(adjustment)} unit(s)\n\n"
                    f"Item: {name}\n"
                    f"Previous: {current_qty}\n"
                    f"New Stock: {new_qty}"
                )
                self.refresh()
                
                # Notify ALL views that inventory changed
                from modules.event_manager import event_manager
                event_manager.notify('inventory_changed', {'action': 'adjust_stock', 'item': name, 'adjustment': adjustment})
            else:
                messagebox.showerror("Error", "Failed to update stock")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to adjust stock: {e}")
    
    def edit_selected_item(self):
        """Edit the selected item with mobile specifications support"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to edit")
            return
        
        # Get item details from tree
        item_values = self.tree.item(selection[0])['values']
        item_id = item_values[0]
        
        # Get full item details from database
        from modules.db import get_conn
        conn = get_conn()
        c = conn.cursor()
        c.execute("""SELECT item_id, sku, name, category, quantity, buy_price, sell_price, 
                            storage, ram, color, description 
                     FROM inventory WHERE item_id=?""", (item_id,))
        item = c.fetchone()
        conn.close()
        
        if not item:
            messagebox.showerror("Error", "Could not load item details")
            return
        
        # Unpack item data
        item_id, sku, name, category, qty, buy_price, sell_price, storage, ram, color, description = item
        
        # Create edit dialog
        win = tb.Toplevel(self.frame)
        win.title("Edit Inventory Item")
        win.geometry("800x700")
        win.resizable(True, True)
        win.minsize(750, 650)
        
        # Center the window
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (800 // 2)
        y = (win.winfo_screenheight() // 2) - (700 // 2)
        win.geometry(f"800x700+{x}+{y}")
        
        # Header
        header = tb.Frame(win, bootstyle="warning", padding=20)
        header.pack(fill="x")
        tb.Label(
            header, 
            text="✏️ Edit Item", 
            font=("Segoe UI", 20, "bold"),
            bootstyle="warning-inverse"
        ).pack(anchor="w")
        tb.Label(
            header, 
            text=f"Editing: {name}",
            font=("Segoe UI", 10),
            bootstyle="warning-inverse"
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
        
        canvas_window = canvas.create_window((0, 0), window=form_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create form fields
        def create_field(parent, label_text, is_required=False, field_type="entry", options=None):
            field_frame = tb.Frame(parent)
            field_frame.pack(fill="x", pady=(0, 18))
            
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
            elif field_type == "text":
                widget = tb.Text(field_frame, height=3, font=("Segoe UI", 11))
                widget.pack(fill="x")
            
            return widget
        
        # Form fields
        e_sku = create_field(form_container, "SKU (Stock Keeping Unit)", is_required=True)
        e_sku.insert(0, sku)
        
        e_name = create_field(form_container, "Item Name", is_required=True)
        e_name.insert(0, name)
        
        from modules.constants import PRODUCT_CATEGORIES
        e_category = create_field(form_container, "Category", is_required=True, field_type="combobox", options=PRODUCT_CATEGORIES)
        e_category.set(category)
        
        # Mobile Specifications Section
        from modules.mobile_spec_manager import MobileSpecManager
        
        spec_frame = tb.Labelframe(form_container, text="📱 Mobile Specifications", padding=20, bootstyle="info")
        
        spec_grid = tb.Frame(spec_frame)
        spec_grid.pack(fill="x")
        spec_grid.columnconfigure(0, weight=1)
        spec_grid.columnconfigure(1, weight=1)
        spec_grid.columnconfigure(2, weight=1)
        
        # Storage field
        storage_frame = tb.Frame(spec_grid)
        storage_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        storage_label_container = tb.Frame(storage_frame)
        storage_label_container.pack(fill="x", pady=(0, 6))
        tb.Label(storage_label_container, text="Storage", font=("Segoe UI", 11, "bold")).pack(side="left")
        tb.Label(storage_label_container, text="*", font=("Segoe UI", 11, "bold"), bootstyle="danger").pack(side="left", padx=(3, 0))
        e_storage = tb.Combobox(
            storage_frame,
            values=MobileSpecManager.get_storage_options(),
            state="normal",
            font=("Segoe UI", 11)
        )
        e_storage.pack(fill="x")
        if storage:
            e_storage.set(storage)
        
        # RAM field
        ram_frame = tb.Frame(spec_grid)
        ram_frame.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        ram_label_container = tb.Frame(ram_frame)
        ram_label_container.pack(fill="x", pady=(0, 6))
        tb.Label(ram_label_container, text="RAM", font=("Segoe UI", 11, "bold")).pack(side="left")
        tb.Label(ram_label_container, text="*", font=("Segoe UI", 11, "bold"), bootstyle="danger").pack(side="left", padx=(3, 0))
        e_ram = tb.Combobox(
            ram_frame,
            values=MobileSpecManager.get_ram_options(),
            state="normal",
            font=("Segoe UI", 11)
        )
        e_ram.pack(fill="x")
        if ram:
            e_ram.set(ram)
        
        # Color field
        color_frame = tb.Frame(spec_grid)
        color_frame.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        color_label_container = tb.Frame(color_frame)
        color_label_container.pack(fill="x", pady=(0, 6))
        tb.Label(color_label_container, text="Color", font=("Segoe UI", 11, "bold")).pack(side="left")
        tb.Label(color_label_container, text="*", font=("Segoe UI", 11, "bold"), bootstyle="danger").pack(side="left", padx=(3, 0))
        e_color = tb.Combobox(
            color_frame,
            values=MobileSpecManager.get_color_options(),
            state="normal",
            font=("Segoe UI", 11)
        )
        e_color.pack(fill="x")
        if color:
            e_color.set(color)
        
        tb.Label(
            spec_frame,
            text="Required for mobile phones and smartphones",
            font=("Segoe UI", 9, "italic"),
            foreground="#6c757d"
        ).pack(anchor="w", pady=(10, 0))
        
        # Category change handler
        def on_category_change(event=None):
            cat = e_category.get()
            if MobileSpecManager.is_mobile_category(cat):
                spec_frame.pack(fill="x", pady=(0, 18), after=e_category.master)
            else:
                spec_frame.pack_forget()
                e_storage.set("")
                e_ram.set("")
                e_color.set("")
        
        e_category.bind("<<ComboboxSelected>>", on_category_change)
        
        # Show specs if current category is mobile
        if MobileSpecManager.is_mobile_category(category):
            spec_frame.pack(fill="x", pady=(0, 18))
        
        # Quantity and prices grid
        grid_frame = tb.Frame(form_container)
        grid_frame.pack(fill="x", pady=(0, 18))
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)
        
        qty_frame = tb.Frame(grid_frame)
        qty_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tb.Label(qty_frame, text="Quantity *", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        e_qty = tb.Entry(qty_frame, font=("Segoe UI", 11))
        e_qty.pack(fill="x")
        e_qty.insert(0, str(qty))
        
        buy_frame = tb.Frame(grid_frame)
        buy_frame.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        tb.Label(buy_frame, text="Buy Price (EGP) *", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        e_buy = tb.Entry(buy_frame, font=("Segoe UI", 11))
        e_buy.pack(fill="x")
        e_buy.insert(0, str(buy_price))
        
        sell_frame = tb.Frame(grid_frame)
        sell_frame.grid(row=0, column=2, sticky="ew", padx=(10, 0))
        tb.Label(sell_frame, text="Sell Price (EGP) *", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        e_sell = tb.Entry(sell_frame, font=("Segoe UI", 11))
        e_sell.pack(fill="x")
        e_sell.insert(0, str(sell_price))
        
        # Description
        e_desc = create_field(form_container, "Description (Optional)", field_type="text")
        if description:
            e_desc.insert("1.0", description)
        
        # Validation message
        validation_label = tb.Label(form_container, text="", font=("Segoe UI", 10))
        validation_label.pack(pady=(10, 0))
        
        # Buttons
        button_frame = tb.Frame(win, padding=20)
        button_frame.pack(fill="x", side="bottom")
        
        def validate_and_save():
            validation_label.configure(text="")
            
            new_sku = e_sku.get().strip()
            new_name = e_name.get().strip()
            new_category = e_category.get()
            new_desc = e_desc.get("1.0", "end").strip()
            
            if not new_sku:
                validation_label.configure(text="❌ SKU is required", bootstyle="danger")
                e_sku.focus()
                return
            
            if not new_name:
                validation_label.configure(text="❌ Item name is required", bootstyle="danger")
                e_name.focus()
                return
            
            try:
                new_qty = int(e_qty.get().strip())
                if new_qty < 0:
                    raise ValueError("Quantity cannot be negative")
            except ValueError as e:
                validation_label.configure(text=f"❌ Invalid quantity: {e}", bootstyle="danger")
                e_qty.focus()
                return
            
            try:
                new_buy = float(e_buy.get().strip())
                if new_buy < 0:
                    raise ValueError("Buy price cannot be negative")
            except ValueError as e:
                validation_label.configure(text=f"❌ Invalid buy price: {e}", bootstyle="danger")
                e_buy.focus()
                return
            
            try:
                new_sell = float(e_sell.get().strip())
                if new_sell < 0:
                    raise ValueError("Sell price cannot be negative")
            except ValueError as e:
                validation_label.configure(text=f"❌ Invalid sell price: {e}", bootstyle="danger")
                e_sell.focus()
                return
            
            # Validate mobile specifications
            new_storage = e_storage.get().strip()
            new_ram = e_ram.get().strip()
            new_color = e_color.get().strip()
            
            is_valid, error_msg = MobileSpecManager.validate_specs(new_storage, new_ram, new_color, new_category)
            if not is_valid:
                validation_label.configure(text=f"❌ {error_msg.split(chr(10))[0]}", bootstyle="danger")
                messagebox.showerror("Missing Specifications", error_msg)
                if not new_storage:
                    e_storage.focus()
                elif not new_ram:
                    e_ram.focus()
                elif not new_color:
                    e_color.focus()
                return
            
            # Update item
            if InventoryController.update_item(item_id, new_sku, new_name, new_category, new_qty, new_buy, new_sell, new_desc, new_storage, new_ram, new_color):
                messagebox.showinfo("✓ Success", f"Item '{new_name}' has been updated!")
                win.destroy()
                self.refresh()
                from modules.event_manager import event_manager
                event_manager.notify('inventory_changed', {'action': 'update', 'item': new_name})
            else:
                validation_label.configure(
                    text="❌ Could not update item. SKU might already exist.",
                    bootstyle="danger"
                )
        
        tb.Button(
            button_frame, 
            text="💾 Save Changes", 
            bootstyle="success",
            command=validate_and_save,
            width=20
        ).pack(side="right", padx=5)
        
        tb.Button(
            button_frame, 
            text="✖ Cancel", 
            bootstyle="secondary",
            command=win.destroy,
            width=15
        ).pack(side="right", padx=5)

    def print_labels_dialog(self):
        """Enhanced dialog for printing barcode labels with quantity control"""
        # Get selected items
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select one or more items to print labels for.")
            return
        
        # Get product data for selected items
        # Tree columns: id(0), sku(1), name(2), category(3), specs(4), qty(5), buy(6), sell(7), value(8)
        selected_products = []
        for item in selection:
            values = self.tree.item(item)['values']
            selected_products.append({
                'item_id': values[0],
                'sku': values[1],
                'name': values[2],
                'category': values[3],
                'quantity': values[5],  # Fixed: qty is now at index 5 (was 4)
                'sell_price': values[7]  # Fixed: sell is now at index 7 (was 6)
            })
        
        # Create dialog
        win = tb.Toplevel(self.frame)
        win.title("🖨️ Print Product Labels")
        win.geometry("800x700")
        win.resizable(True, True)
        
        # Center window
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - 400
        y = (win.winfo_screenheight() // 2) - 350
        win.geometry(f"800x700+{x}+{y}")
        
        # Load preferences
        from modules.label_preferences import LabelPreferences
        prefs = LabelPreferences()
        
        # Header
        header = tb.Frame(win, bootstyle="info", padding=20)
        header.pack(fill="x")
        tb.Label(
            header,
            text="🖨️ Print Product Labels",
            font=("Segoe UI", 18, "bold"),
            bootstyle="info-inverse"
        ).pack(anchor="w")
        tb.Label(
            header,
            text=f"{len(selected_products)} product(s) selected",
            font=("Segoe UI", 10),
            bootstyle="info-inverse"
        ).pack(anchor="w", pady=(5, 0))
        
        # Content
        content = tb.Frame(win, padding=20)
        content.pack(fill="both", expand=True)
        
        # Label Settings
        settings_frame = tb.Labelframe(content, text="Label Settings", padding=15, bootstyle="primary")
        settings_frame.pack(fill="x", pady=(0, 15))
        
        # Label size selection
        tb.Label(settings_frame, text="Label Size:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        size_var = tb.StringVar(value=prefs.get("default_label_size", "medium"))
        
        size_frame = tb.Frame(settings_frame)
        size_frame.pack(fill="x", pady=(0, 10))
        
        tb.Radiobutton(size_frame, text="● Small (50×25mm) - Price tags", variable=size_var, value="small", bootstyle="info").pack(anchor="w", pady=2)
        tb.Radiobutton(size_frame, text="● Medium (70×40mm) - Standard labels", variable=size_var, value="medium", bootstyle="info").pack(anchor="w", pady=2)
        tb.Radiobutton(size_frame, text="● Large (100×50mm) - Detailed shelf labels", variable=size_var, value="large", bootstyle="info").pack(anchor="w", pady=2)
        
        # Cut lines option
        cut_lines_var = tb.BooleanVar(value=prefs.get("show_cut_lines", True))
        tb.Checkbutton(
            settings_frame,
            text="Show cut lines for manual cutting",
            variable=cut_lines_var,
            bootstyle="info-round-toggle"
        ).pack(anchor="w", pady=(5, 10))
        
        # Labels per page info
        info_label = tb.Label(settings_frame, text="", font=("Segoe UI", 9), foreground="#666")
        info_label.pack(anchor="w")
        
        # Product list with quantities
        products_frame = tb.Labelframe(content, text=f"Products ({len(selected_products)} selected)", padding=15, bootstyle="primary")
        products_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Product table
        table_frame = tb.Frame(products_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Create treeview for products
        columns = ("name", "sku", "stock", "qty")
        product_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        product_tree.heading("name", text="Product Name")
        product_tree.heading("sku", text="SKU")
        product_tree.heading("stock", text="Stock")
        product_tree.heading("qty", text="Labels")
        
        product_tree.column("name", width=300)
        product_tree.column("sku", width=120)
        product_tree.column("stock", width=80, anchor="center")
        product_tree.column("qty", width=80, anchor="center")
        
        product_tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=product_tree.yview)
        scrollbar.pack(side="right", fill="y")
        product_tree.configure(yscrollcommand=scrollbar.set)
        
        # Store quantities
        quantities = {}
        default_qty = prefs.get("default_quantity", 1)
        
        # Populate product list
        for product in selected_products:
            quantities[product['item_id']] = default_qty
            product_tree.insert("", "end", values=(
                product['name'],
                product['sku'],
                product['quantity'],
                default_qty
            ), tags=(str(product['item_id']),))
        
        # Quantity controls
        qty_controls = tb.Frame(products_frame)
        qty_controls.pack(fill="x", pady=(10, 0))
        
        def update_totals():
            """Update total labels and pages display"""
            from modules.reports.label_printer import LabelPrinter
            printer = LabelPrinter()
            
            total_labels = sum(quantities.values())
            layout = printer.calculate_layout(size_var.get())
            labels_per_page = layout[0] * layout[1]
            total_pages = (total_labels + labels_per_page - 1) // labels_per_page if labels_per_page > 0 else 0
            
            info_label.config(text=f"Labels per page: {labels_per_page}  |  Total labels: {total_labels}  |  Total pages: {total_pages}")
        
        def match_stock():
            """Set label quantities to match stock quantities"""
            for product in selected_products:
                quantities[product['item_id']] = product['quantity']
            refresh_tree()
            update_totals()
        
        def set_all_qty():
            """Set all quantities to a specific value"""
            qty = simpledialog.askinteger("Set All Quantities", "Enter quantity for all products:", 
                                         initialvalue=1, minvalue=1, maxvalue=100, parent=win)
            if qty:
                for product in selected_products:
                    quantities[product['item_id']] = qty
                refresh_tree()
                update_totals()
        
        def edit_selected_qty():
            """Edit quantity for selected product"""
            selected = product_tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a product to edit quantity.", parent=win)
                return
            
            item = selected[0]
            item_id = int(product_tree.item(item)['tags'][0])
            current_qty = quantities[item_id]
            
            new_qty = simpledialog.askinteger("Edit Quantity", "Enter number of labels to print:", 
                                             initialvalue=current_qty, minvalue=0, maxvalue=100, parent=win)
            if new_qty is not None:
                quantities[item_id] = new_qty
                refresh_tree()
                update_totals()
        
        def refresh_tree():
            """Refresh product tree with updated quantities"""
            for item in product_tree.get_children():
                item_id = int(product_tree.item(item)['tags'][0])
                values = list(product_tree.item(item)['values'])
                values[3] = quantities[item_id]
                product_tree.item(item, values=values)
        
        # Quantity control buttons with uniform width
        tb.Button(qty_controls, text="📦 Match Stock Qty", bootstyle="info-outline", 
                 command=match_stock, width=20).pack(side="left", padx=5)
        tb.Button(qty_controls, text="🔢 Set All Labels", bootstyle="info-outline", 
                 command=set_all_qty, width=20).pack(side="left", padx=5)
        tb.Button(qty_controls, text="✏️ Edit Quantity", bootstyle="info-outline", 
                 command=edit_selected_qty, width=20).pack(side="left", padx=5)
        
        # Double-click to edit quantity
        product_tree.bind("<Double-1>", lambda e: edit_selected_qty())
        
        # Update size change handler
        def on_size_change(*args):
            update_totals()
            prefs.set("default_label_size", size_var.get())
        
        size_var.trace_add("write", on_size_change)
        
        # Initial totals
        update_totals()
        
        # Action buttons
        def generate():
            try:
                from modules.reports.label_printer import LabelPrinter
                import os
                import sys
                import subprocess
                
                # Validate at least one label
                total_labels = sum(quantities.values())
                if total_labels == 0:
                    messagebox.showwarning("No Labels", "Please set at least one product quantity greater than 0.", parent=win)
                    return
                
                # Get full product data from database
                from modules.db import get_conn
                conn = get_conn()
                c = conn.cursor()
                
                products_data = []
                for product in selected_products:
                    c.execute("""
                        SELECT item_id, sku, name, sell_price, storage, ram, color, brand, model, barcode
                        FROM inventory WHERE item_id = ?
                    """, (product['item_id'],))
                    row = c.fetchone()
                    if row:
                        # Use barcode if available, otherwise fall back to SKU
                        barcode_value = row[9] if row[9] else row[1]  # barcode or SKU
                        products_data.append({
                            'item_id': row[0],
                            'sku': row[1],
                            'barcode': barcode_value,  # Add barcode field
                            'name': row[2],
                            'sell_price': row[3],
                            'storage': row[4],
                            'ram': row[5],
                            'color': row[6],
                            'brand': row[7],
                            'model': row[8]
                        })
                conn.close()
                
                # Ensure labels directory exists
                from pathlib import Path
                Path("labels").mkdir(exist_ok=True)
                
                # Generate labels
                printer = LabelPrinter()
                output_path = printer.generate_label_sheet(
                    products=products_data,
                    label_size=size_var.get(),
                    quantities=quantities,
                    show_cut_lines=cut_lines_var.get(),
                    paper_size="a4"  # Use A4 paper size for proper label sheets
                )
                
                # Convert to absolute path for file operations
                abs_output_path = os.path.abspath(output_path)
                
                # Verify file was created
                if not os.path.exists(abs_output_path):
                    raise FileNotFoundError(f"PDF file was not created: {abs_output_path}")
                
                # Save preferences
                prefs.set("show_cut_lines", cut_lines_var.get())
                
                # Success message
                if messagebox.askyesno("Success", 
                                      f"Labels generated successfully!\n\n"
                                      f"File: {output_path}\n"
                                      f"Total labels: {total_labels}\n\n"
                                      f"Open the PDF now?", 
                                      parent=win):
                    # Open PDF with default viewer using absolute path
                    if os.name == 'nt':  # Windows
                        os.startfile(abs_output_path)
                    elif os.name == 'posix':  # macOS and Linux
                        subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', abs_output_path))
                
                win.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate labels:\n{str(e)}", parent=win)
        
        # Additional actions
        def print_all_products():
            """Add all products from current view to the label list"""
            try:
                # Get all items from the inventory view
                all_products = []
                for item_data in self.all_items:
                    all_products.append({
                        'item_id': item_data[0],
                        'sku': item_data[1],
                        'name': item_data[2],
                        'category': item_data[3],
                        'quantity': item_data[4],
                        'sell_price': item_data[6]
                    })
                
                if not all_products:
                    messagebox.showinfo("No Products", "No products found in current view.", parent=win)
                    return
                
                # Update selected_products and quantities
                selected_products.clear()
                selected_products.extend(all_products)
                quantities.clear()
                for product in all_products:
                    quantities[product['item_id']] = default_qty
                
                # Refresh the product tree
                product_tree.delete(*product_tree.get_children())
                for product in selected_products:
                    product_tree.insert("", "end", values=(
                        product['name'],
                        product['sku'],
                        product['quantity'],
                        quantities[product['item_id']]
                    ), tags=(str(product['item_id']),))
                
                # Update header and totals
                header.winfo_children()[1].config(text=f"{len(selected_products)} product(s) selected")
                products_frame.config(text=f"Products ({len(selected_products)} selected)")
                update_totals()
                
                messagebox.showinfo("Success", f"Added {len(all_products)} products from current view.", parent=win)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add all products:\n{str(e)}", parent=win)
        
        def print_category():
            """Add all products from a selected category"""
            try:
                from modules.constants import PRODUCT_CATEGORIES
                from tkinter import simpledialog
                
                # Show category selection dialog
                category_win = tb.Toplevel(win)
                category_win.title("Select Category")
                category_win.geometry("400x300")
                category_win.transient(win)
                
                # Center window
                category_win.update_idletasks()
                x = (category_win.winfo_screenwidth() // 2) - 200
                y = (category_win.winfo_screenheight() // 2) - 150
                category_win.geometry(f"400x300+{x}+{y}")
                
                tb.Label(category_win, text="Select Category", font=("Segoe UI", 14, "bold")).pack(pady=20)
                
                selected_category = tb.StringVar()
                
                # Category list
                list_frame = tb.Frame(category_win)
                list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
                
                for category in PRODUCT_CATEGORIES:
                    tb.Radiobutton(
                        list_frame,
                        text=category,
                        variable=selected_category,
                        value=category,
                        bootstyle="info"
                    ).pack(anchor="w", pady=5)
                
                selected_category.set(PRODUCT_CATEGORIES[0])
                
                def add_category_products():
                    category = selected_category.get()
                    
                    # Get products from this category
                    category_products = []
                    for item_data in self.all_items:
                        if item_data[3] == category:  # category is at index 3
                            category_products.append({
                                'item_id': item_data[0],
                                'sku': item_data[1],
                                'name': item_data[2],
                                'category': item_data[3],
                                'quantity': item_data[4],
                                'sell_price': item_data[6]
                            })
                    
                    if not category_products:
                        messagebox.showinfo("No Products", f"No products found in category: {category}", parent=category_win)
                        return
                    
                    # Update selected_products and quantities
                    selected_products.clear()
                    selected_products.extend(category_products)
                    quantities.clear()
                    for product in category_products:
                        quantities[product['item_id']] = default_qty
                    
                    # Refresh the product tree
                    product_tree.delete(*product_tree.get_children())
                    for product in selected_products:
                        product_tree.insert("", "end", values=(
                            product['name'],
                            product['sku'],
                            product['quantity'],
                            quantities[product['item_id']]
                        ), tags=(str(product['item_id']),))
                    
                    # Update header and totals
                    header.winfo_children()[1].config(text=f"{len(selected_products)} product(s) selected")
                    products_frame.config(text=f"Products ({len(selected_products)} selected)")
                    update_totals()
                    
                    category_win.destroy()
                    messagebox.showinfo("Success", f"Added {len(category_products)} products from {category}.", parent=win)
                
                # Buttons
                btn_frame_cat = tb.Frame(category_win)
                btn_frame_cat.pack(fill="x", padx=20, pady=(0, 20))
                
                tb.Button(btn_frame_cat, text="Cancel", bootstyle="secondary", 
                         command=category_win.destroy, width=15).pack(side="right", padx=5)
                tb.Button(btn_frame_cat, text="Add Products", bootstyle="success", 
                         command=add_category_products, width=15).pack(side="right", padx=5)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add category products:\n{str(e)}", parent=win)
        
        # Bottom buttons
        btn_frame = tb.Frame(win, padding=20)
        btn_frame.pack(fill="x", side="bottom")
        
        # Left side buttons
        tb.Button(btn_frame, text="📋 Print All Products", bootstyle="info-outline", 
                 command=print_all_products, width=20).pack(side="left", padx=5)
        tb.Button(btn_frame, text="📁 Print Category...", bootstyle="info-outline", 
                 command=print_category, width=20).pack(side="left", padx=5)
        
        # Right side buttons
        tb.Button(btn_frame, text="✖ Cancel", bootstyle="secondary", 
                 command=win.destroy, width=15).pack(side="right", padx=5)
        tb.Button(btn_frame, text="🖨️ Generate PDF", bootstyle="success", 
                 command=generate, width=20).pack(side="right", padx=5)
