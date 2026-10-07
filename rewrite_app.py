import re

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Append showAdminView function
new_function = '''
window.showAdminView = function(viewId, el) { 
  document.querySelectorAll('#app-wrapper .sidebar-nav a').forEach(a => a.classList.remove('active'));
  if (el) el.classList.add('active');
  
  const views = ['overview', 'queue', 'new', 'team', 'activity'];
  views.forEach(v => {
    const el = document.getElementById('admin-view-' + v);
    if(el) el.style.display = (v === viewId) ? 'block' : 'none';
  });
};
'''

if 'showAdminView' not in js:
    with open('frontend/app.js', 'a', encoding='utf-8') as f:
        f.write('\n' + new_function)

