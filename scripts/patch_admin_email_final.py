lines = []
with open('D:/IDEATHON/frontend/admin/admin.js', 'r', encoding='utf-8') as f:
    for line in f:
        lines.append(line)

for i in range(len(lines)):
    if 'const tr = document.createElement("tr");' in lines[i]:
        lines[i+1] = '      tr.innerHTML = `\n'
        lines[i+2] = '        <td><strong>${col.name}</strong></td>\n'
        lines[i+3] = '        <td>${col.email || "No Email"}</td>\n'
        lines[i+4] = '        <td><span class="status-badge status-verified">Active</span></td>\n'
        lines[i+5] = '      `;\n'

with open('D:/IDEATHON/frontend/admin/admin.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)
