import re

with open('D:/IDEATHON/frontend/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Update function definition
code = code.replace(
    'function updateSidebarProfile(name) {',
    'function updateSidebarProfile(name, picture) {'
)

# Update avatar selection logic
old_logic = '''  const uiAvatarUrl = https://ui-avatars.com/api/?name=&background=random&color=fff&rounded=true&size=128;

  if (nameEl) nameEl.textContent = name;
  if (avatarEl) {
    avatarEl.innerHTML = <img src="" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">;
    // clear text content if there was any
    avatarEl.style.background = 'transparent';
  }

  const colAvatarEl = document.getElementById("col-user-avatar");
  if (colAvatarEl) {
    colAvatarEl.innerHTML = <img src="" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">;
    colAvatarEl.style.background = 'transparent';
  }'''

new_logic = '''  const avatarUrl = picture || https://ui-avatars.com/api/?name=&background=random&color=fff&rounded=true&size=128;

  if (nameEl) nameEl.textContent = name;
  if (avatarEl) {
    avatarEl.innerHTML = <img src="" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">;
    avatarEl.style.background = 'transparent';
  }

  const colAvatarEl = document.getElementById("col-user-avatar");
  if (colAvatarEl) {
    colAvatarEl.innerHTML = <img src="" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">;
    colAvatarEl.style.background = 'transparent';
  }'''
  
code = code.replace(old_logic, new_logic)

# Update calls to updateSidebarProfile
code = code.replace(
    'updateSidebarProfile("Guest");',
    'updateSidebarProfile("Guest", null);'
)

code = code.replace(
    'updateSidebarProfile(currentUser.name);',
    'updateSidebarProfile(currentUser.name, currentUser.picture);'
)

with open('D:/IDEATHON/frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(code)
