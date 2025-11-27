# -*- coding: utf-8 -*-
# modules/barcode_lookup.py
"""
Barcode lookup module for automatic product information retrieval.
Supports multiple lookup methods:
1. Local database (existing products)
2. External API lookup (future enhancement)
3. Manual product database
"""

from modules.db import get_conn
import json
import os

class BarcodeDatabase:
    """Manages a local database of barcode -> product mappings"""
    
    def __init__(self):
        self.db_file = "barcode_products.json"
        self.load_database()
    
    def load_database(self):
        """Load barcode database from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
            except:
                self.products = {}
        else:
            self.products = self._get_default_products()
            self.save_database()
    
    def save_database(self):
        """Save barcode database to JSON file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving barcode database: {e}")
    
    def _get_default_products(self):
        """Default product database with common phones"""
        return {
            # iPhone Examples
            "194252707050": {
                "name": "iPhone 14 Pro Max",
                "brand": "Apple",
                "model": "iPhone 14 Pro Max",
                "category": "Mobile Phones",
                "storage": "256GB",
                "ram": "6GB",
                "color": "Deep Purple",
                "condition": "New",
                "buy_price": 45000.00,
                "sell_price": 52000.00,
                "warranty_months": 12,
                "description": "Latest iPhone with Dynamic Island"
            },
            "194253001799": {
                "name": "iPhone 15 Pro",
                "brand": "Apple",
                "model": "iPhone 15 Pro",
                "category": "Mobile Phones",
                "storage": "256GB",
                "ram": "8GB",
                "color": "Natural Titanium",
                "condition": "New",
                "buy_price": 48000.00,
                "sell_price": 55000.00,
                "warranty_months": 12,
                "description": "iPhone 15 Pro with A17 Pro chip"
            },
            # Samsung Examples
            "8806094937350": {
                "name": "Samsung Galaxy S24 Ultra",
                "brand": "Samsung",
                "model": "Galaxy S24 Ultra",
                "category": "Mobile Phones",
                "storage": "512GB",
                "ram": "12GB",
                "color": "Titanium Black",
                "condition": "New",
                "buy_price": 50000.00,
                "sell_price": 58000.00,
                "warranty_months": 12,
                "description": "Samsung flagship with S Pen"
            },
            # Xiaomi Examples
            "6941812738894": {
                "name": "Xiaomi 14 Pro",
                "brand": "Xiaomi",
                "model": "Xiaomi 14 Pro",
                "category": "Mobile Phones",
                "storage": "256GB",
                "ram": "12GB",
                "color": "Black",
                "condition": "New",
                "buy_price": 28000.00,
                "sell_price": 33000.00,
                "warranty_months": 12,
                "description": "Xiaomi flagship with Leica camera"
            }
        }
    
    def lookup(self, barcode):
        """
        Look up product information by barcode.
        
        Args:
            barcode: Barcode string
        
        Returns:
            dict with product info or None if not found
        """
        # First check local database
        if barcode in self.products:
            return self.products[barcode].copy()
        
        # Check if product exists in inventory
        product = self.lookup_in_inventory(barcode)
        if product:
            return product
        
        return None
    
    def lookup_in_inventory(self, barcode):
        """Look up product in existing inventory by SKU or barcode"""
        conn = get_conn()
        c = conn.cursor()
        
        # Try to find by SKU or barcode field
        c.execute("""SELECT name, category, buy_price, sell_price, storage, ram, color, 
                            condition, brand, model, warranty_months, description
                     FROM inventory 
                     WHERE sku = ? OR barcode = ?
                     LIMIT 1""", (barcode, barcode))
        
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                "name": row[0],
                "category": row[1],
                "buy_price": row[2],
                "sell_price": row[3],
                "storage": row[4],
                "ram": row[5],
                "color": row[6],
                "condition": row[7],
                "brand": row[8],
                "model": row[9],
                "warranty_months": row[10],
                "description": row[11]
            }
        
        return None
    
    def add_product(self, barcode, product_info):
        """Add a new product to the barcode database"""
        self.products[barcode] = product_info
        self.save_database()
    
    def remove_product(self, barcode):
        """Remove a product from the barcode database"""
        if barcode in self.products:
            del self.products[barcode]
            self.save_database()
            return True
        return False
    
    def get_all_products(self):
        """Get all products in the database"""
        return self.products.copy()


# Global instance
_barcode_db = None

def get_barcode_database():
    """Get or create the global barcode database instance"""
    global _barcode_db
    if _barcode_db is None:
        _barcode_db = BarcodeDatabase()
    return _barcode_db


def lookup_barcode(barcode):
    """
    Convenience function to lookup a barcode.
    
    Args:
        barcode: Barcode string
    
    Returns:
        dict with product info or None if not found
    """
    db = get_barcode_database()
    return db.lookup(barcode)
