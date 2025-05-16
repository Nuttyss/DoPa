import firebase_admin
from firebase_admin import db

ADMINS_DB_REF = "admins"  # Firebase path for admin user IDs

def load_admins():
    """Load admin user IDs from Firebase as a list of ints."""
    data = db.reference(ADMINS_DB_REF).get()
    if not data:
        return []

    if isinstance(data, dict):
        # Stored as {uid: True} or {uid: timestamp}
        return [int(uid) for uid in data.keys()]
    elif isinstance(data, list):
        # Unlikely, but if stored as list
        return [int(uid) for uid in data if uid]

    try:
        # Fallback: try parsing generic structure
        return [int(uid) for uid in data]
    except Exception:
        return []

def save_admins(admins):
    """Save list of admin user IDs to Firebase as {uid: True}."""
    db.reference(ADMINS_DB_REF).set({str(uid): True for uid in admins})

def is_admin(user_id: int) -> bool:
    """Check if a user is an admin."""
    return user_id in load_admins()

def add_admin(user_id: int):
    """Add a user as admin if not already."""
    admins = load_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_admins(admins)

def remove_admin(user_id: int):
    """Remove a user from the admin list."""
    admins = load_admins()
    if user_id in admins:
        admins.remove(user_id)
        save_admins(admins)

def ensure_first_admin(user_id: int):
    """If no admin exists yet, assign the first user who interacts with the bot."""
    if not load_admins():
        add_admin(user_id)
