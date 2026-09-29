import re

with open('D:/IDEATHON/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Change default hidden input
html = html.replace(
    '<input type="hidden" id="auth-mode" value="login">',
    '<input type="hidden" id="auth-mode" value="login_otp">'
)

with open('D:/IDEATHON/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

with open('D:/IDEATHON/frontend/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_js = app_js.replace(
    'setAuthMode("login");',
    'setAuthMode("login_otp");'
)

with open('D:/IDEATHON/frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
