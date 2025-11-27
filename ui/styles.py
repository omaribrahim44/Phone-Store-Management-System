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
                   rowheight=40,  # Even larger rows for maximum comfort
                   font=("Segoe UI", 11),
                   background="#FFFFFF",
                   fieldbackground="#FFFFFF",
                   borderwidth=0)
    
    # Header styling - Modern gradient-like dark header
    style.configure("Treeview.Heading",
                   font=("Segoe UI", 12, "bold"),  # Larger, bolder font
                   background="#1A365D",  # Darker navy for more contrast
                   foreground="white",
                   borderwidth=0,
                   relief="flat",
                   padding=12)  # More padding
    
    # Header hover effect - Lighter blue
    style.map("Treeview.Heading",
             background=[("active", "#2C5282")])
    
    # Selection styling - Vibrant blue highlight
    style.map("Treeview",
             background=[("selected", "#3182CE")],  # Slightly darker blue
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


# Status Badge Color Schemes
STATUS_BADGE_COLORS = {
    "success": {"bg": "#48BB78", "fg": "white"},      # Green
    "warning": {"bg": "#ED8936", "fg": "white"},      # Orange
    "danger": {"bg": "#F56565", "fg": "white"},       # Red
    "info": {"bg": "#4299E1", "fg": "white"},         # Blue
    "secondary": {"bg": "#A0AEC0", "fg": "white"},    # Gray
    "primary": {"bg": "#3182CE", "fg": "white"},      # Dark Blue
}

# Stock Level Colors
STOCK_COLORS = {
    "adequate": "#28a745",      # Green - stock >= 10
    "low": "#fd7e14",           # Orange - 5 <= stock < 10
    "critical": "#dc3545",      # Red - 0 < stock < 5
    "out": "#6c757d"            # Gray - stock == 0
}

# Loading Indicator Style
LOADING_STYLE = {
    "text": "⏳ Loading...",
    "font": ("Segoe UI", 10, "italic"),
    "foreground": "#718096"
}



def get_stock_color(quantity):
    """
    Get color for stock quantity based on thresholds.
    
    Args:
        quantity: int - Stock quantity
    
    Returns:
        str - Color code
    """
    if quantity >= 10:
        return STOCK_COLORS["adequate"]
    elif 5 <= quantity < 10:
        return STOCK_COLORS["low"]
    elif 0 < quantity < 5:
        return STOCK_COLORS["critical"]
    else:  # quantity == 0
        return STOCK_COLORS["out"]


def get_stock_tag(quantity):
    """
    Get tag name for stock quantity.
    
    Args:
        quantity: int - Stock quantity
    
    Returns:
        str - Tag name
    """
    if quantity >= 10:
        return "in_stock"
    elif 5 <= quantity < 10:
        return "low_stock"
    else:
        return "out_of_stock"


def create_status_badge(parent, status, badge_type="status"):
    """
    Create a status badge label with appropriate styling.
    
    Args:
        parent: Parent widget
        status: Status text to display
        badge_type: Type of badge ("success", "warning", "danger", "info", "secondary", "primary")
    
    Returns:
        tb.Label - Configured badge label
    """
    colors = STATUS_BADGE_COLORS.get(badge_type, STATUS_BADGE_COLORS["secondary"])
    
    badge = tb.Label(
        parent,
        text=status,
        font=("Segoe UI", 9, "bold"),
        background=colors["bg"],
        foreground=colors["fg"],
        padding=(8, 4),
        relief="flat"
    )
    
    return badge
