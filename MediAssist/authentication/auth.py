
import json
import hashlib
import hmac
from pathlib import Path

# JSON file to store registered users
USERS_FILE = Path(__file__).parent / "users.json"


def load_users():
    """Load registered users from the JSON file."""

    if not USERS_FILE.exists():
        return {}

    with open(USERS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    """Save registered users to the JSON file."""

    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4)


def hash_password(password):
    """Convert a password into a SHA-256 hash."""

    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(username, password):
    """Register a new user."""

    users = load_users()

    if username in users:
        return False, "Username already exists."

    users[username] = {
        "password_hash": hash_password(password)
    }

    save_users(users)

    return True, "Registration successful. Please log in."


def authenticate_user(username, password):
    """Validate the user's login credentials."""

    users = load_users()

    if username not in users:
        return False

    stored_hash = users[username]["password_hash"]
    entered_hash = hash_password(password)

    return hmac.compare_digest(stored_hash, entered_hash)
