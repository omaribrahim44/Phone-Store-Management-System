# modules/constants.py
"""
Centralized constants for the application to ensure consistency across all modules.
"""

# Product Categories - Used across Inventory, POS, and all related modules
PRODUCT_CATEGORIES = [
    "Mobile Phones",
    "Phone Cases & Covers",
    "Chargers & Cables",
    "AirPods & Earphones",
    "Screen Protectors",
    "Phone Accessories",
    "Repair Parts",
    "Other"
]

# Payment Methods
PAYMENT_METHODS = [
    "Cash",
    "Card",
    "Bank Transfer",
    "Mobile Payment"
]

# User Roles
USER_ROLES = [
    "Admin",
    "Cashier",
    "Technician"
]

# Repair Status Options
REPAIR_STATUS = [
    "Pending",
    "In Progress",
    "Completed",
    "Delivered",
    "Cancelled"
]
