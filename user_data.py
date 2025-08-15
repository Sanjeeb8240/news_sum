import os
import json

# Simple local user preference store (expand with a DB for bigger projects)
USER_DATA_FILE = 'user_prefs.json'

def load_user_prefs():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, 'r') as f:
        return json.load(f)

def save_user_prefs(prefs):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(prefs, f)

def get_user_topics(username):
    prefs = load_user_prefs()
    return prefs.get(username, [])

def set_user_topics(username, topics):
    prefs = load_user_prefs()
    prefs[username] = topics
    save_user_prefs(prefs)
