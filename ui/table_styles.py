# ui/table_styles.py
"""
Centralized table styling for consistent professional appearance across all views
"""
from tkinter import ttk

def apply_professional_table_style():
    """
    Apply professional styling to all Treeview tables in the application.
    Call this function once during app initialization.
    """
    style = ttk.Style()
    
    # Main table styling - improved readability
    style.configure("Treeview",
                   rowheight=35,  # Balanced row height
                   font=("Segoe UI", 10),  # Professional readable font
                   background="#FFFFFF",
                   fieldbackground="#FFFFFF",
                   borderwidth=0)
    
    # Header styling - modern professional blue
    style.configure("Treeview.Heading",
                   font=("Segoe UI", 10, "bold"),  # Clear, readable headers
                   background="#2C5282",  # Professional blue
                   foreground="white",
                   borderwidth=0,
                   relief="flat",
                   padding=10)
    
    # Header hover effect - lighter blue
    style.map("Treeview.Heading",
             background=[("active", "#3182CE")])
    
    # Selection styling - consistent blue theme
    style.map("Treeview",
             background=[("selected", "#3182CE")],
             foreground=[("selected", "white")])
    
    return style


def configure_alternating_rows(tree):
    """
    Configure alternating row colors for a Treeview widget.
    
    Args:
        tree: ttk.Treeview widget
    """
    tree.tag_configure("evenrow", background="#FFFFFF")
    tree.tag_configure("oddrow", background="#F8F9FA")


def configure_status_colors(tree):
    """
    Configure status-based color coding for repair/order status.
    
    Args:
        tree: ttk.Treeview widget
    """
    status_colors = {
        "Received": {"bg": "#FFF5F5", "fg": "#C53030"},      # Light red
        "InProgress": {"bg": "#FFFAF0", "fg": "#DD6B20"},    # Light orange
        "Completed": {"bg": "#F0FFF4", "fg": "#2F855A"},     # Light green
        "Delivered": {"bg": "#EBF8FF", "fg": "#2C5282"},     # Light blue
        "Cancelled": {"bg": "#F7FAFC", "fg": "#718096"}      # Light gray
    }
    
    for status, colors in status_colors.items():
        tree.tag_configure(status, background=colors["bg"], foreground=colors["fg"])


def configure_stock_colors(tree):
    """
    Configure stock level color coding for inventory.
    
    Args:
        tree: ttk.Treeview widget
    """
    tree.tag_configure("in_stock", foreground="#28a745")
    tree.tag_configure("low_stock", foreground="#fd7e14", font=("Segoe UI", 11, "bold"))
    tree.tag_configure("out_of_stock", foreground="#dc3545", font=("Segoe UI", 11, "bold"))


def configure_priority_colors(tree):
    """
    Configure priority/alert color coding.
    
    Args:
        tree: ttk.Treeview widget
    """
    tree.tag_configure("high_priority", background="#FEB2B2", foreground="#742A2A", font=("Segoe UI", 11, "bold"))
    tree.tag_configure("medium_priority", background="#FED7AA", foreground="#7C2D12")
    tree.tag_configure("low_priority", background="#E0E7FF", foreground="#3730A3")


def apply_row_tags(tree, row_index, base_tag=None):
    """
    Apply appropriate tags to a tree row based on index and optional base tag.
    
    Args:
        tree: ttk.Treeview widget
        row_index: int, the index of the row
        base_tag: str, optional base tag (e.g., status, priority)
    
    Returns:
        tuple of tags to apply
    """
    tags = []
    
    # Add base tag if provided (e.g., status, priority)
    if base_tag:
        tags.append(base_tag)
    
    # Add alternating row color if no base tag
    if not base_tag:
        row_color = "evenrow" if row_index % 2 == 0 else "oddrow"
        tags.append(row_color)
    
    return tuple(tags) if tags else ()
