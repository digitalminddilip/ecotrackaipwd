"""
Comprehensive Content Data for EcoTrack AI BCA Project Report.
Contains academic text, specifications, architectural descriptions, tables, and test cases.
Author: Dilip Sharma (DIGITAL MIND DILIP)
"""

PROJECT_TITLE = "ECOTRACK AI"
PROJECT_SUBTITLE = "Next-Gen AI-Powered Civic Cleanliness & Municipal Waste Intelligence Platform"
COURSE_NAME = "Bachelor of Computer Applications (BCA)"
SPECIALIZATION = "Final Year Major Project Report (Group Submission)"
ACADEMIC_YEAR = "2026 – 2027"
GROUP_NAME = "Virus-x"
COLLEGE_NAME = "ITM COLLEGE OF MANAGEMENT"
DEPARTMENT_NAME = "Department of Computer Applications"
GUIDE_NAME = "Prof. SUBHAM CHATURVEDY"
GUIDE_DESIGNATION = "Assistant Professor / Project Guide"
HOD_NAME = "Prof. SHALINI SINGH"
HOD_DESIGNATION = "Head of Department (HOD), Department of Computer Applications"
DIRECTOR_NAME = "Dr. N. K. Singh"
DIRECTOR_DESIGNATION = "Director, ITM College of Management"

TEAM_MEMBERS = [
    {"name": "DILIP KUMAR SHARMA", "roll": "2614018360025", "role": "Team Lead & Full-Stack / AI Architect"},
    {"name": "KARAN YADAV", "roll": "2614018360032", "role": "Backend & Cloud Services Specialist"},
    {"name": "DHIRAJ KUMAR PRAJAPATI", "roll": "2614018360022", "role": "Computer Vision & Verification Specialist"},
    {"name": "GAURAV KUMAR RAWAL", "roll": "2614018360027", "role": "UI/UX & Mobile PWA Specialist"}
]


# Abstract
ABSTRACT_TEXT = (
    "Rapid urbanization and exponential population expansion across Indian metropolitan regions have led to "
    "unprecedented volumes of solid municipal waste, posing severe civic hazards, drainage blockages, and health "
    "crises. Despite extensive municipal initiatives like the Swachh Bharat Abhiyan, traditional civic reporting "
    "mechanisms remain plagued by friction: tedious multi-step manual complaint forms, severe lack of automated "
    "triage, linguistic barriers for non-tech-savvy citizens, and most critically, 'ghost cleanups' where contractors "
    "falsify completion proofs without physical waste collection. Furthermore, standard cloud hosting imposes severe "
    "budgetary constraints and SMTP network blocking (ports 25, 465, 587) that break critical citizen notification systems.\n\n"
    "To resolve these foundational bottlenecks, this project presents EcoTrack AI, an enterprise-grade, "
    "cloud-native civic intelligence platform engineered from the ground up to automate the entire waste lifecycle. "
    "EcoTrack AI integrates cutting-edge Multimodal Artificial Intelligence (Google Gemini Vision combined with a localized "
    "96-dimensional perceptual feature extraction model, EcoTrack-GarbageNet) to classify civic hazards (garbage dumps, "
    "plastic polymers, biohazards, and drainage blockages) from a single camera photograph within < 3.5 seconds. "
    "To eliminate fraudulent contractor claims, the platform introduces a rigorous Computer Vision Verification Engine "
    "enforcing a strict 75.0%+ Structural Similarity Index (SSIM) and perceptual feature match threshold between the "
    "reported hazard and post-cleanup photographic proof before closure.\n\n"
    "To maximize civic participation, the platform features a Bilingual Voice AI Assistant (supporting Hindi and English "
    "voice triage) and a tamper-resistant Green Points gamification ledger that rewards citizens (+10 Green Points) upon "
    "verified waste resolution. To maintain zero-cost operational overhead, the entire software infrastructure is "
    "architected across Render and Vercel free tiers, utilizing a novel Smart Hybrid OTP delivery protocol over Port 443 "
    "HTTPS REST APIs to bypass cloud SMTP blocks. Built on an asynchronous Python FastAPI backend, SQLite in Write-Ahead "
    "Logging (WAL) mode, and a pure Vanilla ES6+ single-page frontend, EcoTrack AI demonstrates a transformative, "
    "scalable, and cost-effective blueprint for next-generation smart municipal governance."
)

# Comparison Table Data
COMPARISON_TABLE_DATA = [
    ["Feature / Dimension", "Traditional Portals / Swachhata App", "EcoTrack AI"],
    ["Incident Reporting Time", "2 to 5 minutes (tedious manual forms)", "< 30 seconds (Camera + GPS Auto-fetch)"],
    ["Hazard Triage & Categorization", "Manual human inspection (delayed 24-48h)", "Instant Multimodal AI Classification (< 3.5s)"],
    ["Proof of Cleanup Verification", "Manual contractor self-certification (Ghost cleanups)", "Automated Computer Vision (75%+ SSIM Gate)"],
    ["Citizen Engagement & Motivation", "Zero incentive; transactional complaints", "Civic Gamification (+10 Green Points Rewards)"],
    ["Linguistic Accessibility", "Static English/Hindi text forms", "Bilingual Conversational Voice AI Assistant"],
    ["Collector Dispatch Workflow", "Disconnected paperwork / WhatsApp messages", "Real-time Field Queue with in-transit states"],
    ["Cloud Infrastructure Cost", "High enterprise cloud license overhead", "$0 Zero-Cost Free-Tier Native Architecture"],
    ["Outbound Email Architecture", "Vulnerable to cloud SMTP port blocks (25/587)", "Resend HTTPS REST over Port 443 + Sandbox Auto-fill"],
]

# Tech Stack Table Data
TECH_STACK_TABLE_DATA = [
    ["Layer / Subsystem", "Technology / Framework", "Version / Standard", "Functional Role in EcoTrack AI"],
    ["Backend Framework", "FastAPI + Starlette", "0.110.0+ / Python 3.11+", "Asynchronous REST API, routing & business logic"],
    ["ASGI Application Server", "Uvicorn", "0.28.0+", "High-throughput asynchronous event-loop server"],
    ["Relational Database", "SQLite 3 (WAL Mode)", "SQLite 3.42+", "Embedded persistence with Write-Ahead Logging concurrency"],
    ["Vision AI Model (Cloud)", "Google Gemini Multimodal", "Gemini 1.5/2.0 Flash", "Zero-shot visual hazard detection & classification"],
    ["Vision AI Model (Edge/Local)", "EcoTrack-GarbageNet", "Custom 96-D Vectors", "Cosine similarity & softmax material classification"],
    ["Proof Verification Engine", "OpenCV / Pillow (PIL)", "SSIM & Perceptual Hash", "Enforcing 75%+ before/after landmark alignment"],
    ["Authentication & Security", "PyJWT & Passlib (Bcrypt)", "HS256, 12-round Salt", "Stateless RBAC authorization & password hashing"],
    ["Communication / Alerts", "Resend HTTPS REST API", "RFC 7519 / Port 443", "Bypassing cloud SMTP blocks for transactional OTP"],
    ["Frontend Client Tier", "Vanilla HTML5, CSS3, ES6+", "W3C Standards Compliant", "High-speed Single Page Application (< 1s load time)"],
    ["Spatial GIS Mapping", "Leaflet.js / OpenStreetMap", "1.9.4+", "Interactive GPS telemetry & incident pins"],
    ["Data Visualizations", "Chart.js", "4.4.0+", "Executive municipal metrics & category doughnut charts"],
    ["Voice Intelligence", "Web Speech API + Gemini", "W3C SpeechRecognition", "Bilingual voice input & real-time audio guidance"],
    ["Hosting & Deployment", "Render & Vercel Edge CDN", "Cloud-Native Free Tier", "Decoupled edge CDN frontend & containerized backend"],
]

print("Base report sections loaded.")
