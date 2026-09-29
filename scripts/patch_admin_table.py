import re

with open('D:/IDEATHON/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

table_section = '''      </section>

      <!-- REPORTS TABLE SECTION -->
      <section class="panel" style="margin-top: 24px; margin-bottom: 24px;">
        <div class="panel-header" style="margin-bottom: 16px; flex-wrap: wrap; gap: 12px;">
          <div>
            <h2 class="panel-title">Report Queue</h2>
            <p class="panel-subtitle">Manage and assign incoming waste reports.</p>
          </div>
          <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
            <input type="text" id="search" placeholder="Search reports..." oninput="renderReports()" style="padding: 8px 12px; border: 1px solid #E5E7EB; border-radius: 8px; font-size: 0.85rem; min-width: 200px;">
            <select id="status-filter" onchange="renderReports()" style="padding: 8px 12px; border: 1px solid #E5E7EB; border-radius: 8px; font-size: 0.85rem;">
              <option value="">All Statuses</option>
              <option value="reported">Reported</option>
              <option value="ai_analyzed">AI Analyzed</option>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="collected">Collected</option>
              <option value="verified">Verified</option>
            </select>
          </div>
        </div>
        <div style="font-size: 0.85rem; color: #6B7280; margin-bottom: 16px;" id="map-count">0 visible</div>
        
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem;">
            <thead>
              <tr style="border-bottom: 1px solid #E5E7EB; color: #6B7280;">
                <th style="padding: 12px 16px; font-weight: 500;">Report Details</th>
                <th style="padding: 12px 16px; font-weight: 500;">Category</th>
                <th style="padding: 12px 16px; font-weight: 500;">Location</th>
                <th style="padding: 12px 16px; font-weight: 500;">Date</th>
                <th style="padding: 12px 16px; font-weight: 500;">Status</th>
                <th style="padding: 12px 16px; font-weight: 500;">Actions</th>
              </tr>
            </thead>
            <tbody id="reports-body">
              <tr><td colspan="6" class="empty">Loading reports...</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- BOTTOM PANELS -->'''

html = html.replace('      </section>\n\n      <!-- BOTTOM PANELS -->', table_section)

with open('D:/IDEATHON/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
