def check_brackets(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    stack = []
    lines = content.split('\n')
    for line_num, line in enumerate(lines):
        for char_num, char in enumerate(line):
            if char in '{[(':
                stack.append((char, line_num))
            elif char in '}])':
                if not stack:
                    return f"Unmatched closing {char} at line {line_num+1}"
                top = stack.pop()[0]
                if (top == '{' and char != '}') or \
                   (top == '[' and char != ']') or \
                   (top == '(' and char != ')'):
                    return f"Mismatched {char} at line {line_num+1}"
    
    if stack:
        return f"Unmatched opening brackets left: {stack}"
    return "All brackets match!"

print(check_brackets('D:/IDEATHON/frontend/admin/admin.js'))
