import json
import os
import hashlib
from datetime import datetime

USER_DATA_FILE = "data/user_sessions.json"

def ensure_data_directory():
    """Ensure data directory exists"""
    if not os.path.exists("data"):
        os.makedirs("data")

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_data():
    """Load user data from JSON file"""
    ensure_data_directory()
    if not os.path.exists(USER_DATA_FILE):
        return {}
    
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_user_data(data):
    """Save user data to JSON file"""
    ensure_data_directory()
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def register_user(username, password, email=""):
    """Register a new user"""
    users = load_user_data()
    
    if username in users:
        return False
    
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
        "preferences": {
            "default_country": "worldwide",
            "default_category": "general",
            "default_language": "en",
            "summary_style": "concise"
        },
        "activity": {
            "login_count": 0,
            "last_login": None,
            "summaries_generated": 0,
            "fact_checks_performed": 0
        }
    }
    
    save_user_data(users)
    return True

def authenticate_user(username, password):
    """Authenticate user login"""
    users = load_user_data()
    
    if username not in users:
        return False
    
    if users[username]["password"] == hash_password(password):
        # Update login info
        users[username]["activity"]["login_count"] += 1
        users[username]["activity"]["last_login"] = datetime.now().isoformat()
        save_user_data(users)
        return True
    
    return False

def get_user_data(username):
    """Get user data"""
    users = load_user_data()
    return users.get(username, {})

def update_user_preferences(username, preferences):
    """Update user preferences"""
    users = load_user_data()
    if username in users:
        users[username]["preferences"].update(preferences)
        save_user_data(users)
        return True
    return False

def increment_user_activity(username, activity_type):
    """Increment user activity counter"""
    users = load_user_data()
    if username in users:
        if activity_type in users[username]["activity"]:
            users[username]["activity"][activity_type] += 1
        else:
            users[username]["activity"][activity_type] = 1
        save_user_data(users)

def get_user_stats(username):
    """Get user statistics"""
    user_data = get_user_data(username)
    if not user_data:
        return None
    
    activity = user_data.get("activity", {})
    return {
        "login_count": activity.get("login_count", 0),
        "summaries_generated": activity.get("summaries_generated", 0),
        "fact_checks_performed": activity.get("fact_checks_performed", 0),
        "last_login": activity.get("last_login", "Never"),
        "member_since": user_data.get("created_at", "Unknown")
    }

def delete_user_data(username):
    """Delete user data (for privacy compliance)"""
    users = load_user_data()
    if username in users:
        del users[username]
        save_user_data(users)
        return True
    return False

def change_user_password(username, old_password, new_password):
    """Change user password"""
    users = load_user_data()
    
    if username not in users:
        return False
    
    # Verify old password
    if users[username]["password"] != hash_password(old_password):
        return False
    
    # Update password
    users[username]["password"] = hash_password(new_password)
    save_user_data(users)
    return True

def get_all_users():
    """Get list of all usernames (for admin purposes)"""
    users = load_user_data()
    return list(users.keys())

def user_exists(username):
    """Check if user exists"""
    users = load_user_data()
    return username in users