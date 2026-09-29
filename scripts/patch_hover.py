import re

with open('D:/IDEATHON/frontend/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Fix sidebar hover
css = css.replace('background: rgba(255, 255, 255, 0.05);', 'background: #f3f4f6;')

# Fix sidebar-brand-text color
css = css.replace(
    '.sidebar-brand-text span {\n  display: block;\n}',
    '.sidebar-brand-text span {\n  display: block;\n  color: var(--text-main);\n}'
)

# Fix sidebar brand logo if any, not needed

with open('D:/IDEATHON/frontend/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)
