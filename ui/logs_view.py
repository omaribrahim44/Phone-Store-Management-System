# ui/logs_view.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from modules.audit_logger import get_logs, get_entity_history
import csv

class LogsFrame:
    def __init__(self, parent):
        self.frame = tb.Frame(parent, padding=15)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(2, weight=1)
        
        # --- Header ---
        header = tb.Frame(self.frame)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        tb.Label(header, text="Audit Logs", font=("Segoe UI", 18, "bold")).pack(side="left")
        tb.Button(header, text="Export to CSV", bootstyle="secondary-outline", command=self.export_logs).pack(side="right", padx=5)
        tb.Button(header, text="Refresh", bootstyle="primary", command=self.refresh).pack(side="right")
        
        # --- Filters ---
        filter_frame = tb.Labelframe(self.frame, text="Filters", padding=10)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        filter_frame.columnconfigure(5, weight=1)
        
        # Row 1: Action Type, Entity Type, User
        tb.Label(filter_frame, text="Action Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.action_filter = tb.Combobox(filter_frame, values=["All", "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "STATUS_CHANGE", "PRINT", "EXPORT"], state="readonly")
        self.action_filter.set("All")
        self.action_filter.grid(row=0, column=1, sticky="ew", padx=5)
        
        tb.Label(filter_frame, text="Entity Type:").grid(row=0, column=2, sticky="w", padx=5)
        self.entity_filter = tb.Combobox(filter_frame, values=["All", "repair", "sale", "inventory", "user", "customer"], state="readonly")
        self.entity_filter.set("All")
        self.entity_filter.grid(row=0, column=3, sticky="ew", padx=5)
        
        tb.Label(filter_frame, text="User:").grid(row=0, column=4, sticky="w", padx=5)
        self.user_filter = tb.Entry(filter_frame)
        self.user_filter.grid(row=0, column=5, sticky="ew", padx=5)
        
        # Row 2: Date Range
        tb.Label(filter_frame, text="Date Range:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_range = tb.Combobox(filter_frame, values=["All Time", "Today", "Last 7 Days", "Last 30 Days"], state="readonly")
        self.date_range.set("Last 7 Days")
        self.date_range.grid(row=1, column=1, sticky="ew", padx=5)
        
        tb.Button(filter_frame, text="Apply Filters", bootstyle="primary", command=self.refresh).grid(row=1, column=5, sticky="e", padx=5)
        
        # --- Logs Table ---
        cols = ("log_id", "timestamp", "user", "action", "entity", "entity_id", "description")
        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=15)
        
        widths = {"log_id": 60, "timestamp": 150, "user": 120, "action": 120, "entity": 100, "entity_id": 80, "description": 400}
        alignments = {"log_id": "center", "timestamp": "w", "user": "w", "action": "center", "entity": "w", "entity_id": "center", "description": "w"}
        for c in cols:
            self.tree.heading(c, text=c.replace("_", " ").upper())
            self.tree.column(c, width=widths.get(c, 100), anchor=alignments.get(c, "w"))
        
        self.tree.grid(row=2, column=0, sticky="nsew")
        
        # Scrollbar
        vsb = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Context menu
        self.tree.bind("<Double-1>", self.show_details)
        
        # Initial load
        self.refresh()
    
    def refresh(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filter values
        action_type = self.action_filter.get()
        if action_type == "All":
            action_type = None
        
        entity_type = self.entity_filter.get()
        if entity_type == "All":
            entity_type = None
        
        user = self.user_filter.get().strip()
        if not user:
            user = None
        
        # Date range
        start_date = None
        end_date = None
        date_range = self.date_range.get()
        
        if date_range == "Today":
            start_date = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        elif date_range == "Last 7 Days":
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        elif date_range == "Last 30 Days":
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        
        # Fetch logs
        try:
            logs = get_logs(
                limit=500,
                user=user,
                action_type=action_type,
                entity_type=entity_type,
                start_date=start_date,
                end_date=end_date
            )
            
            for log in logs:
                # log: (log_id, timestamp, user, action_type, entity_type, entity_id, old_value, new_value, description)
                display_values = (
                    log[0],  # log_id
                    log[1][:19] if log[1] else "",  # timestamp (truncate)
                    log[2] or "System",  # user
                    log[3],  # action_type
                    log[4],  # entity_type
                    log[5] or "",  # entity_id
                    log[8] or ""  # description
                )
                self.tree.insert("", "end", values=display_values)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logs: {e}")
    
    def show_details(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        
        item = self.tree.item(sel[0])['values']
        log_id = item[0]
        
        # Create detail window
        win = tb.Toplevel(self.frame)
        win.title(f"Log Details - ID {log_id}")
        win.geometry("600x400")
        
        detail_frame = tb.Frame(win, padding=20)
        detail_frame.pack(fill="both", expand=True)
        
        # Display all log details
        details_text = f"""
Log ID: {item[0]}
Timestamp: {item[1]}
User: {item[2]}
Action: {item[3]}
Entity Type: {item[4]}
Entity ID: {item[5]}
Description: {item[6]}
        """
        
        text_widget = tb.Text(detail_frame, wrap="word", height=15)
        text_widget.insert("1.0", details_text.strip())
        text_widget.configure(state="disabled")
        text_widget.pack(fill="both", expand=True)
        
        tb.Button(detail_frame, text="Close", bootstyle="secondary", command=win.destroy).pack(pady=10)
    
    def export_logs(self):
        # Get current filtered logs
        logs_data = []
        for item_id in self.tree.get_children():
            item = self.tree.item(item_id)['values']
            logs_data.append(item)
        
        if not logs_data:
            messagebox.showwarning("No Data", "No logs to export.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(["Log ID", "Timestamp", "User", "Action", "Entity Type", "Entity ID", "Description"])
                # Write data
                for row in logs_data:
                    writer.writerow(row)
            
            messagebox.showinfo("Success", f"Exported {len(logs_data)} logs to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {e}")
