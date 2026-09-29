import re

with open('D:/IDEATHON/frontend/admin/admin.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = js.replace(
    '<td></td>',
    '<td></td>'
)

with open('D:/IDEATHON/frontend/admin/admin.js', 'w', encoding='utf-8') as f:
    f.write(js)
