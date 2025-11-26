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
