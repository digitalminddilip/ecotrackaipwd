import re

with open('D:/IDEATHON/frontend/admin/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('src="admin.js"', 'src="admin.js?v=2"')

with open('D:/IDEATHON/frontend/admin/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
