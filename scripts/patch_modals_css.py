import re

with open('D:/IDEATHON/frontend/admin/admin.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Fix modal card
css = css.replace('background: #1e293b;', 'background: #ffffff;')
css = css.replace('box-shadow: 0 25px 50px -12px rgba(0,0,0,0.8);', 'box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15);')

# Fix image preview background
css = css.replace('background: rgba(0,0,0,0.2);', 'background: #f3f4f6;')

# Fix strong tag color
css = css.replace('.modal-body strong { color: white; }', '.modal-body strong { color: var(--text-light); }')

# Fix close button hover
css = css.replace('.btn-close:hover { color: white; }', '.btn-close:hover { color: var(--danger); }')

# Fix modern-select (used in modals for assigning)
css = css.replace(
    'background: rgba(0,0,0,0.2);',
    'background: #f9fafb;'
)

# Fix empty tables if there's any white text
css = css.replace('color: white;', 'color: var(--text-light);')

# Fix scrollbar
css = css.replace('::-webkit-scrollbar-thumb { background: var(--bg-card);', '::-webkit-scrollbar-thumb { background: #d1d5db;')
css = css.replace('::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }', '::-webkit-scrollbar-thumb:hover { background: #9ca3af; }')

# Fix pagination if any
css = css.replace('background: rgba(255,255,255,0.05);', 'background: #f9fafb;')

with open('D:/IDEATHON/frontend/admin/admin.css', 'w', encoding='utf-8') as f:
    f.write(css)
