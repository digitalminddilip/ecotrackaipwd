import re

with open('D:/IDEATHON/backend/main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Make OTP always '123456' for testing since email is not setup
code = code.replace(
    'otp_code = "".join(secrets.choice("0123456789") for _ in range(6))',
    'otp_code = "123456" # Hardcoded for testing since SMTP is not configured'
)

with open('D:/IDEATHON/backend/main.py', 'w', encoding='utf-8') as f:
    f.write(code)
