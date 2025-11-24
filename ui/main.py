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

        # Dashboard (First tab)
        try:
            dash = DashboardFrame(nb)
            nb.add(dash.frame, text="Dashboard")
        except Exception as e:
            print(f"Error loading Dashboard: {e}")
            import traceback
            traceback.print_exc()
        
        # Sales (renamed from POS)
        try:
            sales = SalesFrame(nb)
            nb.add(sales.frame, text="💰 Sales")  # Changed from "POS (Sales)"
        except Exception as e:
            print(f"Error loading Sales: {e}")

        try:
            inv = InventoryFrame(nb)
            nb.add(inv.frame, text="Inventory")
        except Exception as e:
            print(f"Error loading Inventory: {e}")

        try:
            rep = RepairsFrame(nb)
            nb.add(rep.frame, text="Repairs")
        except Exception as e:
            print(f"Error loading Repairs: {e}")

        try:
            cust = CustomersFrame(nb)
            nb.add(cust.frame, text="Customers")
        except Exception as e:
            print(f"Error loading Customers: {e}")
        
        # Logs (NEW - Phase 3)
        try:
            logs = LogsFrame(nb)
            nb.add(logs.frame, text="Audit Logs")
        except Exception as e:
            print(f"Error loading Logs: {e}")

        try:
            users = UsersFrame(nb)
            nb.add(users.frame, text="Users")
        except Exception as e:
            print(f"Error loading Users: {e}")
        
        # Settings
        try:
            sett = SettingsFrame(nb)
            nb.add(sett.frame, text="Settings")
        except Exception as e:
            print(f"Error loading Settings: {e}")

        # Focus on Dashboard by default
        nb.select(0)

        app.mainloop()
    except Exception as e:
        messagebox.showerror("Startup error", str(e))
        raise

if __name__ == "__main__":
    start_app()
