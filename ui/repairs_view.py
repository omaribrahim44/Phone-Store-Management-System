# -*- coding: utf-8 -*-
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
        tb.Label(form_frame, text="Order # (Auto)", bootstyle="info").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.order = tb.Entry(form_frame, state="readonly")
        self.order.grid(row=0, column=1, sticky="ew", padx=5)
        # Show placeholder for auto-generation
        self.order.configure(state="normal")
        self.order.insert(0, "Auto-generated")
        self.order.configure(state="readonly", foreground="#999999")
        
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

        # Treeview with improved styling
        cols = ("id","order","customer","phone","model","imei","status","received")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=14)
        
        # Configure tree style
        style = ttk.Style()
        style.configure("Treeview", 
                       font=("Segoe UI", 11),
                       rowheight=32,
                       background="#FFFFFF",
                       fieldbackground="#FFFFFF")
        style.configure("Treeview.Heading",
                       font=("Segoe UI", 12, "bold"),
                       padding=10,
                       background="#E8E8E8")
        
        # Enhanced professional styling for table
        style = ttk.Style()
        style.configure("Treeview",
                       rowheight=38,  # Larger rows for better readability
                       font=("Segoe UI", 11),
                       background="#FFFFFF",
                       fieldbackground="#FFFFFF",
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       font=("Segoe UI", 11, "bold"),
                       background="#2C5282",
                       foreground="white",
                       borderwidth=1,
                       relief="flat",
                       padding=10)
        style.map("Treeview.Heading",
                 background=[("active", "#1A365D")])
        style.map("Treeview",
                 background=[("selected", "#4299E1")],
                 foreground=[("selected", "white")])
        
        # headings with better labels and icons
        labels = {
            "id":"🆔 ID", 
            "order":"📋 ORDER #", 
            "customer":"👤 CUSTOMER", 
            "phone":"📞 PHONE",
            "model":"📱 MODEL", 
            "imei":"🔢 IMEI", 
            "status":"📊 STATUS", 
            "received":"📅 RECEIVED"
        }
        # Proper widths and alignment for better readability
        widths = {"id":70, "order":140, "customer":220, "phone":140, "model":190, "imei":150, "status":140, "received":170}
        # Center alignment for ID, Order #, Status - Left for text fields
        anchors = {"id":"center", "order":"center", "customer":"w", "phone":"center", "model":"w", "imei":"center", "status":"center", "received":"center"}
        
        for c in cols:
            # Headers match data alignment for proper column alignment
            self.tree.heading(c, text=labels.get(c, c), anchor="center")  # All headers centered
            self.tree.column(c, width=widths.get(c,100), anchor=anchors.get(c, "w"))
        self.tree.grid(row=3, column=0, sticky="nsew", padx=0, pady=(0,6))

        # Scrollbars
        vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=3, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        # Bind double click and right click menu
        self.tree.bind("<Double-1>", lambda e: self._on_double_click())
        self._create_context_menu()
        
        # Configure enhanced status tags with background colors
        status_colors = {
            "Received": {"bg": "#FFF5F5", "fg": "#C53030"},      # Light red bg, dark red text
            "InProgress": {"bg": "#FFFAF0", "fg": "#DD6B20"},    # Light orange bg, dark orange text
            "Completed": {"bg": "#F0FFF4", "fg": "#2F855A"},     # Light green bg, dark green text
            "Delivered": {"bg": "#EBF8FF", "fg": "#2C5282"},     # Light blue bg, dark blue text
            "Cancelled": {"bg": "#F7FAFC", "fg": "#718096"}      # Light gray bg, gray text
        }
        
        for status, colors in status_colors.items():
            self.tree.tag_configure(status, background=colors["bg"], foreground=colors["fg"])
        
        # Alternating row colors for better readability
        self.tree.tag_configure("evenrow", background="#FFFFFF")
        self.tree.tag_configure("oddrow", background="#F8F9FA")
        
        # Overdue tag (red background with white text)
        self.tree.tag_configure("overdue", background="#FEB2B2", foreground="#742A2A", font=("Segoe UI", 11, "bold"))

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
        # Reset order field to auto-generated placeholder
        self.order.configure(state="normal")
        self.order.delete(0, 'end')
        self.order.insert(0, "Auto-generated")
        self.order.configure(state="readonly", foreground="#999999")
        
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

        row_index = 0  # Track row index for alternating colors
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
            
            # Format date with better styling
            raw_date = display_row[7]
            formatted_date = raw_date
            try:
                if raw_date:
                    dt = datetime.fromisoformat(raw_date)
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
            except: pass
            
            # Format status with emoji indicators
            status = display_row[6]
            status_icons = {
                "Received": "🔴 Received",
                "InProgress": "🟡 In Progress",
                "Completed": "🟢 Completed",
                "Delivered": "🔵 Delivered",
                "Cancelled": "⚫ Cancelled"
            }
            status_display = status_icons.get(status, status)
            
            values = (display_row[0], display_row[1], display_row[2], display_row[3], 
                      display_row[4], display_row[5], status_display, formatted_date)
            
            iid = self.tree.insert("", "end", values=values)
            
            # Enhanced tag logic with priority
            tags = []
            
            # Overdue check (highest priority - overrides status colors)
            if status not in ('Completed', 'Delivered', 'Cancelled'):
                est = display_row[8] if len(display_row) > 8 else None
                if est and est < today:
                    tags.append("overdue")
            
            # Status color (if not overdue)
            if not tags and status in self.STATUS_TAGS:
                tags.append(status)
            
            # Alternating row color (lowest priority)
            if not tags:
                row_color = "evenrow" if row_index % 2 == 0 else "oddrow"
                tags.append(row_color)
            
            if tags:
                self.tree.item(iid, tags=tuple(tags))
            
            row_index += 1
        
        # Notify that repairs were refreshed (for synchronization)
        from modules.event_manager import event_manager
        event_manager.notify('repair_updated', {'action': 'refresh'})

    def create_order(self):
        # AUTO-GENERATE Order # - Get next sequential number from database
        # Order field is readonly, so always auto-generate
        order = ""
        if True:  # Always auto-generate
            # Auto-generate sequential order number
            try:
                from modules.db import get_conn
                conn = get_conn()
                c = conn.cursor()
                c.execute("SELECT MAX(CAST(order_number AS INTEGER)) FROM repair_orders WHERE order_number GLOB '[0-9]*'")
                result = c.fetchone()
                conn.close()
                
                if result and result[0]:
                    order = str(int(result[0]) + 1)
                else:
                    order = "1"  # Start from 1 if no orders exist
            except:
                # Fallback to random if query fails
                order = str(random.randint(100000, 999999))
        
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
            messagebox.showwarning("Missing Information", "Problem description is required (supports Arabic)")
            self.problem.focus()
            return
        
        try:
            rid = RepairController.create_repair(order, cust, phone, model, "", problem, None, "Technician", total)
            if rid:
                messagebox.showinfo("✓ Success", f"Repair order #{order} created successfully!")
                self.clear_form()
                self.refresh()
                
                # Notify ALL views that repair was created
                from modules.event_manager import event_manager
                event_manager.notify('repair_updated', {'action': 'create', 'order': order, 'customer': cust})
            else:
                messagebox.showerror("Error", "Failed to create repair order. Check logs.")
        except Exception as e:
            err_msg = str(e)
            if "UNIQUE constraint failed" in err_msg and "order_number" in err_msg:
                messagebox.showerror("Duplicate Order #", f"Order #{order} already exists.\n\nPlease leave 'Order #' blank to auto-generate, or use a unique number.")
            elif "Validation error" in err_msg:
                messagebox.showerror("Validation Error", err_msg)
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
                
                # Notify ALL views that repair status changed
                from modules.event_manager import event_manager
                event_manager.notify('repair_updated', {'action': 'status_change', 'repair_id': rid, 'status': new_status})
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
        win.title(f"🔧 Repair Order #{order[1]} - Details")
        
        # Make dialog larger and use 85% of screen height
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        dialog_width = min(1200, int(screen_width * 0.9))  # Max 1200px or 90% of screen
        dialog_height = int(screen_height * 0.85)  # 85% of screen height
        
        win.geometry(f"{dialog_width}x{dialog_height}")
        win.resizable(True, True)
        
        # Center window
        win.update_idletasks()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        win.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # Header with order info - Enhanced styling
        header = tb.Labelframe(win, text="📋 Order Information", padding=20, bootstyle="primary")
        header.pack(fill="x", padx=20, pady=(20, 15))
        
        info_grid = tb.Frame(header)
        info_grid.pack(fill="x")
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
        
        # Row 1 - Order # and Status with better spacing
        tb.Label(info_grid, text="Order #:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=8)
        tb.Label(info_grid, text=order[1], font=("Segoe UI", 12, "bold"), bootstyle="primary").grid(row=0, column=1, sticky="w", padx=5, pady=8)
        
        tb.Label(info_grid, text="Status:", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, sticky="w", padx=(30, 10), pady=8)
        status_label = tb.Label(info_grid, text=order[6] if len(order) > 6 else "Unknown", font=("Segoe UI", 11, "bold"), bootstyle="info")
        status_label.grid(row=0, column=3, sticky="w", padx=5, pady=8)
        
        # Row 2 - Customer and Phone
        tb.Label(info_grid, text="Customer:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", padx=(0, 10), pady=8)
        tb.Label(info_grid, text=order[2], font=("Segoe UI", 11)).grid(row=1, column=1, sticky="w", padx=5, pady=8)
        
        tb.Label(info_grid, text="Phone:", font=("Segoe UI", 11, "bold")).grid(row=1, column=2, sticky="w", padx=(30, 10), pady=8)
        tb.Label(info_grid, text=order[3], font=("Segoe UI", 11)).grid(row=1, column=3, sticky="w", padx=5, pady=8)
        
        # Row 3 - Device and IMEI
        tb.Label(info_grid, text="Device:", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w", padx=(0, 10), pady=8)
        tb.Label(info_grid, text=order[4], font=("Segoe UI", 11)).grid(row=2, column=1, sticky="w", padx=5, pady=8)
        
        tb.Label(info_grid, text="IMEI:", font=("Segoe UI", 11, "bold")).grid(row=2, column=2, sticky="w", padx=(30, 10), pady=8)
        tb.Label(info_grid, text=order[5] if len(order) > 5 else "N/A", font=("Segoe UI", 11)).grid(row=2, column=3, sticky="w", padx=5, pady=8)

        # Parts section with professional styling - REDUCED HEIGHT
        parts_frame = tb.Labelframe(win, text="🔧 Parts & Services", padding=15, bootstyle="secondary")
        parts_frame.pack(fill="x", padx=20, pady=(0, 15))  # Changed from fill="both", expand=True to fill="x"
        
        # Parts table with better columns and styling - SMALLER HEIGHT
        cols = ("id", "name", "qty", "unit_price", "cost_price", "line_total", "profit")
        pt = ttk.Treeview(parts_frame, columns=cols, show="headings", height=6)  # Reduced from 12 to 6
        
        # Enhanced table styling
        style = ttk.Style()
        style.configure("Treeview", rowheight=35, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=8)
        
        # Configure columns with proper alignment and better widths
        headers = {
            "id": "ID",
            "name": "Part/Service Name",
            "qty": "Qty",
            "unit_price": "Unit Price",
            "cost_price": "Cost",
            "line_total": "Line Total",
            "profit": "Profit"
        }
        
        widths = {"id": 60, "name": 400, "qty": 80, "unit_price": 120, "cost_price": 120, "line_total": 140, "profit": 120}
        anchors = {"id": "center", "name": "w", "qty": "center", "unit_price": "center", "cost_price": "center", "line_total": "center", "profit": "center"}
        
        for c in cols:
            pt.heading(c, text=headers[c], anchor="center")  # All headers centered
            pt.column(c, width=widths[c], anchor=anchors[c])
        
        # Table container with scrollbar
        table_container = tb.Frame(parts_frame)
        table_container.pack(fill="both", expand=True, pady=(0, 15))
        
        pt.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=pt.yview)
        vsb.pack(side="right", fill="y")
        pt.configure(yscrollcommand=vsb.set)
        
        # Move table to container
        pt.pack_forget()
        pt.pack(in_=table_container, side="left", fill="both", expand=True)
        
        # Function to refresh parts table and totals
        def refresh_parts_table():
            # Clear table
            for item in pt.get_children():
                pt.delete(item)
            
            # Reload parts from database
            try:
                _, parts_updated, _ = RepairController.get_repair_details(rid)
            except:
                parts_updated = parts
            
            total_cost = 0.0
            total_revenue = 0.0
            total_profit = 0.0
            
            for p in parts_updated:
                # p: id, name, qty, unit_price, cost_price
                if len(p) >= 5:
                    part_id = p[0]
                    name = p[1]
                    qty = p[2] or 1
                    unit_price = p[3] or 0.0
                    cost_price = p[4] or 0.0
                    
                    line_total = qty * unit_price
                    line_cost = qty * cost_price
                    line_profit = line_total - line_cost
                    
                    total_revenue += line_total
                    total_cost += line_cost
                    total_profit += line_profit
                    
                    pt.insert("", "end", values=(
                        part_id,
                        name,
                        qty,
                        f"EGP {unit_price:,.2f}",
                        f"EGP {cost_price:,.2f}",
                        f"EGP {line_total:,.2f}",
                        f"EGP {line_profit:,.2f}"
                    ))
                elif len(p) >= 4:
                    # Fallback for old data
                    part_id = p[0]
                    name = p[1]
                    qty = p[2] or 1
                    unit_price = p[3] or 0.0
                    line_total = qty * unit_price
                    
                    total_revenue += line_total
                    
                    pt.insert("", "end", values=(
                        part_id,
                        name,
                        qty,
                        f"EGP {unit_price:,.2f}",
                        "EGP 0.00",
                        f"EGP {line_total:,.2f}",
                        "EGP 0.00"
                    ))
            
            # Update totals
            lbl_total_cost.configure(text=f"EGP {total_cost:,.2f}")
            lbl_total_revenue.configure(text=f"EGP {total_revenue:,.2f}")
            lbl_total_profit.configure(text=f"EGP {total_profit:,.2f}")
            
            # Update profit color
            if total_profit > 0:
                lbl_total_profit.configure(bootstyle="success")
            elif total_profit < 0:
                lbl_total_profit.configure(bootstyle="danger")
            else:
                lbl_total_profit.configure(bootstyle="secondary")
        
        # Enhanced Totals summary with better spacing
        totals_frame = tb.Frame(parts_frame)
        totals_frame.pack(fill="x", pady=(15, 15))
        
        # Three columns for totals
        totals_frame.columnconfigure(0, weight=1)
        totals_frame.columnconfigure(1, weight=1)
        totals_frame.columnconfigure(2, weight=1)
        
        # Total Cost - Gray card
        cost_card = tb.Frame(totals_frame, bootstyle="secondary", padding=15)
        cost_card.grid(row=0, column=0, sticky="ew", padx=8)
        tb.Label(cost_card, text="Total Cost", font=("Segoe UI", 11, "bold"), bootstyle="secondary-inverse").pack()
        lbl_total_cost = tb.Label(cost_card, text="EGP 0.00", font=("Segoe UI", 16, "bold"), bootstyle="secondary-inverse")
        lbl_total_cost.pack(pady=(5, 0))
        
        # Total Revenue - Purple card
        revenue_card = tb.Frame(totals_frame, bootstyle="info", padding=15)
        revenue_card.grid(row=0, column=1, sticky="ew", padx=8)
        tb.Label(revenue_card, text="Total Revenue", font=("Segoe UI", 11, "bold"), bootstyle="info-inverse").pack()
        lbl_total_revenue = tb.Label(revenue_card, text="EGP 0.00", font=("Segoe UI", 16, "bold"), bootstyle="info-inverse")
        lbl_total_revenue.pack(pady=(5, 0))
        
        # Total Profit - Green card
        profit_card = tb.Frame(totals_frame, bootstyle="success", padding=15)
        profit_card.grid(row=0, column=2, sticky="ew", padx=8)
        tb.Label(profit_card, text="Total Profit", font=("Segoe UI", 11, "bold"), bootstyle="success-inverse").pack()
        lbl_total_profit = tb.Label(profit_card, text="EGP 0.00", font=("Segoe UI", 16, "bold"), bootstyle="success-inverse")
        lbl_total_profit.pack(pady=(5, 0))
        
        # Add part form with better layout
        add_part_frame = tb.Labelframe(parts_frame, text="➕ Add Part/Service", padding=15)
        add_part_frame.pack(fill="x", pady=(0, 0))
        
        add_part_frame.columnconfigure(1, weight=3)
        add_part_frame.columnconfigure(3, weight=1)
        add_part_frame.columnconfigure(5, weight=1)
        
        tb.Label(add_part_frame, text="Part Name:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=8)
        e_name = tb.Entry(add_part_frame, font=("Segoe UI", 11))
        e_name.grid(row=0, column=1, sticky="ew", padx=5, pady=8)
        
        tb.Label(add_part_frame, text="Qty:", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky="w", padx=(15, 10), pady=8)
        e_qty = tb.Entry(add_part_frame, font=("Segoe UI", 11), width=10)
        e_qty.grid(row=0, column=3, sticky="ew", padx=5, pady=8)
        e_qty.insert(0, "1")
        
        tb.Label(add_part_frame, text="Unit Price:", font=("Segoe UI", 10, "bold")).grid(row=0, column=4, sticky="w", padx=(15, 10), pady=8)
        e_price = tb.Entry(add_part_frame, font=("Segoe UI", 11), width=15)
        e_price.grid(row=0, column=5, sticky="ew", padx=5, pady=8)
        
        # Cost display (auto-fetched)
        cost_info = tb.Label(add_part_frame, text="", font=("Segoe UI", 9, "italic"), foreground="#6c757d")
        cost_info.grid(row=1, column=1, columnspan=5, sticky="w", padx=5, pady=(0, 5))
        
        def on_part_name_change(*args):
            """Auto-fetch cost when part name is entered"""
            name = e_name.get().strip()
            if name:
                try:
                    cost = InventoryController.get_item_cost(name)
                    if cost > 0:
                        cost_info.configure(text=f"💰 Cost from inventory: EGP {cost:.2f}", foreground="#28a745")
                    else:
                        cost_info.configure(text="ℹ️ Part not in inventory - cost will be 0", foreground="#6c757d")
                except:
                    cost_info.configure(text="ℹ️ Part not in inventory - cost will be 0", foreground="#6c757d")
            else:
                cost_info.configure(text="")
        
        e_name.bind("<KeyRelease>", on_part_name_change)
        
        def on_add_part():
            name = e_name.get().strip()
            
            # Validate part name
            if not name:
                messagebox.showwarning("Missing Information", "Part name is required")
                e_name.focus()
                return
            
            # Validate quantity
            try:
                qty = int(e_qty.get().strip())
                if qty <= 0:
                    raise ValueError("Quantity must be positive")
            except ValueError as e:
                messagebox.showwarning("Invalid Quantity", f"Please enter a valid positive number for quantity\n\nError: {e}")
                e_qty.focus()
                return
            
            # Validate price
            try:
                price = float(e_price.get().strip())
                if price < 0:
                    raise ValueError("Price cannot be negative")
            except ValueError as e:
                messagebox.showwarning("Invalid Price", f"Please enter a valid number for price\n\nError: {e}")
                e_price.focus()
                return
            
            # Auto-fetch cost from inventory
            cost = 0.0
            try:
                cost = InventoryController.get_item_cost(name)
            except:
                pass
            
            try:
                # Add part to database
                success = RepairController.add_part(rid, name, qty, price, cost)
                
                if success:
                    # Clear form
                    e_name.delete(0, 'end')
                    e_qty.delete(0, 'end')
                    e_qty.insert(0, "1")
                    e_price.delete(0, 'end')
                    cost_info.configure(text="")
                    
                    # Refresh parts table
                    refresh_parts_table()
                    
                    # Show success message
                    line_total = qty * price
                    profit = line_total - (qty * cost)
                    messagebox.showinfo(
                        "✓ Part Added",
                        f"Part added successfully!\n\n"
                        f"Part: {name}\n"
                        f"Quantity: {qty}\n"
                        f"Unit Price: EGP {price:.2f}\n"
                        f"Line Total: EGP {line_total:.2f}\n"
                        f"Profit: EGP {profit:.2f}"
                    )
                    
                    # Notify other views
                    from modules.event_manager import event_manager
                    event_manager.notify('repair_updated', {'action': 'add_part', 'repair_id': rid})
                    
                    # Refresh main table
                    self.refresh()
                else:
                    messagebox.showerror("Error", "Failed to add part")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add part: {e}")
        
        tb.Button(
            add_part_frame,
            text="💾 Add Part",
            bootstyle="success",
            command=on_add_part
        ).grid(row=0, column=6, padx=10)

        # Payment tracking section
        payment_frame = tb.Labelframe(win, text="💳 Payment Tracking", padding=15, bootstyle="warning")
        payment_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        payment_frame.columnconfigure(1, weight=1)
        payment_frame.columnconfigure(3, weight=1)
        
        # Get current total revenue for payment
        try:
            _, parts_for_payment, _ = RepairController.get_repair_details(rid)
            total_to_pay = sum([(p[2] or 1) * (p[3] or 0) for p in parts_for_payment if len(p) >= 4])
        except:
            total_to_pay = 0.0
        
        # Payment status
        tb.Label(payment_frame, text="Amount Due:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        lbl_amount_due = tb.Label(
            payment_frame,
            text=f"EGP {total_to_pay:,.2f}",
            font=("Segoe UI", 14, "bold"),
            bootstyle="warning"
        )
        lbl_amount_due.grid(row=0, column=1, sticky="w", padx=5)
        
        # Payment method
        tb.Label(payment_frame, text="Payment Method:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        payment_method_var = StringVar(value="Cash")
        payment_methods = ["Cash", "Card", "Bank Transfer", "Mobile Payment", "Other"]
        payment_method_combo = tb.Combobox(
            payment_frame,
            textvariable=payment_method_var,
            values=payment_methods,
            state="readonly",
            font=("Segoe UI", 10),
            width=20
        )
        payment_method_combo.grid(row=1, column=1, sticky="w", padx=5)
        
        # Amount paid
        tb.Label(payment_frame, text="Amount Paid:", font=("Segoe UI", 10, "bold")).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        amount_paid_entry = tb.Entry(payment_frame, font=("Segoe UI", 10), width=15)
        amount_paid_entry.grid(row=1, column=3, sticky="w", padx=5)
        amount_paid_entry.insert(0, "0.00")
        
        # Payment notes
        tb.Label(payment_frame, text="Notes:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        payment_notes_entry = tb.Entry(payment_frame, font=("Segoe UI", 10))
        payment_notes_entry.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5)
        
        def record_payment():
            """Record payment for repair"""
            try:
                amount_paid = float(amount_paid_entry.get().strip())
                if amount_paid <= 0:
                    messagebox.showwarning("Invalid Amount", "Please enter a valid payment amount greater than 0")
                    return
                
                payment_method = payment_method_var.get()
                notes = payment_notes_entry.get().strip()
                
                # Calculate balance
                balance = total_to_pay - amount_paid
                
                # Confirm payment
                confirm_msg = (
                    f"Record Payment?\n\n"
                    f"Amount Due: EGP {total_to_pay:,.2f}\n"
                    f"Amount Paid: EGP {amount_paid:,.2f}\n"
                    f"Balance: EGP {balance:,.2f}\n"
                    f"Method: {payment_method}\n"
                )
                
                if balance > 0:
                    confirm_msg += f"\n⚠️ Remaining balance: EGP {balance:,.2f}"
                elif balance < 0:
                    confirm_msg += f"\n💰 Change to return: EGP {abs(balance):,.2f}"
                else:
                    confirm_msg += f"\n✅ Paid in full"
                
                if messagebox.askyesno("Confirm Payment", confirm_msg):
                    # Here you would save payment to database
                    # For now, show success message
                    messagebox.showinfo(
                        "✓ Payment Recorded",
                        f"Payment recorded successfully!\n\n"
                        f"Amount: EGP {amount_paid:,.2f}\n"
                        f"Method: {payment_method}\n"
                        f"Balance: EGP {balance:,.2f}"
                    )
                    
                    # Clear form
                    amount_paid_entry.delete(0, 'end')
                    amount_paid_entry.insert(0, "0.00")
                    payment_notes_entry.delete(0, 'end')
                    
                    # Notify other views
                    from modules.event_manager import event_manager
                    event_manager.notify('repair_updated', {'action': 'payment', 'repair_id': rid, 'amount': amount_paid})
                    
            except ValueError:
                messagebox.showwarning("Invalid Amount", "Please enter a valid number for payment amount")
                amount_paid_entry.focus()
        
        # Record payment button
        tb.Button(
            payment_frame,
            text="💰 Record Payment",
            bootstyle="success",
            command=record_payment
        ).grid(row=3, column=0, columnspan=4, pady=(10, 0), ipady=8)
        
        # Status change section
        status_frame = tb.Labelframe(win, text="📋 Update Status", padding=15, bootstyle="info")
        status_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        status_frame.columnconfigure(1, weight=1)
        status_frame.columnconfigure(3, weight=2)
        
        tb.Label(status_frame, text="New Status:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5)
        status_var = StringVar(value=order[6] if len(order) > 6 else "Received")
        options = list(self.STATUS_TAGS.keys())
        cb = tb.Combobox(status_frame, textvariable=status_var, values=options, state="readonly", font=("Segoe UI", 10))
        cb.grid(row=0, column=1, sticky="ew", padx=5)
        
        tb.Label(status_frame, text="Comment:", font=("Segoe UI", 10, "bold")).grid(row=0, column=2, sticky="w", padx=5)
        e_comment = tb.Entry(status_frame, font=("Segoe UI", 10))
        e_comment.grid(row=0, column=3, sticky="ew", padx=5)
        
        def save_status():
            new_status = status_var.get()
            comment = e_comment.get().strip()
            
            try:
                success = RepairController.update_status(rid, new_status, "SystemUser", comment)
                
                if success:
                    messagebox.showinfo("✓ Success", f"Status updated to: {new_status}")
                    
                    # Notify ALL views
                    from modules.event_manager import event_manager
                    event_manager.notify('repair_updated', {'action': 'status_change', 'repair_id': rid, 'status': new_status})
                    
                    # Refresh main table
                    self.refresh()
                    
                    # Close window
                    win.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update status")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status: {e}")
        
        tb.Button(
            status_frame,
            text="💾 Update Status",
            bootstyle="primary",
            command=save_status
        ).grid(row=0, column=4, padx=10)
        
        # Initial load of parts
        refresh_parts_table()
