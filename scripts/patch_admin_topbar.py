import re

with open('D:/IDEATHON/frontend/admin/admin.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace(
    'background: rgba(15, 23, 42, 0.8);',
    'background: #ffffff;'
)
css = css.replace(
    'backdrop-filter: blur(10px);',
    ''
)

with open('D:/IDEATHON/frontend/admin/admin.css', 'w', encoding='utf-8') as f:
    f.write(css)
