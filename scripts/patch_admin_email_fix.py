lines = []
with open('D:/IDEATHON/frontend/admin/admin.js', 'r', encoding='utf-8') as f:
    for line in f:
        if '<td></td>' in line:
            line = line.replace('<td></td>', '        <td></td>')
        lines.append(line)

with open('D:/IDEATHON/frontend/admin/admin.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)
