# -*- coding: utf-8 -*-
# modules/barcode_config.py
"""
Barcode scanner configuration and settings.
Handles different scanner types and auto-configuration.
"""

import json
import os

class BarcodeScannerConfig:
    """Manages barcode scanner configuration"""
    
    def __init__(self):
        self.config_file = "barcode_scanner_config.json"
        self.load_config()
    
    def load_config(self):
        """Load scanner configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def save_config(self):
        """Save scanner configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving scanner config: {e}")
    
    def get_default_config(self):
        """Default scanner configuration"""
        return {
            "scanner_type": "USB",  # USB, Bluetooth, Wireless
            "auto_enter": True,  # Scanner sends Enter after scan
            "prefix": "",  # Prefix to strip from barcode
            "suffix": "",  # Suffix to strip from barcode
            "min_length": 8,  # Minimum barcode length
            "max_length": 20,  # Maximum barcode length
            "beep_on_success": True,  # Beep when product found
            "beep_on_error": True,  # Beep when product not found
            "auto_quantity": 1,  # Default quantity to add
            "quick_add_mode": True,  # Add without confirmation
            "duplicate_handling": "increment",  # increment, skip, ask
            "scan_delay_ms": 100,  # Delay between scans (prevent double-scan)
            "default_category": "Mobile Phones",
            "default_condition": "New",
            "default_warranty": 12
        }
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates):
        """Update multiple configuration values"""
        self.config.update(updates)
        self.save_config()


# Global instance
_scanner_config = None

def get_scanner_config():
    """Get or create the global scanner config instance"""
    global _scanner_config
    if _scanner_config is None:
        _scanner_config = BarcodeScannerConfig()
    return _scanner_config
