"""
Specification Preference Manager Module

This module manages user preferences for mobile specifications, including
remembering last-used values for storage, RAM, and color across sessions.

Author: Kiro AI
Date: 2025-11-27
"""

import json
import os
from typing import Dict, Optional


class SpecPreferenceManager:
    """
    Manages user preferences for mobile specifications.
    
    This class handles:
    - Loading preferences from JSON file
    - Saving last-used specification values
    - Retrieving last-used values
    - Resetting to default values
    - Graceful handling of corrupted or missing files
    """
    
    # Default preference values
    DEFAULT_PREFERENCES = {
        "last_storage": "128GB",
        "last_ram": "8GB",
        "last_color": "Black",
        "storage_options": ["64GB", "128GB", "256GB", "512GB", "1TB", "2TB"],
        "ram_options": ["2GB", "3GB", "4GB", "6GB", "8GB", "12GB", "16GB", "18GB"],
        "color_options": [
            "Black", "White", "Blue", "Red", "Green",
            "Gold", "Silver", "Purple", "Pink", "Gray", "Other"
        ],
        "mobile_categories": ["Mobile", "Phone", "Smartphone"],
        "auto_focus_enabled": True,
        "remember_last_values": True
    }
    
    def __init__(self, pref_file: str = "mobile_spec_preferences.json"):
        """
        Initialize the preference manager.
        
        Args:
            pref_file: Path to the preference file (default: mobile_spec_preferences.json)
        """
        self.pref_file = pref_file
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict:
        """
        Load preferences from JSON file.
        
        Returns:
            Dictionary containing preferences
            
        If the file doesn't exist or is corrupted, returns default preferences
        and creates a new file with defaults.
        """
        try:
            if os.path.exists(self.pref_file):
                with open(self.pref_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    
                # Merge with defaults to ensure all keys exist
                merged_prefs = self.DEFAULT_PREFERENCES.copy()
                merged_prefs.update(prefs)
                return merged_prefs
            else:
                # File doesn't exist, create with defaults
                self._save_preferences(self.DEFAULT_PREFERENCES)
                return self.DEFAULT_PREFERENCES.copy()
                
        except (json.JSONDecodeError, IOError) as e:
            # File is corrupted or can't be read, use defaults
            print(f"Warning: Could not load preferences from {self.pref_file}: {e}")
            print("Using default preferences and creating new file.")
            self._save_preferences(self.DEFAULT_PREFERENCES)
            return self.DEFAULT_PREFERENCES.copy()
    
    def _save_preferences(self, prefs: Dict) -> bool:
        """
        Save preferences to JSON file.
        
        Args:
            prefs: Dictionary of preferences to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.pref_file, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error: Could not save preferences to {self.pref_file}: {e}")
            return False

    
    def get_last_storage(self) -> str:
        """
        Get the last-used storage value.
        
        Returns:
            Last-used storage value (e.g., "256GB")
            
        Examples:
            >>> manager = SpecPreferenceManager()
            >>> manager.get_last_storage()
            '128GB'
        """
        return self.preferences.get("last_storage", self.DEFAULT_PREFERENCES["last_storage"])
    
    def get_last_ram(self) -> str:
        """
        Get the last-used RAM value.
        
        Returns:
            Last-used RAM value (e.g., "8GB")
            
        Examples:
            >>> manager = SpecPreferenceManager()
            >>> manager.get_last_ram()
            '8GB'
        """
        return self.preferences.get("last_ram", self.DEFAULT_PREFERENCES["last_ram"])
    
    def get_last_color(self) -> str:
        """
        Get the last-used color value.
        
        Returns:
            Last-used color value (e.g., "Black")
            
        Examples:
            >>> manager = SpecPreferenceManager()
            >>> manager.get_last_color()
            'Black'
        """
        return self.preferences.get("last_color", self.DEFAULT_PREFERENCES["last_color"])
    
    def get_all_last_specs(self) -> Dict[str, str]:
        """
        Get all last-used specification values as a dictionary.
        
        Returns:
            Dictionary with keys: last_storage, last_ram, last_color
            
        Examples:
            >>> manager = SpecPreferenceManager()
            >>> manager.get_all_last_specs()
            {'last_storage': '128GB', 'last_ram': '8GB', 'last_color': 'Black'}
        """
        return {
            "last_storage": self.get_last_storage(),
            "last_ram": self.get_last_ram(),
            "last_color": self.get_last_color()
        }
    
    def save_last_specs(self, storage: str, ram: str, color: str) -> bool:
        """
        Save last-used specification values.
        
        Args:
            storage: Storage value to remember (e.g., "256GB")
            ram: RAM value to remember (e.g., "8GB")
            color: Color value to remember (e.g., "Black")
            
        Returns:
            True if saved successfully, False otherwise
            
        Examples:
            >>> manager = SpecPreferenceManager()
            >>> manager.save_last_specs("256GB", "12GB", "Blue")
            True
        """
        # Update in-memory preferences
        self.preferences["last_storage"] = storage
        self.preferences["last_ram"] = ram
        self.preferences["last_color"] = color
        
        # Save to file
        return self._save_preferences(self.preferences)
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all preferences to default values.
        
        Returns:
            True if reset successfully, False otherwise
            
        Examples:
            >>> manager = SpecPreferenceManager()
            >>> manager.reset_to_defaults()
            True
        """
        self.preferences = self.DEFAULT_PREFERENCES.copy()
        return self._save_preferences(self.preferences)
