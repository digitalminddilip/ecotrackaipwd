import re

with open('D:/IDEATHON/frontend/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

css = css.replace(
    'border-top: 1px solid rgba(255, 255, 255, 0.1);',
    'border-top: 1px solid var(--border-light);'
)

with open('D:/IDEATHON/frontend/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)
