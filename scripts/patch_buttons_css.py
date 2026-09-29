import re

with open('D:/IDEATHON/frontend/admin/admin.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Fix button colors
css = css.replace('.btn-primary { background: var(--primary); color: var(--text-light); }', '.btn-primary { background: var(--primary); color: #ffffff; }')
css = css.replace('.btn-danger { background: var(--danger); color: var(--text-light); }', '.btn-danger { background: var(--danger); color: #ffffff; }')
css = css.replace('.btn-success { background: #3b82f6; color: var(--text-light); }', '.btn-success { background: #3b82f6; color: #ffffff; }')

# Fix badge color
css = css.replace(
    '''background: var(--danger);
  color: var(--text-light);''',
    '''background: var(--danger);
  color: #ffffff;'''
)

# Fix outline hover
css = css.replace(
    '.btn-outline:hover { background: rgba(255,255,255,0.1); color: var(--text-light); }',
    '.btn-outline:hover { background: #f3f4f6; color: var(--text-light); }'
)

# Fix table header
css = css.replace('color: var(--text-muted);\n  background: #f9fafb;', 'color: var(--text-muted);\n  background: #f9fafb;')

with open('D:/IDEATHON/frontend/admin/admin.css', 'w', encoding='utf-8') as f:
    f.write(css)
