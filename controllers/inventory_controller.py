# -*- coding: utf-8 -*-
# controllers/inventory_controller.py
from modules import models
from modules.audit_logger import log_action
from modules.quick_add_templates import get_templates

class InventoryController:
    @staticmethod
    def get_all_items():
        return models.get_inventory()
    
    @staticmethod
    def add_item(sku, name, qty, buy, sell, category, desc, storage=None, ram=None, color=None, 
                 condition=None, brand=None, model=None, warranty_months=None):
        """Add item with optional phone specifications"""
        success = models.add_inventory_item(
            sku, name, qty, buy, sell, category, desc,
            storage=storage, ram=ram, color=color, condition=condition,
            brand=brand, model=model, warranty_months=warranty_months
        )
        if success:
            specs_info = []
            if storage: specs_info.append(f"Storage: {storage}")
            if ram: specs_info.append(f"RAM: {ram}")
            if color: specs_info.append(f"Color: {color}")
            specs_str = ", ".join(specs_info) if specs_info else ""
            
            log_action(
                user="System",
                action_type="CREATE",
                entity_type="inventory",
                description=f"Added inventory item: {name} (SKU: {sku}, Qty: {qty}, Cat: {category}" + 
                           (f", {specs_str}" if specs_str else "") + ")"
            )
        return success
    
    @staticmethod
    def get_item_cost(name_or_sku):
        return models.get_item_cost(name_or_sku)
    
    @staticmethod
    def update_item(item_id, sku, name, category, qty, buy_price, sell_price, description=None, storage=None, ram=None, color=None):
        """Update an inventory item with optional mobile specifications"""
        success = models.update_inventory_item(item_id, sku, name, category, qty, buy_price, sell_price, description, storage, ram, color)
        if success:
            log_action(
                user="System",
                action_type="UPDATE",
                entity_type="inventory",
                description=f"Updated inventory item: {name} (SKU: {sku}, New Qty: {qty})"
            )
        return success
    
    @staticmethod
    def delete_item(item_id, item_name, sku):
        """Delete an inventory item by ID"""
        success = models.delete_inventory_item(item_id)
        if success:
            log_action(
                user="System",
                action_type="DELETE",
                entity_type="inventory",
                description=f"Deleted inventory item: {item_name} (SKU: {sku}, ID: {item_id})"
            )
        return success
    
    @staticmethod
    def add_product_from_quick_add(product_data):
        """
        Add a product from Quick Add dialog with validation.
        
        Args:
            product_data: Dictionary containing product fields
                Required: name, sku, category, quantity, buy_price, sell_price
                Optional: description, storage, ram, color, condition, brand, model, warranty_months
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # Validate required fields
        is_valid, error_msg = InventoryController.validate_required_fields(product_data)
        if not is_valid:
            return (False, error_msg)
        
        # Extract fields
        sku = product_data.get('sku', '')
        name = product_data.get('name', '')
        quantity = product_data.get('quantity', 0)
        buy_price = product_data.get('buy_price', 0.0)
        sell_price = product_data.get('sell_price', 0.0)
        category = product_data.get('category', '')
        description = product_data.get('description', '')
        
        # Optional phone specifications
        storage = product_data.get('storage')
        ram = product_data.get('ram')
        color = product_data.get('color')
        condition = product_data.get('condition')
        brand = product_data.get('brand')
        model = product_data.get('model')
        warranty_months = product_data.get('warranty_months')
        
        # Add the product
        success = InventoryController.add_item(
            sku=sku,
            name=name,
            qty=quantity,
            buy=buy_price,
            sell=sell_price,
            category=category,
            desc=description,
            storage=storage,
            ram=ram,
            color=color,
            condition=condition,
            brand=brand,
            model=model,
            warranty_months=warranty_months
        )
        
        if success:
            return (True, f"Product '{name}' added successfully with SKU: {sku}")
        else:
            return (False, "Failed to add product. Please check the data and try again.")
    
    @staticmethod
    def validate_required_fields(product_data):
        """
        Validate that all required fields are present and valid.
        
        Args:
            product_data: Dictionary containing product fields
        
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        required_fields = {
            'name': 'Product Name',
            'sku': 'SKU',
            'category': 'Category',
            'quantity': 'Quantity',
            'buy_price': 'Buy Price',
            'sell_price': 'Sell Price'
        }
        
        missing_fields = []
        for field, display_name in required_fields.items():
            value = product_data.get(field)
            if value is None or value == '' or (isinstance(value, str) and value.strip() == ''):
                missing_fields.append(display_name)
        
        if missing_fields:
            return (False, f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate data types and values
        try:
            quantity = int(product_data.get('quantity', 0))
            if quantity < 0:
                return (False, "Quantity must be a positive number")
        except (ValueError, TypeError):
            return (False, "Quantity must be a valid number")
        
        try:
            buy_price = float(product_data.get('buy_price', 0))
            if buy_price < 0:
                return (False, "Buy Price must be a positive number")
        except (ValueError, TypeError):
            return (False, "Buy Price must be a valid number")
        
        try:
            sell_price = float(product_data.get('sell_price', 0))
            if sell_price < 0:
                return (False, "Sell Price must be a positive number")
        except (ValueError, TypeError):
            return (False, "Sell Price must be a valid number")
        
        return (True, "")
    
    @staticmethod
    def generate_unique_sku(prefix="ITEM-"):
        """
        Generate a unique SKU using the templates module.
        
        Args:
            prefix: SKU prefix (default: "ITEM-")
        
        Returns:
            str: Unique SKU
        """
        templates = get_templates()
        return templates.generate_sku(prefix)
