# modules/event_manager.py
"""
Central event manager for real-time synchronization across all views.
When data changes in one view, all other views are automatically notified and refreshed.
"""

class EventManager:
    """Singleton event manager for application-wide notifications"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance.listeners = {
                'inventory_changed': [],
                'sale_completed': [],
                'repair_updated': [],
                'customer_updated': [],
            }
        return cls._instance
    
    def subscribe(self, event_type, callback):
        """Subscribe a callback to an event type"""
        if event_type in self.listeners:
            if callback not in self.listeners[event_type]:
                self.listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type, callback):
        """Unsubscribe a callback from an event type"""
        if event_type in self.listeners and callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
    
    def notify(self, event_type, data=None):
        """Notify all subscribers of an event"""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event callback for {event_type}: {e}")
    
    def clear_all(self):
        """Clear all listeners (useful for testing)"""
        for event_type in self.listeners:
            self.listeners[event_type] = []


# Global instance
event_manager = EventManager()
