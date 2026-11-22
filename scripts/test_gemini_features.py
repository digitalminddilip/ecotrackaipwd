"""
Test suite verifying Gemini API features in EcoTrack AI:
1. Gemini Multimodal Dual-Image Cleanup Auditor
2. Gemini Municipal Executive Briefing Engine
3. Integrated FastAPI Endpoints
"""

import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import find_user_by_email, get_report_image_data, get_report_evidence_data
from backend.auth import create_token
from backend.image_comparison import gemini_audit_cleanup
from backend.ai_executive import generate_executive_briefing


def test_gemini_features():
    print("==================================================================")
    print("🌿 Testing EcoTrack AI - Gemini API Features Verification Suite")
    print("==================================================================")

    # 1. Test Cleanup Auditor Direct Function
    print("\n[1/4] Testing Gemini Dual-Image Cleanup Auditor...")
    sample_rep_id = "rpt-75c12727"
    img1 = get_report_image_data(sample_rep_id)
    img2 = get_report_evidence_data(sample_rep_id)
    assert img1 is not None and img2 is not None, f"Images for {sample_rep_id} missing in SQLite"

    audit = gemini_audit_cleanup(img1, img2, category="garbage_dumps", description="Street waste dump")
    print("  -> Verdict:", audit.get("verdict"))
    print("  -> Location Match:", f"{audit.get('location_match_pct')}%")
    print("  -> Cleanliness Score:", f"{audit.get('cleanliness_pct')}%")
    print("  -> Provider:", audit.get("provider"))
    print("  -> Recommended Action:", audit.get("recommended_action"))
    print("  -> Summary:", audit.get("audit_summary")[:80] + "...")
    assert audit.get("success") is True, "Audit failed"
    print("  [PASS] Dual-Image Cleanup Auditor operational.")

    # 2. Test Executive Briefing Direct Function
    print("\n[2/4] Testing Gemini Municipal Executive Briefing Engine...")
    stats = {
        "total_reports": 30,
        "pending_reports": 6,
        "collected_reports": 24,
        "category_counts": {"plastic": 15, "garbage_dumps": 10, "drain_blockage": 5},
        "status_counts": {"verified": 22, "collected": 2, "assigned": 6}
    }
    briefing = generate_executive_briefing(stats, [{"report_id": "rpt-01", "category": "plastic", "status": "assigned"}])
    print("  -> Hygiene Index:", f"{briefing.get('hygiene_index')}/100")
    print("  -> Rating Grade:", briefing.get("rating_grade"))
    print("  -> Status:", briefing.get("district_status"))
    print("  -> Headline:", briefing.get("executive_headline"))
    print("  -> Findings count:", len(briefing.get("key_findings", [])))
    print("  -> Directives count:", len(briefing.get("urgent_directives", [])))
    assert briefing.get("success") is True, "Briefing failed"
    print("  [PASS] Municipal Executive Briefing operational.")

    # 3. Test FastAPI REST Endpoints via TestClient
    print("\n[3/4] Testing FastAPI REST Endpoints with Admin Token...")
    admin = find_user_by_email("dilipksharma1244@gmail.com")
    assert admin is not None, "Admin user not found in SQLite"
    token = create_token(admin["user_id"], admin["role"])
    client = TestClient(app)

    # 3a. GET /reports/{id}/verify-audit
    resp_audit = client.get(f"/reports/{sample_rep_id}/verify-audit", headers={"Authorization": f"Bearer {token}"})
    print("  -> GET /reports/{id}/verify-audit Status:", resp_audit.status_code)
    assert resp_audit.status_code == 200, f"Expected 200, got {resp_audit.status_code}"
    audit_json = resp_audit.json()
    assert audit_json["report_id"] == sample_rep_id
    print("  [PASS] Verify Audit endpoint working.")

    # 3b. GET /analytics/ai-briefing
    resp_brief = client.get("/analytics/ai-briefing", headers={"Authorization": f"Bearer {token}"})
    print("  -> GET /analytics/ai-briefing Status:", resp_brief.status_code)
    assert resp_brief.status_code == 200, f"Expected 200, got {resp_brief.status_code}"
    brief_json = resp_brief.json()
    assert "hygiene_index" in brief_json
    print("  [PASS] AI Briefing endpoint working.")

    # 4. Test /image-compare endpoint integration
    print("\n[4/4] Testing POST /image-compare with dual image payload...")
    files = {
        "photo1": ("before.jpg", img1, "image/jpeg"),
        "photo2": ("after.jpg", img2, "image/jpeg")
    }
    resp_compare = client.post("/image-compare", files=files, headers={"Authorization": f"Bearer {token}"})
    print("  -> POST /image-compare Status:", resp_compare.status_code)
    assert resp_compare.status_code == 200, f"Expected 200, got {resp_compare.status_code}"
    compare_json = resp_compare.json()
    assert "gemini_audit" in compare_json, "gemini_audit missing in /image-compare response"
    print("  -> Audit in /image-compare verdict:", compare_json["gemini_audit"]["verdict"])
    print("  [PASS] /image-compare endpoint upgraded.")

    print("\n==================================================================")
    print("🎉 ALL GEMINI API FEATURES VERIFIED SUCCESSFULLY!")
    print("==================================================================")


if __name__ == "__main__":
    test_gemini_features()
