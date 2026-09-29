import re

with open('D:/IDEATHON/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove btn-send-otp
html = re.sub(
    r'<button type="button" id="btn-send-otp" class="primary-button neon-btn"[^>]*>Send\s*OTP</button>',
    '',
    html
)

with open('D:/IDEATHON/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
