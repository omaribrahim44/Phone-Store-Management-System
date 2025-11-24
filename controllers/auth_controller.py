# controllers/auth_controller.py
from modules import models
from modules.audit_logger import log_action

class AuthController:
    @staticmethod
    def login(username, password):
        user = models.get_user(username)
        if user and models.verify_password(user[2], password):
            log_action(
                user=username,
                action_type="LOGIN",
                entity_type="user",
                description=f"User {username} logged in"
            )
            return user
        return None
    
    @staticmethod
    def get_all_users():
        return models.get_all_users()
    
    @staticmethod
    def add_user(username, password):
        success = models.add_user(username, password)
        if success:
            log_action(
                user="Admin",
                action_type="CREATE",
                entity_type="user",
                description=f"Created user: {username}"
            )
        return success
    
    @staticmethod
    def delete_user(user_id):
        success = models.delete_user_by_id(user_id)
        if success:
            log_action(
                user="Admin",
                action_type="DELETE",
                entity_type="user",
                entity_id=user_id,
                description=f"Deleted user ID: {user_id}"
            )
        return success
    
    @staticmethod
    def update_password(user_id, new_password):
        success = models.update_user_password(user_id, new_password)
        if success:
            log_action(
                user="Admin",
                action_type="UPDATE",
                entity_type="user",
                entity_id=user_id,
                description=f"Updated password for user ID: {user_id}"
            )
        return success
