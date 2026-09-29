import re

with open('D:/IDEATHON/backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'user_id=stored_user["user_id"], name=stored_user["name"], role=stored_user["role"]',
    'user_id=stored_user["user_id"], name=stored_user["name"], email=stored_user.get("email", ""), role=stored_user["role"], picture=stored_user.get("picture", "") or ""'
)

with open('D:/IDEATHON/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(code)
