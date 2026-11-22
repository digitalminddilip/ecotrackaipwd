"""
EcoTrack AI - BCA Project Report Generator
Generates submission-ready DOCX and PDF files for college submission (hard copy printout).
Author: Dilip Sharma (DIGITAL MIND DILIP)
"""

import os
import sys
from datetime import datetime

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "report_assets")
OUTPUT_DOCX = os.path.join(BASE_DIR, "EcoTrack_AI_Project_Report.docx")
OUTPUT_PDF = os.path.join(BASE_DIR, "EcoTrack_AI_Project_Report.pdf")

print("Base Dir:", BASE_DIR)
print("Assets Dir:", ASSETS_DIR)
