# -*- coding: utf-8 -*-
# modules/label_preferences.py
"""
Label Preferences Manager
Manages user preferences for label printing (size, cut lines, quantities, etc.)
"""

import json
from pathlib import Path


class LabelPreferences:
    """Manages label printing preferences with persistence to JSON file"""
    
    # Default preferences
    DEFAULT_PREFERENCES = {
        "default_label_size": "medium",
        "show_cut_lines": True,
        "default_quantity": 1,
        "auto_print_new_products": False,
        "paper_size": "letter",
        "last_output_directory": "labels/"
    }
    
    def __init__(self, config_file="label_preferences.json"):
        """
        Initialize preferences manager.
        
        Args:
            config_file: Path to JSON configuration file
        """
        self.config_file = Path(config_file)
        self.preferences = self.DEFAULT_PREFERENCES.copy()
        self.load()
    
    def load(self):
        """Load preferences from JSON file, or use defaults if file doesn't exist"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_prefs = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.preferences.update(loaded_prefs)
                return True
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load label preferences: {e}")
                print("Using default preferences")
                return False
        return False
    
    def save(self):
        """Save current preferences to JSON file"""
        try:
            # Ensure parent directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=4)
            return True
        except IOError as e:
            print(f"Error: Could not save label preferences: {e}")
            return False
    
    def get(self, key, default=None):
        """
        Get a preference value.
        
        Args:
            key: Preference key
            default: Default value if key doesn't exist
        
        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)
    
    def set(self, key, value):
        """
        Set a preference value and save to file.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.preferences[key] = value
        self.save()
    
    def get_all(self):
        """Get all preferences as a dictionary"""
        return self.preferences.copy()
    
    def reset_to_defaults(self):
        """Reset all preferences to default values and save"""
        self.preferences = self.DEFAULT_PREFERENCES.copy()
        self.save()
