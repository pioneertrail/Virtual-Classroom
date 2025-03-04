import json
import os
import hashlib
from datetime import datetime, timedelta
from email_handler import EmailHandler

class UserAuth:
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
        self.users = self.load_users()
        self.email_handler = EmailHandler()
        self.recovery_codes = {}  # Store recovery codes temporarily

    def load_users(self):
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=2)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, name, email):
        if username in self.users:
            return False, "Username already exists!"
        
        self.users[username] = {
            "password": self.hash_password(password),
            "name": name,
            "email": email,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_users()
        return True, "Registration successful! You can now log in."

    def login(self, username, password):
        if username not in self.users:
            return False, "Username not found!"
        
        if self.users[username]["password"] != self.hash_password(password):
            return False, "Incorrect password!"
        
        self.current_user = username
        return True, f"Welcome back, {self.users[username]['name']}!"

    def logout(self):
        if self.current_user:
            username = self.current_user
            self.current_user = None
            return f"Goodbye, {self.users[username]['name']}!"
        return "No user logged in."

    def is_logged_in(self):
        return self.current_user is not None

    def get_current_user(self):
        if self.current_user:
            return self.users[self.current_user]
        return None

    def initiate_password_recovery(self, username):
        if username not in self.users:
            return False, "Username not found!"
        
        email = self.users[username].get('email')
        if not email:
            return False, "No email address found for this account!"
        
        # Generate and store recovery code
        recovery_code = self.email_handler.generate_recovery_code()
        self.recovery_codes[username] = {
            'code': recovery_code,
            'expires': datetime.now() + timedelta(minutes=15)
        }
        
        # Send recovery email
        success, message = self.email_handler.send_recovery_email(email, recovery_code)
        return success, message

    def verify_recovery_code(self, username, code):
        if username not in self.recovery_codes:
            return False, "No recovery code requested!"
        
        recovery_data = self.recovery_codes[username]
        if datetime.now() > recovery_data['expires']:
            del self.recovery_codes[username]
            return False, "Recovery code has expired!"
        
        if recovery_data['code'] != code:
            return False, "Invalid recovery code!"
        
        return True, "Code verified successfully!"

    def reset_password(self, username, new_password):
        if username not in self.users:
            return False, "Username not found!"
        
        self.users[username]["password"] = self.hash_password(new_password)
        self.save_users()
        del self.recovery_codes[username]  # Clear recovery code
        return True, "Password reset successfully!" 