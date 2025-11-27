# -*- coding: utf-8 -*-
# modules/smart_barcode_entry.py
"""
Smart barcode entry widget with auto-detection and configuration.
Handles different scanner types and provides intelligent input processing.
"""

import time
from datetime import datetime

class SmartBarcodeProcessor:
    """Processes barcode input with intelligent filtering and validation"""
    
    def __init__(self, config):
        self.config = config
        self.last_scan_time = 0
        self.scan_buffer = []
        self.last_barcode = None
    
    def process_input(self, raw_input):
        """
        Process raw barcode input with filtering and validation.
        
        Args:
            raw_input: Raw string from scanner
        
        Returns:
            tuple: (is_valid, cleaned_barcode, message)
        """
        # Check scan delay to prevent double-scanning
        current_time = time.time() * 1000  # milliseconds
        scan_delay = self.config.get('scan_delay_ms', 100)
        
        if current_time - self.last_scan_time < scan_delay:
            return (False, None, "Too fast - preventing double scan")
        
        self.last_scan_time = current_time
        
        # Clean the input
        barcode = raw_input.strip()
        
        # Remove prefix if configured
        prefix = self.config.get('prefix', '')
        if prefix and barcode.startswith(prefix):
            barcode = barcode[len(prefix):]
        
        # Remove suffix if configured
        suffix = self.config.get('suffix', '')
        if suffix and barcode.endswith(suffix):
            barcode = barcode[:-len(suffix)]
        
        # Validate length
        min_len = self.config.get('min_length', 8)
        max_len = self.config.get('max_length', 20)
        
        if len(barcode) < min_len:
            return (False, None, f"Barcode too short (min {min_len} characters)")
        
        if len(barcode) > max_len:
            return (False, None, f"Barcode too long (max {max_len} characters)")
        
        # Check for duplicate
        if barcode == self.last_barcode:
            duplicate_handling = self.config.get('duplicate_handling', 'increment')
            if duplicate_handling == 'skip':
                return (False, None, "Duplicate scan - skipped")
        
        self.last_barcode = barcode
        
        return (True, barcode, "Valid barcode")
    
    def reset(self):
        """Reset the processor state"""
        self.last_scan_time = 0
        self.scan_buffer = []
        self.last_barcode = None


class BarcodeInputHelper:
    """Helper for barcode input with keyboard detection"""
    
    def __init__(self):
        self.input_buffer = []
        self.last_key_time = 0
        self.scanner_speed_threshold = 50  # ms between keystrokes for scanner
    
    def is_scanner_input(self, key_time):
        """
        Detect if input is from scanner (fast typing) or keyboard (slow typing).
        
        Scanners typically input at 10-50ms per character.
        Humans typically type at 100-300ms per character.
        """
        if not self.last_key_time:
            self.last_key_time = key_time
            return True
        
        time_diff = key_time - self.last_key_time
        self.last_key_time = key_time
        
        return time_diff < self.scanner_speed_threshold
    
    def add_character(self, char):
        """Add character to buffer"""
        current_time = time.time() * 1000
        
        # If too much time passed, reset buffer (new input)
        if current_time - self.last_key_time > 200:
            self.input_buffer = []
        
        self.input_buffer.append(char)
        self.last_key_time = current_time
    
    def get_buffer(self):
        """Get current buffer content"""
        return ''.join(self.input_buffer)
    
    def clear_buffer(self):
        """Clear the input buffer"""
        self.input_buffer = []
        self.last_key_time = 0


def format_barcode_for_display(barcode):
    """Format barcode for display with grouping"""
    if len(barcode) <= 8:
        return barcode
    
    # Group in chunks of 4 for readability
    chunks = [barcode[i:i+4] for i in range(0, len(barcode), 4)]
    return ' '.join(chunks)


def validate_barcode_format(barcode):
    """
    Validate barcode format and return type.
    
    Returns:
        tuple: (is_valid, barcode_type, message)
    """
    if not barcode:
        return (False, None, "Empty barcode")
    
    # Check if numeric
    if barcode.isdigit():
        length = len(barcode)
        
        # EAN-13 (most common for retail)
        if length == 13:
            return (True, "EAN-13", "Valid EAN-13 barcode")
        
        # UPC-A (North America)
        elif length == 12:
            return (True, "UPC-A", "Valid UPC-A barcode")
        
        # EAN-8 (small products)
        elif length == 8:
            return (True, "EAN-8", "Valid EAN-8 barcode")
        
        # Other numeric
        else:
            return (True, "Numeric", f"Valid numeric barcode ({length} digits)")
    
    # Alphanumeric (Code 128, Code 39, etc.)
    elif barcode.isalnum():
        return (True, "Alphanumeric", "Valid alphanumeric barcode")
    
    # Contains special characters
    else:
        return (True, "Custom", "Custom barcode format")


def suggest_barcode_fixes(barcode):
    """Suggest fixes for common barcode scanning errors"""
    suggestions = []
    
    # Check for common OCR errors
    ocr_fixes = {
        'O': '0', 'o': '0',  # Letter O to zero
        'I': '1', 'l': '1',  # Letter I/l to one
        'S': '5', 's': '5',  # Letter S to five
        'B': '8',            # Letter B to eight
    }
    
    fixed = barcode
    for wrong, correct in ocr_fixes.items():
        if wrong in fixed:
            fixed = fixed.replace(wrong, correct)
    
    if fixed != barcode:
        suggestions.append(("OCR Fix", fixed))
    
    # Check for missing leading zeros
    if barcode.isdigit() and len(barcode) in [7, 11, 12]:
        padded = barcode.zfill(len(barcode) + 1)
        suggestions.append(("Add Leading Zero", padded))
    
    # Check for extra characters
    if len(barcode) > 13:
        trimmed = barcode[:13]
        if trimmed.isdigit():
            suggestions.append(("Trim to EAN-13", trimmed))
    
    return suggestions
