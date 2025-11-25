# ui/main.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from ui.inventory_view import InventoryFrame
from ui.repairs_view import RepairsFrame
from ui.users_view import UsersFrame
from ui.dashboard_view import DashboardFrame
from ui.customers_view import CustomersFrame
from ui.sales_view import SalesFrame  # Changed from pos_view
from ui.reports_view import ReportsFrame
from ui.settings_view import SettingsFrame
from ui.logs_view import LogsFrame

from ui.styles import apply_styles

def start_app(theme_name="flatly"):
    try:
        # Apply styles (creates Window/Style internally or we use it to configure)
        # ttkbootstrap's Window creates a style, so we might need to adjust
        app = tb.Window(themename=theme_name)
        
        # Apply custom styles after window creation
        from ui.styles import apply_styles
        apply_styles(theme_name)

        app.title("Shop Manager - Modern UI")
        app.geometry("1150x750")

        nb = tb.Notebook(app, bootstyle="primary")
        nb.pack(expand=1, fill="both", padx=8, pady=8)
        
        # Import event manager for real-time sync
        from modules.event_manager import event_manager

        # Dashboard (First tab)
        dash = None
        try:
            dash = DashboardFrame(nb)
            nb.add(dash.frame, text="Dashboard")
        except Exception as e:
            print(f"Error loading Dashboard: {e}")
            import traceback
            traceback.print_exc()
        
        # Sales (renamed from POS)
        sales = None
        try:
            sales = SalesFrame(nb)
            nb.add(sales.frame, text="💰 Sales")  # Changed from "POS (Sales)"
        except Exception as e:
            print(f"Error loading Sales: {e}")
            import traceback
            traceback.print_exc()

        # Inventory
        inv = None
        try:
            inv = InventoryFrame(nb)
            nb.add(inv.frame, text="Inventory")
        except Exception as e:
            print(f"Error loading Inventory: {e}")
            import traceback
            traceback.print_exc()

        # Repairs
        rep = None
        try:
            rep = RepairsFrame(nb)
            nb.add(rep.frame, text="Repairs")
        except Exception as e:
            print(f"Error loading Repairs: {e}")
            import traceback
            traceback.print_exc()

        # Customers
        cust = None
        try:
            cust = CustomersFrame(nb)
            nb.add(cust.frame, text="Customers")
        except Exception as e:
            print(f"Error loading Customers: {e}")
            import traceback
            traceback.print_exc()
        
        # Reports (NEW - Sales Reports)
        reports = None
        try:
            reports = ReportsFrame(nb)
            nb.add(reports.frame, text="📊 Reports")
        except Exception as e:
            print(f"Error loading Reports: {e}")
            import traceback
            traceback.print_exc()
        
        # Logs (NEW - Phase 3)
        logs = None
        try:
            logs = LogsFrame(nb)
            nb.add(logs.frame, text="Audit Logs")
        except Exception as e:
            print(f"Error loading Logs: {e}")
            import traceback
            traceback.print_exc()

        # Users
        users = None
        try:
            users = UsersFrame(nb)
            nb.add(users.frame, text="Users")
        except Exception as e:
            print(f"Error loading Users: {e}")
            import traceback
            traceback.print_exc()
        
        # Settings
        sett = None
        try:
            sett = SettingsFrame(nb)
            nb.add(sett.frame, text="Settings")
        except Exception as e:
            print(f"Error loading Settings: {e}")
            import traceback
            traceback.print_exc()
        
        # ===== REAL-TIME SYNCHRONIZATION SETUP =====
        # Subscribe all views to relevant events for automatic refresh
        
        # When inventory changes -> refresh Sales, Dashboard, Repairs
        if sales:
            event_manager.subscribe('inventory_changed', lambda data: sales.refresh_inventory())
        if dash:
            event_manager.subscribe('inventory_changed', lambda data: dash.refresh_data())
        if rep:
            event_manager.subscribe('inventory_changed', lambda data: rep.refresh() if hasattr(rep, 'refresh') else None)
        
        # When sale completes -> refresh Inventory, Dashboard, Customers
        if inv:
            event_manager.subscribe('sale_completed', lambda data: inv.refresh())
        if dash:
            event_manager.subscribe('sale_completed', lambda data: dash.refresh_data())
        if cust:
            event_manager.subscribe('sale_completed', lambda data: cust.refresh() if hasattr(cust, 'refresh') else None)
        
        # When repair updated -> refresh Dashboard, Customers
        if dash:
            event_manager.subscribe('repair_updated', lambda data: dash.refresh_data())
        if cust:
            event_manager.subscribe('repair_updated', lambda data: cust.refresh() if hasattr(cust, 'refresh') else None)
        
        # When customer updated -> refresh Customers view, Dashboard
        if cust:
            event_manager.subscribe('customer_updated', lambda data: cust.refresh() if hasattr(cust, 'refresh') else None)
        if dash:
            event_manager.subscribe('customer_updated', lambda data: dash.refresh_data())

        # Focus on Dashboard by default
        nb.select(0)
        
        # Start database monitor for real-time sync across multiple instances
        try:
            from modules.db_monitor import start_database_monitor
            from pathlib import Path
            db_path = Path(__file__).resolve().parents[1] / "shop.db"
            start_database_monitor(db_path, check_interval=3)  # Check every 3 seconds
            print("✅ Real-time database synchronization enabled")
        except Exception as e:
            print(f"⚠️ Database monitor not started: {e}")

        app.mainloop()
    except Exception as e:
        messagebox.showerror("Startup error", str(e))
        raise

if __name__ == "__main__":
    start_app()
