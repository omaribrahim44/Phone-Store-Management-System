# -*- coding: utf-8 -*-
# controllers/pos_controller.py
from modules import models
from modules.audit_logger import log_action

class POSController:
    @staticmethod
    def create_sale(customer_name, items, customer_phone=None, customer_email=None, customer_address=None, 
                   seller_name="System", discount_percent=0, payment_method="Cash", notes=None):
        """
        Create a comprehensive sale record with all details for reporting.
        
        Args:
            customer_name: Customer name
            items: list of dicts with keys: id, sku, name, category, qty, price, cost
            customer_phone: Customer phone (optional)
            customer_email: Customer email (optional)
            customer_address: Customer address (optional)
            seller_name: Name of the person making the sale
            discount_percent: Discount percentage applied
            payment_method: Payment method (Cash, Card, etc.)
            notes: Additional notes about the sale
        
        Returns:
            sale_id if successful, None otherwise
        """
        # Get or create customer
        customer_id = None
        if customer_name or customer_phone:
            customer_id = models.get_or_create_customer(
                name=customer_name or "Walk-in",
                phone=customer_phone,
                email=customer_email,
                address=customer_address,
                customer_type='Sales'
            )
        
        # Calculate totals
        subtotal = sum([i['qty'] * i['price'] for i in items])
        discount_amount = (subtotal * discount_percent) / 100
        total = subtotal - discount_amount
        
        # Create comprehensive sale record
        sale_id = models.create_sale_detailed(
            customer_name=customer_name,
            customer_id=customer_id,
            customer_phone=customer_phone,
            customer_email=customer_email,
            customer_address=customer_address,
            items=items,
            subtotal=subtotal,
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            total_amount=total,
            seller_name=seller_name,
            payment_method=payment_method,
            notes=notes
        )
        
        if sale_id:
            # Update customer statistics
            if customer_id:
                models.update_customer_purchase(customer_id, total)
            
            log_action(
                user=seller_name,
                action_type="CREATE",
                entity_type="sale",
                entity_id=sale_id,
                description=f"Sale by {seller_name} for {customer_name}, items: {len(items)}, total: EGP {total:.2f}"
            )
        return sale_id
    
    @staticmethod
    def get_sales_history():
        return models.get_sales_history()
