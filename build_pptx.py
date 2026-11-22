import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

DARK_BG = RGBColor(15, 23, 42)      # #0F172A
CARD_BG = RGBColor(30, 41, 59)      # #1E293B
CARD_BORDER = RGBColor(51, 65, 85)  # #334155
EMERALD = RGBColor(16, 185, 129)    # #10B981
CYAN = RGBColor(56, 189, 248)       # #38BDF8
AMBER = RGBColor(245, 158, 11)      # #F59E0B
WHITE = RGBColor(248, 250, 252)     # #F8FAFC
GRAY = RGBColor(148, 163, 184)      # #94A3B8

def add_bg(slide):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = DARK_BG
    bg.line.color.rgb = DARK_BG
    return bg

def add_header(slide, title_text, category_text="ECOTRACK AI (CLEANCONNECT) • PITCH DECK"):
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = EMERALD
    
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = WHITE

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.5)
    return shape

# ==========================================
# SLIDE 1: TITLE SLIDE
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
add_bg(s1)

badge = add_card(s1, Inches(0.8), Inches(1.2), Inches(3.8), Inches(0.45), EMERALD, EMERALD)
tf_b = badge.text_frame
p_b = tf_b.paragraphs[0]
p_b.text = "🌿 NEXT-GEN CIVIC INTELLIGENCE"
p_b.font.size = Pt(11)
p_b.font.bold = True
p_b.font.color.rgb = DARK_BG
p_b.alignment = PP_ALIGN.CENTER

tb = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.2))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "EcoTrack AI (CleanConnect)"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = WHITE

p2 = tf.add_paragraph()
p2.text = "Next-Gen AI-Powered Civic Cleanliness & Municipal Waste Intelligence Platform"
p2.font.size = Pt(20)
p2.font.color.rgb = CYAN

cards_data = [
    ("Multimodal Vision AI", "Gemini 1.5/2.0 + Perceptual Hashing for automated waste hazard triage.", EMERALD),
    ("Voice AI Assistant", "Conversational English & Hinglish voice reporting for zero-friction civic input.", CYAN),
    ("Municipal Command Center", "Live GIS spatial clustering, collector dispatch & CV before/after proof verification.", AMBER)
]

for i, (title, desc, color) in enumerate(cards_data):
    card = add_card(s1, Inches(0.8 + i*3.95), Inches(4.3), Inches(3.8), Inches(2.0))
    tb_c = s1.shapes.add_textbox(Inches(1.0 + i*3.95), Inches(4.5), Inches(3.4), Inches(1.6))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p_t = tf_c.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(16)
    p_t.font.bold = True
    p_t.font.color.rgb = color
    
    p_d = tf_c.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = GRAY

foot_tb = s1.shapes.add_textbox(Inches(0.8), Inches(6.6), Inches(11.7), Inches(0.5))
tf_foot = foot_tb.text_frame
p_f = tf_foot.paragraphs[0]
p_f.text = "Built & Presented by: Dilip Sharma (DIGITAL MIND DILIP)  •  Cloud-Native & Docker Ready"
p_f.font.size = Pt(12)
p_f.font.color.rgb = GRAY

s1.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (15-20s):\n"
    "Good morning judges and evaluators! Today, I am proud to present EcoTrack AI—also known as CleanConnect. "
    "It is a next-generation civic cleanliness and municipal waste intelligence platform designed to eliminate urban waste bottlenecks "
    "by bridging the gap between citizens encountering hazards and municipal sanitation squads in real time."
)

# ==========================================
# SLIDE 2: THE PROBLEM STATEMENT
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
add_bg(s2)
add_header(s2, "The Urban Sanitation Crisis: Why Current Systems Fail")

problems = [
    ("1. Citizen Reporting Friction", 
     "• Traditional portals require lengthy forms, OTP delays, or desktop access.\n"
     "• No instant validation: citizens abandon reports due to lack of visibility.\n"
     "• Exclusion: Non-tech savvy or illiterate citizens cannot type complaint descriptions.",
     RGBColor(239, 68, 68)),
    ("2. Municipal Blindspots & Delays", 
     "• Authorities lack real-time geospatial visibility into waste density hotspots.\n"
     "• Manual triage: staff waste hours sorting duplicate or irrelevant photos.\n"
     "• Inefficient routing leads to delayed pickups and overflowing municipal dumps.",
     AMBER),
    ("3. The Verification Gap & Ghost Cleanups", 
     "• Ground contractors mark tasks 'Completed' without verifiable visual proof.\n"
     "• Municipal supervisors cannot inspect hundreds of sites manually.\n"
     "• Lack of accountability erodes citizen trust and wastes public funds.",
     RGBColor(244, 63, 94))
]

for i, (title, points, color) in enumerate(problems):
    add_card(s2, Inches(0.8 + i*3.95), Inches(1.8), Inches(3.8), Inches(4.8))
    tb_p = s2.shapes.add_textbox(Inches(1.0 + i*3.95), Inches(2.0), Inches(3.4), Inches(4.4))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True
    p_title = tf_p.paragraphs[0]
    p_title.text = title
    p_title.font.size = Pt(16)
    p_title.font.bold = True
    p_title.font.color.rgb = color
    
    for line in points.split("\n"):
        p_pt = tf_p.add_paragraph()
        p_pt.text = line
        p_pt.font.size = Pt(12)
        p_pt.font.color.rgb = WHITE if line.startswith("•") else GRAY

s2.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (30-40s):\n"
    "Every city struggles with municipal waste. Over 62 million tonnes of waste is generated annually, yet nearly 40% remains unattended. "
    "Why? Because the system is broken on three fronts: First, reporting is full of friction—citizens don't want to fill 10-field forms. "
    "Second, municipal authorities operate completely blind without spatial heatmaps. And third, the biggest loophole: ghost cleanups, "
    "where contractors claim a spot is cleaned without any algorithmic verification."
)

# ==========================================
# SLIDE 3: THE SOLUTION — ECOTRACK AI
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
add_bg(s3)
add_header(s3, "The Solution: A 360° Closed-Loop Civic Intelligence Ecosystem")

sol_steps = [
    ("Step 1: 15-Sec Report", "Citizen snaps photo or speaks via Voice AI. Auto-GPS geotags the exact site coordinates.", CYAN),
    ("Step 2: AI Triage", "Multimodal AI classifies waste material, hazard severity, and disposal bin in milliseconds.", EMERALD),
    ("Step 3: GIS Dispatch", "Admin Command Center clusters reports on live map & auto-routes nearest collector.", AMBER),
    ("Step 4: CV Verification", "Collector uploads cleanup proof. Computer vision validates 75%+ site match before closure.", RGBColor(168, 85, 247)),
    ("Step 5: Green Rewards", "Verified cleanup awards civic Green Points. Citizen tracks progress on public leaderboard.", EMERALD)
]

for i, (title, desc, color) in enumerate(sol_steps):
    card = add_card(s3, Inches(0.8 + i*2.38), Inches(1.9), Inches(2.25), Inches(4.5))
    tb_s = s3.shapes.add_textbox(Inches(0.9 + i*2.38), Inches(2.1), Inches(2.05), Inches(4.1))
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True
    p_num = tf_s.paragraphs[0]
    p_num.text = f"0{i+1}"
    p_num.font.size = Pt(28)
    p_num.font.bold = True
    p_num.font.color.rgb = color
    
    p_t = tf_s.add_paragraph()
    p_t.text = title
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = WHITE
    
    p_d = tf_s.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = GRAY

s3.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (30s):\n"
    "EcoTrack AI solves this through an end-to-end closed loop: "
    "A citizen reports in 15 seconds via camera or Hinglish voice. "
    "Our multimodal AI engine instantly categorizes the waste and recyclability. "
    "The municipal command center visualizes the issue on a live GIS heatmap and assigns the nearest collector. "
    "Once cleaned, the collector submits photo evidence, which our Computer Vision verification engine compares against the original. "
    "Only after algorithmic verification is the ticket closed and Green Points credited to the citizen!"
)

# ==========================================
# SLIDE 4: CORE AI INNOVATIONS
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
add_bg(s4)
add_header(s4, "Under the Hood: Three Core AI Innovations")

ai_cards = [
    ("1. Multimodal Waste Vision Pipeline",
     "• Google Gemini Vision API for high-level scene reasoning.\n"
     "• Local Perceptual Model (96-Dimensional feature extractor: Color Histograms, RGB & HSV moments).\n"
     "• Zero-downtime offline fallback: Works even if external cloud APIs are unreachable.\n"
     "• Material detection: Plastic, Biodegradable, Glass, Metal, Paper, Cardboard.",
     EMERALD),
    ("2. Conversational Voice AI Assistant",
     "• Natural bilingual processing supporting English & Hinglish conversational queries.\n"
     "• Speech-to-action pipeline: Allows non-literate citizens to report waste by speaking.\n"
     "• Answers queries regarding recycling guidelines, segregation bins (Blue vs Green), and reporting status.\n"
     "• Instant context-aware responses with zero typing required.",
     CYAN),
    ("3. Computer Vision Verification Engine",
     "• Algorithmic Before-and-After image comparison.\n"
     "• Background structure invariant matching: Verifies that the post-cleanup photo is indeed taken at the SAME physical location.\n"
     "• 75%+ visual clearance threshold required to approve report closure.\n"
     "• Automatically stops fake/ghost cleanup claims and fraudulent reward claims.",
     AMBER)
]

for i, (title, body, color) in enumerate(ai_cards):
    add_card(s4, Inches(0.8 + i*3.95), Inches(1.8), Inches(3.8), Inches(4.8))
    tb_a = s4.shapes.add_textbox(Inches(1.0 + i*3.95), Inches(2.0), Inches(3.4), Inches(4.4))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True
    p_t = tf_a.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(16)
    p_t.font.bold = True
    p_t.font.color.rgb = color
    
    for line in body.split("\n"):
        p_l = tf_a.add_paragraph()
        p_l.text = line
        p_l.font.size = Pt(12)
        p_l.font.color.rgb = WHITE if line.startswith("•") else GRAY

s4.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (40s):\n"
    "Let me highlight three technical breakthroughs in our AI architecture: "
    "First, our dual-layer vision pipeline. We combine Google Gemini Vision for deep semantic categorization with a custom 96-dimensional local feature extractor. If the internet drops or an API quota expires, our local perceptual model takes over seamlessly. "
    "Second, our Voice AI Assistant. India has diverse linguistic needs; our Voice AI understands English and Hinglish seamlessly. A citizen can literally say 'Yahan kachra pada hai' and the assistant guides the reporting. "
    "Third, our CV verification engine: It mathematically verifies background invariants between the before and after pictures, preventing fraudulent contractor submissions."
)

# ==========================================
# SLIDE 5: 3 ROLE-BASED PORTALS
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
add_bg(s5)
add_header(s5, "Role-Based Architecture: Dedicated Portals for Every Stakeholder")

roles = [
    ("👤 CITIZEN PORTAL",
     "Empowering the Public",
     "• 1-Click Camera & Voice AI Reporting\n"
     "• Automated GPS Geotagging & Address Reverse Geocoding\n"
     "• Live Status Tracker (Reported -> In Progress -> Verified)\n"
     "• Gamification: Green Points & Community Leaderboard\n"
     "• Google OAuth 2.0 & Email OTP Login",
     CYAN),
    ("🚛 COLLECTOR PORTAL",
     "Arming the Ground Workforce",
     "• Real-time queue of nearby assigned sanitation tickets\n"
     "• Turn-by-turn map navigation to exact hazard GPS coords\n"
     "• 1-Tap Task Acceptance & In-Progress status update\n"
     "• Camera upload for mandatory After-Cleanup Photo Evidence\n"
     "• Fast OTP-based mobile authentication",
     AMBER),
    ("🛡️ MUNICIPAL ADMIN CENTER",
     "Executive Command & Oversight",
     "• Live GIS spatial map with real-time incident pins\n"
     "• Collector fleet dispatching & workforce utilization metrics\n"
     "• Automated AI verification audit with manual override\n"
     "• Comprehensive analytics: resolution time & category trends\n"
     "• Exportable audit reports for municipal governance",
     EMERALD)
]

for i, (title, sub, bullets, color) in enumerate(roles):
    add_card(s5, Inches(0.8 + i*3.95), Inches(1.8), Inches(3.8), Inches(4.8))
    tb_r = s5.shapes.add_textbox(Inches(1.0 + i*3.95), Inches(2.0), Inches(3.4), Inches(4.4))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p_t = tf_r.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(17)
    p_t.font.bold = True
    p_t.font.color.rgb = color
    
    p_s = tf_r.add_paragraph()
    p_s.text = sub
    p_s.font.size = Pt(12)
    p_s.font.bold = True
    p_s.font.color.rgb = GRAY
    
    for line in bullets.split("\n"):
        p_b = tf_r.add_paragraph()
        p_b.text = line
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = WHITE

s5.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (30s):\n"
    "EcoTrack AI is not just a citizen app; it is a full enterprise tripartite ecosystem: "
    "Citizens get zero-friction reporting and rewarding gamification. "
    "Sanitation collectors get a streamlined mobile task queue with turn-by-turn navigation and camera proof submission. "
    "And municipal administrators get an executive command center with live GIS geospatial mapping, collector dispatching, and audit trails."
)

# ==========================================
# SLIDE 6: SYSTEM ARCHITECTURE & SCALABILITY (NO IBM)
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
add_bg(s6)
add_header(s6, "Engineering Architecture: High-Concurrency & Zero-Cost Cloud")

left_card = add_card(s6, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.8))
tb_l = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.4))
tf_l = tb_l.text_frame
tf_l.word_wrap = True
p_l1 = tf_l.paragraphs[0]
p_l1.text = "🏛️ Technology Stack Matrix"
p_l1.font.size = Pt(18)
p_l1.font.bold = True
p_l1.font.color.rgb = CYAN

stack_items = [
    ("Backend Runtime", "FastAPI (Python 3.12+) with Uvicorn Async ASGI Engine"),
    ("Database", "High-Concurrency SQLite / PostgreSQL with indexed spatial tables"),
    ("AI / ML Pipeline", "Google Gemini 1.5/2.0 API + 96-D Perceptual NumPy Engine"),
    ("GIS / Mapping", "Leaflet.js + OpenStreetMap + Google Geolocation / Geocoding"),
    ("Security & Auth", "JWT (HS256) + Bcrypt Password Hashing + OAuth 2.0 + OTP"),
    ("Frontend UI", "Zero-Bloat Vanilla JS, HTML5 Canvas, Modern CSS3")
]

for label, val in stack_items:
    p_item = tf_l.add_paragraph()
    p_item.text = f"• {label}: {val}"
    p_item.font.size = Pt(12)
    p_item.font.color.rgb = WHITE

right_card = add_card(s6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
tb_r = s6.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.4))
tf_r = tb_r.text_frame
tf_r.word_wrap = True
p_r1 = tf_r.paragraphs[0]
p_r1.text = "⚡ Scalable Cloud-Native Deployment"
p_r1.font.size = Pt(18)
p_r1.font.bold = True
p_r1.font.color.rgb = EMERALD

cloud_items = [
    ("Zero-Cost $0 Production Stack", "Configured to run completely free across Render (backend) and Vercel (frontend)."),
    ("High Concurrency & Low Latency", "Asynchronous non-blocking event loop handles thousands of concurrent civic alerts effortlessly."),
    ("Containerized Microservices", "Multi-platform Docker containerization (`docker-compose.yml`) for instant 1-click cloud deployment."),
    ("Resilient Self-Healing Architecture", "Automated systemd process supervision and health-check monitoring for continuous 24/7 uptime.")
]

for label, val in cloud_items:
    p_item = tf_r.add_paragraph()
    p_item.text = f"• {label}:"
    p_item.font.size = Pt(13)
    p_item.font.bold = True
    p_item.font.color.rgb = AMBER
    p_sub = tf_r.add_paragraph()
    p_sub.text = f"  {val}"
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = WHITE

s6.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (35s):\n"
    "On the engineering side, EcoTrack AI is built on a high-concurrency FastAPI async backend. "
    "Crucially, the entire system is containerized with Docker and engineered for zero-cost deployment using Render and Vercel. "
    "Why does this matter? Municipalities and campuses often lack heavy software budgets. Our architecture delivers enterprise-grade 99.9% uptime, async throughput for thousands of simultaneous citizen reports, and automated self-healing without requiring expensive cloud infrastructure."
)

# ==========================================
# SLIDE 7: LIVE DEMO WALKTHROUGH
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
add_bg(s7)
add_header(s7, "Live Demo Playbook: 2-Minute End-to-End Walkthrough")

demo_steps = [
    ("Phase 1: Citizen Report", "• Snap/upload photo of garbage pile.\n• Gemini AI classifies: 'Plastic Waste (Blue Bin)'.\n• Auto-geotags coordinates instantly.", CYAN),
    ("Phase 2: Voice AI Interaction", "• Citizen asks in Hinglish: 'Plastic kahan dispose karein?'\n• Voice AI responds with exact bin & recycling guidance.\n• Voice reporting demonstrated live.", EMERALD),
    ("Phase 3: Admin Command Dispatch", "• Admin opens /admin/ dashboard.\n• New red pin appears on GIS map.\n• Admin assigns task to nearby collector with 1 click.", AMBER),
    ("Phase 4: Collector Proof & Verification", "• Collector opens task queue.\n• Uploads after-cleanup photo evidence.\n• CV Engine compares images, verifies cleanup, closes ticket & awards points!", RGBColor(168, 85, 247))
]

for i, (title, desc, color) in enumerate(demo_steps):
    add_card(s7, Inches(0.8 + i*2.95), Inches(1.8), Inches(2.8), Inches(4.8))
    tb_d = s7.shapes.add_textbox(Inches(0.95 + i*2.95), Inches(2.0), Inches(2.5), Inches(4.4))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    p_t = tf_d.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(16)
    p_t.font.bold = True
    p_t.font.color.rgb = color
    
    for line in desc.split("\n"):
        p_l = tf_d.add_paragraph()
        p_l.text = line
        p_l.font.size = Pt(12)
        p_l.font.color.rgb = WHITE

s7.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (20s):\n"
    "Now let's see EcoTrack AI in action! In our live demo, we will execute the complete 4-stage lifecycle in under 2 minutes: Citizen report -> Instant AI categorization -> Voice AI interaction -> Admin dispatch -> Collector proof upload -> Automated CV verification!"
)

# ==========================================
# SLIDE 8: IMPACT, SUSTAINABILITY & SDG
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
add_bg(s8)
add_header(s8, "Civic Impact, Feasibility & Global SDG Alignment")

impact_cards = [
    ("⚡ 60% Faster Resolution",
     "Automated routing and instant AI triage reduces municipal response time from days to hours.",
     EMERALD),
    ("🛡️ Zero Ghost Cleanups",
     "Mandatory computer vision verification ensures 100% of claimed cleanups actually happened.",
     CYAN),
    ("💰 100% Zero-Cost Cloud",
     "Engineered to run seamlessly on $0 free tiers (Render + Vercel) with minimal server memory footprint.",
     AMBER),
    ("🌱 UN SDG 11 & 12 Alignment",
     "Directly drives Sustainable Cities (SDG 11) and Responsible Consumption & Segregation (SDG 12).",
     RGBColor(168, 85, 247))
]

for i, (title, desc, color) in enumerate(impact_cards):
    r = i // 2
    c = i % 2
    add_card(s8, Inches(0.8 + c*5.95), Inches(1.8 + r*2.5), Inches(5.75), Inches(2.25))
    tb_imp = s8.shapes.add_textbox(Inches(1.0 + c*5.95), Inches(2.0 + r*2.5), Inches(5.35), Inches(1.85))
    tf_imp = tb_imp.text_frame
    tf_imp.word_wrap = True
    p_t = tf_imp.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(18)
    p_t.font.bold = True
    p_t.font.color.rgb = color
    
    p_d = tf_imp.add_paragraph()
    p_d.text = desc
    p_d.font.size = Pt(13)
    p_d.font.color.rgb = WHITE

s8.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (30s):\n"
    "Beyond the code, what is the real-world impact? "
    "First, we reduce hazard turnaround times by over 60%. "
    "Second, we eliminate contractor fraud through algorithmic verification. "
    "Third, our zero-cost architecture allows any municipality or campus to deploy this without waiting for multi-lakh budget approvals. "
    "It directly drives UN Sustainable Development Goals 11 and 12 and national missions like Swachh Bharat."
)

# ==========================================
# SLIDE 9: COMPETITIVE ADVANTAGE
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
add_bg(s9)
add_header(s9, "Competitive Matrix: Why EcoTrack AI Outperforms Existing Solutions")

table_shape = add_card(s9, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
tb_tbl = s9.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.4))
tf_tbl = tb_tbl.text_frame
tf_tbl.word_wrap = True

rows = [
    ("Capability / Feature", "Traditional Govt Portals", "Generic Complaint Apps", "EcoTrack AI (CleanConnect)"),
    ("Multimodal AI Waste Classification", "❌ None (Manual Review)", "❌ None", "✅ Gemini Vision + 96D Local Model"),
    ("Bilingual Voice AI Assistant (Hinglish)", "❌ None", "❌ None", "✅ Full Conversational Voice Agent"),
    ("Automated Proof Verification (CV)", "❌ None (Trust-based)", "❌ Basic Photo Upload", "✅ CV Before/After Feature Match (75%+)"),
    ("Real-Time GIS Spatial Heatmaps", "❌ Static lists/tables", "⚠️ Rudimentary Maps", "✅ Interactive Live Spatial Clustering"),
    ("Civic Gamification & Green Points", "❌ None", "⚠️ Static badges", "✅ Dynamic Ledger & Public Leaderboard"),
    ("Zero-Cost Production Ready", "❌ Expensive Servers", "⚠️ Generic Cloud", "✅ $0 Cloud Native (Render + Vercel) / Docker")
]

for idx, (col1, col2, col3, col4) in enumerate(rows):
    p_row = tf_tbl.paragraphs[0] if idx == 0 else tf_tbl.add_paragraph()
    line_text = f"{col1:<35} | {col2:<24} | {col3:<24} | {col4}"
    p_row.text = line_text
    p_row.font.size = Pt(12)
    if idx == 0:
        p_row.font.bold = True
        p_row.font.color.rgb = CYAN
    else:
        p_row.font.color.rgb = WHITE

s9.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (30s):\n"
    "When you compare EcoTrack AI to traditional government portals and generic apps, the difference is night and day. "
    "Competitors rely on manual human triage and trust-based claims. We automate classification with multimodal AI, enable voice accessibility in Hinglish, and algorithmically enforce proof before tasks can be marked complete."
)

# ==========================================
# SLIDE 10: ROADMAP & CLOSING
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
add_bg(s10)
add_header(s10, "Roadmap & Vision: Building Clean, Intelligent Cities")

card_r1 = add_card(s10, Inches(0.8), Inches(1.8), Inches(3.8), Inches(3.6))
tb_r1 = s10.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(3.4), Inches(3.2))
tf_r1 = tb_r1.text_frame
tf_r1.word_wrap = True
p1 = tf_r1.paragraphs[0]
p1.text = "Phase 1: Present (Delivered)"
p1.font.size = Pt(16)
p1.font.bold = True
p1.font.color.rgb = EMERALD
for pt in ["• Live 3-role portal system", "• Multimodal Gemini & Voice AI", "• CV Before/After verification", "• Docker containerized & cloud-ready"]:
    p = tf_r1.add_paragraph()
    p.text = pt
    p.font.size = Pt(12)
    p.font.color.rgb = WHITE

card_r2 = add_card(s10, Inches(4.75), Inches(1.8), Inches(3.8), Inches(3.6))
tb_r2 = s10.shapes.add_textbox(Inches(4.95), Inches(2.0), Inches(3.4), Inches(3.2))
tf_r2 = tb_r2.text_frame
tf_r2.word_wrap = True
p2 = tf_r2.paragraphs[0]
p2.text = "Phase 2: Next 60 Days"
p2.font.size = Pt(16)
p2.font.bold = True
p2.font.color.rgb = CYAN
for pt in ["• IoT ultrasonic smart bin sensors", "• Automated fleet route optimization", "• WhatsApp & Telegram Bot reporting", "• Regional Indian languages (Tamil, Hindi)"]:
    p = tf_r2.add_paragraph()
    p.text = pt
    p.font.size = Pt(12)
    p.font.color.rgb = WHITE

card_r3 = add_card(s10, Inches(8.7), Inches(1.8), Inches(3.8), Inches(3.6))
tb_r3 = s10.shapes.add_textbox(Inches(8.9), Inches(2.0), Inches(3.4), Inches(3.2))
tf_r3 = tb_r3.text_frame
tf_r3.word_wrap = True
p3 = tf_r3.paragraphs[0]
p3.text = "Phase 3: 6 Months & Beyond"
p3.font.size = Pt(16)
p3.font.bold = True
p3.font.color.rgb = AMBER
for pt in ["• Municipal ERP & Smart City integration", "• Corporate CSR sponsorship for Green Points", "• Redemptions for metro passes & utility bills", "• National Swachh Bharat integration"]:
    p = tf_r3.add_paragraph()
    p.text = pt
    p.font.size = Pt(12)
    p.font.color.rgb = WHITE

close_card = add_card(s10, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.4), EMERALD, EMERALD)
tb_close = s10.shapes.add_textbox(Inches(1.0), Inches(5.7), Inches(11.3), Inches(1.2))
tf_close = tb_close.text_frame
tf_close.word_wrap = True
p_c1 = tf_close.paragraphs[0]
p_c1.text = "Thank You! Questions & Discussion"
p_c1.font.size = Pt(22)
p_c1.font.bold = True
p_c1.font.color.rgb = DARK_BG
p_c1.alignment = PP_ALIGN.CENTER
p_c2 = tf_close.add_paragraph()
p_c2.text = "EcoTrack AI (CleanConnect) • Turning Civic Cleanliness into a Collective Movement"
p_c2.font.size = Pt(13)
p_c2.font.color.rgb = DARK_BG
p_c2.alignment = PP_ALIGN.CENTER

s10.notes_slide.notes_text_frame.text = (
    "SPEAKER NOTES (20s):\n"
    "In conclusion, EcoTrack AI transforms civic cleanliness from a thankless municipal burden into an accountable, intelligent, and rewarding community movement. "
    "The code is fully built, containerized, tested, and ready for deployment. "
    "Thank you so much, judges. I am now open to your questions!"
)

output_path = r"D:\IDEATHON\EcoTrack_AI_Presentation.pptx"
prs.save(output_path)
print(f"Presentation saved successfully without IBM references to: {output_path}")
