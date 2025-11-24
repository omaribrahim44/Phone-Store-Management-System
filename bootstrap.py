# bootstrap.py
"""Utility functions for application startup.
This module isolates configuration loading and other lightweight bootstrap tasks
so that the main entry point (app.py) stays minimal and readable.
"""
import config

def get_theme():
    """Return the UI theme from configuration, falling back to 'flatly'."""
    cfg = config.load_config()
    return cfg.get("theme", "flatly")
