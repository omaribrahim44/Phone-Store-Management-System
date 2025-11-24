# ui/styles.py
import ttkbootstrap as tb
from tkinter import ttk

def apply_styles(theme_name="flatly"):
    """
    Applies global styles to the application.
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
    
    # Treeview styles - Better spacing and readability
    style.configure("Treeview", font=default_font, rowheight=32)
    style.configure("Treeview.Heading", font=header_font, padding=8)
    
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
