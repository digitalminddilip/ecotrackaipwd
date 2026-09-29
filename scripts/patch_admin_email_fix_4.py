import re

with open('D:/IDEATHON/frontend/admin/admin.js', 'r', encoding='utf-8') as f:
    js = f.read()

new_tr = '''        <td><strong></strong></td>
        <td></td>
        <td><span class="status-badge status-verified">Active</span></td>'''

js = re.sub(r'<td><strong>\$\{col\.name\}</strong></td>\s*<td.*?>.*?</td>\s*<td><span class="status-badge status-verified">Active</span></td>', new_tr, js, flags=re.DOTALL)

with open('D:/IDEATHON/frontend/admin/admin.js', 'w', encoding='utf-8') as f:
    f.write(js)
