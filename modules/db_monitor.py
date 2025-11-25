# modules/db_monitor.py
"""
Database change monitor for real-time synchronization across multiple app instances.
Monitors database file for changes and triggers UI updates.
"""

import os
import time
import threading
from pathlib import Path
from modules.event_manager import event_manager

class DatabaseMonitor:
    """Monitor database file for changes and notify all views"""
    
    def __init__(self, db_path, check_interval=2):
        self.db_path = Path(db_path)
        self.check_interval = check_interval
        self.last_modified = None
        self.monitoring = False
        self.monitor_thread = None
        
    def start(self):
        """Start monitoring database for changes"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.last_modified = self.get_db_modified_time()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Database monitor started")
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️ Database monitor stopped")
    
    def get_db_modified_time(self):
        """Get database file last modified time"""
        try:
            return os.path.getmtime(self.db_path)
        except:
            return None
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                current_modified = self.get_db_modified_time()
                
                if current_modified and self.last_modified:
                    if current_modified > self.last_modified:
                        # Database changed! Notify all views
                        print(f"🔄 Database changed detected at {time.strftime('%H:%M:%S')}")
                        self._notify_changes()
                        self.last_modified = current_modified
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Error in database monitor: {e}")
                time.sleep(self.check_interval)
    
    def _notify_changes(self):
        """Notify all views about database changes"""
        # Trigger refresh events for all data types
        event_manager.notify('database_changed', {'source': 'external'})
        event_manager.notify('inventory_changed', {'source': 'external'})
        event_manager.notify('sale_completed', {'source': 'external'})
        event_manager.notify('customer_updated', {'source': 'external'})


# Global monitor instance
db_monitor = None

def start_database_monitor(db_path, check_interval=2):
    """Start the global database monitor"""
    global db_monitor
    if db_monitor is None:
        db_monitor = DatabaseMonitor(db_path, check_interval)
        db_monitor.start()
    return db_monitor

def stop_database_monitor():
    """Stop the global database monitor"""
    global db_monitor
    if db_monitor:
        db_monitor.stop()
        db_monitor = None
