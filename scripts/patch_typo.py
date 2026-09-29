import re

with open('D:/IDEATHON/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('id collector-reports', 'id="collected-reports"')

with open('D:/IDEATHON/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
