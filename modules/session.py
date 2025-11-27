# modules/session.py
"""
Session Management System
Tracks logged-in user and session state
"""

from datetime import datetime, timedelta
from typing import Optional, Dict

class SessionManager:
    """Manages user session state"""
    
    def __init__(self):
        self.current_user: Optional[Dict] = None
        self.login_time: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.session_timeout_minutes = 30  # 30 minutes of inactivity
    
    def login(self, user_data: tuple) -> bool:
        """
        Log in a user and start session.
        
        Args:
            user_data: Tuple from database (user_id, username, password, full_name, role, created_at)
        
        Returns:
            True if login successful
        """
        if not user_data or len(user_data) < 5:
            return False
        
        self.current_user = {
            'user_id': user_data[0],
            'username': user_data[1],
            'full_name': user_data[3] if len(user_data) > 3 else user_data[1],
            'role': user_data[4] if len(user_data) > 4 else 'Cashier',
            'created_at': user_data[5] if len(user_data) > 5 else None,
        }
        self.login_time = datetime.now()
        self.last_activity = datetime.now()
        
        # Log the login
        from modules.audit_logger import log_action
        log_action(
            user=self.current_user['username'],
            action_type="LOGIN",
            entity_type="session",
            description=f"User {self.current_user['username']} ({self.current_user['role']}) logged in"
        )
        
        return True
    
    def logout(self):
        """Log out current user and clear session"""
        if self.current_user:
            # Log the logout
            from modules.audit_logger import log_action
            log_action(
                user=self.current_user['username'],
                action_type="LOGOUT",
                entity_type="session",
                description=f"User {self.current_user['username']} logged out"
            )
        
        self.current_user = None
        self.login_time = None
        self.last_activity = None
    
    def check_session(self) -> bool:
        """
        Check if session is still valid.
        
        Returns:
            True if session is valid, False if expired
        """
        if not self.current_user:
            return False
        
        # Check if session has timed out
        if self.last_activity:
            inactive_time = datetime.now() - self.last_activity
            if inactive_time > timedelta(minutes=self.session_timeout_minutes):
                # Session expired
                from modules.audit_logger import log_action
                log_action(
                    user=self.current_user['username'],
                    action_type="SESSION_TIMEOUT",
                    entity_type="session",
                    description=f"Session timed out after {self.session_timeout_minutes} minutes of inactivity"
                )
                self.logout()
                return False
        
        # Update last activity
        self.last_activity = datetime.now()
        return True
    
    def get_current_user(self) -> Optional[Dict]:
        """
        Get current logged-in user.
        
        Returns:
            User dict or None if not logged in
        """
        if self.check_session():
            return self.current_user
        return None
    
    def get_username(self) -> str:
        """Get current username or 'System' if not logged in"""
        if self.current_user:
            return self.current_user['username']
        return 'System'
    
    def get_user_role(self) -> str:
        """Get current user role or empty string if not logged in"""
        if self.current_user:
            return self.current_user['role']
        return ''
    
    def get_full_name(self) -> str:
        """Get current user's full name"""
        if self.current_user:
            return self.current_user.get('full_name', self.current_user['username'])
        return 'Guest'
    
    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in"""
        return self.check_session()
    
    def get_session_duration(self) -> Optional[timedelta]:
        """Get how long the current session has been active"""
        if self.login_time:
            return datetime.now() - self.login_time
        return None
    
    def extend_session(self):
        """Extend session by updating last activity time"""
        if self.current_user:
            self.last_activity = datetime.now()


# Global session manager instance
_session_manager = SessionManager()


# Convenience functions for easy access
def login(user_data: tuple) -> bool:
    """Log in a user"""
    return _session_manager.login(user_data)


def logout():
    """Log out current user"""
    _session_manager.logout()


def get_current_user() -> Optional[Dict]:
    """Get current logged-in user"""
    return _session_manager.get_current_user()


def get_username() -> str:
    """Get current username"""
    return _session_manager.get_username()


def get_user_role() -> str:
    """Get current user role"""
    return _session_manager.get_user_role()


def is_logged_in() -> bool:
    """Check if user is logged in"""
    return _session_manager.is_logged_in()


def check_session() -> bool:
    """Check if session is valid"""
    return _session_manager.check_session()


def extend_session():
    """Extend current session"""
    _session_manager.extend_session()


def get_session_manager() -> SessionManager:
    """Get the global session manager instance"""
    return _session_manager
