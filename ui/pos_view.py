# ui/pos_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
import os
from datetime import datetime
from controllers.pos_controller import POSController
from controllers.inventory_controller import InventoryController

class POSFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=15)
        self.cart = [] # list of dicts: {id, name, qty, price, cost, max_qty}
        
        # Layout: Left (Inventory Search), Right (Cart & Checkout)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # --- Left Panel: Inventory ---
        left_panel = tb.Labelframe(self.frame, text="Available Items", padding=10)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.rowconfigure(1, weight=1)
        
        # Search
        search_frame = tb.Frame(left_panel)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tb.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_var = tb.StringVar()
        self.search_var.trace("w", self.filter_inventory)
        tb.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True)
        
        # Inventory List
        cols = ("id", "sku", "name", "stock", "price")
        self.inv_tree = ttk.Treeview(left_panel, columns=cols, show="headings", height=15)
        widths = {"id":50, "sku":80, "name":200, "stock":60, "price":80}
        alignments = {"id":"center", "sku":"w", "name":"w", "stock":"center", "price":"e"}
        for c in cols:
            self.inv_tree.heading(c, text=c.upper())
            self.inv_tree.column(c, width=widths[c], anchor=alignments[c])
        self.inv_tree.grid(row=1, column=0, sticky="nsew", pady=5)
        
        # Add to Cart Button - Ensure it's visible
        btn_frame = tb.Frame(left_panel)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        tb.Button(btn_frame, text="Add to Cart →", bootstyle="success", command=self.add_to_cart).pack(side="right", padx=10)

        # --- Right Panel: Cart ---
        right_panel = tb.Labelframe(self.frame, text="Current Sale", padding=15, bootstyle="primary")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(1, weight=1)
        
        # Customer Name
        cust_frame = tb.Frame(right_panel)
        cust_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tb.Label(cust_frame, text="Customer:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 5))
        self.cust_name = tb.Entry(cust_frame, font=("Segoe UI", 10))
        self.cust_name.pack(side="left", fill="x", expand=True)
        self.cust_name.insert(0, "Walk-in Customer")
        
        # Cart List
        c_cols = ("id", "name", "qty", "price", "total")
        self.cart_tree = ttk.Treeview(right_panel, columns=c_cols, show="headings", height=12)
        c_widths = {"id":40, "name":180, "qty":50, "price":70, "total":70}
        c_alignments = {"id":"center", "name":"w", "qty":"center", "price":"e", "total":"e"}
        for c in c_cols:
            self.cart_tree.heading(c, text=c.upper())
            self.cart_tree.column(c, width=c_widths[c], anchor=c_alignments[c])
        self.cart_tree.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        # Totals & Actions
        action_frame = tb.Frame(right_panel)
        action_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        self.lbl_total = tb.Label(action_frame, text="Total: EGP 0.00", font=("Segoe UI", 16, "bold"), bootstyle="success")
        self.lbl_total.pack(side="right")
        
        btn_frame = tb.Frame(right_panel)
        btn_frame.grid(row=3, column=0, sticky="ew")
        tb.Button(btn_frame, text="Remove Item", bootstyle="warning-outline", command=self.remove_from_cart).pack(side="left", padx=(0, 5))
        tb.Button(btn_frame, text="Clear Cart", bootstyle="danger-outline", command=self.clear_cart).pack(side="left")
        tb.Button(btn_frame, text="Checkout", bootstyle="success", command=self.checkout).pack(side="right")

        # Load Data
        self.all_inventory = []
        self.refresh_inventory()

    def refresh_inventory(self):
        try:
            self.all_inventory = InventoryController.get_all_items()
            self.filter_inventory()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def filter_inventory(self, *args):
        query = self.search_var.get().lower()
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
            
        for row in self.all_inventory:
            # row: id, sku, name, qty, buy, sell, desc
            if query and query not in str(row[1]).lower() and query not in str(row[2]).lower():
                continue
            # Display: id, sku, name, stock, sell_price
            self.inv_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[5]))

    def add_to_cart(self):
        sel = self.inv_tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select an item from the list.")
            return
        else:
            messagebox.showwarning("Out of Stock", "Item is out of stock.")

    def remove_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel: return
        idx = self.cart_tree.index(sel[0])
        del self.cart[idx]
        self.update_cart_view()

    def clear_cart(self):
        if messagebox.askyesno("Clear Cart", "Remove all items from cart?"):
            self.cart = []
            self.update_cart_view()

    def update_cart_view(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        total = 0.0
        for i in self.cart:
            line_total = i['qty'] * i['price']
            total += line_total
            self.cart_tree.insert("", "end", values=(i['id'], i['name'], i['qty'], f"{i['price']:.2f}", f"{line_total:.2f}"))
            
        self.lbl_total.configure(text=f"Total: EGP {total:,.2f}")

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items first.")
            return
            
        cust_name = self.cust_name.get().strip() or "Walk-in"
        
        # Prepare items for DB: (item_id, qty, unit_price, cost_price)
        db_items = [(i['id'], i['qty'], i['price'], i['cost']) for i in self.cart]
        
        try:
            sale_id = POSController.create_sale(cust_name, db_items)
            if sale_id:
                messagebox.showinfo("Success", f"Sale #{sale_id} completed!")
                
                # Generate Receipt
                try:
                    from modules.reports.receipt_generator import generate_sales_receipt_pdf
                    # items for receipt: (name, qty, price, total)
                    receipt_items = [(i['name'], i['qty'], i['price'], i['qty']*i['price']) for i in self.cart]
                    
                    # Sale tuple: (sale_id, date, cust_name, total)
                    total = sum([i['qty']*i['price'] for i in self.cart])
                    sale_data = (sale_id, datetime.now().isoformat()[:16], cust_name, total)
                    
                    pdf_path = generate_sales_receipt_pdf(sale_data, receipt_items)
                    
                    # Auto-open
                    try:
                        os.startfile(pdf_path)
                    except:
                        messagebox.showinfo("Receipt", f"Saved to {pdf_path}")
                        
                except Exception as e:
                    messagebox.showerror("Receipt Error", f"Could not generate receipt: {e}")

                self.cart = []
                self.update_cart_view()
                self.refresh_inventory()
            else:
                messagebox.showerror("Failed", "Could not record sale.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
