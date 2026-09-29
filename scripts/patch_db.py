import re

with open('D:/IDEATHON/backend/database.py', 'r', encoding='utf-8') as f:
    db = f.read()

db = db.replace(
    'points INTEGER DEFAULT 0',
    'points INTEGER DEFAULT 0,\n                    picture TEXT'
)

db = db.replace(
    'def save_user(user_id: str, name: str, email: str, role: str, password_hash: str, created_at: str) -> None:',
    'def save_user(user_id: str, name: str, email: str, role: str, password_hash: str, created_at: str, picture: str = \"\") -> None:'
)

db = db.replace(
    '\"INSERT INTO users (user_id, name, email, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)\",',
    '\"INSERT INTO users (user_id, name, email, role, password_hash, created_at, picture) VALUES (?, ?, ?, ?, ?, ?, ?)\",'
)

db = db.replace(
    '(user_id, name, email, role, password_hash, created_at),',
    '(user_id, name, email, role, password_hash, created_at, picture),'
)

db = db.replace(
    'cursor.execute(\"SELECT user_id, name, email, role, points FROM users\")',
    'cursor.execute(\"SELECT user_id, name, email, role, points, picture FROM users\")'
)

# Also add update_user_picture function
update_pic_func = '''
def update_user_picture(email: str, picture: str) -> None:
    with connect() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET picture = ? WHERE email = ?",
            (picture, email.lower()),
        )
        connection.commit()
'''
db = db + update_pic_func

with open('D:/IDEATHON/backend/database.py', 'w', encoding='utf-8') as f:
    f.write(db)
