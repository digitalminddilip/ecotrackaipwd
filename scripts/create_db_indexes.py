import sqlite3
import os

DB_PATH = os.getenv("ECOTRACK_DATABASE", os.getenv("CLEANCONNECT_DATABASE", "cleanconnect.db"))

print(f"Connecting to {DB_PATH}...")
con = sqlite3.connect(DB_PATH)
cur = con.cursor()

indexes = [
    ("idx_reports_user_id", "CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id)"),
    ("idx_reports_status", "CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)"),
    ("idx_reports_collector_id", "CREATE INDEX IF NOT EXISTS idx_reports_collector_id ON reports(collector_id)"),
    ("idx_reports_timestamp", "CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON reports(timestamp DESC)"),
    ("idx_reports_category", "CREATE INDEX IF NOT EXISTS idx_reports_category ON reports(category)"),
    ("idx_reports_location", "CREATE INDEX IF NOT EXISTS idx_reports_location ON reports(latitude, longitude)"),
    ("idx_reports_status_timestamp", "CREATE INDEX IF NOT EXISTS idx_reports_status_timestamp ON reports(status, timestamp DESC)"),
    ("idx_notifications_role_read", "CREATE INDEX IF NOT EXISTS idx_notifications_role_read ON notifications(target_role, is_read)"),
    ("idx_notifications_timestamp", "CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications(timestamp DESC)"),
    ("idx_site_visits_timestamp", "CREATE INDEX IF NOT EXISTS idx_site_visits_timestamp ON site_visits(timestamp DESC)"),
    ("idx_site_visits_ip", "CREATE INDEX IF NOT EXISTS idx_site_visits_ip ON site_visits(ip_address)"),
    ("idx_users_role", "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)"),
    ("idx_users_email", "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"),
]

for name, sql in indexes:
    cur.execute(sql)
    print(f"Index ensured: {name}")

con.commit()

print("\nCurrent Database Indexes:")
cur.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index'")
for row in cur.fetchall():
    print(f"  - {row[0]} (on table {row[1]})")

con.close()
print("All performance indexes created successfully.")
