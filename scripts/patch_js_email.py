import re

with open('D:/IDEATHON/frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Fix fallback
js = js.replace(
    'if (emailEl) emailEl.textContent = currentUser.email || ${currentUser.name.toLowerCase().replace(" ", "")}@ecotrack.local;',
    'if (emailEl) { if (currentUser.email) { emailEl.textContent = currentUser.email; } else { emailEl.style.display = "none"; } }'
)

with open('D:/IDEATHON/frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
