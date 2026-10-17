# 🌿 EcoTrack AI (CleanConnect)
### *Next-Gen AI-Powered Civic Cleanliness & Municipal Waste Intelligence Platform*
#### **Built & Optimized for IBM Z® Datathon / IBM LinuxONE Community Cloud (s390x)**

[![IBM LinuxONE](https://img.shields.io/badge/Deployed%20on-IBM%20LinuxONE%20Community%20Cloud-052F5F?style=for-the-badge&logo=ibm)](https://www.ibm.com/it-infrastructure/linuxone)
[![Architecture](https://img.shields.io/badge/Architecture-s390x%20%7C%20x86_64-006699?style=for-the-badge)](https://www.ibm.com/z)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Uvicorn-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Container-Docker%20Multi--Arch-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.style=for-the-badge)]()

---

## 📌 Executive Summary
**EcoTrack AI (CleanConnect)** is an enterprise-grade civic cleanliness platform designed to streamline urban sanitation operations, empower citizens, and provide municipal authorities with real-time spatial analytics.

By leveraging **IBM Z (LinuxONE)** enterprise cloud infrastructure, the platform benefits from:
- **Mission-Critical Reliability:** 99.999% uptime for civic reporting and emergency sanitation alerts.
- **High Concurrency & Fast Throughput:** Efficient processing of high-volume citizen reports and AI queries.
- **Enterprise Security:** Hardened Linux kernel on s390x architecture with role-based access control.

---

## 🚀 Key Features

1. 📸 **Multimodal AI Waste Classification**:
   - Automated categorization of reported hazards (Garbage Dumps, Dead Animals, Blocked Drains, Uncleaned Dustbins) using Gemini Multimodal AI and local perceptual hashing.
2. 🎙️ **Voice AI Civic Assistant**:
   - Conversational voice reporting in **English & Hinglish**, enabling citizens to report sanitation issues simply by speaking aloud.
3. 🗺️ **Live GIS Geospatial Mapping**:
   - Interactive clustering and visual markers across urban zones with GPS geotagging and reverse geocoding.
4. 👨‍💼 **3 Role-Based Portals**:
   - **Citizen:** Report issues, track status, earn cleanliness rewards & leaderboard points.
   - **Collector:** Dedicated task acceptance, turn-by-turn routing, and before-and-after photo evidence verification.
   - **Administrator:** Comprehensive analytics, collector dispatching, audit trails, and status approval workflows.
5. 🔐 **Zero-Friction Authentication**:
   - JWT authentication, secure bcrypt hashing, Google Sign-In, and SMTP OTP verification.

---

## ⚡ Quick Deployment on IBM Z Community Cloud

### Option A: 1-Click Automated Script (Recommended)
On your IBM LinuxONE Community Cloud virtual machine:
```bash
git clone https://github.com/dilipksharma1244-ops/Clean-Connect-AI.git
cd Clean-Connect-AI
chmod +x deploy-ibm-z.sh
./deploy-ibm-z.sh
```
*The script installs all s390x dependencies, builds the environment, starts `ecotrack.service` via systemd, and prints your live public URL.*

### Option B: Docker Container on IBM Z (s390x)
```bash
# Build multi-arch container
docker build -t ecotrack-ai:ibm-z .

# Run container
docker run -d -p 8000:8000 --name ecotrack-ai --restart always ecotrack-ai:ibm-z
```

---

## 🔑 Demo Access Credentials

| Role | Email | Password | Access Details |
| :--- | :--- | :--- | :--- |
| 🛡️ **Administrator** | `dilipksharma1244@gmail.com` | `Dilip@2006` | Access `/admin/` for executive analytics & management |
| 🚛 **Sanitation Collector**| `digitalminddilip0906@gmail.com` | *(OTP Login)* | Collector mobile interface & pickup confirmation |
| 👤 **Citizen / Public** | `citizen@cleanconnect.local` | `Citizen@123` | Public reporting, Voice AI, Leaderboard |

---

## 🌐 Endpoints & API

- **Web Application:** `http://<LINUXONE_IP>:8000/`
- **Admin Command Center:** `http://<LINUXONE_IP>:8000/admin/`
- **Interactive Swagger Docs:** `http://<LINUXONE_IP>:8000/docs`
- **System Health Check:** `http://<LINUXONE_IP>:8000/health`

---

## 🏛️ System Architecture

```
[ Citizens / Collectors / Admins ]
              │ (HTTP / WebSockets / Voice)
              ▼
    [ IBM LinuxONE (s390x) ]
              │
   ┌──────────┴─────────────────────────┐
   │  FastAPI + Uvicorn Async Server     │
   ├────────────────────────────────────┤
   │  • Multimodal AI Image Classifier  │
   │  • Voice AI Assistant (Gemini)     │
   │  • Geospatial Routing Service      │
   │  • JWT Auth & RBAC Security        │
   └──────────┬─────────────────────────┘
              │
   ┌──────────┴─────────────────────────┐
   │  Embedded SQLite High-Speed DB     │
   │  (cleanconnect.db)                 │
   └────────────────────────────────────┘
```

---

## 📄 Submission Checklist
- [x] Tested & compatible with **IBM Z / LinuxONE (`s390x`)**
- [x] Dockerfile & `docker-compose.yml` verified
- [x] Multi-user role-based authentication working
- [x] Interactive UI + Admin dashboard verified
- [x] Automated systemd 24/7 service ready
- [x] Pre-seeded with 29 active reports and demo accounts
