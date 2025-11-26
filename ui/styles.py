# ui/styles.py
import ttkbootstrap as tb
from tkinter import ttk

def apply_styles(theme_name="flatly"):
    """
    Applies global styles to the application including professional table styling.
    """
    style = tb.Style(theme=theme_name)
    
    # Configure Global Font - Improved readability
    # Segoe UI is standard on Windows, Roboto/Helvetica elsewhere
    default_font = ("Segoe UI", 10)
    header_font = ("Segoe UI", 11, "bold")
    title_font = ("Segoe UI", 20, "bold")
    large_title_font = ("Segoe UI", 24, "bold")
    
    # Base styles
    style.configure(".", font=default_font)
    
    # === PROFESSIONAL TREEVIEW/TABLE STYLES ===
    # Main table styling - Enhanced for better readability
    style.configure("Treeview",
                   rowheight=38,  # Larger rows for comfortable reading
                   font=("Segoe UI", 11),
                   background="#FFFFFF",
                   fieldbackground="#FFFFFF",
                   borderwidth=0)
    
    # Header styling - Navy blue professional look
    style.configure("Treeview.Heading",
                   font=("Segoe UI", 11, "bold"),
                   background="#2C5282",
                   foreground="white",
                   borderwidth=1,
                   relief="flat",
                   padding=10)
    
    # Header hover effect
    style.map("Treeview.Heading",
             background=[("active", "#1A365D")])
    
    # Selection styling - Bright blue highlight
    style.map("Treeview",
             background=[("selected", "#4299E1")],
             foreground=[("selected", "white")])
    
    # Custom styles for specific widgets
    style.configure("Title.TLabel", font=title_font)
    style.configure("LargeTitle.TLabel", font=large_title_font)
    style.configure("Header.TLabel", font=header_font)
    
    # Button styles - Better padding
    style.configure("TButton", padding=8)
    
    # Label frame styles - Better padding
    style.configure("TLabelframe", padding=15)
    style.configure("TLabelframe.Label", font=header_font)
    
    return style


def configure_table_tags(tree, table_type="general"):
    """
    Configure color tags for different table types.
    
    Args:
        tree: ttk.Treeview widget
        table_type: str - "general", "status", "stock", "priority"
    """
    # Alternating row colors (for all tables)
    tree.tag_configure("evenrow", background="#FFFFFF")
    tree.tag_configure("oddrow", background="#F8F9FA")
    
    if table_type == "status":
        # Status-based colors (for repairs, orders)
        tree.tag_configure("Received", background="#FFF5F5", foreground="#C53030")
        tree.tag_configure("InProgress", background="#FFFAF0", foreground="#DD6B20")
        tree.tag_configure("Completed", background="#F0FFF4", foreground="#2F855A")
        tree.tag_configure("Delivered", background="#EBF8FF", foreground="#2C5282")
        tree.tag_configure("Cancelled", background="#F7FAFC", foreground="#718096")
        tree.tag_configure("overdue", background="#FEB2B2", foreground="#742A2A", font=("Segoe UI", 11, "bold"))
    
    elif table_type == "stock":
        # Stock level colors (for inventory)
        tree.tag_configure("in_stock", foreground="#28a745")
        tree.tag_configure("low_stock", foreground="#fd7e14", font=("Segoe UI", 11, "bold"))
        tree.tag_configure("out_of_stock", foreground="#dc3545", font=("Segoe UI", 11, "bold"))
    
    elif table_type == "priority":
        # Priority colors (for logs, alerts)
        tree.tag_configure("high", background="#FEB2B2", foreground="#742A2A", font=("Segoe UI", 11, "bold"))
        tree.tag_configure("medium", background="#FED7AA", foreground="#7C2D12")
        tree.tag_configure("low", background="#E0E7FF", foreground="#3730A3")
        tree.tag_configure("info", background="#DBEAFE", foreground="#1E40AF")
