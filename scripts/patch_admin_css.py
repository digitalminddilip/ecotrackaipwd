import re

with open('D:/IDEATHON/frontend/admin/admin.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Update CSS variables to light mode
old_vars = ''':root {
  --bg-dark: #0f172a;
  --bg-card: rgba(30, 41, 59, 0.7);
  --text-light: #f8fafc;
  --text-muted: #94a3b8;
  --primary: #10b981;
  --primary-hover: #059669;
  --danger: #ef4444;
  --warning: #f59e0b;
  --info: #3b82f6;
  --border: rgba(255, 255, 255, 0.1);
  --glass-blur: blur(12px);
  --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
  
  --sidebar-width: 260px;
}'''

new_vars = ''':root {
  --bg-dark: #f3f9f6;
  --bg-card: #ffffff;
  --text-light: #1f2937;
  --text-muted: #6b7280;
  --primary: #22c55e;
  --primary-hover: #16a34a;
  --danger: #ef4444;
  --warning: #f59e0b;
  --info: #3b82f6;
  --border: #e5e7eb;
  --glass-blur: blur(0px);
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  
  --sidebar-width: 260px;
}'''

css = css.replace(old_vars, new_vars)

# Remove hardcoded dark background from sidebar
css = css.replace(
    'background: rgba(15, 23, 42, 0.95);',
    'background: #ffffff;'
)

# Remove glass-card background and border specific to dark mode if they exist
css = re.sub(
    r'\.glass-card\s*\{[^}]*\}',
    '.glass-card {\n  background: var(--bg-card);\n  border-radius: 12px;\n  border: 1px solid var(--border);\n  box-shadow: var(--shadow);\n}',
    css
)

# Fix sidebar header text color
css = css.replace(
    'color: var(--text-light);',
    'color: var(--text-light);'
)

# Fix table header colors
css = css.replace(
    'background: rgba(0, 0, 0, 0.2);',
    'background: #f9fafb;'
)

# Fix recent-item background hover
css = css.replace(
    'background: rgba(255, 255, 255, 0.05);',
    'background: #f9fafb;'
)
css = css.replace(
    'background: rgba(255, 255, 255, 0.1);',
    'background: #f3f4f6;'
)
css = css.replace(
    'border-bottom: 1px solid rgba(255, 255, 255, 0.05);',
    'border-bottom: 1px solid var(--border);'
)

# Modal card background
css = css.replace(
    'background: var(--bg-dark);',
    'background: var(--bg-card);'
)

with open('D:/IDEATHON/frontend/admin/admin.css', 'w', encoding='utf-8') as f:
    f.write(css)
