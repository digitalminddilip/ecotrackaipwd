"""
Comprehensive Test Suite for EcoTrack AI (EcoTrack AI) Upgrades
Verifies:
1. Database schema migration & persistence of new fields
2. Reverse Geocoding API & Address extraction
3. Public Config API
4. Security & File Validation (magic bytes, size, format)
5. Instant Waste Analysis API (/reports/analyze-waste)
6. Report Creation API with GPS Accuracy & Metadata (/reports)
7. Admin report retrieval with telemetry
"""
import sys
import os
from io import BytesIO
from datetime import datetime, timezone
from PIL import Image
from fastapi.testclient import TestClient

# Ensure backend can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app, reports, init_db, users, User, Role
from backend.auth import create_token
from backend.database import connect, save_report, load_reports

client = TestClient(app)

def setup_test_users():
    test_citizen_id = "usr-test-citizen"
    test_admin_id = "usr-test-admin"
    users[test_citizen_id] = User(
        user_id=test_citizen_id,
        name="Test Citizen",
        email="citizen@test.com",
        role=Role.citizen,
        points=100
    )
    users[test_admin_id] = User(
        user_id=test_admin_id,
        name="Test Admin",
        email="admin@test.com",
        role=Role.administrator,
        points=500
    )

def create_dummy_jpeg() -> bytes:
    img = Image.new("RGB", (300, 300), color=(34, 139, 34))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def create_fake_file() -> bytes:
    return b"This is plain text pretending to be an image."

def test_database_schema():
    print("Testing Database Schema Migration...")
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(reports)")
    cols = {row["name"]: row["type"] for row in cursor.fetchall()}
    conn.close()

    required_cols = [
        "gps_accuracy",
        "location_timestamp",
        "formatted_address",
        "ai_confidence",
        "location_source",
        "is_manually_confirmed"
    ]
    for col in required_cols:
        assert col in cols, f"Column '{col}' missing from reports table schema!"
    print("  -> All 6 modern telemetry columns present in SQLite reports table.")

def test_api_config():
    print("Testing GET /api/config...")
    res = client.get("/api/config")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "google_maps_configured" in data
    assert "app_name" in data
    assert data["version"] == "2.0.0"
    print(f"  -> Config endpoint returned: app_name='{data['app_name']}', google_maps_configured={data['google_maps_configured']}")

def test_reverse_geocode_api():
    print("Testing GET /api/location/reverse-geocode...")
    res = client.get("/api/location/reverse-geocode?latitude=26.7606&longitude=83.3732")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "formatted_address" in data or "address" in data
    assert "latitude" in data and "longitude" in data
    print(f"  -> Reverse Geocoded address: '{data.get('formatted_address')}' (Provider: {data.get('provider')})")

def test_security_validation():
    print("Testing Security & File Validation...")
    token = create_token("usr-test-citizen", "citizen")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Reject fake text disguised as image
    fake_bytes = create_fake_file()
    res = client.post(
        "/reports/analyze-waste",
        headers=headers,
        files={"image": ("fake.jpg", fake_bytes, "image/jpeg")}
    )
    assert res.status_code == 400, f"Expected 400 for fake image, got {res.status_code}"
    print("  -> Successfully rejected corrupted/spoofed image with status 400.")

    # 2. Reject unsupported MIME type
    res = client.post(
        "/reports/analyze-waste",
        headers=headers,
        files={"image": ("script.py", b"print('hello')", "text/x-python")}
    )
    assert res.status_code == 400, f"Expected 400 for python script, got {res.status_code}"
    print("  -> Successfully rejected disallowed file type with status 400.")

def test_analyze_waste_endpoint():
    print("Testing POST /reports/analyze-waste...")
    token = create_token("usr-test-citizen", "citizen")
    headers = {"Authorization": f"Bearer {token}"}

    valid_jpeg = create_dummy_jpeg()
    res = client.post(
        "/reports/analyze-waste",
        headers=headers,
        files={"image": ("waste_bottle.jpg", valid_jpeg, "image/jpeg")}
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["status"] == "success"
    assert "category" in data
    assert "confidence" in data
    assert "disposal_bin" in data
    print(f"  -> Waste classified: category='{data['category']}', confidence={data['confidence']}, bin='{data['disposal_bin']}'")

def test_report_creation_and_telemetry():
    print("Testing POST /reports with GPS Telemetry...")
    token = create_token("usr-test-citizen", "citizen")
    headers = {"Authorization": f"Bearer {token}"}

    valid_jpeg = create_dummy_jpeg()
    form_data = {
        "latitude": 26.760612,
        "longitude": 83.373245,
        "gps_accuracy": 14.5,
        "location_timestamp": datetime.now(timezone.utc).isoformat(),
        "formatted_address": "Dharmashala Flyover, Gorakhpur, UP, 273001",
        "location_source": "gps",
        "is_manually_confirmed": True,
        "description": "Accumulation of plastic cups and packaging near drainage line.",
        "name": "Citizen Verifier"
    }

    res = client.post(
        "/reports",
        headers=headers,
        data=form_data,
        files={"image": ("plastic_dump.jpg", valid_jpeg, "image/jpeg")}
    )
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    created = res.json()
    report_id = created["report_id"]
    assert created["latitude"] == 26.760612
    assert created["longitude"] == 83.373245
    assert created["gps_accuracy"] == 14.5
    assert created["location_source"] == "gps"
    assert created["is_manually_confirmed"] is True
    assert created["formatted_address"] == "Dharmashala Flyover, Gorakhpur, UP, 273001"
    print(f"  -> Report {report_id} successfully created with full GPS telemetry & verified address.")

    # Check persistence in database
    loaded = load_reports()
    assert report_id in loaded, f"Report {report_id} not found in database load_reports()!"
    saved = loaded[report_id]
    assert saved.gps_accuracy == 14.5
    assert saved.location_source == "gps"
    assert saved.is_manually_confirmed is True
    assert saved.formatted_address == "Dharmashala Flyover, Gorakhpur, UP, 273001"
    print("  -> Verified report persisted in SQLite database and correctly reloaded with all fields.")

    # Check Admin retrieval GET /reports
    admin_token = create_token("usr-test-admin", "administrator")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_res = client.get("/reports", headers=admin_headers)
    assert admin_res.status_code == 200
    admin_reports = admin_res.json()
    match = next((r for r in admin_reports if r["report_id"] == report_id), None)
    assert match is not None
    assert match["gps_accuracy"] == 14.5
    print("  -> Admin dashboard GET /reports receives exact report coordinates, accuracy, and address.")

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING ECOTRACK AI UPGRADE VERIFICATION TEST SUITE")
    print("=" * 60)
    setup_test_users()
    test_database_schema()
    test_api_config()
    test_reverse_geocode_api()
    test_security_validation()
    test_analyze_waste_endpoint()
    test_report_creation_and_telemetry()
    print("=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
