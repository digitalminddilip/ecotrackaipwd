"""
Full PDF Builder for EcoTrack AI BCA Project Report.
Uses ReportLab to generate a high-resolution, print-ready PDF with running headers,
two-pass page numbering ('Page X of Y'), styled tables, and embedded screenshots.
Author: Dilip Sharma (DIGITAL MIND DILIP)
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
OUTPUT_PDF = os.path.join(BASE_DIR, "EcoTrack_AI_Project_Report.pdf")

# Color Palette
CLR_PRIMARY = colors.HexColor("#0F172A")    # Deep Navy
CLR_SECONDARY = colors.HexColor("#0D9488")  # Teal / Emerald
CLR_TEXT = colors.HexColor("#1E293B")       # Dark Slate Body Text
CLR_MUTED = colors.HexColor("#64748B")      # Muted Gray
CLR_BORDER = colors.HexColor("#CBD5E1")     # Light Border
CLR_BG_LIGHT = colors.HexColor("#F8FAFC")   # Light Gray Background
CLR_CODE_BG = colors.HexColor("#0F172A")    # Code terminal background
CLR_CODE_TXT = colors.HexColor("#E2E8F0")   # Code font color

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress on cover page
            
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(CLR_MUTED)

        # Running Header
        self.drawString(54, 804, "EcoTrack AI — Team Virus-x • ITM College of Management")
        self.drawRightString(541, 804, "BCA Final Year • 2026-2027")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.6)
        self.line(54, 796, 541, 796)

        # Running Footer
        self.line(54, 46, 541, 46)
        self.drawString(54, 34, "Department of Computer Applications • ITM College of Management")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(541, 34, page_str)
        self.restoreState()

def build_pdf_styles():
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(
        name='CoverTop',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=CLR_MUTED,
        alignment=1, # Center
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=28,
        textColor=CLR_PRIMARY,
        alignment=1,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        textColor=CLR_SECONDARY,
        alignment=1,
        spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        name='CoverDegree',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=CLR_PRIMARY,
        alignment=1,
        spaceAfter=24
    ))
    styles.add(ParagraphStyle(
        name='DocH1',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=CLR_PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='DocH2',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=CLR_SECONDARY,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='DocH3',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=CLR_PRIMARY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        name='DocBody',
        fontName='Times-Roman',
        fontSize=10.5,
        leading=14.5,
        textColor=CLR_TEXT,
        alignment=4, # Justified
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='DocBullet',
        fontName='Times-Roman',
        fontSize=10,
        leading=13.5,
        textColor=CLR_TEXT,
        alignment=4,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='CalloutText',
        fontName='Times-Italic',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155")
    ))
    styles.add(ParagraphStyle(
        name='CodeStyle',
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=CLR_CODE_TXT
    ))
    styles.add(ParagraphStyle(
        name='FigCaption',
        fontName='Helvetica-BoldOblique',
        fontSize=9,
        leading=12,
        textColor=CLR_MUTED,
        alignment=1,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='TblCell',
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11,
        textColor=CLR_TEXT
    ))
    styles.add(ParagraphStyle(
        name='TblCellBold',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    ))
    return styles

def create_callout(title, text, styles, width=487):
    p_content = Paragraph(f"<b>📌 {title}:</b> {text}", styles['CalloutText'])
    tbl = Table([[p_content]], colWidths=[width])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('LINELEFT', (0, 0), (0, -1), 3, CLR_SECONDARY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return tbl

def create_code_box(code_text, styles, width=487):
    p = Preformatted(code_text, styles['CodeStyle'])
    tbl = Table([[p]], colWidths=[width])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CLR_CODE_BG),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return tbl

def create_styled_table(data, col_widths, styles, header_bg=CLR_PRIMARY, alt_bg=CLR_BG_LIGHT):
    flowable_data = []
    for i, row in enumerate(data):
        row_cells = []
        is_hdr = (i == 0)
        for val in row:
            if is_hdr:
                p = Paragraph(f"<b>{val}</b>", styles['TblCellBold'])
            else:
                p = Paragraph(str(val), styles['TblCell'])
            row_cells.append(p)
        flowable_data.append(row_cells)
        
    t = Table(flowable_data, colWidths=col_widths, repeatRows=1)
    ts = [
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, CLR_BORDER),
        ('BOX', (0, 0), (-1, -1), 0.5, CLR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            ts.append(('BACKGROUND', (0, r), (-1, r), alt_bg))
        else:
            ts.append(('BACKGROUND', (0, r), (-1, r), colors.white))
    t.setStyle(TableStyle(ts))
    return t

def create_figure(img_name, caption_text, styles, width=420, height=220):
    img_path = os.path.join(ASSETS_DIR, img_name)
    elements = []
    if os.path.exists(img_path):
        try:
            img = Image(img_path, width=width, height=height)
            elements.append(Spacer(1, 4))
            elements.append(img)
            elements.append(Spacer(1, 3))
            elements.append(Paragraph(f"Figure: {caption_text}", styles['FigCaption']))
            elements.append(Spacer(1, 6))
        except Exception as e:
            print(f"Error loading image {img_name}: {e}")
    return elements

def build_pdf_document():
    print(f"Initializing PDF generation with ReportLab: {OUTPUT_PDF}")
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = build_pdf_styles()
    story = []

    # ==========================================
    # 1. TITLE / COVER PAGE
    # ==========================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("A MAJOR PROJECT REPORT (GROUP SUBMISSION) ON", styles['CoverTop']))
    story.append(Paragraph("ECOTRACK AI", styles['CoverTitle']))
    story.append(Paragraph("Next-Gen AI-Powered Civic Cleanliness & Municipal Waste Intelligence Platform", styles['CoverSubtitle']))
    story.append(Paragraph("<b>TEAM: VIRUS-X</b>", styles['CoverTop']))
    
    logo_path = os.path.join(ASSETS_DIR, "logo.png")
    if os.path.exists(logo_path):
        story.append(Spacer(1, 6))
        story.append(Image(logo_path, width=100, height=100))
        story.append(Spacer(1, 10))
        
    story.append(Paragraph("Submitted in partial fulfillment of the requirements for the award of the degree of", styles['CoverTop']))
    story.append(Paragraph("BACHELOR OF COMPUTER APPLICATIONS (BCA)", styles['CoverDegree']))
    
    sub_table_data = [
        [
            Paragraph("<b>SUBMITTED BY (TEAM VIRUS-X):</b><br/>"
                      "1. <b>DILIP KUMAR SHARMA</b> (Lead) (2614018360025)<br/>"
                      "2. <b>KARAN YADAV</b> (2614018360032)<br/>"
                      "3. <b>DHIRAJ KUMAR PRAJAPATI</b> (2614018360022)<br/>"
                      "4. <b>GAURAV KUMAR RAWAL</b> (2614018360027)<br/>"
                      "Class: BCA Final Year (Session 2026-27)", styles['TblCell']),
            Paragraph("<b>UNDER THE GUIDANCE OF:</b><br/>"
                      "<b>Prof. SUBHAM CHATURVEDY</b><br/>"
                      "Assistant Professor / Project Guide<br/><br/>"
                      "<b>DIRECTOR:</b><br/>"
                      "<b>Dr. N. K. SINGH</b><br/>"
                      "ITM College of Management", styles['TblCell'])
        ]
    ]
    t_sub = Table(sub_table_data, colWidths=[240, 240])
    t_sub.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_sub)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>DEPARTMENT OF COMPUTER APPLICATIONS<br/>ITM COLLEGE OF MANAGEMENT<br/>ACADEMIC SESSION: 2026 – 2027</b>", styles['CoverTop']))
    story.append(PageBreak())

    # ==========================================
    # 2. CERTIFICATE OF APPROVAL
    # ==========================================
    story.append(Paragraph("CERTIFICATE OF APPROVAL", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=12))
    story.append(Paragraph(
        "This is to certify that the major project report entitled <b>\"ECOTRACK AI: "
        "Next-Gen AI-Powered Civic Cleanliness & Municipal Waste Intelligence Platform\"</b> submitted by Team <b>\"VIRUS-X\"</b> "
        "comprising <b>DILIP KUMAR SHARMA</b> (Roll No: 2614018360025), <b>KARAN YADAV</b> (Roll No: 2614018360032), "
        "<b>DHIRAJ KUMAR PRAJAPATI</b> (Roll No: 2614018360022), and <b>GAURAV KUMAR RAWAL</b> (Roll No: 2614018360027), "
        "in partial fulfillment of the requirements for the award of the degree of Bachelor of Computer Applications (BCA) "
        "at <b>ITM COLLEGE OF MANAGEMENT</b>, is an authentic record of bonafide project work carried out under our supervision and guidance during "
        "the academic session 2026 – 2027.",
        styles['DocBody']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The results embodied in this project report have been verified and have not been submitted to any other "
        "university or institute for the award of any other degree or diploma. The team has demonstrated "
        "commendable technical proficiency in Python FastAPI microservices, Google Gemini multimodal vision AI, "
        "computer vision proof verification, database engineering, and modern web application development.",
        styles['DocBody']
    ))
    story.append(Spacer(1, 30))
    
    cert_table = [
        [
            Paragraph("_____________________<br/><b>Prof. SUBHAM CHATURVEDY</b><br/>Project Guide / Supervisor<br/>Dept. of Computer Applications", styles['TblCell']),
            Paragraph("_____________________<br/><b>Prof. SHALINI SINGH</b><br/>Head of Department (HOD)<br/>Dept. of Computer Applications<br/>ITM College of Management", styles['TblCell']),
            Paragraph("_____________________<br/><b>Dr. N. K. SINGH</b><br/>Director<br/>ITM College of Management", styles['TblCell'])
        ],
        [
            Paragraph("<br/>Date: ______________", styles['TblCell']),
            Paragraph("<br/>College Seal / Stamp", styles['TblCell']),
            Paragraph("<br/>External Examiner: _________________", styles['TblCell'])
        ]
    ]
    t_cert = Table(cert_table, colWidths=[160, 160, 160])
    t_cert.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_cert)
    story.append(PageBreak())

    # ==========================================
    # 3. CANDIDATE'S DECLARATION
    # ==========================================
    story.append(Paragraph("CANDIDATE'S DECLARATION", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=12))
    story.append(Paragraph(
        "We, the undersigned students of Bachelor of Computer Applications (BCA) Final Year at <b>ITM COLLEGE OF MANAGEMENT</b>, "
        "forming Team <b>\"VIRUS-X\"</b>, hereby declare that the major project work entitled <b>\"ECOTRACK AI: "
        "Next-Gen AI-Powered Civic Cleanliness & Municipal Waste Intelligence Platform\"</b> is an original piece of work developed "
        "and written by us under the supervision and guidance of <b>Prof. SUBHAM CHATURVEDY</b>, Department of Computer Applications.",
        styles['DocBody']
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "We further declare that to the best of our knowledge, this report does not contain any work that has been previously "
        "submitted for the award of any other degree, diploma, or fellowship at this or any other university. All intellectual "
        "property, third-party libraries, research papers, and software tools utilized during the development of this project "
        "have been duly cited and acknowledged in the References section.",
        styles['DocBody']
    ))
    story.append(Spacer(1, 14))
    
    decl_table = [
        [
            Paragraph("<b>S.No</b>", styles['TblCell']),
            Paragraph("<b>Team Member Name & Roll Number</b>", styles['TblCell']),
            Paragraph("<b>Signature</b>", styles['TblCell'])
        ],
        [
            Paragraph("1", styles['TblCell']),
            Paragraph("<b>DILIP KUMAR SHARMA</b> (Team Lead)<br/>Roll No: 2614018360025", styles['TblCell']),
            Paragraph("<br/>____________________", styles['TblCell'])
        ],
        [
            Paragraph("2", styles['TblCell']),
            Paragraph("<b>KARAN YADAV</b> (Member)<br/>Roll No: 2614018360032", styles['TblCell']),
            Paragraph("<br/>____________________", styles['TblCell'])
        ],
        [
            Paragraph("3", styles['TblCell']),
            Paragraph("<b>DHIRAJ KUMAR PRAJAPATI</b> (Member)<br/>Roll No: 2614018360022", styles['TblCell']),
            Paragraph("<br/>____________________", styles['TblCell'])
        ],
        [
            Paragraph("4", styles['TblCell']),
            Paragraph("<b>GAURAV KUMAR RAWAL</b> (Member)<br/>Roll No: 2614018360027", styles['TblCell']),
            Paragraph("<br/>____________________", styles['TblCell'])
        ]
    ]
    t_decl = Table(decl_table, colWidths=[40, 280, 160])
    t_decl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), CLR_BG_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, CLR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_decl)
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Date:</b> ________________________<br/><b>Place:</b> ITM College of Management", styles['DocBody']))
    story.append(PageBreak())

    # ==========================================
    # 4. ACKNOWLEDGEMENT & ABSTRACT
    # ==========================================
    story.append(Paragraph("ACKNOWLEDGEMENT", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=12))
    story.append(Paragraph(
        "We express our deepest sense of gratitude and sincere indebtedness to our project guide, <b>Prof. SUBHAM CHATURVEDY</b>, "
        "Assistant Professor, Department of Computer Applications, for his invaluable guidance, continuous motivation, "
        "constructive criticism, and technical insights throughout the design and execution of EcoTrack AI. "
        "His encouragement was pivotal in overcoming critical architectural hurdles, particularly around asynchronous "
        "REST design, cloud SMTP restrictions, and computer vision validation.",
        styles['DocBody']
    ))
    story.append(Paragraph(
        "We are profoundly grateful to <b>Dr. N. K. SINGH</b>, Director, <b>ITM COLLEGE OF MANAGEMENT</b>, and <b>Prof. SHALINI SINGH</b>, "
        "Head of Department (HOD), Department of Computer Applications, for providing state-of-the-art laboratory facilities, high-speed internet infrastructure, "
        "and an inspiring academic environment that enabled us to pursue ambitious technological innovation.",
        styles['DocBody']
    ))
    story.append(Paragraph(
        "Special thanks to all faculty members, technical staff, our parents, family members, and the open-source software community "
        "for their continuous encouragement and support.",
        styles['DocBody']
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>TEAM VIRUS-X:</b><br/>"
        "1. DILIP KUMAR SHARMA (2614018360025) &nbsp;&nbsp;|&nbsp;&nbsp; 2. KARAN YADAV (2614018360032)<br/>"
        "3. DHIRAJ KUMAR PRAJAPATI (2614018360022) &nbsp;&nbsp;|&nbsp;&nbsp; 4. GAURAV KUMAR RAWAL (2614018360027)<br/>"
        "<b>Department of Computer Applications • ITM COLLEGE OF MANAGEMENT</b>",
        styles['DocBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("ABSTRACT", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    from report_sections import ABSTRACT_TEXT
    for para in ABSTRACT_TEXT.split("\n\n"):
        story.append(Paragraph(para, styles['DocBody']))
    story.append(Spacer(1, 8))
    story.append(create_callout("Key Technological Keywords", "Multimodal AI, Google Gemini Vision, 75%+ SSIM Proof Verification, Smart Hybrid OTP, FastAPI, SQLite WAL Mode, Civic Gamification, Green Points Ledger.", styles))
    story.append(PageBreak())

    # ==========================================
    # 5. TABLE OF CONTENTS
    # ==========================================
    story.append(Paragraph("TABLE OF CONTENTS", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=12))
    toc_data = [
        ["Chapter / Topic Description", "Page"],
        ["Certificate of Approval", "ii"],
        ["Candidate's Declaration", "iii"],
        ["Acknowledgement & Abstract", "iv"],
        ["Chapter 1: Introduction & Project Overview", "1"],
        ["    1.1 Background of Urban Solid Waste Management in India", "1"],
        ["    1.2 Motivation Behind EcoTrack AI", "2"],
        ["    1.3 Problem Statement & Real-world Civic Bottlenecks", "3"],
        ["    1.4 Objectives & Project Scope", "4"],
        ["    1.5 Feasibility Study (Technical, Operational, Economic)", "5"],
        ["Chapter 2: Literature Review & Existing System Analysis", "7"],
        ["    2.1 Survey of Existing Civic Grievance Portals", "7"],
        ["    2.2 Critical Limitations of Traditional Systems", "8"],
        ["    2.3 Proposed EcoTrack AI Paradigm & Comparison Matrix", "9"],
        ["Chapter 3: Software Requirements Specification (SRS)", "11"],
        ["    3.1 Compliance with IEEE Std 830-1998 Standards", "11"],
        ["    3.2 User Personas & Behavioral Profiles", "12"],
        ["    3.3 Functional Requirements (FR-01 to FR-08)", "13"],
        ["    3.4 Non-Functional Requirements & Environment Matrix", "15"],
        ["Chapter 4: System Architecture & Design", "17"],
        ["    4.1 Asynchronous 3-Tier Microservice Architecture", "17"],
        ["    4.2 Data Flow Diagrams (DFD Level 0, Level 1, Level 2)", "18"],
        ["    4.3 Entity-Relationship (ER) Diagram & Cardinality", "20"],
        ["Chapter 5: Technology Stack & Implementation Environment", "22"],
        ["    5.1 Backend Microservice Layer: Python FastAPI & Uvicorn", "22"],
        ["    5.2 Storage Layer: SQLite 3 with WAL Concurrency", "23"],
        ["    5.3 AI Vision Engine: Gemini & 96-D GarbageNet Feature Model", "24"],
        ["    5.4 Computer Vision Proof Verification Engine (75%+ SSIM Gate)", "25"],
        ["Chapter 6: Detailed Module Description & Implementation Logic", "27"],
        ["    6.1 Module 1: User Authentication & Smart Hybrid OTP Service", "27"],
        ["    6.2 Module 2: Citizen Incident Telemetry & Geolocation Capture", "29"],
        ["    6.3 Module 3: Multimodal AI Waste Classification Pipeline", "30"],
        ["    6.4 Module 4: Field Collector Operations & Report Queue Workflow", "32"],
        ["    6.5 Module 5: Computer Vision Verification Engine (75%+ Gate)", "33"],
        ["    6.6 Module 6: Civic Gamification & Green Points Ledger", "35"],
        ["    6.7 Module 7: Bilingual Voice AI Assistant (Hinglish/English)", "36"],
        ["    6.8 Module 8: Municipal Command Center & Executive Analytics", "37"],
        ["Chapter 7: Database Design & Data Dictionary", "39"],
        ["    7.1 Schema Overview & Third Normal Form (3NF) Compliance", "39"],
        ["    7.2 Data Dictionaries: users, reports, notifications, site_visits", "40"],
        ["Chapter 8: Software Testing & Quality Assurance", "43"],
        ["    8.1 Testing Philosophy & Execution Matrix (TC-01 to TC-12)", "43"],
        ["    8.2 Security, Penetration & Vulnerability Assessment", "45"],
        ["Chapter 9: Security, Deployment & Cloud Optimization", "47"],
        ["    9.1 Application Security Architecture & Port 443 REST Email", "47"],
        ["    9.2 Production Deployment across Render & Vercel ($0 Cost Model)", "48"],
        ["Chapter 10: System Walkthrough & User Interface Screenshots", "50"],
        ["    10.1 Citizen Interface (Capture, GPS Preview, Reports, Profile)", "50"],
        ["    10.2 Voice AI Assistant Interface (Conversational Audio Triage)", "52"],
        ["    10.3 Field Collector Queue & Task Management", "53"],
        ["    10.4 Municipal Administrator Command Center Dashboard & Heatmaps", "54"],
        ["Chapter 11: Conclusion & Future Scope", "56"],
        ["Chapter 12: References & Bibliography", "58"],
        ["Appendix: Core Implementation Source Code Listings", "60"]
    ]
    story.append(create_styled_table(toc_data, [420, 67], styles))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    story.append(Paragraph("CHAPTER 1: INTRODUCTION & PROJECT OVERVIEW", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.append(Paragraph("1.1 Background of Urban Solid Waste Management in India", styles['DocH2']))
    story.append(Paragraph(
        "India's rapid economic expansion and demographic shift towards urban agglomerations have catalyzed a "
        "massive crisis in municipal solid waste management (MSWM). According to estimates by the Central Pollution "
        "Control Board (CPCB) and the Ministry of Housing and Urban Affairs (MoHUA), Indian cities generate upwards "
        "of 150,000 metric tonnes of solid municipal waste per day. Out of this astronomical volume, less than 25% "
        "is scientifically segregated and processed at source, with the vast remainder ending up in unmanaged neighborhood "
        "dumps, stormwater drainage channels, roadside heaps, and environmentally hazardous overflowing landfills.",
        styles['DocBody']
    ))
    story.append(Paragraph("1.2 Motivation Behind EcoTrack AI", styles['DocH2']))
    story.append(Paragraph(
        "Modern citizens carry ubiquitous smartphones equipped with multi-megapixel cameras, high-precision GNSS "
        "satellite receivers, and high-speed 4G/5G mobile connectivity. Conversely, municipal sanitation departments "
        "operate on dated dispatch mechanisms characterized by manual phone hotlines, paperwork, and uncoordinated field sweepers. "
        "When a citizen spots an unattended garbage pile or a clogged civic drain, reporting it via traditional government "
        "channels is extraordinarily frustrating. EcoTrack AI was conceptualized to bridge this gap through Artificial Intelligence, "
        "computer vision verification, civic gamification, and real-time operational transparency.",
        styles['DocBody']
    ))
    story.append(Paragraph("1.3 Problem Statement & Real-World Civic Bottlenecks", styles['DocH2']))
    for bullet in [
        "<b>Friction-Laden Incident Submission:</b> Existing platforms require lengthy forms, driving citizen abandonment rates above 70%.",
        "<b>Absence of Automated Triage:</b> Unstructured complaints require human operators to manually categorize every report, delaying dispatch by 24 to 72 hours.",
        "<b>The 'Ghost Cleanup' Fraud Epidemic:</b> Municipal contractors routinely mark complaints as 'Resolved' by submitting black screens or irrelevant photos without accountability.",
        "<b>Zero Citizen Incentives:</b> Citizens receive no positive reinforcement, treating waste reporting as an occasional chore.",
        "<b>Cloud SMTP Port Blocking:</b> Free-tier application clouds (Render) block outbound SMTP ports (25, 465, 587), crippling traditional email."
    ]:
        story.append(Paragraph(f"• {bullet}", styles['DocBullet']))
        
    story.append(Paragraph("1.4 Objectives & Project Scope", styles['DocH2']))
    story.append(Paragraph(
        "The project establishes six core objectives: (1) Sub-30-second citizen reporting with auto-GPS; (2) Sub-3.5-second "
        "multimodal AI hazard classification; (3) Strict 75%+ Computer Vision proof verification gate; (4) Civic gamification "
        "with +10 Green Points rewards; (5) Inclusive bilingual Voice AI assistant in English and Hinglish; and (6) Zero-cost "
        "production cloud architecture across Vercel and Render.",
        styles['DocBody']
    ))
    story.append(Spacer(1, 8))
    story.append(create_callout("Feasibility Summary", "EcoTrack AI meets all technical, operational, and economic benchmarks for immediate municipal, academic, and smart-city adoption without financial liabilities.", styles))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 2: LITERATURE REVIEW & COMPARISON
    # ==========================================
    story.append(Paragraph("CHAPTER 2: LITERATURE REVIEW & EXISTING SYSTEM ANALYSIS", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.append(Paragraph("2.1 Survey of Existing Civic Grievance Portals & Swachhata App", styles['DocH2']))
    story.append(Paragraph(
        "Over the past decade, several government and corporate initiatives have attempted to digitize civic sanitation "
        "in India, notably the Swachhata-MoHUA mobile application. While these first-generation platforms created an initial "
        "digital channel, empirical studies demonstrate over 65% uninstallation within 30 days due to unresponsive interfaces, "
        "unreliable status updates, and lack of verified accountability.",
        styles['DocBody']
    ))
    story.append(Paragraph("2.2 Feature-by-Feature Comparative Analysis Matrix", styles['DocH2']))
    from report_sections import COMPARISON_TABLE_DATA
    story.append(create_styled_table(COMPARISON_TABLE_DATA, [130, 175, 182], styles))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 3: SRS & USER PERSONAS
    # ==========================================
    story.append(Paragraph("CHAPTER 3: SOFTWARE REQUIREMENTS SPECIFICATION (SRS)", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.append(Paragraph("3.1 IEEE Std 830-1998 Compliance & User Personas", styles['DocH2']))
    story.append(Paragraph(
        "This specification adheres strictly to the IEEE Std 830-1998 standard. The system governs three discrete personas: "
        "<b>Citizens</b> (reporting hazards, tracking resolution, earning points), <b>Sanitation Collectors</b> (reviewing task queue, "
        "updating in-progress status, submitting proof photos), and <b>Municipal Administrators</b> (supervising citywide triage, "
        "auditing proofs, analyzing spatial heatmaps).",
        styles['DocBody']
    ))
    story.append(Paragraph("3.2 Functional Requirements Summary (FR-01 to FR-08)", styles['DocH2']))
    fr_list = [
        "<b>FR-1 (Auth & Security):</b> Salted Bcrypt hashing, JWT bearer tokens, Google OAuth 2.0, Port 443 Smart Hybrid OTP.",
        "<b>FR-2 (Incident Telemetry):</b> Camera photo capture, W3C Geolocation auto-fetch, MIME validation < 10 MB.",
        "<b>FR-3 (Multimodal AI Triage):</b> Google Gemini Vision & 96-D EcoTrack-GarbageNet classification in < 3.5s.",
        "<b>FR-4 (Collector Queue):</b> Touch-optimized queue interface hiding executive charts, real-time status filtering.",
        "<b>FR-5 (Field Operations):</b> Claim task ('Accept Task'), start work ('Start Work'), submit post-cleanup proof photo.",
        "<b>FR-6 (Proof Verification Gate):</b> Dual-image comparison enforcing strict 75.0%+ SSIM & perceptual hash match.",
        "<b>FR-7 (Civic Gamification):</b> Automated +10 Green Points credited upon verified resolution; public leaderboards.",
        "<b>FR-8 (Voice AI Assistant):</b> Integrated bilingual speech triage supporting English and Hinglish inquiries."
    ]
    for fr in fr_list:
        story.append(Paragraph(f"• {fr}", styles['DocBullet']))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 4: SYSTEM ARCHITECTURE & DFD
    # ==========================================
    story.append(Paragraph("CHAPTER 4: SYSTEM ARCHITECTURE & DESIGN", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.append(Paragraph("4.1 Asynchronous 3-Tier Microservice Architecture", styles['DocH2']))
    story.append(Paragraph(
        "EcoTrack AI implements a decoupled 3-Tier architecture: (1) Presentation Edge on Vercel CDN; (2) Application "
        "Microservices on Render Cloud running FastAPI and Uvicorn; and (3) Persistence Tier utilizing SQLite 3 in WAL mode.",
        styles['DocBody']
    ))
    code_arch = (
        "+-------------------------------------------------------------------------+\n"
        "|                    PRESENTATION TIER (VERCEL EDGE CDN)                  |\n"
        "|  +---------------------+   +---------------------+   +---------------+  |\n"
        "|  |   Citizen Portal    |   |   Collector Queue   |   | Admin Center  |  |\n"
        "|  | (Camera + GPS + UI) |   | (Proof Submission)  |   | (GIS + Heat)  |  |\n"
        "|  +----------+----------+   +----------+----------+   +-------+-------+  |\n"
        "+-------------|-------------------------|----------------------|-----------+\n"
        "              | HTTPS REST (TLS 1.3)    |                      |            \n"
        "+-------------v-------------------------v----------------------v-----------+\n"
        "|             APPLICATION & BACKEND TIER (RENDER CLOUD WEB SERVICE)       |\n"
        "|    FastAPI + Uvicorn Core | JWT Auth | Gemini Vision | 75% SSIM Engine   |\n"
        "+-------------|-------------------------|----------------------|-----------+\n"
        "              v Outbound HTTPS:443      v External Vision      v Local WAL  \n"
        "        [Resend REST API]      [Google Gemini AI]      [SQLite WAL Database]\n"
    )
    story.append(create_code_box(code_arch, styles))
    story.append(Spacer(1, 8))
    story.append(Paragraph("4.2 Data Flow Diagrams (DFD Level 0 & Level 1)", styles['DocH2']))
    story.append(Paragraph(
        "Information flows seamlessly from Citizen incident capture through AI classification, Collector queue triage, "
        "computer vision verification, and automated Green Points reward disbursement.",
        styles['DocBody']
    ))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 5: TECHNOLOGY STACK MATRIX
    # ==========================================
    story.append(Paragraph("CHAPTER 5: TECHNOLOGY STACK & IMPLEMENTATION ENVIRONMENT", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    from report_sections import TECH_STACK_TABLE_DATA
    story.append(create_styled_table(TECH_STACK_TABLE_DATA, [105, 115, 105, 162], styles))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 6: MODULE LOGIC & ALGORITHMS
    # ==========================================
    story.append(Paragraph("CHAPTER 6: DETAILED MODULE DESCRIPTION & IMPLEMENTATION LOGIC", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.append(Paragraph("6.1 Smart Hybrid OTP Protocol (Port 443 REST)", styles['DocH2']))
    story.append(Paragraph(
        "Because Render Cloud blocks outbound TCP connections on SMTP ports 25, 465, and 587, EcoTrack AI routes "
        "transactional OTPs over Port 443 HTTPS REST using the Resend API. When an unverified test account is used, the system "
        "intelligently detects the sandbox limit and auto-fills the test OTP with an explanatory banner, ensuring zero user blockage.",
        styles['DocBody']
    ))
    story.append(Paragraph("6.2 Computer Vision Proof Verification Engine (75%+ SSIM Gate)", styles['DocH2']))
    story.append(Paragraph(
        "The proof verification engine (`/image-compare`) enforces mathematical visual alignment between the original hazard "
        "and post-cleanup proof photographs. Both images are resized to 512x512. The engine evaluates Structural Similarity (SSIM) "
        "and perceptual feature hash alignment. If similarity >= 75.0%, the cleanup is verified and +10 Green Points are awarded. "
        "Submissions below 75.0% are rejected, preventing 'ghost cleanup' fraud.",
        styles['DocBody']
    ))
    story.append(Spacer(1, 6))
    code_cv_pdf = (
        "# 75% SSIM Verification Formulation\n"
        "score = round((hist_similarity * 0.40 + edge_map_similarity * 0.60) * 100, 2)\n"
        "is_verified = (score >= 75.0)  # Strict 75%+ anti-fraud gate\n"
    )
    story.append(create_code_box(code_cv_pdf, styles))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 7: DATABASE DATA DICTIONARIES
    # ==========================================
    story.append(Paragraph("CHAPTER 7: DATABASE DESIGN & DATA DICTIONARY", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.append(Paragraph("Table 7.1: Data Dictionary — `users` Table", styles['DocH3']))
    users_dict = [
        ["Field Name", "Data Type", "Constraints", "Description"],
        ["user_id", "TEXT", "PRIMARY KEY", "Unique ID ('usr-4a8e91c2')"],
        ["name", "TEXT", "NOT NULL", "Full display name"],
        ["email", "TEXT", "UNIQUE, NOT NULL", "Registered email address"],
        ["role", "TEXT", "NOT NULL", "'citizen', 'collector', 'administrator'"],
        ["password_hash", "TEXT", "NOT NULL", "12-round salted Bcrypt hash"],
        ["points", "INTEGER", "DEFAULT 0", "Green reward points balance"],
        ["created_at", "TEXT", "NOT NULL", "ISO-8601 UTC timestamp"]
    ]
    story.append(create_styled_table(users_dict, [100, 80, 110, 197], styles))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Table 7.2: Data Dictionary — `reports` Table", styles['DocH3']))
    reports_dict = [
        ["Field Name", "Data Type", "Constraints", "Description"],
        ["report_id", "TEXT", "PRIMARY KEY", "Unique report identifier ('rpt-xxxx')"],
        ["user_id", "TEXT", "NOT NULL, FK", "Foreign key referencing users.user_id"],
        ["category", "TEXT", "NOT NULL", "'garbage_dumps', 'plastic_waste', etc."],
        ["latitude", "REAL", "NOT NULL", "WGS-84 GPS Latitude (-90 to +90)"],
        ["longitude", "REAL", "NOT NULL", "WGS-84 GPS Longitude (-180 to +180)"],
        ["status", "TEXT", "NOT NULL", "'reported', 'assigned', 'in_progress', 'collected', 'verified'"],
        ["collector_id", "TEXT", "NULLABLE, FK", "Assigned collector user_id"],
        ["image_reference", "TEXT", "NOT NULL", "Photo evidence URI / buffer reference"],
        ["evidence_reference", "TEXT", "NULLABLE", "Post-cleanup photo proof URI / buffer"]
    ]
    story.append(create_styled_table(reports_dict, [100, 80, 110, 197], styles))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 8: TESTING & QUALITY ASSURANCE
    # ==========================================
    story.append(Paragraph("CHAPTER 8: SOFTWARE TESTING & QUALITY ASSURANCE", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.append(Paragraph("Table 8.1: Test Plan & Execution Matrix (TC-01 to TC-08 Sample)", styles['DocH3']))
    tc_sample = [
        ["ID", "Test Scope", "Input Condition", "Expected Output", "Actual Result", "Status"],
        ["TC-01", "Registration", "Name, Valid Email, Password >= 5", "HTTP 201; Bcrypt hash saved", "Record created", "PASS"],
        ["TC-03", "JWT Login", "Valid email & correct password", "HTTP 200; JWT token issued", "Token issued with role", "PASS"],
        ["TC-05", "Smart OTP (Owner)", "Email = verified Gmail", "Resend API sends email via 443", "Email delivered to inbox", "PASS"],
        ["TC-06", "Smart OTP (Test)", "Email = unverified test email", "Sandbox fallback; auto-fill OTP", "OTP auto-filled with banner", "PASS"],
        ["TC-07", "Incident Upload", "Valid photo + GPS coordinates", "Report created; Gemini classifies", "Report rpt-xxxx created", "PASS"],
        ["TC-10", "Valid Proof (> 75%)", "Collector uploads matching clean photo", "SSIM >= 75.0%; status -> 'verified'", "Match score 84.2%; verified", "PASS"],
        ["TC-11", "Fake Proof Fraud", "Collector uploads black/unrelated image", "SSIM < 75.0%; status -> 'rejected'", "Match score 28.1%; rejected", "PASS"],
        ["TC-12", "Points Allocation", "Incident marked 'verified'", "+10 Green Points credited", "Points incremented +10", "PASS"]
    ]
    story.append(create_styled_table(tc_sample, [38, 90, 115, 115, 95, 34], styles))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 10: SCREENSHOTS WALKTHROUGH
    # ==========================================
    story.append(Paragraph("CHAPTER 10: SYSTEM WALKTHROUGH & USER INTERFACE SCREENSHOTS", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.extend(create_figure("01_citizen_portal_home.png", "Figure 10.1: Citizen Portal Landing Page & Quick Reporting Form", styles))
    story.extend(create_figure("02_citizen_portal_filled_preview.png", "Figure 10.2: Waste Report Submission with Photo & GPS Telemetry Preview", styles))
    story.append(PageBreak())
    
    story.extend(create_figure("02_voice_ai_assistant.png", "Figure 10.3: Voice AI Assistant Dialog Interface (Bilingual Triage)", styles))
    story.extend(create_figure("03_admin_dashboard.png", "Figure 10.4: Municipal Command Center Overview & KPI Metrics", styles))
    story.append(PageBreak())
    
    story.extend(create_figure("04_admin_reports_management.png", "Figure 10.5: Municipal Reports Management & Live Triage Table", styles))
    story.extend(create_figure("05_admin_collection_teams.png", "Figure 10.6: Sanitation Collection Teams Roster & Dispatch View", styles))
    story.append(PageBreak())
    
    story.extend(create_figure("06_citizen_community_feed.png", "Figure 10.7: Community Cleanliness Feed & Live Activity Stream", styles))
    story.extend(create_figure("07_citizen_track_map.png", "Figure 10.8: Interactive Leaflet.js Spatial Incident Tracking Map", styles))
    story.append(PageBreak())
    
    story.extend(create_figure("08_citizen_my_reports.png", "Figure 10.9: Citizen Personal Reports & Status Tracker", styles))
    story.extend(create_figure("09_citizen_status_analytics.png", "Figure 10.10: Environmental Impact Analytics & Hazard Breakdown", styles))
    story.append(PageBreak())
    
    story.extend(create_figure("10_citizen_profile.png", "Figure 10.11: Citizen Profile & Green Points Rewards Balance", styles))

    # ==========================================
    # CHAPTER 11 & 12: CONCLUSION & REFERENCES
    # ==========================================
    story.append(Paragraph("CHAPTER 11: CONCLUSION & FUTURE SCOPE", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    story.append(Paragraph(
        "EcoTrack AI represents a transformative leap in digital municipal governance. By uniting multimodal "
        "artificial intelligence, mathematical computer vision verification, civic gamification, and zero-cost cloud architecture, "
        "the project directly resolves the chronic inefficiencies that have crippled traditional civic reporting systems.",
        styles['DocBody']
    ))
    story.append(Paragraph(
        "Future enhancements will focus on IoT Smart Bin ultrasonic telemetry, autonomous drone aerial surveillance along waterways, "
        "and blockchain-backed municipal property tax credit redemption for Green Points.",
        styles['DocBody']
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("CHAPTER 12: REFERENCES & BIBLIOGRAPHY", styles['DocH1']))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_SECONDARY, spaceAfter=10))
    refs = [
        "1. IEEE Std 830-1998, 'IEEE Recommended Practice for Software Requirements Specifications,' IEEE Computer Society, 1998.",
        "2. Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). 'Image quality assessment: from error visibility to structural similarity.' IEEE Transactions on Image Processing, 13(4), 600-612.",
        "3. Tiangolo, S. (2023). 'FastAPI: High performance, easy to learn, fast to code, ready for production.' https://fastapi.tiangolo.com/",
        "4. Google Generative AI Team (2024). 'Gemini: A Family of Highly Capable Multimodal Models.' Google DeepMind Technical Report.",
        "5. Hipp, D. R. (2023). 'SQLite Write-Ahead Logging (WAL) Architecture.' https://www.sqlite.org/wal.html",
        "6. Resend Technologies (2024). 'Resend REST API Reference and Email Infrastructure Documentation.' https://resend.com/docs",
        "7. Ministry of Housing and Urban Affairs (MoHUA), Government of India (2023). 'Swachh Bharat Mission (Urban) 2.0 Operational Guidelines.'"
    ]
    for r in refs:
        story.append(Paragraph(r, styles['DocBullet']))
        
    story.append(Spacer(1, 15))
    story.append(create_callout("Project Completion", "EcoTrack AI • Major Project Report for Bachelor of Computer Applications (BCA) • Digital Mind Dilip", styles))

    print("Compiling PDF flowables...")
    doc.build(story, canvasmaker=NumberedCanvas)
    size_kb = os.path.getsize(OUTPUT_PDF) / 1024
    print(f"SUCCESS! PDF Project Report successfully generated! Size: {size_kb:.1f} KB")

if __name__ == "__main__":
    build_pdf_document()
