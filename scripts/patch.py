import re

with open('D:/IDEATHON/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Citizen Header
html = re.sub(
    r'<div class="cit-logo-icon"><i class="fa-solid fa-leaf"></i></div>',
    '<img src="logo.png" alt="EcoTrack AI" style="height: 32px; margin-right: 8px;">',
    html
)

# 2. Citizen Sidebar
html = re.sub(
    r'<div class="sidebar-brand-icon"><i class="fa-solid fa-leaf"></i></div>',
    '<img src="logo.png" alt="EcoTrack AI" style="height: 32px; margin-right: 8px;">',
    html
)

# 3. Citizen Footer
footer_replacement = '''<footer class="cit-footer">
      <div style="text-align: center; margin-bottom: 8px;">
        <img src="logo.png" alt="EcoTrack AI Logo" style="height: 40px; display: inline-block;">
      </div>
      <div class="cit-footer-pwd">PWD</div>
      <div class="cit-footer-copy">@2026Ecotrack AI</div>
    </footer>'''
html = re.sub(r'<footer class="cit-footer">.*?</footer>', footer_replacement, html, flags=re.DOTALL)

# 4. Admin Mobile Header
html = re.sub(
    r'<i class="fa-solid fa-leaf" style="color: #f69446; margin-right: 6px;"></i> EcoTrack AI',
    '<img src="logo.png" alt="EcoTrack AI" style="height: 24px; margin-right: 6px;"> EcoTrack AI',
    html
)

# 5. Collector Sidebar
html = re.sub(
    r'<div class="col-brand-icon"><i class="fa-solid fa-truck"></i></div>',
    '<img src="logo.png" alt="EcoTrack AI" style="height: 32px; margin-right: 8px;">',
    html
)

# 6. Admin Footer (append before </main> in app-wrapper)
admin_footer = '''      <footer style="text-align: center; padding: 40px 24px 24px; margin-top: auto;">
        <img src="logo.png" alt="EcoTrack AI Logo" style="height: 40px; display: inline-block;">
        <div style="font-size: 12px; color: #888; margin-top: 8px;">Powered by EcoTrack AI</div>
      </footer>
    </main>
  </div>

  <!-- COLLECTOR DASHBOARD -->'''
html = html.replace('    </main>\n  </div>\n\n  <!-- COLLECTOR DASHBOARD -->', admin_footer)

# 7. Collector Footer (append before </main> in collector dashboard)
col_footer = '''      <footer style="text-align: center; padding: 24px; margin-top: auto;">
        <img src="logo.png" alt="EcoTrack AI Logo" style="height: 40px; display: inline-block;">
        <div style="font-size: 12px; color: var(--col-text-muted); margin-top: 8px;">Powered by EcoTrack AI</div>
      </footer>
    </main>
  </div>

  <!-- Hidden Report Form for JS -->'''
html = html.replace('    </main>\n  </div>\n\n  <!-- Hidden Report Form for JS -->', col_footer)


with open('D:/IDEATHON/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
