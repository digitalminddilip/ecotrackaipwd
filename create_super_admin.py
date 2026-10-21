import argparse
import getpass
import os
import sys
import uuid
from datetime import datetime, timezone
import sqlite3

# Ensure backend modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.auth import hash_password
except ImportError:
    import base64
    import hashlib

    def hash_password(password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
        return f"{base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def get_db_path() -> str:
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("CLEANCONNECT_DATABASE", "cleanconnect.db")


def create_or_update_super_admin(email: str, password: str, name: str) -> dict:
    email = email.strip().lower()
    name = name.strip() or email.split("@")[0]
    db_path = get_db_path()

    if not email:
        raise ValueError("Email cannot be empty.")
    if not password:
        raise ValueError("Password cannot be empty.")

    password_hash = hash_password(password)
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        # Ensure users table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                picture TEXT
            )
            """
        )

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            user_id = existing_user["user_id"]
            cursor.execute(
                """
                UPDATE users
                SET name = ?, role = 'administrator', password_hash = ?
                WHERE user_id = ?
                """,
                (name, password_hash, user_id),
            )
            action = "updated"
        else:
            user_id = f"usr-{uuid.uuid4().hex[:8]}"
            cursor.execute(
                """
                INSERT INTO users (user_id, name, email, role, password_hash, created_at, points, picture)
                VALUES (?, ?, ?, 'administrator', ?, ?, 0, '')
                """,
                (user_id, name, email, password_hash, now_iso),
            )
            action = "created"

        conn.commit()
        return {
            "action": action,
            "user_id": user_id,
            "name": name,
            "email": email,
            "role": "administrator",
        }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Create or promote a Super Admin (Administrator) for CleanConnect.")
    parser.add_argument("--email", help="Super Admin email address", default=None)
    parser.add_argument("--name", help="Super Admin full name", default=None)
    parser.add_argument("--password", help="Super Admin password (optional via CLI, will prompt if omitted)", default=None)

    args = parser.parse_args()

    email = args.email
    if not email:
        email = input("Enter Super Admin email: ").strip()

    name = args.name
    if not name:
        default_name = email.split("@")[0] if "@" in email else "Super Admin"
        prompt_name = input(f"Enter Super Admin full name [{default_name}]: ").strip()
        name = prompt_name if prompt_name else default_name

    password = args.password
    if not password:
        password = getpass.getpass("Enter Super Admin password: ").strip()
        confirm = getpass.getpass("Confirm password: ").strip()
        if password != confirm:
            print("Error: Passwords do not match.", file=sys.stderr)
            sys.exit(1)

    if not password:
        print("Error: Password cannot be empty.", file=sys.stderr)
        sys.exit(1)

    try:
        result = create_or_update_super_admin(email=email, password=password, name=name)
        action_verb = "created" if result["action"] == "created" else "promoted/updated"
        print(f"\n[SUCCESS] Super Admin successfully {action_verb}!")
        print(f"  User ID : {result['user_id']}")
        print(f"  Name    : {result['name']}")
        print(f"  Email   : {result['email']}")
        print(f"  Role    : {result['role']}")
        print(f"\nYou can now sign in at the Admin Portal (/admin/) or using /auth/login.")
    except Exception as e:
        print(f"\n[ERROR] Failed to create super admin: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
