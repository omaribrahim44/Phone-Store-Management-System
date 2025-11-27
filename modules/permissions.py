# modules/permissions.py
"""
Role-Based Access Control (RBAC) System
Defines permissions for different user roles
"""

# Define all available permissions
PERMISSIONS = {
    # User Management
    'manage_users': 'Create, edit, and delete users',
    'view_users': 'View user list',
    'change_passwords': 'Change user passwords',
    
    # Inventory Management
    'manage_inventory': 'Add, edit, and delete inventory items',
    'view_inventory': 'View inventory',
    'adjust_prices': 'Modify buy/sell prices',
    
    # Sales
    'create_sale': 'Create new sales',
    'view_sales': 'View sales history',
    'delete_sale': 'Delete sales records',
    'apply_discount': 'Apply discounts to sales',
    
    # Repairs
    'create_repair': 'Create new repair orders',
    'view_repairs': 'View repair orders',
    'edit_repair': 'Edit repair orders',
    'delete_repair': 'Delete repair orders',
    'change_repair_status': 'Change repair status',
    
    # Customers
    'manage_customers': 'Add, edit, and delete customers',
    'view_customers': 'View customer list',
    
    # Reports
    'view_reports': 'View reports and analytics',
    'export_data': 'Export data to CSV/PDF',
    
    # Settings
    'manage_settings': 'Modify system settings',
    'view_logs': 'View audit logs',
    'manage_backups': 'Create and restore backups',
}

# Define role permissions
ROLE_PERMISSIONS = {
    'Admin': [
        # Full access to everything
        'manage_users',
        'view_users',
        'change_passwords',
        'manage_inventory',
        'view_inventory',
        'adjust_prices',
        'create_sale',
        'view_sales',
        'delete_sale',
        'apply_discount',
        'create_repair',
        'view_repairs',
        'edit_repair',
        'delete_repair',
        'change_repair_status',
        'manage_customers',
        'view_customers',
        'view_reports',
        'export_data',
        'manage_settings',
        'view_logs',
        'manage_backups',
    ],
    
    'Manager': [
        # Can manage operations but not users or settings
        'view_users',
        'manage_inventory',
        'view_inventory',
        'adjust_prices',
        'create_sale',
        'view_sales',
        'apply_discount',
        'create_repair',
        'view_repairs',
        'edit_repair',
        'change_repair_status',
        'manage_customers',
        'view_customers',
        'view_reports',
        'export_data',
        'view_logs',
    ],
    
    'Cashier': [
        # Can only perform sales and basic operations
        'view_inventory',
        'create_sale',
        'view_sales',
        'create_repair',
        'view_repairs',
        'view_customers',
    ],
}


class PermissionError(Exception):
    """Raised when user lacks required permission"""
    pass


def has_permission(user_role: str, permission: str) -> bool:
    """
    Check if a user role has a specific permission.
    
    Args:
        user_role: User's role (Admin, Manager, Cashier)
        permission: Permission to check
    
    Returns:
        True if user has permission, False otherwise
    """
    if not user_role:
        return False
    
    # Admin has all permissions
    if user_role == 'Admin':
        return True
    
    # Check if role exists and has permission
    role_perms = ROLE_PERMISSIONS.get(user_role, [])
    return permission in role_perms


def get_user_permissions(user_role: str) -> list:
    """
    Get all permissions for a user role.
    
    Args:
        user_role: User's role
    
    Returns:
        List of permission strings
    """
    if user_role == 'Admin':
        return list(PERMISSIONS.keys())
    
    return ROLE_PERMISSIONS.get(user_role, [])


def require_permission(permission: str):
    """
    Decorator to check if current user has required permission.
    Raises PermissionError if user lacks permission.
    
    Usage:
        @require_permission('manage_inventory')
        def delete_item(item_id):
            # Only users with manage_inventory permission can call this
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get current user from session
            from modules.session import get_current_user
            user = get_current_user()
            
            if not user:
                raise PermissionError("No user logged in")
            
            user_role = user.get('role', '')
            
            if not has_permission(user_role, permission):
                raise PermissionError(
                    f"User role '{user_role}' lacks permission: {permission}"
                )
            
            return func(*args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


def check_permission_silent(user_role: str, permission: str) -> bool:
    """
    Check permission without raising exception.
    Useful for UI elements that should be hidden/disabled.
    
    Args:
        user_role: User's role
        permission: Permission to check
    
    Returns:
        True if user has permission, False otherwise
    """
    return has_permission(user_role, permission)


def get_role_description(role: str) -> str:
    """Get human-readable description of role capabilities"""
    descriptions = {
        'Admin': 'Full system access - can manage users, settings, and all operations',
        'Manager': 'Can manage inventory, sales, repairs, and view reports',
        'Cashier': 'Can create sales, repairs, and view basic information',
    }
    return descriptions.get(role, 'Unknown role')
