import re

with open('D:/IDEATHON/frontend/auth.css', 'r', encoding='utf-8') as f:
    css = f.read()

new_root = ''':root {
  --app-bg: #F1FCF3;
  --box-bg: rgba(255, 255, 255, 0.95);
  --text-primary: #1D3B1F;
  --text-secondary: #575B58;
  --input-bg: #FFFFFF;
  --input-border: #DFF9E5;
  --primary-color: #2BA84A;
  --primary-text: #ffffff;
  --error-color: #EF4444;
  --auth-font: 'Inter', sans-serif;
  --eco-primary-hover: #1D3B1F;
  --eco-dark: #082B13;
}'''

css = re.sub(r':root\s*\{[^}]*\}', new_root, css)

new_neon = '''.primary-button.neon-btn {
  background: var(--primary-color);
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 6px -1px rgba(43, 168, 74, 0.3), 0 2px 4px -2px rgba(43, 168, 74, 0.3);
}

.primary-button.neon-btn:hover {
  background: var(--eco-primary-hover);
  box-shadow: 0 6px 12px -2px rgba(43, 168, 74, 0.4);
}'''

css = re.sub(r'\.primary-button\.neon-btn\s*\{[^}]*\}\s*\.primary-button\.neon-btn:hover\s*\{[^}]*\}', new_neon, css, flags=re.DOTALL)

# Let's also ensure .primary-button doesn't have existing neon borders
css = re.sub(r'border:\s*2px\s*solid\s*var\(--primary-color\);', 'border: none;', css)

with open('D:/IDEATHON/frontend/auth.css', 'w', encoding='utf-8') as f:
    f.write(css)
