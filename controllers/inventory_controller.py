# controllers/inventory_controller.py
from modules import models
from modules.audit_logger import log_action

class InventoryController:
    @staticmethod
    def get_all_items():
        return models.get_inventory()
    
    @staticmethod
    def add_item(sku, name, qty, buy, sell, category, desc):
        success = models.add_inventory_item(sku, name, qty, buy, sell, category, desc)
        if success:
            log_action(
                user="System",
                action_type="CREATE",
                entity_type="inventory",
                description=f"Added inventory item: {name} (SKU: {sku}, Qty: {qty}, Cat: {category})"
            )
        return success
    
    @staticmethod
    def get_item_cost(name_or_sku):
        return models.get_item_cost(name_or_sku)
    
    @staticmethod
    def update_item(item_id, sku, name, category, qty, buy_price, sell_price, description=None):
        """Update an inventory item"""
        success = models.update_inventory_item(item_id, sku, name, category, qty, buy_price, sell_price, description)
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
