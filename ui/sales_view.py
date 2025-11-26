# -*- coding: utf-8 -*-
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
        self.frame = tb.Frame(parent, padding=20)
        self.cart = []  # list of dicts: {id, sku, name, qty, price, cost, max_qty}
        
        # Callback for when sale completes (to notify other views)
        self.on_sale_complete = None
        
        # Simple 2-column layout
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # --- LEFT PANEL: Product Selection ---
        left_panel = tb.Frame(self.frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(3, weight=1)
        
        # Title
        tb.Label(left_panel, text="📦 Product Selection", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Search
        search_frame = tb.Frame(left_panel)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        tb.Label(search_frame, text="Search:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.search_var = tb.StringVar()
        self.search_var.trace("w", self.filter_inventory)
        tb.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11)).grid(row=0, column=1, sticky="ew")
        
        # Category filter
        filter_frame = tb.Frame(left_panel)
        filter_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Import categories from constants for consistency
        from modules.constants import PRODUCT_CATEGORIES
        
        tb.Label(filter_frame, text="Category:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        self.category_filter = tb.Combobox(filter_frame, values=["All"] + PRODUCT_CATEGORIES, state="readonly", width=20, font=("Segoe UI", 10))
        self.category_filter.set("All")
        self.category_filter.pack(side="left")
        self.category_filter.bind("<<ComboboxSelected>>", self.filter_inventory)
        
        # Inventory table
        inv_frame = tb.Frame(left_panel)
        inv_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        inv_frame.columnconfigure(0, weight=1)
        inv_frame.rowconfigure(0, weight=1)
        
        cols = ("id", "sku", "name", "stock", "price")
        self.inv_tree = ttk.Treeview(inv_frame, columns=cols, show="headings", height=20)
        
        # Center-align all headers
        self.inv_tree.heading("id", text="ID", anchor="center")
        self.inv_tree.heading("sku", text="SKU", anchor="center")
        self.inv_tree.heading("name", text="Product Name", anchor="center")
        self.inv_tree.heading("stock", text="Stock", anchor="center")
        self.inv_tree.heading("price", text="Price", anchor="center")
        
        # Center-align all columns with adjusted widths
        self.inv_tree.column("id", width=50, anchor="center")
        self.inv_tree.column("sku", width=120, anchor="center")
        self.inv_tree.column("name", width=200, anchor="center")  # Reduced from 250
        self.inv_tree.column("stock", width=150, anchor="center")  # Increased from 80
        self.inv_tree.column("price", width=120, anchor="center")
        
        self.inv_tree.grid(row=0, column=0, sticky="nsew")
        
        inv_scroll = ttk.Scrollbar(inv_frame, orient="vertical", command=self.inv_tree.yview)
        inv_scroll.grid(row=0, column=1, sticky="ns")
        self.inv_tree.configure(yscrollcommand=inv_scroll.set)
        
        # Stock color tags
        self.inv_tree.tag_configure("in_stock", foreground="#28a745")
        self.inv_tree.tag_configure("low_stock", foreground="#fd7e14", font=("Segoe UI", 10, "bold"))
        self.inv_tree.tag_configure("out_of_stock", foreground="#dc3545", font=("Segoe UI", 10, "bold"))
        
        # Add button
        tb.Button(left_panel, text="➕ Add to Cart", bootstyle="success", command=self.add_to_cart).grid(row=4, column=0, sticky="ew")
        
        # Double-click to add
        self.inv_tree.bind("<Double-1>", lambda e: self.add_to_cart())
        
        # --- RIGHT PANEL: Cart & Checkout ---
        right_panel = tb.Frame(self.frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(3, weight=1)  # Cart table row gets ALL the space
        
        # Title
        tb.Label(right_panel, text="🛒 Current Sale", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Customer Information - ENLARGED 2-ROW LAYOUT
        cust_frame = tb.Labelframe(right_panel, text="Customer Information", padding=12)
        cust_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        cust_frame.columnconfigure(1, weight=1)
        cust_frame.columnconfigure(3, weight=1)
        
        # Row 1: Name (required) and Phone
        tb.Label(cust_frame, text="Name:*", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cust_name = tb.Entry(cust_frame, font=("Segoe UI", 11))
        self.cust_name.grid(row=0, column=1, sticky="ew", pady=6)
        
        tb.Label(cust_frame, text="Phone:", font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", padx=(20, 10), pady=6)
        self.cust_phone = tb.Entry(cust_frame, font=("Segoe UI", 11))
        self.cust_phone.grid(row=0, column=3, sticky="ew", pady=6)
        self.cust_phone.bind("<KeyRelease>", self.search_customer)
        
        # Row 2: Email and Address (both optional)
        tb.Label(cust_frame, text="Email:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cust_email = tb.Entry(cust_frame, font=("Segoe UI", 11))
        self.cust_email.grid(row=1, column=1, sticky="ew", pady=6)
        
        tb.Label(cust_frame, text="Address:", font=("Segoe UI", 10)).grid(row=1, column=2, sticky="w", padx=(20, 10), pady=6)
        self.cust_address = tb.Entry(cust_frame, font=("Segoe UI", 11))
        self.cust_address.grid(row=1, column=3, sticky="ew", pady=6)
        
        # Customer info display with clear button
        cust_info_container = tb.Frame(cust_frame)
        cust_info_container.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(5, 0))
        cust_info_container.columnconfigure(0, weight=1)
        
        self.cust_info_label = tb.Label(cust_info_container, text="", font=("Segoe UI", 9, "italic"), foreground="#6c757d")
        self.cust_info_label.grid(row=0, column=0, sticky="w")
        
        self.clear_customer_btn = tb.Button(cust_info_container, text="❌ Clear", bootstyle="danger-outline", command=self.clear_customer_data)
        # Don't grid yet - show when customer found
        
        # Track last found phone
        self._last_found_phone = None
        
        # Sale info cards
        info_frame = tb.Frame(right_panel)
        info_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(2, weight=1)
        
        items_card = tb.Frame(info_frame, bootstyle="info", padding=5)
        items_card.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        tb.Label(items_card, text="Items", font=("Segoe UI", 8, "bold"), bootstyle="info-inverse").pack()
        self.lbl_items_count = tb.Label(items_card, text="0", font=("Segoe UI", 11, "bold"), bootstyle="info-inverse")
        self.lbl_items_count.pack()
        
        qty_card = tb.Frame(info_frame, bootstyle="warning", padding=5)
        qty_card.grid(row=0, column=1, sticky="ew", padx=3)
        tb.Label(qty_card, text="Qty", font=("Segoe UI", 8, "bold"), bootstyle="warning-inverse").pack()
        self.lbl_total_qty = tb.Label(qty_card, text="0", font=("Segoe UI", 11, "bold"), bootstyle="warning-inverse")
        self.lbl_total_qty.pack()
        
        profit_card = tb.Frame(info_frame, bootstyle="secondary", padding=5)
        profit_card.grid(row=0, column=2, sticky="ew", padx=(3, 0))
        tb.Label(profit_card, text="Profit", font=("Segoe UI", 8, "bold"), bootstyle="secondary-inverse").pack()
        self.lbl_profit = tb.Label(profit_card, text="EGP 0", font=("Segoe UI", 11, "bold"), bootstyle="secondary-inverse")
        self.lbl_profit.pack()
        
        # Cart table - MASSIVELY ENLARGED - TAKES UP MOST OF THE SPACE
        cart_frame = tb.Labelframe(right_panel, text="🛒 Cart Items", padding=15, bootstyle="primary")
        cart_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 8))
        cart_frame.columnconfigure(0, weight=1)
        cart_frame.rowconfigure(0, weight=1)
        
        c_cols = ("sku", "name", "qty", "stock", "price", "total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=c_cols, show="headings", height=25)  # MUCH LARGER HEIGHT
        
        # Center-align all headers for consistency
        self.cart_tree.heading("sku", text="SKU", anchor="center")
        self.cart_tree.heading("name", text="Product Name", anchor="center")
        self.cart_tree.heading("qty", text="Qty", anchor="center")
        self.cart_tree.heading("stock", text="Available", anchor="center")
        self.cart_tree.heading("price", text="Unit Price", anchor="center")
        self.cart_tree.heading("total", text="Line Total", anchor="center")
        
        # Center-align all columns with wider spacing
        self.cart_tree.column("sku", width=140, anchor="center", minwidth=120)
        self.cart_tree.column("name", width=300, anchor="center", minwidth=250)
        self.cart_tree.column("qty", width=90, anchor="center", minwidth=80)
        self.cart_tree.column("stock", width=120, anchor="center", minwidth=100)
        self.cart_tree.column("price", width=130, anchor="center", minwidth=110)
        self.cart_tree.column("total", width=150, anchor="center", minwidth=130)
        
        # Enhanced style for cart tree - MUCH MORE COMFORTABLE AND VISUAL
        style = ttk.Style()
        style.configure("Treeview", 
                       rowheight=42,  # Increased from 35 to 42 for better spacing
                       font=("Segoe UI", 13),  # Larger font
                       background="#FFFFFF",
                       fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading", 
                       font=("Segoe UI", 13, "bold"),  # Larger header font
                       padding=12)  # More padding
        style.map("Treeview", background=[("selected", "#0078D7")])
        
        # Add alternating row colors for better readability
        self.cart_tree.tag_configure('oddrow', background='#F8F9FA')
        self.cart_tree.tag_configure('evenrow', background='#FFFFFF')
        
        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        
        cart_scroll = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_tree.yview)
        cart_scroll.grid(row=0, column=1, sticky="ns")
        self.cart_tree.configure(yscrollcommand=cart_scroll.set)
        
        # Cart buttons
        cart_btn_frame = tb.Frame(right_panel)
        cart_btn_frame.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        cart_btn_frame.columnconfigure(0, weight=1)
        cart_btn_frame.columnconfigure(1, weight=1)
        cart_btn_frame.columnconfigure(2, weight=1)
        
        tb.Button(cart_btn_frame, text="Edit Qty", bootstyle="info-outline", command=self.edit_quantity).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tb.Button(cart_btn_frame, text="Remove", bootstyle="warning-outline", command=self.remove_from_cart).grid(row=0, column=1, sticky="ew", padx=5)
        tb.Button(cart_btn_frame, text="Clear Cart", bootstyle="danger-outline", command=self.clear_cart).grid(row=0, column=2, sticky="ew", padx=(5, 0))
        
        # Summary - COMPACT
        summary_frame = tb.Labelframe(right_panel, text="Summary", padding=10)
        summary_frame.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        
        # Compact summary layout
        summary_grid = tb.Frame(summary_frame)
        summary_grid.pack(fill="x")
        summary_grid.columnconfigure(1, weight=1)
        summary_grid.columnconfigure(3, weight=1)
        
        # Row 1: Subtotal and Discount
        tb.Label(summary_grid, text="Subtotal:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=3)
        self.lbl_subtotal = tb.Label(summary_grid, text="EGP 0.00", font=("Segoe UI", 10, "bold"))
        self.lbl_subtotal.grid(row=0, column=1, sticky="e", pady=3)
        
        tb.Label(summary_grid, text="Discount %:", font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", padx=(15, 5), pady=3)
        self.discount_var = tb.StringVar(value="")
        discount_entry = tb.Entry(summary_grid, textvariable=self.discount_var, width=6, font=("Segoe UI", 10))
        discount_entry.grid(row=0, column=3, sticky="e", pady=3)
        self.discount_var.trace("w", lambda *args: self.update_cart_view())
        
        # Row 2: Payment and Notes
        tb.Label(summary_grid, text="Payment:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=3)
        self.payment_method_var = tb.StringVar(value="Cash")
        from modules.constants import PAYMENT_METHODS
        payment_combo = tb.Combobox(
            summary_grid,
            textvariable=self.payment_method_var,
            values=PAYMENT_METHODS,
            state="readonly",
            width=12,
            font=("Segoe UI", 9)
        )
        payment_combo.grid(row=1, column=1, sticky="ew", pady=3)
        
        tb.Label(summary_grid, text="Notes:", font=("Segoe UI", 10)).grid(row=1, column=2, sticky="w", padx=(15, 5), pady=3)
        self.notes_text = tb.Entry(summary_grid, font=("Segoe UI", 9))
        self.notes_text.grid(row=1, column=3, sticky="ew", pady=3)
        self.notes_text.insert(0, "Optional...")
        self.notes_text.config(foreground='#999999')
        
        def on_notes_focus_in(event):
            if self.notes_text.get() == "Optional...":
                self.notes_text.delete(0, "end")
                self.notes_text.config(foreground='#000000')
        
        def on_notes_focus_out(event):
            if not self.notes_text.get().strip():
                self.notes_text.insert(0, "Optional...")
                self.notes_text.config(foreground='#999999')
        
        self.notes_text.bind('<FocusIn>', on_notes_focus_in)
        self.notes_text.bind('<FocusOut>', on_notes_focus_out)
        
        # Total - PROMINENT
        ttk.Separator(summary_frame, orient="horizontal").pack(fill="x", pady=8)
        total_row = tb.Frame(summary_frame)
        total_row.pack(fill="x")
        tb.Label(total_row, text="TOTAL:", font=("Segoe UI", 13, "bold")).pack(side="left")
        self.lbl_total = tb.Label(total_row, text="EGP 0.00", font=("Segoe UI", 16, "bold"), bootstyle="success")
        self.lbl_total.pack(side="right")
        
        # Checkout button - LARGER
        self.checkout_btn = tb.Button(right_panel, text="✅ CHECKOUT", bootstyle="success", command=self.checkout, padding=12)
        self.checkout_btn.grid(row=6, column=0, sticky="ew")
        
        # Load inventory
        self.all_inventory = []
        self.refresh_inventory()

    def refresh_inventory(self):
        try:
            self.all_inventory = InventoryController.get_all_items()
            self.filter_inventory()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def filter_inventory(self, *args):
        """Filter inventory and show AVAILABLE stock (accounting for items in cart)"""
        query = self.search_var.get().lower()
        category = self.category_filter.get()
        
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        for row in self.all_inventory:
            # row: id, sku, name, category, qty, buy_price, sell_price
            if query and query not in str(row[1]).lower() and query not in str(row[2]).lower():
                continue
            
            if category != "All" and str(row[3]) != category:
                continue
            
            item_id = row[0]
            stock = int(row[4]) if row[4] else 0
            sell_price = float(row[6])
            
            # Calculate available stock (subtract quantity in cart)
            qty_in_cart = 0
            for cart_item in self.cart:
                if cart_item['id'] == item_id:
                    qty_in_cart = cart_item['qty']
                    break
            
            available_stock = stock - qty_in_cart
            
            # Determine stock display and tag based on AVAILABLE stock
            if available_stock <= 0:
                stock_display = f"❌ OUT ({qty_in_cart} in cart)"
                tag = "out_of_stock"
            elif available_stock < 5:
                stock_display = f"⚠️ {available_stock}" + (f" ({qty_in_cart} in cart)" if qty_in_cart > 0 else "")
                tag = "low_stock"
            else:
                stock_display = f"✓ {available_stock}" + (f" ({qty_in_cart} in cart)" if qty_in_cart > 0 else "")
                tag = "in_stock"
            
            self.inv_tree.insert("", "end", values=(row[0], row[1], row[2], stock_display, f"{sell_price:.2f}"), tags=(tag,))

    def clear_customer_data(self):
        """Clear customer fields except phone"""
        self.cust_name.delete(0, "end")
        self.cust_email.delete(0, "end")
        self.cust_address.delete(0, "end")
        self.cust_info_label.configure(text="")
        self.clear_customer_btn.grid_forget()
        self.cust_name.focus()
    
    def search_customer(self, event=None):
        """Search for existing customer by phone number and auto-fill - ENHANCED AUTO-COMPLETE"""
        phone = self.cust_phone.get().strip()
        
        # Clear fields if phone changed from last found customer
        if hasattr(self, '_last_found_phone') and self._last_found_phone and phone != self._last_found_phone:
            # Only clear if user is typing a different number
            if not phone.startswith(self._last_found_phone[:len(phone)]):
                self.cust_name.delete(0, "end")
                self.cust_email.delete(0, "end")
                self.cust_address.delete(0, "end")
                self.cust_info_label.configure(text="")
                self.clear_customer_btn.grid_forget()
                self._last_found_phone = None
        
        if not phone or len(phone) < 3:
            if not hasattr(self, '_last_found_phone') or not self._last_found_phone:
                self.cust_info_label.configure(text="")
                self.clear_customer_btn.grid_forget()
            return
        
        try:
            from modules.models import search_customer_by_phone
            customer = search_customer_by_phone(phone)
            
            if customer:
                full_phone = customer[2] or ""
                name = customer[1] or ""
                email = customer[3] or ""
                address = customer[4] or ""
                total_spent = customer[8] or 0.0
                
                # Auto-complete phone number if partial match
                if full_phone and phone != full_phone and full_phone.startswith(phone):
                    # Save cursor position
                    cursor_pos = len(phone)
                    # Complete the phone number
                    self.cust_phone.delete(0, "end")
                    self.cust_phone.insert(0, full_phone)
                    # Select the auto-completed part
                    self.cust_phone.select_range(cursor_pos, "end")
                    self.cust_phone.icursor(cursor_pos)
                
                # Auto-fill other fields
                self.cust_name.delete(0, "end")
                self.cust_name.insert(0, name)
                
                self.cust_email.delete(0, "end")
                if email:
                    self.cust_email.insert(0, email)
                
                self.cust_address.delete(0, "end")
                if address:
                    self.cust_address.insert(0, address)
                
                self._last_found_phone = full_phone
                self.cust_info_label.configure(text=f"✅ Existing customer | Total spent: EGP {total_spent:,.0f}", foreground="#28a745")
                self.clear_customer_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))
            else:
                # Only clear if we had a previous match
                if hasattr(self, '_last_found_phone') and self._last_found_phone:
                    self.cust_info_label.configure(text="🆕 New customer", foreground="#007bff")
                    self.clear_customer_btn.grid_forget()
                    self._last_found_phone = None
        except Exception as e:
            print(f"Error searching customer: {e}")
    


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
        """Add item to cart - ENFORCE STOCK LIMITS"""
        # row: id, sku, name, category, qty, buy_price, sell_price
        item_id = row[0]
        sku = row[1]
        name = row[2]
        category = row[3] if len(row) > 3 else "Unknown"
        stock = int(row[4])
        buy_price = float(row[5])
        sell_price = float(row[6])
        
        # Check stock availability
        if stock <= 0:
            messagebox.showwarning(
                "❌ Out of Stock",
                f"'{name}' is currently out of stock.\n\nCannot add to cart."
            )
            return
        
        # Check if item already in cart
        for item in self.cart:
            if item['id'] == item_id:
                # Check if we can add one more
                if item['qty'] >= stock:
                    messagebox.showwarning(
                        "⚠️ Stock Limit Reached",
                        f"Cannot add more '{name}'.\n\n"
                        f"Available stock: {stock}\n"
                        f"Already in cart: {item['qty']}"
                    )
                    return
                item['qty'] += 1
                self.update_cart_view()
                self.refresh_inventory()  # Update product list to show reduced available stock
                return
        
        # Add new item to cart with category
        self.cart.append({
            'id': item_id,
            'sku': sku,
            'name': name,
            'category': category,
            'qty': 1,
            'price': sell_price,
            'cost': buy_price,
            'max_qty': stock
        })
        self.update_cart_view()
        self.refresh_inventory()  # Update product list to show reduced available stock

    def edit_quantity(self):
        """Edit quantity of selected cart item - ENFORCE STOCK LIMITS"""
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an item from the cart.")
            return
        
        try:
            idx = self.cart_tree.index(sel[0])
            item = self.cart[idx]
            
            new_qty = simpledialog.askinteger(
                "Edit Quantity", 
                f"Enter new quantity for:\n{item['name']}\n\n"
                f"Available stock: {item['max_qty']}", 
                initialvalue=item['qty'], 
                minvalue=1,
                maxvalue=item['max_qty']
            )
            
            if new_qty and new_qty != item['qty']:
                item['qty'] = new_qty
                self.update_cart_view()
                self.refresh_inventory()  # Update product list
        except Exception as e:
            messagebox.showerror("Error", f"Could not edit quantity: {e}")

    def remove_from_cart(self):
        """Remove selected item from cart - UPDATE PRODUCT LIST"""
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an item from the cart.")
            return
        
        try:
            idx = self.cart_tree.index(sel[0])
            del self.cart[idx]
            self.update_cart_view()
            self.refresh_inventory()  # Update product list to show stock is available again
        except Exception as e:
            messagebox.showerror("Error", f"Could not remove item: {e}")

    def clear_cart(self):
        """Clear all items from cart - UPDATE PRODUCT LIST"""
        if not self.cart:
            messagebox.showinfo("Empty Cart", "Cart is already empty.")
            return
        
        if messagebox.askyesno("Clear Cart", f"Remove all {len(self.cart)} items from cart?"):
            self.cart = []
            self.update_cart_view()
            self.refresh_inventory()  # Update product list to show all stock available again

    def update_cart_view(self):
        """Update cart display and calculate totals - SHOW AVAILABLE STOCK"""
        # Clear cart tree
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        print(f"DEBUG: Updating cart with {len(self.cart)} items")
        
        subtotal = 0.0
        total_qty = 0
        total_cost = 0.0
        
        # Add items to cart tree with available stock info and alternating colors
        for idx, item in enumerate(self.cart):
            line_total = item['qty'] * item['price']
            line_cost = item['qty'] * item['cost']
            subtotal += line_total
            total_qty += item['qty']
            total_cost += line_cost
            
            # Calculate remaining available stock (max_qty - qty in cart)
            available_stock = item['max_qty'] - item['qty']
            stock_display = f"{available_stock} left"
            
            values = (
                item['sku'], 
                item['name'], 
                item['qty'], 
                stock_display,
                f"{item['price']:.2f}",  # Removed EGP prefix for cleaner look
                f"{line_total:.2f}"  # Removed EGP prefix for cleaner look
            )
            
            # Alternate row colors for better visual separation
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            print(f"DEBUG: Inserting cart item: {values}")
            self.cart_tree.insert("", "end", values=values, tags=(tag,))
        
        print(f"DEBUG: Cart tree now has {len(self.cart_tree.get_children())} rows")
        
        # Calculate discount - handle empty or placeholder
        try:
            discount_str = self.discount_var.get().strip()
            # Treat empty or "0" placeholder as 0%
            if not discount_str or discount_str == "0":
                discount_pct = 0.0
            else:
                discount_pct = float(discount_str)
                discount_pct = max(0, min(100, discount_pct))
        except:
            discount_pct = 0.0
        
        discount_amount = (subtotal * discount_pct) / 100
        grand_total = subtotal - discount_amount
        profit = grand_total - total_cost
        
        # Update info cards
        self.lbl_items_count.configure(text=str(len(self.cart)))
        self.lbl_total_qty.configure(text=str(total_qty))
        self.lbl_profit.configure(text=f"EGP {profit:.0f}")
        
        # Update summary labels
        self.lbl_subtotal.configure(text=f"EGP {subtotal:,.2f}")
        self.lbl_total.configure(text=f"EGP {grand_total:,.2f}")
        
        # Enable/disable checkout
        if self.cart:
            self.checkout_btn.configure(state="normal")
        else:
            self.checkout_btn.configure(state="disabled")
        
        # Force update
        self.cart_tree.update_idletasks()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items to cart first.")
            return
        
        cust_name = self.cust_name.get().strip()
        cust_phone = self.cust_phone.get().strip()
        cust_email = self.cust_email.get().strip()
        cust_address = self.cust_address.get().strip()
        
        # Validate required fields
        if not cust_name:
            messagebox.showwarning("Customer Name Required", "Please enter customer name.")
            self.cust_name.focus()
            return
        
        # Email and Address are now optional - no validation needed
        
        # Calculate discount
        try:
            discount_str = self.discount_var.get().strip()
            discount_pct = float(discount_str) if discount_str and discount_str != "0" else 0.0
        except:
            discount_pct = 0.0
        
        # Get payment method
        payment_method = self.payment_method_var.get()
        
        # Get notes (check if it's placeholder)
        notes = self.notes_text.get().strip()
        if notes == "Optional..." or not notes:
            notes = None
        
        # Prepare items with full details for comprehensive tracking
        items_detailed = self.cart  # Already has all details: id, sku, name, category, qty, price, cost
        
        try:
            sale_id = POSController.create_sale(
                customer_name=cust_name,
                items=items_detailed,
                customer_phone=cust_phone or None,
                customer_email=cust_email,  # Now mandatory
                customer_address=cust_address,  # Now mandatory
                seller_name="Cashier",  # TODO: Get from logged-in user
                discount_percent=discount_pct,
                payment_method=payment_method,  # User-selected payment method
                notes=notes  # Sale notes
            )
            
            if sale_id:
                # Calculate totals for receipt
                subtotal = sum([i['qty']*i['price'] for i in self.cart])
                try:
                    discount_str = self.discount_var.get().strip()
                    discount_pct = float(discount_str) if discount_str and discount_str != "0" else 0.0
                except:
                    discount_pct = 0.0
                
                discount_amount = (subtotal * discount_pct) / 100
                grand_total = subtotal - discount_amount
                
                # Store sale data for receipt with MORE details
                receipt_items = [(i['sku'], i['name'], i['qty'], i['price'], i['qty']*i['price']) for i in self.cart]
                sale_data = {
                    'sale_id': sale_id,
                    'date_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'customer_name': cust_name,
                    'customer_phone': cust_phone,
                    'customer_email': cust_email,
                    'customer_address': cust_address,
                    'subtotal': subtotal,
                    'discount_percent': discount_pct,
                    'discount_amount': discount_amount,
                    'grand_total': grand_total,
                    'payment_method': payment_method,
                    'notes': notes
                }
                
                # Reset cart and form BEFORE showing success dialog
                cart_copy = self.cart.copy()
                self.cart = []
                self.discount_var.set("")
                self.cust_name.delete(0, "end")
                self.cust_phone.delete(0, "end")
                self.cust_email.delete(0, "end")
                self.cust_address.delete(0, "end")
                self.cust_info_label.configure(text="")
                self.clear_customer_btn.grid_forget()
                self._last_found_phone = None
                
                # Clear notes
                self.notes_text.delete(0, "end")
                self.notes_text.insert(0, "Optional...")
                self.notes_text.config(foreground='#999999')
                
                self.update_cart_view()
                self.refresh_inventory()
                
                # Show success dialog with print button
                self.show_sale_success_dialog(sale_data, receipt_items)
                
                # Notify ALL views that sale completed
                from modules.event_manager import event_manager
                event_manager.notify('sale_completed', {'sale_id': sale_id, 'customer': cust_name, 'total': grand_total})
            else:
                messagebox.showerror("Failed", "Could not record sale.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_sale_success_dialog(self, sale_data, receipt_items):
        """Show professional success dialog with detailed information and print receipt button"""
        # Create success dialog - MAXIMIZE HEIGHT
        dialog = tb.Toplevel(self.frame)
        dialog.title("✓ Sale Completed Successfully")
        
        # Get screen height and make dialog 90% of screen height
        screen_height = dialog.winfo_screenheight()
        dialog_height = int(screen_height * 0.9)
        dialog_width = 900
        
        dialog.geometry(f"{dialog_width}x{dialog_height}")
        dialog.resizable(True, True)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog_width // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Make dialog modal
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # === PRINT BUTTON FUNCTIONS - DEFINE FIRST ===
        def print_receipt():
            """Generate and print receipt"""
            try:
                from modules.reports.receipt_generator import generate_sales_receipt_pdf
                pdf_path = generate_sales_receipt_pdf(sale_data, receipt_items)
                
                try:
                    os.startfile(pdf_path)
                    messagebox.showinfo("Receipt Generated", f"✓ Receipt opened!\n\nSaved to:\n{pdf_path}")
                except:
                    messagebox.showinfo("Receipt Saved", f"✓ Receipt saved!\n\nLocation:\n{pdf_path}")
            except Exception as e:
                messagebox.showerror("Receipt Error", f"Could not generate receipt:\n{str(e)}")
        
        def close_dialog():
            dialog.destroy()
        
        # Success header - COMPACT
        header = tb.Frame(dialog, bootstyle="success", padding=15)
        header.pack(fill="x")
        
        # Success icon and message - SMALLER
        header_content = tb.Frame(header, bootstyle="success")
        header_content.pack()
        
        tb.Label(
            header_content,
            text="✓",
            font=("Segoe UI", 40, "bold"),
            bootstyle="success-inverse"
        ).pack(side="left", padx=(0, 15))
        
        header_text = tb.Frame(header_content, bootstyle="success")
        header_text.pack(side="left")
        
        tb.Label(
            header_text,
            text="Sale Completed Successfully!",
            font=("Segoe UI", 18, "bold"),
            bootstyle="success-inverse"
        ).pack(anchor="w")
        
        tb.Label(
            header_text,
            text="Transaction recorded in the system",
            font=("Segoe UI", 10),
            bootstyle="success-inverse"
        ).pack(anchor="w")
        
        # Scrollable content area - BETWEEN header and buttons
        content_container = tb.Frame(dialog)
        content_container.pack(fill="both", expand=True, pady=(0, 0))
        
        # Create canvas for scrolling
        canvas = tb.Canvas(content_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
        details_frame = tb.Frame(canvas, padding=25)
        
        details_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=details_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Make canvas expand to fill width
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        def bind_to_mousewheel(widget):
            try:
                widget.bind("<MouseWheel>", on_mousewheel)
                widget.bind("<Button-4>", on_mousewheel)
                widget.bind("<Button-5>", on_mousewheel)
            except:
                pass
            for child in widget.winfo_children():
                bind_to_mousewheel(child)
        
        def unbind_from_mousewheel(widget):
            try:
                widget.unbind("<MouseWheel>")
                widget.unbind("<Button-4>")
                widget.unbind("<Button-5>")
            except:
                pass
            for child in widget.winfo_children():
                unbind_from_mousewheel(child)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Sale information card
        info_frame = tb.Labelframe(
            details_frame, 
            text="  📋 Sale Information  ", 
            padding=20,
            bootstyle="info"
        )
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_grid = tb.Frame(info_frame)
        info_grid.pack(fill="x")
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
        
        # Sale ID with styling
        id_frame = tb.Frame(info_grid)
        id_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))
        
        tb.Label(
            id_frame,
            text="Sale ID:",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")
        
        tb.Label(
            id_frame,
            text=f"#{sale_data['sale_id']}",
            font=("Segoe UI", 20, "bold"),
            bootstyle="info"
        ).pack(side="left", padx=(10, 0))
        
        ttk.Separator(info_grid, orient="horizontal").grid(row=1, column=0, columnspan=4, sticky="ew", pady=12)
        
        # Row 1: Date/Time and Payment Method
        tb.Label(info_grid, text="📅 Date/Time:", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w", pady=6)
        tb.Label(info_grid, text=sale_data['date_time'], font=("Segoe UI", 11)).grid(row=2, column=1, sticky="w", padx=(10, 20), pady=6)
        
        tb.Label(info_grid, text="💳 Payment:", font=("Segoe UI", 11, "bold")).grid(row=2, column=2, sticky="w", pady=6)
        tb.Label(info_grid, text=sale_data['payment_method'], font=("Segoe UI", 11)).grid(row=2, column=3, sticky="w", padx=(10, 0), pady=6)
        
        # Customer Details Card
        cust_frame = tb.Labelframe(
            details_frame,
            text="  👤 Customer Details  ",
            padding=20,
            bootstyle="primary"
        )
        cust_frame.pack(fill="x", pady=(0, 15))
        
        cust_grid = tb.Frame(cust_frame)
        cust_grid.pack(fill="x")
        cust_grid.columnconfigure(1, weight=1)
        cust_grid.columnconfigure(3, weight=1)
        
        # Customer Name
        tb.Label(cust_grid, text="Name:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        tb.Label(cust_grid, text=sale_data['customer_name'], font=("Segoe UI", 12, "bold"), bootstyle="primary").grid(row=0, column=1, sticky="w", padx=(10, 20), pady=6)
        
        # Phone
        tb.Label(cust_grid, text="Phone:", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, sticky="w", pady=6)
        tb.Label(cust_grid, text=sale_data['customer_phone'] or "N/A", font=("Segoe UI", 11)).grid(row=0, column=3, sticky="w", padx=(10, 0), pady=6)
        
        # Email
        if sale_data['customer_email']:
            tb.Label(cust_grid, text="Email:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", pady=6)
            tb.Label(cust_grid, text=sale_data['customer_email'], font=("Segoe UI", 11)).grid(row=1, column=1, columnspan=3, sticky="w", padx=(10, 0), pady=6)
        
        # Address
        if sale_data['customer_address']:
            tb.Label(cust_grid, text="Address:", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w", pady=6)
            tb.Label(cust_grid, text=sale_data['customer_address'], font=("Segoe UI", 11), wraplength=600).grid(row=2, column=1, columnspan=3, sticky="w", padx=(10, 0), pady=6)
        
        # Products Purchased - Detailed Table
        products_frame = tb.Labelframe(
            details_frame,
            text="  📦 Products Purchased  ",
            padding=15,
            bootstyle="secondary"
        )
        products_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Create table for products
        prod_cols = ("sku", "name", "qty", "price", "total")
        prod_tree = ttk.Treeview(products_frame, columns=prod_cols, show="headings", height=8)
        
        # Configure headers
        prod_tree.heading("sku", text="SKU", anchor="center")
        prod_tree.heading("name", text="Product Name", anchor="center")
        prod_tree.heading("qty", text="Qty", anchor="center")
        prod_tree.heading("price", text="Unit Price", anchor="center")
        prod_tree.heading("total", text="Total", anchor="center")
        
        # Configure columns
        prod_tree.column("sku", width=120, anchor="center")
        prod_tree.column("name", width=250, anchor="center")
        prod_tree.column("qty", width=80, anchor="center")
        prod_tree.column("price", width=120, anchor="center")
        prod_tree.column("total", width=120, anchor="center")
        
        # Add products
        for idx, item in enumerate(receipt_items):
            # item: (sku, name, qty, price, total)
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            prod_tree.insert("", "end", values=(
                item[0],  # SKU
                item[1],  # Name
                item[2],  # Qty
                f"{item[3]:,.2f}",  # Price
                f"{item[4]:,.2f}"  # Total
            ), tags=(tag,))
        
        prod_tree.tag_configure('evenrow', background='#FFFFFF')
        prod_tree.tag_configure('oddrow', background='#F8F9FA')
        
        prod_tree.pack(fill="both", expand=True)
        
        # Scrollbar for products
        prod_scroll = ttk.Scrollbar(products_frame, orient="vertical", command=prod_tree.yview)
        prod_scroll.pack(side="right", fill="y")
        prod_tree.configure(yscrollcommand=prod_scroll.set)
        
        # Financial Summary Card
        summary_frame = tb.Labelframe(
            details_frame,
            text="  💰 Financial Summary  ",
            padding=20,
            bootstyle="success"
        )
        summary_frame.pack(fill="x", pady=(0, 15))
        
        summary_grid = tb.Frame(summary_frame)
        summary_grid.pack(fill="x")
        summary_grid.columnconfigure(1, weight=1)
        
        # Subtotal
        tb.Label(summary_grid, text="Subtotal:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="w", pady=5)
        tb.Label(summary_grid, text=f"EGP {sale_data['subtotal']:,.2f}", font=("Segoe UI", 12)).grid(row=0, column=1, sticky="e", pady=5)
        
        # Discount
        if sale_data['discount_percent'] > 0:
            tb.Label(summary_grid, text=f"Discount ({sale_data['discount_percent']}%):", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", pady=5)
            tb.Label(summary_grid, text=f"- EGP {sale_data['discount_amount']:,.2f}", font=("Segoe UI", 12), bootstyle="danger").grid(row=1, column=1, sticky="e", pady=5)
        
        ttk.Separator(summary_grid, orient="horizontal").grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Grand Total
        tb.Label(summary_grid, text="TOTAL:", font=("Segoe UI", 16, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        tb.Label(summary_grid, text=f"EGP {sale_data['grand_total']:,.2f}", font=("Segoe UI", 20, "bold"), bootstyle="success").grid(row=3, column=1, sticky="e", pady=5)
        
        # Items count
        total_qty = sum(item[2] for item in receipt_items)
        tb.Label(
            summary_frame,
            text=f"Total Items: {len(receipt_items)} | Total Quantity: {total_qty}",
            font=("Segoe UI", 10, "italic"),
            foreground="#6c757d"
        ).pack(pady=(10, 0))
        
        # Print receipt function
        def print_receipt():
            """Generate and print receipt"""
            try:
                # Try to import receipt generator
                try:
                    from modules.reports.receipt_generator import generate_sales_receipt_pdf
                    pdf_path = generate_sales_receipt_pdf(sale_data, receipt_items)
                    
                    # Open PDF
                    try:
                        os.startfile(pdf_path)
                        messagebox.showinfo(
                            "Receipt Generated", 
                            f"✓ Receipt opened successfully!\n\nSaved to:\n{pdf_path}"
                        )
                    except:
                        messagebox.showinfo(
                            "Receipt Saved", 
                            f"✓ Receipt saved successfully!\n\nLocation:\n{pdf_path}\n\nPlease open it manually."
                        )
                except ImportError:
                    # Fallback: Simple text receipt
                    messagebox.showinfo(
                        "Print Receipt",
                        f"Receipt for Sale #{sale_data['sale_id']}\n\n"
                        f"Customer: {sale_data['customer_name']}\n"
                        f"Date: {sale_data['date_time']}\n"
                        f"Total: EGP {sale_data['grand_total']:,.2f}\n\n"
                        f"Receipt generator module not found.\n"
                        f"Please install receipt generator for PDF receipts."
                    )
            except Exception as e:
                messagebox.showerror("Receipt Error", f"Could not generate receipt:\n{e}")
        
        def close_dialog():
            """Close the dialog"""
            unbind_from_mousewheel(dialog)
            dialog.destroy()
        
        # === BUTTONS SECTION - AT THE VERY BOTTOM ===
        # Separator line
        ttk.Separator(dialog, orient="horizontal").pack(fill="x", pady=10)
        
        # Buttons container with background
        buttons_container = tb.Frame(dialog, padding=25, bootstyle="light")
        buttons_container.pack(fill="x", side="bottom")
        
        # Info message ABOVE buttons
        tb.Label(
            buttons_container,
            text="💡 You can print the receipt now or close to continue",
            font=("Segoe UI", 11, "italic"),
            foreground="#6c757d"
        ).pack(pady=(0, 15))
        
        # Buttons row - CENTERED
        buttons_row = tb.Frame(buttons_container)
        buttons_row.pack()
        
        # Print Receipt button - VERY LARGE AND BLUE
        print_btn = tb.Button(
            buttons_row,
            text="🖨️  PRINT RECEIPT",
            bootstyle="primary",
            command=print_receipt,
            width=30
        )
        print_btn.pack(side="left", padx=15, ipady=15)
        
        # Close button - LARGE AND GREEN
        close_btn = tb.Button(
            buttons_row,
            text="✓  CLOSE",
            bootstyle="success",
            command=close_dialog,
            width=30
        )
        close_btn.pack(side="left", padx=15, ipady=15)
        
        # Bind mouse wheel
        try:
            bind_to_mousewheel(dialog)
        except:
            pass
        
        # Close on Escape key
        dialog.bind("<Escape>", lambda e: close_dialog())
        
        # Handle window close
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        
        # Force update to ensure buttons are visible
        dialog.update_idletasks()
