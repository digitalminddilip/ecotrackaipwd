import re

with open('D:/IDEATHON/frontend/admin/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Logo
old_logo = '''      <div class="sidebar-header">
        <i class="fa-solid fa-leaf text-primary"></i>
        <span>EcoTrack<span class="text-primary">AI</span></span>
      </div>'''

new_logo = '''      <div class="sidebar-header" style="justify-content: flex-start; padding-left: 20px;">
        <img src="../logo.png" alt="EcoTrack AI" style="height: 32px; margin-right: 8px;">
        <span style="font-size: 1.25rem; font-weight: 700; color: #1f2937;">EcoTrack AI</span>
      </div>'''

html = html.replace(old_logo, new_logo)

with open('D:/IDEATHON/frontend/admin/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
