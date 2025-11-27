# -*- coding: utf-8 -*-
# app.py
"""Entry point for the Shop Manager desktop application."""

# Standard imports
import sys
import config

# Ensure UTF-8 encoding for Arabic and international characters
if sys.version_info[0] >= 3:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Local imports
from modules.backup_manager import auto_backup_check
from modules.health import run_preflight_checks
from modules.logger import log
from ui.main import start_app

if __name__ == "__main__":
    # Initialize logger
    log.info("=" * 50)
    log.info("Application starting...")

    # Run preflight diagnostics
    preflight = run_preflight_checks()
    if not preflight.get("ok", False):
        log.critical("Startup aborted due to failed preflight checks")
        raise SystemExit(1)

    # Check for auto-backup
    try:
        if auto_backup_check():
            log.info("Auto-backup completed successfully")
    except Exception as e:
        log.error(f"Auto-backup failed: {e}")

    # Load theme from configuration
    cfg = config.load_config()
    theme = cfg.get("theme", "cosmo")
    log.info(f"Loaded configuration. Theme: {theme}")

    # TEMPORARY: Skip login for testing
    # To enable login, uncomment the lines below and comment out start_app()
    
    # from ui.login_view import show_login
    # log.info("Showing login screen...")
    # show_login(lambda: start_app(theme_name=theme))
    
    # Direct start without login (TEMPORARY)
    log.info("Starting application without login (login disabled for testing)...")
    start_app(theme_name=theme)
