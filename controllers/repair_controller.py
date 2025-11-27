# -*- coding: utf-8 -*-
# controllers/repair_controller.py
from modules import models
from modules.audit_logger import log_action

class RepairController:
    @staticmethod
    def get_all_repairs():
        return models.get_repairs()
    
    @staticmethod
    def create_repair(order_num, cust, phone, model, imei, problem, est_date, tech, total, note="", email=None, address=None):
        # Get or create customer record
        customer_id = None
        if cust or phone:
            customer_id = models.get_or_create_customer(
                name=cust or "Unknown",
                phone=phone,
                email=email,
                address=address,
                customer_type='Repairs'
            )
        
        # Create repair order with customer_id
        repair_id = models.create_repair_order(order_num, cust, phone, model, imei, problem, est_date, tech, note, total, customer_id)
        
        if repair_id:
            # Update customer repair statistics
            if customer_id:
                models.update_customer_repair(customer_id)
            
            log_action(
                user=cust,
                action_type="CREATE",
                entity_type="repair",
                entity_id=repair_id,
                description=f"Created repair order {order_num} for {model}"
            )
        return repair_id
    
    @staticmethod
    def get_repair_details(repair_id):
        return models.get_repair_details(repair_id)
    
    @staticmethod
    def add_part(repair_id, part_name, qty, price, cost):
        success = models.add_repair_part(repair_id, part_name, qty, price, cost)
        if success:
            log_action(
                user="System",
                action_type="UPDATE",
                entity_type="repair",
                entity_id=repair_id,
                description=f"Added part: {part_name} (qty: {qty})"
            )
        return success
    
    @staticmethod
    def update_status(repair_id, new_status, user, comment=""):
        # Get old status first
        try:
            order, _, _ = models.get_repair_details(repair_id)
            old_status = order[6] if order and len(order) > 6 else "Unknown"
        except:
            old_status = "Unknown"
        
        success = models.update_repair_status(repair_id, new_status, user, comment)
        if success:
            log_action(
                user=user,
                action_type="STATUS_CHANGE",
                entity_type="repair",
                entity_id=repair_id,
                old_value=old_status,
                new_value=new_status,
                description=f"Status changed from {old_status} to {new_status}"
            )
        return success

    
    @staticmethod
    def delete_repair(repair_id, user="System"):
        """
        Delete a repair order and all associated data.
        
        Args:
            repair_id: The repair order ID to delete
            user: User performing the deletion (for audit log)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get repair details before deletion for logging
        try:
            order, _, _ = models.get_repair_details(repair_id)
            if order:
                order_number = order[1] if len(order) > 1 else "Unknown"
                customer_name = order[2] if len(order) > 2 else "Unknown"
                device_model = order[4] if len(order) > 4 else "Unknown"
            else:
                order_number = "Unknown"
                customer_name = "Unknown"
                device_model = "Unknown"
        except:
            order_number = "Unknown"
            customer_name = "Unknown"
            device_model = "Unknown"
        
        # Delete the repair order (cascade will handle parts and history)
        success = models.delete_repair_order(repair_id)
        
        if success:
            log_action(
                user=user,
                action_type="DELETE",
                entity_type="repair",
                entity_id=repair_id,
                description=f"Deleted repair order {order_number} - Customer: {customer_name}, Device: {device_model}"
            )
        
        return success
