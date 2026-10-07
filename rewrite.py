import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Wrap the overview sections
html = html.replace('<!-- PAGE HEADER -->', '<div id="admin-view-overview">\n      <!-- PAGE HEADER -->')
html = html.replace('</section>\n\n    </main>', '</section>\n      </div>\n\n      <!-- Other Views Here -->\n    </main>')

# Now inject the new views
new_views = '''
      <!-- VIEW: Report queue -->
      <div id="admin-view-queue" style="display: none;">
        <section class="page-header">
          <div class="page-eyebrow">COMMAND CENTER / QUEUE</div>
          <h1 class="page-title">Report Queue</h1>
        </section>
        <section class="panel" style="margin-top: 24px; overflow-x: auto;">
          <div style="display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap;">
            <input type="text" id="search" placeholder="Search report ID..." style="padding: 10px 16px; border-radius: 8px; border: 1px solid var(--col-border); min-width: 250px;">
            <select id="status-filter" style="padding: 10px 16px; border-radius: 8px; border: 1px solid var(--col-border);">
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="collected">Collected</option>
              <option value="verified">Verified</option>
            </select>
            <div id="map-count" style="align-self: center; font-weight: 500; color: var(--col-text-muted);">0 visible</div>
          </div>
          <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
              <tr style="border-bottom: 1px solid var(--col-border);">
                <th style="padding: 12px; color: var(--col-text-muted); font-weight: 500;">Report</th>
                <th style="padding: 12px; color: var(--col-text-muted); font-weight: 500;">Category</th>
                <th style="padding: 12px; color: var(--col-text-muted); font-weight: 500;">Location</th>
                <th style="padding: 12px; color: var(--col-text-muted); font-weight: 500;">Date</th>
                <th style="padding: 12px; color: var(--col-text-muted); font-weight: 500;">Status</th>
                <th style="padding: 12px; color: var(--col-text-muted); font-weight: 500;">Action</th>
              </tr>
            </thead>
            <tbody id="reports-body">
              <tr><td colspan="6" class="empty">Loading...</td></tr>
            </tbody>
          </table>
        </section>
      </div>

      <!-- VIEW: New report -->
      <div id="admin-view-new" style="display: none;">
        <section class="page-header">
          <div class="page-eyebrow">COMMAND CENTER / NEW</div>
          <h1 class="page-title">New Report</h1>
        </section>
        <section class="panel" style="margin-top: 24px;">
           <p>Log a report on behalf of a citizen or collector.</p>
           <form id="admin-report-form" style="display: flex; flex-direction: column; gap: 16px; max-width: 600px; margin-top: 24px;">
            <textarea placeholder="Description..." style="padding: 12px; border-radius: 8px; border: 1px solid var(--col-border); min-height: 100px;"></textarea>
            <button type="button" class="col-btn-primary" style="align-self: flex-start;">Submit Report</button>
           </form>
        </section>
      </div>

      <!-- VIEW: Collection team -->
      <div id="admin-view-team" style="display: none;">
        <section class="page-header">
          <div class="page-eyebrow">COMMAND CENTER / TEAM</div>
          <h1 class="page-title">Collection Team</h1>
        </section>
        <section class="panel" style="margin-top: 24px;">
          <p>Manage collectors and routing assignments.</p>
          <div style="margin-top: 24px; display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));">
            <div style="padding: 16px; border: 1px solid var(--col-border); border-radius: 12px; display: flex; align-items: center; gap: 16px;">
              <div style="width: 48px; height: 48px; border-radius: 50%; background: var(--col-primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">RV</div>
              <div>
                <div style="font-weight: 600;">Rahul Verma</div>
                <div style="font-size: 0.8rem; color: var(--col-text-muted);">Active Route 2</div>
              </div>
            </div>
            <div style="padding: 16px; border: 1px solid var(--col-border); border-radius: 12px; display: flex; align-items: center; gap: 16px;">
              <div style="width: 48px; height: 48px; border-radius: 50%; background: var(--col-primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">SK</div>
              <div>
                <div style="font-weight: 600;">Sunita Kaur</div>
                <div style="font-size: 0.8rem; color: var(--col-text-muted);">Idle</div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- VIEW: Activity -->
      <div id="admin-view-activity" style="display: none;">
        <section class="page-header">
          <div class="page-eyebrow">COMMAND CENTER / LOGS</div>
          <h1 class="page-title">Activity Log</h1>
        </section>
        <section class="panel" style="margin-top: 24px;">
          <p>System-wide actions and events.</p>
          <div style="margin-top: 24px; display: flex; flex-direction: column; gap: 16px;">
            <div style="padding: 16px; border: 1px solid var(--col-border); border-radius: 8px;">
               <div style="font-weight: 600;">Report #RE-889 verified</div>
               <div style="font-size: 0.85rem; color: var(--col-text-muted); margin-top: 4px;">2 hours ago by System</div>
            </div>
            <div style="padding: 16px; border: 1px solid var(--col-border); border-radius: 8px;">
               <div style="font-weight: 600;">Collector RV started route</div>
               <div style="font-size: 0.85rem; color: var(--col-text-muted); margin-top: 4px;">4 hours ago by Rahul Verma</div>
            </div>
          </div>
        </section>
      </div>
'''
html = html.replace('<!-- Other Views Here -->', new_views)

# Update sidebar links to have onclick
html = html.replace('<a href="#" class="active"><i class="fa-solid fa-chart-line"></i> Overview</a>', '<a href="#" class="active" onclick="showAdminView(\'overview\', this)"><i class="fa-solid fa-chart-line"></i> Overview</a>')
html = html.replace('<a href="#"><i class="fa-regular fa-rectangle-list"></i> Report queue</a>', '<a href="#" onclick="showAdminView(\'queue\', this)"><i class="fa-regular fa-rectangle-list"></i> Report queue</a>')
html = html.replace('<a href="#"><i class="fa-regular fa-file-lines"></i> New report</a>', '<a href="#" onclick="showAdminView(\'new\', this)"><i class="fa-regular fa-file-lines"></i> New report</a>')
html = html.replace('<a href="#"><i class="fa-solid fa-users"></i> Collection team</a>', '<a href="#" onclick="showAdminView(\'team\', this)"><i class="fa-solid fa-users"></i> Collection team</a>')
html = html.replace('<a href="#"><i class="fa-solid fa-chart-area"></i> Activity</a>', '<a href="#" onclick="showAdminView(\'activity\', this)"><i class="fa-solid fa-chart-area"></i> Activity</a>')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
