import re

with open('D:/IDEATHON/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove from sidebar
html = html.replace(
    '<a href="#" class="col-nav-link"><i class="fa-solid fa-clock-rotate-left"></i> History</a>',
    ''
)

old_logout = '''      <button class="col-logout-btn" onclick="enterGuestMode(); setAuthMode('login'); byId('collector-dashboard-wrapper').hidden=true; document.body.classList.remove('collector-mode'); openSignIn();"><i class="fa-solid fa-arrow-right-from-bracket"></i> Logout</button>'''
html = html.replace(old_logout, '')

# 2. Add to footer
old_footer = '''      <footer style="text-align: center; padding: 24px; margin-top: auto;">
        <img src="logo.png" alt="EcoTrack AI Logo" style="height: 40px; display: inline-block;">
        <div style="font-size: 12px; color: var(--col-text-muted); margin-top: 8px;">Powered by EcoTrack AI</div>
      </footer>'''

new_footer = '''      <footer style="text-align: center; padding: 24px; margin-top: auto; border-top: 1px solid var(--col-border);">
        <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 24px;">
          <a href="#" class="col-btn-outline" style="text-decoration: none; padding: 8px 16px; border-radius: 8px; border: 1px solid var(--col-border); display: inline-flex; align-items: center; gap: 8px; color: var(--col-text-main); font-weight: 500;"><i class="fa-solid fa-clock-rotate-left"></i> History</a>
          <button class="col-logout-btn" style="margin-top: 0; padding: 8px 16px; width: auto;" onclick="enterGuestMode(); setAuthMode('login_otp'); byId('collector-dashboard-wrapper').hidden=true; document.body.classList.remove('collector-mode'); openSignIn();"><i class="fa-solid fa-arrow-right-from-bracket"></i> Logout</button>
        </div>
        <img src="logo.png" alt="EcoTrack AI Logo" style="height: 40px; display: inline-block;">
        <div style="font-size: 12px; color: var(--col-text-muted); margin-top: 8px;">Powered by EcoTrack AI</div>
      </footer>'''

html = html.replace(old_footer, new_footer)

with open('D:/IDEATHON/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
