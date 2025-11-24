# ui/sales_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, simpledialog
import os
from datetime import datetime
from controllers.pos_controller import POSController
from controllers.inventory_controller import InventoryController

class SalesFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=25)
        self.cart = []  # list of dicts: {id, sku, name, qty, price, cost, max_qty}
        
        # Layout: Left (Inventory Search), Right (Cart & Checkout) - Bigger proportions
        self.frame.columnconfigure(0, weight=2)  # Left panel bigger
        self.frame.columnconfigure(1, weight=3)  # Right panel even bigger
        self.frame.rowconfigure(0, weight=1)
        
        # --- Left Panel: Product Selection ---
        left_panel = tb.Labelframe(self.frame, text="📦 Product Selection", padding=20, bootstyle="info")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        left_panel.rowconfigure(3, weight=1)
        
        # Search & Filter
        search_frame = tb.Frame(left_panel)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        search_frame.columnconfigure(1, weight=1)
        
        tb.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.search_var = tb.StringVar()
        self.search_var.trace("w", self.filter_inventory)
        search_entry = tb.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 12))
        search_entry.grid(row=0, column=1, sticky="ew")
        search_entry.focus()
        
        # Category Filter
        filter_frame = tb.Frame(left_panel)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        tb.Label(filter_frame, text="📂 Category:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 10))
        self.category_filter = tb.Combobox(filter_frame, values=["All", "Mobile", "Covers", "Charger", "AirPods", "Accessories", "Parts", "Other"], state="readonly", width=20, font=("Segoe UI", 11))
        self.category_filter.set("All")
        self.category_filter.pack(side="left")
        self.category_filter.bind("<<ComboboxSelected>>", self.filter_inventory)
        
        # Product Info Display - Bigger
        info_frame = tb.Labelframe(left_panel, text="📋 Product Details", padding=15, bootstyle="secondary")
        info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        self.product_info = tb.Label(info_frame, text="Select a product to view details", font=("Segoe UI", 11), justify="left", wraplength=700)
        self.product_info.pack(fill="x")
        
        # Inventory List with color-coded stock - Bigger
        cols = ("id", "sku", "name", "category", "stock", "price")
        self.inv_tree = ttk.Treeview(left_panel, columns=cols, show="headings", height=20)
        widths = {"id":60, "sku":120, "name":280, "category":140, "stock":80, "price":100}
        alignments = {"id":"center", "sku":"w", "name":"w", "category":"w", "stock":"center", "price":"e"}
        labels = {"id":"ID", "sku":"SKU", "name":"Product Name", "category":"Category", "stock":"Stock", "price":"Price"}
        
        for c in cols:
            self.inv_tree.heading(c, text=labels.get(c, c.upper()), anchor="w" if alignments[c] == "w" else "center")
            self.inv_tree.column(c, width=widths[c], anchor=alignments[c])
        
        self.inv_tree.grid(row=3, column=0, sticky="nsew", pady=(0, 12))
        
        # Bind selection event to show product details
        self.inv_tree.bind("<<TreeviewSelect>>", self.show_product_details)
        
        # Scrollbar
        inv_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=self.inv_tree.yview)
        inv_scroll.grid(row=3, column=1, sticky="ns", pady=(0, 12))
        self.inv_tree.configure(yscrollcommand=inv_scroll.set)
        
        # Stock color tags with better colors
        self.inv_tree.tag_configure("in_stock", foreground="#28a745", font=("Segoe UI", 10))
        self.inv_tree.tag_configure("low_stock", foreground="#fd7e14", font=("Segoe UI", 10))
        self.inv_tree.tag_configure("very_low", foreground="#dc3545", font=("Segoe UI", 10, "bold"))
        self.inv_tree.tag_configure("out_of_stock", foreground="#6c757d", font=("Segoe UI", 10, "italic"))
        
        # Alternating row colors
        self.inv_tree.tag_configure('odd_row', background='#F8F9FA')
        self.inv_tree.tag_configure('even_row', background='#FFFFFF')
        
        # Add to Cart Button - Larger and more prominent
        tb.Button(left_panel, text="➕ Add to Cart", bootstyle="success", command=self.add_to_cart, width=25).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 0))
        
        # Double-click to add
        self.inv_tree.bind("<Double-1>", lambda e: self.add_to_cart())

        # --- Right Panel: Cart & Checkout ---
        right_panel = tb.Labelframe(self.frame, text="🛒 Current Sale", padding=20, bootstyle="primary")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(4, weight=1)
        
        # Customer Information Section - Bigger with more fields
        cust_section = tb.Labelframe(right_panel, text="👤 Customer Information", padding=15, bootstyle="info")
        cust_section.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        cust_section.columnconfigure(1, weight=1)
        cust_section.columnconfigure(3, weight=1)
        
        # Row 1: Name and Phone
        tb.Label(cust_section, text="Name:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cust_name = tb.Entry(cust_section, font=("Segoe UI", 11))
        self.cust_name.grid(row=0, column=1, sticky="ew", pady=6)
        # Empty placeholder - no default text
        
        tb.Label(cust_section, text="Phone:", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, sticky="w", padx=(15, 10), pady=6)
        self.cust_phone = tb.Entry(cust_section, font=("Segoe UI", 11))
        self.cust_phone.grid(row=0, column=3, sticky="ew", pady=6)
        self.cust_phone.bind("<KeyRelease>", self.search_customer)
        
        # Row 2: Email and Address
        tb.Label(cust_section, text="Email:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cust_email = tb.Entry(cust_section, font=("Segoe UI", 11))
        self.cust_email.grid(row=1, column=1, sticky="ew", pady=6)
        
        tb.Label(cust_section, text="Address:", font=("Segoe UI", 11, "bold")).grid(row=1, column=2, sticky="w", padx=(15, 10), pady=6)
        self.cust_address = tb.Entry(cust_section, font=("Segoe UI", 11))
        self.cust_address.grid(row=1, column=3, sticky="ew", pady=6)
        
        # Customer Info Display
        self.cust_info_label = tb.Label(cust_section, text="", font=("Segoe UI", 10, "italic"), foreground="#6c757d")
        self.cust_info_label.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
        
        # Barcode Entry - Bigger
        barcode_frame = tb.Frame(right_panel)
        barcode_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        barcode_frame.columnconfigure(1, weight=1)
        
        tb.Label(barcode_frame, text="🔍 Barcode/SKU:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.barcode_entry = tb.Entry(barcode_frame, font=("Segoe UI", 12))
        self.barcode_entry.grid(row=0, column=1, sticky="ew")
        self.barcode_entry.bind("<Return>", self.scan_barcode)
        
        # Sale Info Display - Bigger cards
        sale_info_frame = tb.Frame(right_panel)
        sale_info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        sale_info_frame.columnconfigure(0, weight=1)
        sale_info_frame.columnconfigure(1, weight=1)
        sale_info_frame.columnconfigure(2, weight=1)
        
        # Items Count
        items_card = tb.Frame(sale_info_frame, bootstyle="info", padding=12)
        items_card.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tb.Label(items_card, text="Items", font=("Segoe UI", 10, "bold"), bootstyle="info-inverse").pack()
        self.lbl_items_count = tb.Label(items_card, text="0", font=("Segoe UI", 20, "bold"), bootstyle="info-inverse")
        self.lbl_items_count.pack()
        
        # Total Quantity
        qty_card = tb.Frame(sale_info_frame, bootstyle="warning", padding=12)
        qty_card.grid(row=0, column=1, sticky="ew", padx=8)
        tb.Label(qty_card, text="Quantity", font=("Segoe UI", 10, "bold"), bootstyle="warning-inverse").pack()
        self.lbl_total_qty = tb.Label(qty_card, text="0", font=("Segoe UI", 20, "bold"), bootstyle="warning-inverse")
        self.lbl_total_qty.pack()
        
        # Profit Estimate
        profit_card = tb.Frame(sale_info_frame, bootstyle="secondary", padding=12)
        profit_card.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        tb.Label(profit_card, text="Est. Profit", font=("Segoe UI", 10, "bold"), bootstyle="secondary-inverse").pack()
        self.lbl_profit = tb.Label(profit_card, text="EGP 0", font=("Segoe UI", 20, "bold"), bootstyle="secondary-inverse")
        self.lbl_profit.pack()
        
        # Cart Table - Bigger
        c_cols = ("id", "sku", "name", "qty", "price", "total")
        self.cart_tree = ttk.Treeview(right_panel, columns=c_cols, show="headings", height=15)
        c_widths = {"id":60, "sku":120, "name":300, "qty":80, "price":120, "total":140}
        c_alignments = {"id":"center", "sku":"w", "name":"w", "qty":"center", "price":"e", "total":"e"}
        c_labels = {"id":"ID", "sku":"SKU", "name":"Product", "qty":"Qty", "price":"Unit Price", "total":"Total"}
        
        for c in c_cols:
            self.cart_tree.heading(c, text=c_labels.get(c, c.upper()), anchor="w" if c_alignments[c] == "w" else "center")
            self.cart_tree.column(c, width=c_widths[c], anchor=c_alignments[c])
        
        self.cart_tree.grid(row=4, column=0, sticky="nsew", pady=(0, 15))
        
        # Cart scrollbar
        cart_scroll = ttk.Scrollbar(right_panel, orient="vertical", command=self.cart_tree.yview)
        cart_scroll.grid(row=4, column=1, sticky="ns", pady=(0, 15))
        self.cart_tree.configure(yscrollcommand=cart_scroll.set)
        
        # Alternating row colors for cart
        self.cart_tree.tag_configure('odd_cart', background='#F8F9FA')
        self.cart_tree.tag_configure('even_cart', background='#FFFFFF')
        
        # Summary Section - Bigger
        summary_frame = tb.Labelframe(right_panel, text="💰 Summary", padding=18, bootstyle="success")
        summary_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        # Subtotal
        subtotal_frame = tb.Frame(summary_frame)
        subtotal_frame.pack(fill="x", pady=6)
        tb.Label(subtotal_frame, text="Subtotal:", font=("Segoe UI", 13, "bold")).pack(side="left")
        self.lbl_subtotal = tb.Label(subtotal_frame, text="EGP 0.00", font=("Segoe UI", 13, "bold"))
        self.lbl_subtotal.pack(side="right")
        
        # Discount
        discount_frame = tb.Frame(summary_frame)
        discount_frame.pack(fill="x", pady=6)
        tb.Label(discount_frame, text="Discount:", font=("Segoe UI", 12, "bold")).pack(side="left")
        self.discount_var = tb.StringVar(value="0")
        discount_entry = tb.Entry(discount_frame, textvariable=self.discount_var, width=14, font=("Segoe UI", 12))
        discount_entry.pack(side="right", padx=(10, 0))
        discount_entry.bind("<KeyRelease>", lambda e: self.update_cart_view())
        tb.Label(discount_frame, text="EGP", font=("Segoe UI", 11)).pack(side="right")
        
        # Separator
        ttk.Separator(summary_frame, orient="horizontal").pack(fill="x", pady=10)
        
        # Grand Total
        total_frame = tb.Frame(summary_frame)
        total_frame.pack(fill="x", pady=6)
        tb.Label(total_frame, text="TOTAL:", font=("Segoe UI", 20, "bold")).pack(side="left")
        self.lbl_total = tb.Label(total_frame, text="EGP 0.00", font=("Segoe UI", 26, "bold"), bootstyle="success")
        self.lbl_total.pack(side="right")
        
        # Action Buttons - Reorganized for better UX
        btn_frame = tb.Frame(right_panel)
        btn_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
        
        # Top row - Cart management buttons
        top_btn_row = tb.Frame(btn_frame)
        top_btn_row.pack(fill="x", pady=(0, 8))
        top_btn_row.columnconfigure(0, weight=1)
        top_btn_row.columnconfigure(1, weight=1)
        top_btn_row.columnconfigure(2, weight=1)
        
        tb.Button(top_btn_row, text="✏️ Edit Qty", bootstyle="info", command=self.edit_quantity).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tb.Button(top_btn_row, text="🗑️ Remove", bootstyle="warning", command=self.remove_from_cart).grid(row=0, column=1, sticky="ew", padx=5)
        tb.Button(top_btn_row, text="🧹 Clear Cart", bootstyle="danger", command=self.clear_cart).grid(row=0, column=2, sticky="ew", padx=(5, 0))
        
        # Bottom row - Primary checkout button
        bottom_btn_row = tb.Frame(btn_frame)
        bottom_btn_row.pack(fill="x")
        
        self.checkout_btn = tb.Button(bottom_btn_row, text="✅ CHECKOUT", bootstyle="success", command=self.checkout)
        self.checkout_btn.pack(fill="x", ipady=8)  # Extra padding for prominence

        # Load Data
        self.all_inventory = []
        self.refresh_inventory()

    def refresh_inventory(self):
        try:
            self.all_inventory = InventoryController.get_all_items()
            self.filter_inventory()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_product_details(self, event=None):
        """Display detailed information about selected product"""
        sel = self.inv_tree.selection()
        if not sel:
            self.product_info.configure(text="Select a product to view details")
            return
        
        values = self.inv_tree.item(sel[0])['values']
        item_id = values[0]
        
        # Find full item data
        for row in self.all_inventory:
            if row[0] == item_id:
                # row: id, sku, name, category, qty, buy_price, sell_price
                sku = row[1]
                name = row[2]
                category = row[3]
                stock = int(row[4])
                sell_price = float(row[5])
                
                # Stock status
                if stock == 0:
                    stock_status = "❌ Out of Stock"
                elif stock < 5:
                    stock_status = f"⚠️ Very Low Stock ({stock} units)"
                elif stock < 10:
                    stock_status = f"⚡ Low Stock ({stock} units)"
                else:
                    stock_status = f"✅ In Stock ({stock} units)"
                
                info_text = f"SKU: {sku} | Category: {category} | Price: EGP {sell_price:.2f} | {stock_status}"
                self.product_info.configure(text=info_text)
                break
    
    def search_customer(self, event=None):
        """Search for existing customer by phone number and auto-fill all fields"""
        phone = self.cust_phone.get().strip()
        if not phone or len(phone) < 3:
            self.cust_info_label.configure(text="")
            return
        
        try:
            from modules.models import get_all_customers
            customers = get_all_customers()
            
            # Search for matching phone
            for cust in customers:
                if phone in str(cust[1]):  # cust[1] is phone
                    # Found customer - auto-fill all fields
                    self.cust_name.delete(0, "end")
                    self.cust_name.insert(0, cust[0])  # cust[0] is name
                    
                    # Note: Email and Address not in current database
                    # Will be saved on next purchase
                    
                    order_count = cust[2] if len(cust) > 2 else 0
                    last_visit = cust[3] if len(cust) > 3 else "N/A"
                    
                    self.cust_info_label.configure(
                        text=f"✅ Existing Customer | {order_count} previous orders | Last visit: {last_visit}",
                        foreground="#28a745"
                    )
                    return
            
            # No match found
            self.cust_info_label.configure(text="🆕 New Customer - Please fill in details", foreground="#007bff")
        except Exception as e:
            print(f"Error searching customer: {e}")

    def filter_inventory(self, *args):
        query = self.search_var.get().lower()
        category = self.category_filter.get()
        
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        idx = 0
        for row in self.all_inventory:
            # row: id, sku, name, category, qty, sell_price (6 values)
            if query and query not in str(row[1]).lower() and query not in str(row[2]).lower():
                continue
            
            if category != "All" and str(row[3]) != category:
                continue
            
            # Determine stock tag
            stock = int(row[4]) if row[4] else 0
            if stock == 0:
                stock_tag = "out_of_stock"
            elif stock < 5:
                stock_tag = "very_low"
            elif stock < 10:
                stock_tag = "low_stock"
            else:
                stock_tag = "in_stock"
            
            # Alternating row tag
            row_tag = 'odd_row' if idx % 2 == 0 else 'even_row'
            
            # Display: id, sku, name, category, stock, sell_price
            self.inv_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], stock, f"{row[5]:.2f}"), tags=(stock_tag, row_tag))
            idx += 1

    def scan_barcode(self, event=None):
        """Add item to cart by barcode/SKU"""
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            return
        
        # Find item by SKU
        for row in self.all_inventory:
            if str(row[1]).lower() == barcode.lower():  # Match SKU
                # Add to cart
                self.add_item_to_cart(row)
                self.barcode_entry.delete(0, "end")
                return
        
        messagebox.showwarning("Not Found", f"No item found with SKU/Barcode: {barcode}")
        self.barcode_entry.delete(0, "end")

    def add_to_cart(self):
        sel = self.inv_tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select an item from the list.")
            return
        
        values = self.inv_tree.item(sel[0])['values']
        item_id = values[0]
        
        # Find full item data
        for row in self.all_inventory:
            if row[0] == item_id:
                self.add_item_to_cart(row)
                break

    def add_item_to_cart(self, row):
        """Add item to cart with stock validation"""
        # row: id, sku, name, category, qty, sell_price (6 values)
        item_id = row[0]
        sku = row[1]
        name = row[2]
        category = row[3]
        stock = int(row[4])
        sell_price = float(row[5])
        
        if stock <= 0:
            messagebox.showwarning("Out of Stock", f"{name} is out of stock.")
            return
        
        # Check if item already in cart
        for item in self.cart:
            if item['id'] == item_id:
                if item['qty'] < stock:
                    item['qty'] += 1
                    self.update_cart_view()
                    return
                else:
                    messagebox.showwarning("Stock Limit", f"Cannot add more. Only {stock} in stock.")
                    return
        
        # Add new item to cart
        self.cart.append({
            'id': item_id,
            'sku': sku,
            'name': name,
            'qty': 1,
            'price': sell_price,
            'cost': 0.0,  # Cost not available in current query
            'max_qty': stock
        })
        self.update_cart_view()

    def edit_quantity(self):
        """Edit quantity of selected cart item"""
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select an item from the cart.")
            return
        
        idx = self.cart_tree.index(sel[0])
        item = self.cart[idx]
        
        new_qty = simpledialog.askinteger("Edit Quantity", f"Enter quantity for {item['name']}:", 
                                          initialvalue=item['qty'], minvalue=1, maxvalue=item['max_qty'])
        if new_qty:
            item['qty'] = new_qty
            self.update_cart_view()

    def remove_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = self.cart_tree.index(sel[0])
        del self.cart[idx]
        self.update_cart_view()

    def clear_cart(self):
        if self.cart and messagebox.askyesno("Clear Cart", "Remove all items from cart?"):
            self.cart = []
            self.update_cart_view()

    def update_cart_view(self):
        """Update cart display and calculate totals"""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        subtotal = 0.0
        total_qty = 0
        total_cost = 0.0
        
        for idx, i in enumerate(self.cart):
            line_total = i['qty'] * i['price']
            line_cost = i['qty'] * i['cost']
            subtotal += line_total
            total_qty += i['qty']
            total_cost += line_cost
            
            row_tag = 'odd_cart' if idx % 2 == 0 else 'even_cart'
            self.cart_tree.insert("", "end", values=(i['id'], i['sku'], i['name'], i['qty'], f"{i['price']:.2f}", f"{line_total:.2f}"), tags=(row_tag,))
        
        # Calculate discount
        try:
            discount = float(self.discount_var.get() or 0)
        except:
            discount = 0.0
            self.discount_var.set("0")
        
        # Calculate total (no tax)
        grand_total = subtotal - discount
        
        # Calculate estimated profit
        profit = grand_total - total_cost
        
        # Update sale info cards
        self.lbl_items_count.configure(text=str(len(self.cart)))
        self.lbl_total_qty.configure(text=str(total_qty))
        self.lbl_profit.configure(text=f"EGP {profit:.0f}")
        
        # Update summary labels
        self.lbl_subtotal.configure(text=f"EGP {subtotal:,.2f}")
        self.lbl_total.configure(text=f"EGP {grand_total:,.2f}")
        
        # Enable/disable checkout button based on cart contents
        if self.cart:
            self.checkout_btn.configure(state="normal")
        else:
            self.checkout_btn.configure(state="disabled")

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items to cart first.")
            return
        
        # Get customer information
        cust_name = self.cust_name.get().strip()
        cust_phone = self.cust_phone.get().strip()
        cust_email = self.cust_email.get().strip()
        cust_address = self.cust_address.get().strip()
        
        # Validate at least name or phone
        if not cust_name and not cust_phone:
            if not messagebox.askyesno("No Customer Info", "No customer information provided.\n\nProceed with anonymous sale?"):
                return
            cust_name = "Walk-in Customer"
        
        # Prepare items for DB: (item_id, qty, unit_price, cost_price)
        db_items = [(i['id'], i['qty'], i['price'], i['cost']) for i in self.cart]
        
        try:
            # Pass all customer data to controller
            sale_id = POSController.create_sale(
                customer_name=cust_name,
                items=db_items,
                customer_phone=cust_phone,
                customer_email=cust_email,
                customer_address=cust_address
            )
            if sale_id:
                messagebox.showinfo("Success", f"✅ Sale #{sale_id} completed successfully!")
                
                # Generate Receipt
                try:
                    from modules.reports.receipt_generator import generate_sales_receipt_pdf
                    
                    # Calculate totals (no tax)
                    subtotal = sum([i['qty']*i['price'] for i in self.cart])
                    try:
                        discount = float(self.discount_var.get() or 0)
                    except:
                        discount = 0.0
                    
                    grand_total = subtotal - discount
                    
                    # Items for receipt: (name, qty, price, total)
                    receipt_items = [(i['name'], i['qty'], i['price'], i['qty']*i['price']) for i in self.cart]
                    
                    # Sale tuple: (sale_id, date, cust_name, subtotal, discount, total)
                    sale_data = (sale_id, datetime.now().isoformat()[:16], cust_name, subtotal, discount, grand_total)
                    
                    pdf_path = generate_sales_receipt_pdf(sale_data, receipt_items)
                    
                    # Auto-open
                    try:
                        os.startfile(pdf_path)
                    except:
                        messagebox.showinfo("Receipt", f"Receipt saved to:\n{pdf_path}")
                        
                except Exception as e:
                    messagebox.showerror("Receipt Error", f"Could not generate receipt: {e}")

                # Reset all fields
                self.cart = []
                self.discount_var.set("0")
                self.cust_name.delete(0, "end")
                self.cust_phone.delete(0, "end")
                self.cust_email.delete(0, "end")
                self.cust_address.delete(0, "end")
                self.cust_info_label.configure(text="")
                self.product_info.configure(text="Select a product to view details")
                self.update_cart_view()
                self.refresh_inventory()
            else:
                messagebox.showerror("Failed", "Could not record sale.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
