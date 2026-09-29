import re

with open('D:/IDEATHON/backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update User model
code = code.replace(
    '    role: Role',
    '    role: Role\n    picture: str = \"\"'
)

# 2. Update imports from database
code = code.replace(
    'from .database import find_user_by_email, init_db, load_reports, load_users, save_report, save_user, update_user_password, get_report_image_data, get_report_evidence_data',
    'from .database import find_user_by_email, init_db, load_reports, load_users, save_report, save_user, update_user_password, get_report_image_data, get_report_evidence_data, update_user_picture'
)

# 3. Update startup to load picture
code = code.replace(
    'role=Role(u[\"role\"]),',
    'role=Role(u[\"role\"]),\n            picture=u.get(\"picture\", \"\") or \"\",'
)

# 4. Update google_login
google_login_old = '''        email = email.lower()
        stored_user = find_user_by_email(email)
        
        if not stored_user:
            user_id = f"usr-{uuid4().hex[:8]}"
            name = idinfo.get("name", email.split("@")[0])
            # Save user with random password since they use Google
            save_user(user_id, name, email, Role.citizen.value, hash_password(uuid4().hex), datetime.now(timezone.utc).isoformat())
            users[user_id] = User(user_id=user_id, name=name, role=Role.citizen)
            role = Role.citizen.value
        else:
            user_id = stored_user["user_id"]
            role = stored_user["role"]'''

google_login_new = '''        email = email.lower()
        picture = idinfo.get("picture", "")
        stored_user = find_user_by_email(email)
        
        if not stored_user:
            user_id = f"usr-{uuid4().hex[:8]}"
            name = idinfo.get("name", email.split("@")[0])
            save_user(user_id, name, email, Role.citizen.value, hash_password(uuid4().hex), datetime.now(timezone.utc).isoformat(), picture)
            users[user_id] = User(user_id=user_id, name=name, role=Role.citizen, picture=picture)
            role = Role.citizen.value
        else:
            user_id = stored_user["user_id"]
            role = stored_user["role"]
            if picture:
                update_user_picture(email, picture)
                if user_id in users:
                    users[user_id].picture = picture'''

code = code.replace(google_login_old, google_login_new)

with open('D:/IDEATHON/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(code)
