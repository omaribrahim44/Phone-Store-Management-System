# modules/backup_manager.py
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import config
from modules.logger import log

BACKUP_DIR = Path(__file__).resolve().parents[1] / "backups"

def ensure_backup_dir():
    """Ensure the backups directory exists."""
    BACKUP_DIR.mkdir(exist_ok=True)

def create_backup(backup_name=None):
    """
    Create a backup of the database.
    Returns the backup file path or None if failed.
    """
    ensure_backup_dir()
    
    if not backup_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.db"
    
    backup_path = BACKUP_DIR / backup_name
    
    try:
        # Copy the database file
        shutil.copy2(config.DB_PATH, backup_path)
        log.info(f"Backup created: {backup_path}")
        
        # Update config with last backup date
        cfg = config.load_config()
        if "backup" not in cfg:
            cfg["backup"] = {}
        cfg["backup"]["last_backup_date"] = datetime.now().isoformat()
        config.save_config(cfg)
        
        # Cleanup old backups
        cleanup_old_backups()
        
        return str(backup_path)
    except Exception as e:
        log.error(f"Backup failed: {e}")
        return None

def list_backups():
    """
    List all available backups.
    Returns list of tuples: (filename, size_mb, date_modified)
    """
    ensure_backup_dir()
    
    backups = []
    for file in BACKUP_DIR.glob("*.db"):
        stat = file.stat()
        size_mb = stat.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stat.st_mtime)
        backups.append((file.name, size_mb, modified.strftime("%Y-%m-%d %H:%M:%S")))
    
    # Sort by date (newest first)
    backups.sort(key=lambda x: x[2], reverse=True)
    return backups

def restore_backup(backup_filename):
    """
    Restore database from a backup file.
    Returns True if successful, False otherwise.
    """
    backup_path = BACKUP_DIR / backup_filename
    
    if not backup_path.exists():
        log.error(f"Backup file not found: {backup_filename}")
        return False
    
    try:
        # Create a safety backup of current database before restoring
        safety_backup = BACKUP_DIR / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(config.DB_PATH, safety_backup)
        
        # Restore the backup
        shutil.copy2(backup_path, config.DB_PATH)
        log.info(f"Database restored from: {backup_filename}")
        return True
    except Exception as e:
        log.error(f"Restore failed: {e}")
        return False

def delete_backup(backup_filename):
    """
    Delete a backup file.
    Returns True if successful, False otherwise.
    """
    backup_path = BACKUP_DIR / backup_filename
    
    try:
        backup_path.unlink()
        log.info(f"Backup deleted: {backup_filename}")
        return True
    except Exception as e:
        log.error(f"Delete backup failed: {e}")
        return False

def cleanup_old_backups():
    """
    Delete old backups, keeping only the most recent ones.
    """
    cfg = config.load_config()
    max_backups = cfg.get("backup", {}).get("max_backups", 10)
    
    backups = list_backups()
    
    # Delete oldest backups if we exceed max_backups
    if len(backups) > max_backups:
        for backup in backups[max_backups:]:
            delete_backup(backup[0])
            log.info(f"Cleaned up old backup: {backup[0]}")

def auto_backup_check():
    """
    Check if auto-backup is due and create one if needed.
    Returns True if backup was created, False otherwise.
    """
    cfg = config.load_config()
    backup_cfg = cfg.get("backup", {})
    
    if not backup_cfg.get("auto_backup_enabled", False):
        return False
    
    last_backup = backup_cfg.get("last_backup_date")
    frequency = backup_cfg.get("auto_backup_frequency", "daily")
    
    # Determine if backup is due
    backup_due = False
    
    if not last_backup:
        backup_due = True
    else:
        last_backup_dt = datetime.fromisoformat(last_backup)
        now = datetime.now()
        
        if frequency == "daily":
            # Backup if last backup was yesterday or earlier
            if (now - last_backup_dt).days >= 1:
                backup_due = True
        elif frequency == "weekly":
            # Backup if last backup was 7+ days ago
            if (now - last_backup_dt).days >= 7:
                backup_due = True
    
    if backup_due:
        log.info("Auto-backup is due, creating backup...")
        result = create_backup()
        return result is not None
    
    return False
