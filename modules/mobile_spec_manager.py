"""
Mobile Specification Manager Module

This module manages mobile phone specifications (storage, RAM, color) for inventory management.
It provides category detection, dropdown options, validation, and formatting functionality.

Author: Kiro AI
Date: 2025-11-27
"""

from typing import List, Tuple, Optional


class MobileSpecManager:
    """
    Manages mobile specification fields in inventory dialogs.
    
    This class provides static methods for:
    - Detecting mobile categories
    - Providing dropdown options for storage, RAM, and color
    - Validating mobile specifications
    - Formatting specifications for display
    """
    
    # Mobile category keywords (case-insensitive)
    MOBILE_CATEGORIES = ["mobile", "phone", "smartphone"]
    
    # Storage options sorted by size (ascending)
    STORAGE_OPTIONS = ["64GB", "128GB", "256GB", "512GB", "1TB", "2TB"]
    
    # RAM options sorted by size (ascending)
    RAM_OPTIONS = ["2GB", "3GB", "4GB", "6GB", "8GB", "12GB", "16GB", "18GB"]
    
    # Color options sorted alphabetically
    COLOR_OPTIONS = [
        "Black", "Blue", "Gold", "Gray", "Green", 
        "Other", "Pink", "Purple", "Red", "Silver", "White"
    ]
    
    @staticmethod
    def is_mobile_category(category: str) -> bool:
        """
        Check if a category requires mobile specifications.
        
        Args:
            category: The product category to check
            
        Returns:
            True if the category is a mobile category, False otherwise
            
        Examples:
            >>> MobileSpecManager.is_mobile_category("Mobile")
            True
            >>> MobileSpecManager.is_mobile_category("Phone")
            True
            >>> MobileSpecManager.is_mobile_category("Laptop")
            False
        """
        if not category:
            return False
        
        category_lower = category.lower().strip()
        
        # Check if any mobile keyword is in the category name
        return any(keyword in category_lower for keyword in MobileSpecManager.MOBILE_CATEGORIES)
    
    @staticmethod
    def get_storage_options() -> List[str]:
        """
        Get list of storage options for dropdown.
        
        Returns:
            List of storage options sorted by size (ascending)
            
        Examples:
            >>> MobileSpecManager.get_storage_options()
            ['64GB', '128GB', '256GB', '512GB', '1TB', '2TB']
        """
        return MobileSpecManager.STORAGE_OPTIONS.copy()
    
    @staticmethod
    def get_ram_options() -> List[str]:
        """
        Get list of RAM options for dropdown.
        
        Returns:
            List of RAM options sorted by size (ascending)
            
        Examples:
            >>> MobileSpecManager.get_ram_options()
            ['2GB', '3GB', '4GB', '6GB', '8GB', '12GB', '16GB', '18GB']
        """
        return MobileSpecManager.RAM_OPTIONS.copy()
    
    @staticmethod
    def get_color_options() -> List[str]:
        """
        Get list of color options for dropdown.
        
        Returns:
            List of color options sorted alphabetically
            
        Examples:
            >>> MobileSpecManager.get_color_options()
            ['Black', 'Blue', 'Gold', 'Gray', 'Green', 'Other', 'Pink', 'Purple', 'Red', 'Silver', 'White']
        """
        return MobileSpecManager.COLOR_OPTIONS.copy()

    
    @staticmethod
    def validate_specs(storage: Optional[str], ram: Optional[str], color: Optional[str], 
                      category: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate mobile specifications.
        
        Args:
            storage: Storage capacity value
            ram: RAM capacity value
            color: Color value
            category: Optional category to check if validation is needed
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if all specs are valid, False otherwise
            - error_message: Empty string if valid, error message if invalid
            
        Examples:
            >>> MobileSpecManager.validate_specs("256GB", "8GB", "Black")
            (True, '')
            >>> MobileSpecManager.validate_specs("", "8GB", "Black")
            (False, 'Please fill in the following mobile specifications:\\n  • Storage')
        """
        # If category is provided and it's not a mobile category, skip validation
        if category and not MobileSpecManager.is_mobile_category(category):
            return (True, "")
        
        missing_fields = []
        
        # Check for missing or empty fields
        if not storage or not storage.strip():
            missing_fields.append("Storage")
        if not ram or not ram.strip():
            missing_fields.append("RAM")
        if not color or not color.strip():
            missing_fields.append("Color")
        
        # If any fields are missing, return error
        if missing_fields:
            error_msg = "Please fill in the following mobile specifications:\n" + \
                       "\n".join(f"  • {field}" for field in missing_fields)
            return (False, error_msg)
        
        return (True, "")
    
    @staticmethod
    def format_specs_display(storage: Optional[str], ram: Optional[str], 
                            color: Optional[str]) -> str:
        """
        Format specifications for display in inventory table.
        
        Args:
            storage: Storage capacity value
            ram: RAM capacity value
            color: Color value
            
        Returns:
            Formatted string in format "Storage | RAM | Color"
            Returns "N/A" if all specs are missing
            Returns partial format if some specs are present
            
        Examples:
            >>> MobileSpecManager.format_specs_display("256GB", "8GB", "Black")
            '256GB | 8GB | Black'
            >>> MobileSpecManager.format_specs_display(None, None, None)
            'N/A'
            >>> MobileSpecManager.format_specs_display("256GB", "", "Black")
            '256GB | Black'
        """
        # Collect non-empty specs
        specs = []
        
        if storage and storage.strip():
            specs.append(storage.strip())
        if ram and ram.strip():
            specs.append(ram.strip())
        if color and color.strip():
            specs.append(color.strip())
        
        # If no specs, return N/A
        if not specs:
            return "N/A"
        
        # Join specs with separator
        return " | ".join(specs)
