# -*- coding: utf-8 -*-
# modules/quick_add_templates.py
"""
Quick Add Templates for fast bulk inventory entry.
Allows creating product templates with pre-filled common values.
"""

import json
import os
from datetime import datetime

class QuickAddTemplates:
    """Manages quick add templates for inventory"""
    
    def __init__(self):
        self.templates_file = "quick_add_templates.json"
        self.load_templates()
    
    def load_templates(self):
        """Load templates from file"""
        if os.path.exists(self.templates_file):
            try:
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except:
                self.templates = self.get_default_templates()
        else:
            self.templates = self.get_default_templates()
            self.save_templates()
    
    def save_templates(self):
        """Save templates to file"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving templates: {e}")
    
    def get_default_templates(self):
        """Default quick add templates"""
        return {
            "Chinese Phone - Generic": {
                "category": "Mobile Phones",
                "condition": "New",
                "warranty_months": 12,
                "buy_price": 0,
                "sell_price": 0,
                "description": "Imported phone",
                "auto_sku": True,  # Auto-generate SKU
                "sku_prefix": "CN-"
            },
            "iPhone - Used": {
                "category": "Mobile Phones",
                "brand": "Apple",
                "condition": "Used - Good",
                "warranty_months": 3,
                "buy_price": 0,
                "sell_price": 0,
                "auto_sku": True,
                "sku_prefix": "IP-USED-"
            },
            "Samsung - New": {
                "category": "Mobile Phones",
                "brand": "Samsung",
                "condition": "New",
                "warranty_months": 12,
                "buy_price": 0,
                "sell_price": 0,
                "auto_sku": True,
                "sku_prefix": "SAM-"
            },
            "Phone Accessory": {
                "category": "Phone Accessories",
                "condition": "New",
                "warranty_months": 6,
                "buy_price": 0,
                "sell_price": 0,
                "auto_sku": True,
                "sku_prefix": "ACC-"
            },
            "Screen Protector": {
                "category": "Screen Protectors",
                "condition": "New",
                "warranty_months": 0,
                "buy_price": 0,
                "sell_price": 0,
                "auto_sku": True,
                "sku_prefix": "SP-"
            }
        }
    
    def get_template(self, template_name):
        """Get a specific template"""
        return self.templates.get(template_name, {}).copy()
    
    def get_all_templates(self):
        """Get all template names"""
        return list(self.templates.keys())
    
    def add_template(self, name, template_data):
        """Add a new template"""
        self.templates[name] = template_data
        self.save_templates()
    
    def delete_template(self, name):
        """Delete a template"""
        if name in self.templates:
            del self.templates[name]
            self.save_templates()
            return True
        return False
    
    def generate_sku(self, prefix="ITEM-"):
        """Generate a unique SKU"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{prefix}{timestamp}"


# Global instance
_templates = None

def get_templates():
    """Get or create the global templates instance"""
    global _templates
    if _templates is None:
        _templates = QuickAddTemplates()
    return _templates
