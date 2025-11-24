# config.py
import os
import json

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "shop.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")
CONFIG_FILE = os.path.join(BASE_DIR, "shop_config.json")

# Default Settings
DEFAULT_SHOP_INFO = {
    "name": "Mobile Care Center",
    "address": "123 Tech Street, Downtown",
    "phone": "+20 123 456 7890",
    "email": "info@mobilecare.com",
    "currency": "EGP",
    "tax_rate": 14.0,  # Egypt VAT rate
    "logo_path": "assets/logo.png",
    "theme": "cosmo"
}

DEFAULT_CONFIG = {
    "database": {
        "path": str(DB_PATH)
    },
    "logging": {
        "log_file": str(LOG_FILE),
        "level": "INFO"
    },
    "shop_info": DEFAULT_SHOP_INFO,
    "theme": "cosmo",
    "backup": {
        "auto_backup_enabled": True,
        "auto_backup_frequency": "daily",
        "last_backup_date": None,
        "max_backups": 10
    }
}

def load_config():
    """Load shop configuration from JSON file, or return defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge with defaults to ensure all keys exist
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    """Save configuration to JSON file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
