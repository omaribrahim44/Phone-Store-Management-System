# controllers/pos_controller.py
from modules import models
from modules.audit_logger import log_action

class POSController:
    @staticmethod
    def create_sale(customer_name, items, customer_phone=None, customer_email=None, customer_address=None):
        """
        items: list of tuples (item_id, qty, unit_price, cost_price)
        Creates sale and links to customer
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
        
        # Create sale
        sale_id = models.create_sale(customer_name, items, customer_id)
        
        if sale_id:
            total = sum([i[1] * i[2] for i in items])
            
            # Update customer statistics
            if customer_id:
                models.update_customer_purchase(customer_id, total)
            
            log_action(
                user=customer_name,
                action_type="CREATE",
                entity_type="sale",
                entity_id=sale_id,
                description=f"Created sale for {customer_name}, total: {total:.2f}"
            )
        return sale_id
    
    @staticmethod
    def get_sales_history():
        return models.get_sales_history()
