import re

with open('D:/IDEATHON/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(
    r'<div class="auth-nav">\s*<div class="auth-icon-btn" id="auth-back-btn"><i class="fa-solid fa-arrow-left"></i></div>\s*<div class="auth-icon-btn"><i class="fa-solid fa-arrows-rotate"></i></div>\s*</div>',
    '',
    html
)

with open('D:/IDEATHON/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
