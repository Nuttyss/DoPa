import firebase_admin
from firebase_admin import db

ADMINS_DB_REF = "admins"  # Firebase path for admins list

def load_admins():
    """Load admin user IDs from Firebase as a list of ints."""
    admins_data = db.reference(ADMINS_DB_REF).get()
    if not admins_data:
        return []
    # Firebase might return a dict (if you store as dict), or a list.
    # Normalize to list of ints:
    if isinstance(admins_data, dict):
        # If stored as {uid: True} or {uid: timestamp} or something, extract keys
        try:
            return [int(uid) for uid in admins_data.keys()]
        except Exception:
            pass
    elif isinstance(admins_data, list):
        return [int(uid) for uid in admins_data if uid]
    # Fallback: try to parse as list of ints
    try:
        return [int(uid) for uid in admins_data]
    except Exception:
        return []

def save_admins(admins):
    """Save list of admin user IDs to Firebase."""
    # Firebase does not handle pure lists well (index-based), better save as dict with value True
    admins_dict = {str(uid): True for uid in admins}
    db.reference(ADMINS_DB_REF).set(admins_dict)

def is_admin(user_id: int) -> bool:
    """Check if user_id is in admins."""
    return user_id in load_admins()

def add_admin(user_id: int):
    """Add a new admin ID to Firebase."""
    admins = load_admins()
    if user_id not in admins:
        admins.append(user_id)
        save_admins(admins)

def remove_admin(user_id: int):
    """Remove an admin ID from Firebase."""
    admins = load_admins()
    if user_id in admins:
        admins.remove(user_id)
        save_admins(admins)

def ensure_first_admin(user_id: int):
    """Ensure at least one admin exists. If no admins, add this user as admin."""
    admins = load_admins()
    if not admins:
        add_admin(user_id)
