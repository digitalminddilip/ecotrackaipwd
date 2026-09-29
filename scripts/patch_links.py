import re

with open('D:/IDEATHON/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove the links from the form-actions-row
html = re.sub(
    r'<div style="display:flex; gap:12px">\s*<a href="#" class="forgot-link" id="link-login-otp">Login with OTP</a>\s*<a href="#" class="forgot-link" id="link-login-password"[^>]*>Login with Password</a>\s*<a href="#" class="forgot-link" id="link-forgot">Forgot Password\?</a>\s*</div>',
    '',
    html
)

# Also remove group-password entirely to clean up UI? 
# Wait, if they switch to "Register" mode, the password field is needed by the backend.
# If they want it completely gone, I should just hide it in CSS or leave it hidden.
# But wait! If they register, they MUST provide a password!
# Let's check pp.js to see what happens on register. If the user only wants to use OTP and Google login, they shouldn't even have a "Sign up" button that requires a password.
# But I will just remove the "Login with Password" link for now.

with open('D:/IDEATHON/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
