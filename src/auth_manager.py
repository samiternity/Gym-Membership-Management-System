import json
import os
from datetime import datetime

class AuthManager:
    """Handles user authentication and session management."""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.users_db = {}
        self.current_user = None
        
        self.ensure_data_dir()
        self.load_users()
        self.create_default_admin()
    
    def ensure_data_dir(self):
        """Ensures the data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_users(self):
        """Loads users from JSON file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    self.users_db = json.load(f)
            except json.JSONDecodeError:
                print("Error decoding users.json, initializing empty.")
                self.users_db = {}
        else:
            self.users_db = {}
    
    def save_users(self):
        """Saves users to JSON file."""
        with open(self.users_file, 'w') as f:
            json.dump(self.users_db, f, indent=4)
    
    def create_default_admin(self):
        """Creates default admin account if no users exist."""
        if not self.users_db:
            admin_user = {
                "username": "admin",
                "password": "admin123",
                "role": "Admin",
                "created_date": datetime.now().strftime("%Y-%m-%d")
            }
            self.users_db["U001"] = admin_user
            self.save_users()
            print("Default admin account created: username='admin', password='admin123'")
    
    def validate_credentials(self, username, password):
        """Validates username and password.
        
        Args:
            username: Username to validate
            password: Password to validate
            
        Returns:
            tuple: (success: bool, user_id: str or None, message: str)
        """
        for user_id, user_data in self.users_db.items():
            if user_data['username'] == username:
                if user_data['password'] == password:
                    return True, user_id, "Login successful"
                else:
                    return False, None, "Incorrect password"
        return False, None, "Username not found"
    
    def login(self, username, password):
        """Attempts to log in a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            tuple: (success: bool, user_data: dict or None, message: str)
        """
        success, user_id, message = self.validate_credentials(username, password)
        
        if success:
            self.current_user = {
                "user_id": user_id,
                "username": username,
                "role": self.users_db[user_id]['role']
            }
            return True, self.current_user, message
        else:
            return False, None, message
    
    def logout(self):
        """Logs out the current user."""
        self.current_user = None
    
    def get_current_user(self):
        """Returns the currently logged-in user."""
        return self.current_user
    
    def is_logged_in(self):
        """Checks if a user is currently logged in."""
        return self.current_user is not None
    
    def change_password(self, username, new_password):
        """Changes a user's password.
        
        Args:
            username: Username of the user
            new_password: New password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        for user_id, user_data in self.users_db.items():
            if user_data['username'] == username:
                user_data['password'] = new_password
                self.save_users()
                return True, "Password changed successfully"
        return False, "User not found"
    
    def add_user(self, username, password, role="Admin"):
        """Adds a new user.
        
        Args:
            username: Username for new user
            password: Password for new user
            role: Role (default: Admin)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Check if username already exists
        for user_data in self.users_db.values():
            if user_data['username'] == username:
                return False, "Username already exists"
        
        # Generate new user ID
        user_ids = [int(uid[1:]) for uid in self.users_db.keys()]
        new_id = f"U{max(user_ids) + 1:03d}" if user_ids else "U001"
        
        # Create new user
        new_user = {
            "username": username,
            "password": password,
            "role": role,
            "created_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.users_db[new_id] = new_user
        self.save_users()
        return True, f"User {username} created successfully"
