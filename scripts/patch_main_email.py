import re

with open('D:/IDEATHON/backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Update User model
code = code.replace(
    '    role: Role',
    '    email: str\n    role: Role'
)

# Update users dict population
code = code.replace(
    'role=Role(u["role"]),',
    'email=u.get("email", ""), role=Role(u["role"]),'
)

# Update register endpoint
code = code.replace(
    'users[user_id] = User(user_id=user_id, name=request.name, role=Role.citizen)',
    'users[user_id] = User(user_id=user_id, name=request.name, email=email, role=Role.citizen)'
)

# Update google_login endpoint
code = code.replace(
    'users[user_id] = User(user_id=user_id, name=name, role=Role.citizen, picture=picture)',
    'users[user_id] = User(user_id=user_id, name=name, email=email, role=Role.citizen, picture=picture)'
)

with open('D:/IDEATHON/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(code)
