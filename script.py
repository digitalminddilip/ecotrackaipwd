with open('D:/IDEATHON/frontend/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    form.reset();
    getLocation();
    if (byId("file-label")) byId("file-label").textContent = "Choose a photo";
    message.style.color = "#27ae60";
    message.textContent = `Reference No: ${result.report_id} - Record successful and confirmation letter will be sent soon`;
    
    // Clear message after 5 seconds
    setTimeout(() => {
      if (message.textContent.includes(result.report_id)) message.textContent = "";
    }, 5000);
    
    await loadDashboard();"""

replacement = """    form.reset();
    getLocation();
    if (byId("file-label")) byId("file-label").textContent = "Choose a photo";
    message.textContent = "";
    
    // Show notification alert
    alert(`Report submitted successfully!\nReference No: ${result.report_id}\nA confirmation will be sent soon.`);
    
    await loadDashboard();
    
    // Auto-navigate to My Reports view
    const reportsLinks = document.querySelectorAll('.col-nav-link');
    for (let link of reportsLinks) {
      if (link.textContent.includes('My Reports')) {
        showCitView('reports', link);
        break;
      }
    }"""

if target in content:
    content = content.replace(target, replacement)
    with open('D:/IDEATHON/frontend/app.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced successfully')
else:
    print('Target not found')
