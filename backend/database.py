from contextlib import closing
import sqlite3
import os
from datetime import datetime, timezone
from typing import Any

DB_PATH = os.getenv("CLEANCONNECT_DATABASE", "cleanconnect.db")

def connect():
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection

def init_db() -> None:
    try:
        with closing(connect()) as connection, connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    points INTEGER DEFAULT 0,
                    picture TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    image_reference TEXT NOT NULL,
                    image_data BLOB,
                    ai_result TEXT,
                    category TEXT,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    description TEXT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    collector_id TEXT,
                    evidence_reference TEXT,
                    evidence_data BLOB
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details_json TEXT,
                    target_role TEXT NOT NULL DEFAULT 'administrator',
                    is_read INTEGER NOT NULL DEFAULT 0,
                    timestamp TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS site_visits (
                    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT,
                    user_agent TEXT,
                    path TEXT,
                    timestamp TEXT NOT NULL
                )
                """
            )

            # Ensure last_login column exists in users table
            cursor.execute("PRAGMA table_info(users)")
            user_cols = [col["name"] for col in cursor.fetchall()]
            if "last_login" not in user_cols:
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
                except Exception:
                    pass

            connection.commit()
            
           
            
            # Seed or reset admin user to ensure login works for demo
            cursor.execute("SELECT user_id FROM users WHERE email = 'dilipksharma1244@gmail.com'")
            admin = cursor.fetchone()
            import uuid
            from .auth import hash_password
            admin_hash = hash_password("Dilip@2006")
            
            if not admin:
                admin_id = f"usr-{uuid.uuid4().hex[:8]}"
                cursor.execute(
                    "INSERT INTO users (user_id, name, email, role, password_hash, created_at, points, picture) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (admin_id, "Dilip Kumar Sharma", "dilipksharma1244@gmail.com", "administrator", admin_hash, datetime.utcnow().isoformat(), 0, "")
                )
            else:
                cursor.execute("UPDATE users SET password_hash = ? WHERE email = 'dilipksharma1244@gmail.com'", (admin_hash,))
            cursor.execute("SELECT user_id FROM users WHERE email = 'ecotrackaipwd@gmail.com'")
            superadmin = cursor.fetchone()
            if not superadmin:
                sa_id = f"usr-{uuid.uuid4().hex[:8]}"
                sa_hash = hash_password("EcoTrack@2026")
                cursor.execute(
                    "INSERT INTO users (user_id, name, email, role, password_hash, created_at, points, picture) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (sa_id, "EcoTrack Super Admin", "ecotrackaipwd@gmail.com", "administrator", sa_hash, datetime.utcnow().isoformat(), 0, "")
                )

            connection.commit()

    except Exception as e:
        print(f"Error initializing DB: {e}")

def save_user(user_id: str, name: str, email: str, role: str, password_hash: str, created_at: str, picture: str = "") -> None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, name, email, role, password_hash, created_at, picture) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, name, email.lower(), role, password_hash, created_at, picture),
        )
        connection.commit()

def update_user_password(email: str, password_hash: str) -> None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (password_hash, email.lower()),
        )
        connection.commit()

def find_user_by_email(email: str) -> dict[str, Any] | None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
    return dict(row) if row else None

def find_user_by_id(user_id: str) -> dict[str, Any] | None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
    return dict(row) if row else None

def load_users() -> list[dict[str, Any]]:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, email, role, points, picture FROM users")
        return [dict(row) for row in cursor.fetchall()]

def add_user_points(user_id: str, points: int) -> None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (points, user_id))
        connection.commit()

def load_reports() -> dict[str, Any]:
    from .main import Report

    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        # Exclude image_data and evidence_data to save memory during bulk loads
        cursor.execute("""
            SELECT report_id, user_id, image_reference, ai_result, category, 
                   latitude, longitude, description, timestamp, status, 
                   collector_id, evidence_reference 
            FROM reports ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
            
    return {
        row["report_id"]: Report(
            report_id=row["report_id"],
            user_id=row["user_id"],
            image_reference=row["image_reference"],
            ai_result=row["ai_result"],
            category=row["category"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            description=row["description"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            status=row["status"],
            collector_id=row["collector_id"],
            evidence_reference=row["evidence_reference"],
        )
        for row in rows
    }

def get_report_image_data(report_id: str) -> bytes | None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute("SELECT image_data FROM reports WHERE report_id = ?", (report_id,))
        row = cursor.fetchone()
    return row["image_data"] if row and row["image_data"] else None

def get_report_evidence_data(report_id: str) -> bytes | None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute("SELECT evidence_data FROM reports WHERE report_id = ?", (report_id,))
        row = cursor.fetchone()
    return row["evidence_data"] if row and row["evidence_data"] else None

def save_report(report: Any, image_data: bytes | None = None, evidence_data: bytes | None = None) -> None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        
        # Check if exists to do UPSERT
        cursor.execute("SELECT report_id FROM reports WHERE report_id = ?", (report.report_id,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(
                """
                INSERT INTO reports (
                    report_id, user_id, image_reference, image_data, ai_result, category,
                    latitude, longitude, description, timestamp, status,
                    collector_id, evidence_reference, evidence_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.report_id,
                    report.user_id,
                    report.image_reference,
                    image_data,
                    report.ai_result,
                    report.category,
                    report.latitude,
                    report.longitude,
                    report.description,
                    report.timestamp.isoformat(),
                    report.status.value,
                    report.collector_id,
                    report.evidence_reference,
                    evidence_data,
                ),
            )
        else:
            # Update fields. Note: We only update BLOB data if it's provided.
            update_sql = """
                UPDATE reports SET
                    ai_result = ?,
                    category = ?,
                    status = ?,
                    collector_id = ?,
                    evidence_reference = ?
            """
            params = [
                report.ai_result, report.category, report.status.value, 
                report.collector_id, report.evidence_reference
            ]
            
            if evidence_data is not None:
                update_sql += ", evidence_data = ?"
                params.append(evidence_data)
                
            if image_data is not None:
                update_sql += ", image_data = ?"
                params.append(image_data)
                
            update_sql += " WHERE report_id = ?"
            params.append(report.report_id)
            
            cursor.execute(update_sql, tuple(params))
            
        connection.commit()

def save_notification(
    notification_id: str,
    notification_type: str,
    title: str,
    message: str,
    details_json: str,
    target_role: str = "administrator",
    timestamp: str | None = None,
) -> None:
    from datetime import datetime, timezone
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO notifications (
                notification_id, type, title, message, details_json, target_role, is_read, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (notification_id, notification_type, title, message, details_json, target_role, ts),
        )
        connection.commit()

def load_notifications(target_role: str = "administrator", limit: int = 50) -> list[dict[str, Any]]:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT notification_id, type, title, message, details_json, target_role, is_read, timestamp
            FROM notifications
            WHERE target_role = ? OR target_role = 'all'
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (target_role, limit),
        )
        rows = cursor.fetchall()
    return [dict(row) for row in rows]

def mark_notification_read(notification_id: str) -> None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE notification_id = ?",
            (notification_id,),
        )
        connection.commit()

def mark_all_notifications_read(target_role: str = "administrator") -> None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE notifications SET is_read = 1 WHERE target_role = ? OR target_role = 'all'",
            (target_role,),
        )
        connection.commit()

def update_user_picture(email: str, picture: str) -> None:
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET picture = ? WHERE email = ?",
            (picture, email.lower()),
        )
        connection.commit()

def record_site_visit(ip_address: str, path: str = "/", user_agent: str = "") -> None:
    try:
        with closing(connect()) as connection, connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO site_visits (ip_address, user_agent, path, timestamp) VALUES (?, ?, ?, ?)",
                (ip_address or "unknown", (user_agent or "")[:250], path[:100], datetime.now(timezone.utc).isoformat()),
            )
            connection.commit()
    except Exception as e:
        print(f"Error recording visit: {e}")


def update_user_last_login(user_id: str) -> None:
    try:
        with closing(connect()) as connection, connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE user_id = ?",
                (datetime.now(timezone.utc).isoformat(), user_id),
            )
            connection.commit()
    except Exception as e:
        print(f"Error updating last login: {e}")


def get_platform_user_and_visitor_stats() -> dict[str, Any]:
    today_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with closing(connect()) as connection, connection:
        cursor = connection.cursor()
        
        # 1. Accounts count by role
        cursor.execute("SELECT role, COUNT(*) as count FROM users GROUP BY role")
        role_counts = {row["role"]: row["count"] for row in cursor.fetchall()}
        citizen_count = role_counts.get("citizen", 0)
        collector_count = role_counts.get("collector", 0)
        admin_count = role_counts.get("administrator", 0)
        total_users = sum(role_counts.values())
        
        # 2. Daily new citizens registered today
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'citizen' AND substr(created_at, 1, 10) = ?", (today_prefix,))
        new_citizens_today = cursor.fetchone()["count"]
        
        # 3. Daily active citizens (logged in or registered today)
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'citizen' AND (substr(last_login, 1, 10) = ? OR substr(created_at, 1, 10) = ?)", (today_prefix, today_prefix))
        active_citizens_today = cursor.fetchone()["count"]

        # 4. Total and unique website visitors
        cursor.execute("SELECT COUNT(*) as total_visits, COUNT(DISTINCT ip_address) as unique_visitors FROM site_visits")
        visit_row = cursor.fetchone()
        total_visits = visit_row["total_visits"] if visit_row else 0
        unique_visitors = visit_row["unique_visitors"] if visit_row else 0

        cursor.execute("SELECT COUNT(*) as count FROM site_visits WHERE substr(timestamp, 1, 10) = ?", (today_prefix,))
        visits_today = cursor.fetchone()["count"]
        
        return {
            "citizens": citizen_count,
            "collectors": collector_count,
            "administrators": admin_count,
            "total_users": total_users,
            "new_citizens_today": new_citizens_today,
            "active_citizens_today": active_citizens_today,
            "total_visits": total_visits,
            "unique_visitors": unique_visitors,
            "visits_today": visits_today,
        }

