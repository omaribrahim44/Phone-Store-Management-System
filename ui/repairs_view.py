# ui/repairs_view.py
import csv
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, filedialog
from tkinter import StringVar
from tkinter import StringVar
from datetime import datetime, timedelta
import random

from controllers.repair_controller import RepairController
from controllers.inventory_controller import InventoryController
from modules.reports.receipt_generator import generate_receipt_pdf

def set_placeholder(entry: ttk.Entry, text: str, color="#888888"):
    """Adds placeholder behavior to a ttk Entry widget."""
    def on_focus_in(e):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.configure(foreground="black")
    def on_focus_out(e):
        if entry.get().strip() == "":
            entry.insert(0, text)
            entry.configure(foreground=color)
    entry.insert(0, text)
    entry.configure(foreground=color)
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

class RepairsFrame:
    STATUS_TAGS = {
        "Received": "info",
        "Diagnosed": "warning",
        "InProgress": "primary",
        "WaitingParts": "secondary",
        "Completed": "success",
        "Delivered": "success",
        "Cancelled": "danger"
    }

    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=12)
        # Make layout responsive
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)  # treeview row expands

        # Top: search & filters
        ctrl = tb.Frame(self.frame)
        ctrl.grid(row=0, column=0, sticky="ew", pady=(0,8))
        ctrl.columnconfigure(1, weight=1)

        tb.Label(ctrl, text="Search:").grid(row=0, column=0, sticky="w", padx=(0,6))
        self.search_var = StringVar()
        self.search_entry = tb.Entry(ctrl, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        set_placeholder(self.search_entry, "Order #, Customer, Model, IMEI ...")

        tb.Button(ctrl, text="Go", bootstyle="primary", command=self.refresh).grid(row=0, column=2, padx=6)

        tb.Label(ctrl, text="Status:").grid(row=0, column=3, padx=(12,6))
        self.status_filter = tb.Combobox(ctrl, values=["All"] + list(self.STATUS_TAGS.keys()), state="readonly", width=18)
        self.status_filter.current(0)
        self.status_filter.grid(row=0, column=4)

        tb.Button(ctrl, text="Export CSV", bootstyle="secondary-outline", command=self.export_csv).grid(row=0, column=5, padx=8)
        tb.Button(ctrl, text="Refresh", bootstyle="primary", command=self.refresh).grid(row=0, column=6, padx=(6,0))

        # Form: New Repair (Modern Card Style)
        form_frame = tb.Labelframe(self.frame, text="New Repair Order", padding=15, bootstyle="primary")
        form_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Grid Layout for Form
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        form_frame.columnconfigure(5, weight=1)

        # Row 1
        tb.Label(form_frame, text="Order #").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.order = tb.Entry(form_frame); self.order.grid(row=0, column=1, sticky="ew", padx=5)
        
        tb.Label(form_frame, text="Customer").grid(row=0, column=2, sticky="w", padx=5)
        self.cust = tb.Entry(form_frame); self.cust.grid(row=0, column=3, sticky="ew", padx=5)
        
        tb.Label(form_frame, text="Phone").grid(row=0, column=4, sticky="w", padx=5)
        self.phone = tb.Entry(form_frame); self.phone.grid(row=0, column=5, sticky="ew", padx=5)

        # Row 2
        tb.Label(form_frame, text="Device Model").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.model = tb.Entry(form_frame); self.model.grid(row=1, column=1, sticky="ew", padx=5)
        
        tb.Label(form_frame, text="IMEI / SN").grid(row=1, column=2, sticky="w", padx=5)
        imei_frame = tb.Frame(form_frame)
        imei_frame.grid(row=1, column=3, sticky="ew", padx=5)
        self.imei = tb.Entry(imei_frame)
        self.imei.pack(side="left", fill="x", expand=True)
        
        # IMEI scan indicator
        self.imei_status = tb.Label(imei_frame, text="", font=("Segoe UI", 8), width=10)
        self.imei_status.pack(side="left", padx=5)
        
        # Bind Enter key for barcode scanner
        self.imei.bind('<Return>', self.on_imei_scanned)
        self.imei.bind('<FocusIn>', lambda e: self.imei_status.configure(text="📷 Ready", bootstyle="info"))
        self.imei.bind('<FocusOut>', lambda e: self.imei_status.configure(text=""))
        
        tb.Label(form_frame, text="Est. Cost").grid(row=1, column=4, sticky="w", padx=5)
        self.estimate = tb.Entry(form_frame); self.estimate.grid(row=1, column=5, sticky="ew", padx=5)

        # Row 3 - Problem Description (Required Field)
        tb.Label(form_frame, text="Problem *", bootstyle="danger").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.problem = tb.Entry(form_frame)
        self.problem.grid(row=2, column=1, columnspan=5, sticky="ew", padx=5)
        set_placeholder(self.problem, "Describe the issue (e.g., Screen broken, Battery not charging...)")

        # Create Button & Clear Button
        btn_frame = tb.Frame(form_frame)
        btn_frame.grid(row=3, column=5, sticky="e", padx=5, pady=(10, 0))
        tb.Button(btn_frame, text="Clear", bootstyle="secondary-outline", command=self.clear_form).pack(side="left", padx=(0, 5))
        tb.Button(btn_frame, text="Create Order", bootstyle="success", command=self.create_order).pack(side="left")

        # Treeview
        cols = ("id","order","customer","phone","model","imei","status","received")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=14)
        
        # headings with better labels
        labels = {
            "id":"ID", "order":"Order #", "customer":"Customer", "phone":"Phone",
            "model":"Model", "imei":"IMEI", "status":"Status", "received":"Received"
        }
        # Adjusted widths and alignment - using 'w' (left) for most to prevent visual shifting
        widths = {"id":50, "order":120, "customer":200, "phone":120, "model":150, "imei":120, "status":120, "received":140}
        anchors = {"id":"center", "order":"w", "customer":"w", "phone":"w", "model":"w", "imei":"w", "status":"center", "received":"w"}
        
        for c in cols:
            self.tree.heading(c, text=labels.get(c, c).upper(), anchor="w") # Ensure headers are left-aligned
            self.tree.column(c, width=widths.get(c,100), anchor=anchors.get(c, "w"))
        self.tree.grid(row=3, column=0, sticky="nsew", padx=0, pady=(0,6))

        # Scrollbars
        vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=3, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        # Bind double click and right click menu
        self.tree.bind("<Double-1>", lambda e: self._on_double_click())
        self._create_context_menu()
        
        # Configure tags
        for status, bootstyle in self.STATUS_TAGS.items():
            self.tree.tag_configure(status, foreground=None) # default
        
        # Overdue tag (red text)
        self.tree.tag_configure("overdue", foreground="red")

        # Footer actions
        footer = tb.Frame(self.frame); footer.grid(row=4, column=0, sticky="ew", pady=(6,0))
        footer.columnconfigure(0, weight=1)
        left = tb.Frame(footer); left.grid(row=0, column=0, sticky="w")
        right = tb.Frame(footer); right.grid(row=0, column=1, sticky="e")
        tb.Button(left, text="Open Selected", bootstyle="secondary", command=self.open_selected).pack(side="left", padx=6)
        tb.Button(left, text="Print Selected", bootstyle="primary", command=self.print_selected).pack(side="left", padx=6)
        tb.Button(left, text="Export Selected (TXT)", bootstyle="secondary", command=self.export_selected_txt).pack(side="left", padx=6)
        tb.Button(right, text="Mark Completed", bootstyle="success-outline", command=lambda: self.change_status("Completed")).pack(side="right", padx=6)
        tb.Button(right, text="Refresh", bootstyle="primary", command=self.refresh).pack(side="right", padx=6)

        # initial load
        self.refresh()
    
    def clear_form(self):
        self.order.delete(0, 'end')
        self.cust.delete(0, 'end')
        self.model.delete(0, 'end')
        self.phone.delete(0, 'end')
        self.imei.delete(0, 'end')
        self.problem.delete(0, 'end')
        set_placeholder(self.problem, "Describe the issue (e.g., Screen broken, Battery not charging...)")
        self.estimate.delete(0, 'end')
    
    def on_imei_scanned(self, event):
        """Handle IMEI scan from barcode scanner"""
        imei = self.imei.get().strip()
        
        if not imei:
            return
        
        # Validate IMEI
        if validate_imei(imei):
            # Format IMEI for display
            formatted = format_imei(imei)
            self.imei.delete(0, 'end')
            self.imei.insert(0, formatted)
            
            # Check for duplicates
            duplicate = check_duplicate_imei(imei.replace(" ", ""))
            if duplicate:
                self.imei_status.configure(text="⚠️ Duplicate", bootstyle="warning")
                messagebox.showwarning(
                    "Duplicate IMEI",
                    f"This IMEI already exists in order #{duplicate[1]} for {duplicate[2]}.\n\nProceed with caution."
                )
            else:
                self.imei_status.configure(text="✓ Valid", bootstyle="success")
                # Log the scan
                log_scan(imei, "IMEI", "current_user", "REPAIRS")
            
            # Move to next field
            self.estimate.focus()
        else:
            self.imei_status.configure(text="✗ Invalid", bootstyle="danger")
            messagebox.showerror("Invalid IMEI", "The scanned IMEI is not valid. Please check and try again.")
        
        return 'break'  # Prevent default Enter behavior

    # ---------- core ----------
    def refresh(self):
        try:
            rows = RepairController.get_all_repairs()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load repairs: {e}")
            return

        q = (self.search_var.get() or "").strip().lower()
        placeholder = "order #, customer, model, imei ...".lower()
        if q == placeholder:
            q = ""
            
        status_filter = (self.status_filter.get() or "All")
        today = datetime.now().isoformat()[:10]

        # clear tree
        for r in self.tree.get_children():
            self.tree.delete(r)

        for row in rows:
            # row: id, order, cust, phone, model, imei, status, received, estimated
            display_row = list(row)
            if q:
                combined = " ".join([str(x) for x in display_row]).lower()
                if q not in combined:
                    continue
            if status_filter and status_filter != "All":
                stat = display_row[6] if len(display_row) > 6 else ""
                if stat != status_filter:
                    continue
            
            # Tree cols: id, order, customer, phone, model, imei, status, received
            # We map row indices: 0, 1, 2, 3, 4, 5, 6, 7
            
            # Format date
            raw_date = display_row[7]
            formatted_date = raw_date
            try:
                if raw_date:
                    dt = datetime.fromisoformat(raw_date)
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
            except: pass
            
            values = (display_row[0], display_row[1], display_row[2], display_row[3], 
                      display_row[4], display_row[5], display_row[6], formatted_date)
            
            iid = self.tree.insert("", "end", values=values)
            
            # Tag logic
            tags = []
            stat = display_row[6]
            if stat in self.STATUS_TAGS:
                tags.append(stat)
            
            # Overdue check
            if stat not in ('Completed', 'Delivered', 'Cancelled'):
                est = display_row[8] if len(display_row) > 8 else None
                if est and est < today:
                    tags.append("overdue")
            
            if tags:
                self.tree.item(iid, tags=tuple(tags))

    def create_order(self):
        # Simple 6-digit random number for Order #
        default_order = str(random.randint(100000, 999999))
        order = self.order.get().strip() or default_order
        cust = self.cust.get().strip()
        model = self.model.get().strip()
        phone = self.phone.get().strip()
        problem = self.problem.get().strip()
        
        # Check if problem is placeholder text
        placeholder_text = "Describe the issue (e.g., Screen broken, Battery not charging...)"
        if problem == placeholder_text:
            problem = ""
        
        try:
            total = float(self.estimate.get() or 0)
        except:
            total = 0.0
        
        # Validate required fields
        if not cust:
            messagebox.showwarning("Missing Information", "Customer name is required")
            self.cust.focus()
            return
        
        if not model:
            messagebox.showwarning("Missing Information", "Device model is required")
            self.model.focus()
            return
        
        if not problem:
            messagebox.showwarning("Missing Information", "Problem description is required")
            self.problem.focus()
            return
        
        try:
            rid = RepairController.create_repair(order, cust, phone, model, "", problem, None, "", total)
            if rid:
                messagebox.showinfo("✓ Success", f"Repair order #{order} created successfully!")
                self.clear_form()
                self.refresh()
            else:
                messagebox.showerror("Error", "Failed to create repair order. Check logs.")
        except Exception as e:
            err_msg = str(e)
            if "UNIQUE constraint failed" in err_msg and "order_number" in err_msg:
                messagebox.showerror("Duplicate Order #", f"Order #{order} already exists.\n\nPlease leave 'Order #' blank to auto-generate, or use a unique number.")
            else:
                messagebox.showerror("Create Failed", err_msg)

    # ---------- selection helpers ----------
    def _get_selected_id(self):
        sel = self.tree.selection()
        print(f"DEBUG: selection = {sel}")
        if not sel:
            return None
        item = self.tree.item(sel[0])['values']
        print(f"DEBUG: selected item values = {item}")
        return item[0] if item else None

    def open_selected(self):
        rid = self._get_selected_id()
        if not rid:
            messagebox.showwarning("No selection", "Please select a repair order first.")
            return
        self.open_detail_window(rid)

    def _on_double_click(self):
        self.open_selected()

    # ---------- context menu ----------
    def _create_context_menu(self):
        self.menu = tb.Menu(self.frame, tearoff=0)
        self.menu.add_command(label="Open", command=self.open_selected)
        self.menu.add_command(label="Print", command=self.print_selected)
        
        # Status Submenu
        status_menu = tb.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Change Status", menu=status_menu)
        for s in ["Received", "Diagnosis", "Waiting for Parts", "Repairing", "Ready", "Delivered", "Cancelled", "Completed"]:
            status_menu.add_command(label=s, command=lambda st=s: self.change_status(st))
            
        self.menu.add_separator()
        self.menu.add_command(label="Export Selected (TXT)", command=self.export_selected_txt)
        self.tree.bind("<Button-3>", lambda e: self._show_menu(e))

    def _show_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()

    # ---------- printing / export ----------
    def print_selected(self):
        print("DEBUG: print_selected called")
        rid = self._get_selected_id()
        if not rid:
            messagebox.showwarning("No selection", "Please select a repair order first.")
            return
        
        try:
            print(f"DEBUG: Fetching details for rid={rid}")
            order, parts, history = RepairController.get_repair_details(rid)
        except Exception as e:
            print(f"DEBUG: get_repair_details failed: {e}")
            messagebox.showerror("Error", f"Failed to load order details: {e}")
            return

        try:
            print(f"DEBUG: Generating PDF for order {rid}")
            # Generate PDF using new generator
            pdf_path = generate_receipt_pdf(order, parts, history)
            print(f"DEBUG: PDF generated at {pdf_path}")
            
            # Auto-open the PDF (Print Preview)
            try:
                print("DEBUG: Opening PDF...")
                os.startfile(pdf_path)
                print("DEBUG: PDF opened.")
            except Exception as e:
                print(f"DEBUG: Failed to open PDF: {e}")
                # Fallback for non-Windows or if startfile fails
                messagebox.showinfo("PDF Generated", f"Receipt saved to:\n{pdf_path}")
                
        except Exception as e:
            print(f"DEBUG: Print error: {e}")
            messagebox.showerror("Error", f"Failed to generate receipt: {e}")
            messagebox.showwarning("PDF failed", f"PDF generation unavailable or failed: {e}\nA plain-text file will be created as fallback.")
            self.export_selected_txt()

    def export_selected_txt(self):
        rid = self._get_selected_id()
        if not rid:
            messagebox.showwarning("No selection", "Please select a repair order first.")
            return
        try:
            order, parts, history = RepairController.get_repair_details(rid)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load order details: {e}")
            return

        lines = [
            "=== Repair Receipt ===",
            f"Order: {order[1] if len(order)>1 else rid}",
            f"Customer: {order[2] if len(order)>2 else ''}",
            f"Phone: {order[3] if len(order)>3 else ''}",
            f"Model: {order[4] if len(order)>4 else ''}",
            "Parts:"
        ]
        for p in parts:
            if len(p) >= 4:
                lines.append(f"{p[1]} x{p[2]} @ {p[3]}")
            else:
                lines.append(str(p))
        fname = f"receipt_ORDER_{rid}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Exported", f"Saved: {fname}")

    def export_csv(self):
        rows = [self.tree.item(i)['values'] for i in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("No data", "No rows to export.")
            return
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], initialfile="repairs_export.csv")
        if not fn:
            return
        with open(fn, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.tree["columns"])
            for r in rows:
                writer.writerow(r)
        messagebox.showinfo("Exported", f"Exported {len(rows)} rows to {fn}")

    # ---------- status ----------
    def change_status(self, new_status: str):
        rid = self._get_selected_id()
        if not rid:
            messagebox.showwarning("No selection", "Please select a repair order first.")
            return
        if messagebox.askyesno("Confirm", f"Set status to '{new_status}'?"):
            try:
                _ = RepairController.update_status(rid, new_status, "SystemUser", "")
                messagebox.showinfo("OK", f"Status set to {new_status}")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Failed", str(e))

    # ---------- detail window ----------
    def open_detail_window(self, rid):
        try:
            order, parts, history = RepairController.get_repair_details(rid)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load details: {e}")
            return

        win = tb.Toplevel(self.frame)
        win.title(f"Repair #{rid}")
        win.geometry("900x600")

        header = tb.Frame(win); header.pack(fill="x", padx=8, pady=6)
        tb.Label(header, text=f"Order: {order[1]}", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky="w")
        tb.Label(header, text=f"Customer: {order[2]}   Phone: {order[3]}").grid(row=1, column=0, sticky="w")

        # parts tree
        cols = ("id","name","qty","price","cost","total")
        pt = ttk.Treeview(win, columns=cols, show="headings", height=8)
        widths = {"id":50,"name":300,"qty":60,"price":80,"cost":80,"total":80}
        for c in cols:
            pt.heading(c, text=c.upper()); pt.column(c, width=widths.get(c,80))
        pt.pack(fill="x", padx=8, pady=6)

        total_parts = 0.0
        for p in parts:
            # p: id, name, qty, unit_price, cost_price
            if len(p) >= 5:
                cost = p[4] or 0.0
                tot = (p[2] or 1) * (p[3] or 0)
                pt.insert("", "end", values=(p[0], p[1], p[2], f"{p[3]:.2f}", f"{cost:.2f}", f"{tot:.2f}"))
                total_parts += tot
            elif len(p) >= 4:
                # fallback for old data
                tot = (p[2] or 1) * (p[3] or 0)
                pt.insert("", "end", values=(p[0], p[1], p[2], f"{p[3]:.2f}", "0.00", f"{tot:.2f}"))
                total_parts += tot

        tot_frame = tb.Frame(win); tot_frame.pack(fill="x", padx=8, pady=6)
        tb.Label(tot_frame, text=f"Parts total: {total_parts:.2f}").pack(side="left")

        addf = tb.Frame(win); addf.pack(fill="x", padx=8, pady=6)
        tb.Label(addf, text="Part name").grid(row=0, column=0); e_name = tb.Entry(addf); e_name.grid(row=0, column=1)
        tb.Label(addf, text="Qty").grid(row=0, column=2); e_qty = tb.Entry(addf, width=6); e_qty.grid(row=0, column=3)
        tb.Label(addf, text="Unit price").grid(row=0, column=4); e_price = tb.Entry(addf, width=12); e_price.grid(row=0, column=5)
        
        def on_add_part():
            name = e_name.get().strip()
            try: q = int(e_qty.get() or 1)
            except: q = 1
            try: pr = float(e_price.get() or 0)
            except: pr = 0.0
            
            if not name:
                messagebox.showerror("Error", "Part name required"); return
            
            # Auto-fetch cost
            cost = 0.0
            try:
                cost = InventoryController.get_item_cost(name)
            except: pass

            try:
                # Pass cost to add_repair_part
                _ = RepairController.add_part(rid, name, q, pr, cost)
                pt.insert("", "end", values=(None, name, q, f"{pr:.2f}", f"{cost:.2f}", f"{q*pr:.2f}"))
                messagebox.showinfo("OK", f"Part added (Cost: {cost})")
            except Exception as e:
                messagebox.showerror("Failed", str(e))
        tb.Button(addf, text="Add Part", bootstyle="success", command=on_add_part).grid(row=0, column=6, padx=6)

        # status change
        sf = tb.Frame(win); sf.pack(fill="x", padx=8, pady=6)
        tb.Label(sf, text="Change status").grid(row=0, column=0)
        status_var = StringVar(value=order[9] if len(order)>9 else (order[9] if order else "Received"))
        options = list(self.STATUS_TAGS.keys())
        cb = tb.Combobox(sf, textvariable=status_var, values=options, state="readonly"); cb.grid(row=0, column=1)
        e_comment = tb.Entry(sf, width=40); e_comment.grid(row=0, column=2, padx=8)
        def save_status():
            new = status_var.get(); comment = e_comment.get().strip()
            try:
                _ = RepairController.update_status(rid, new, "SystemUser", comment)
                messagebox.showinfo("OK", "Status updated"); win.destroy(); self.refresh()
            except Exception as e:
                messagebox.showerror("Failed", str(e))
        tb.Button(sf, text="Update", bootstyle="primary", command=save_status).grid(row=0, column=3, padx=6)
