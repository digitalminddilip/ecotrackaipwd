# 🚀 EcoTrack AI (CleanConnect) - IBM Z Community Cloud Deployment Guide

[![IBM Z](https://img.shields.io/badge/Architecture-IBM%20Z%20%7C%20LinuxONE%20(s390x)-052F5F?style=for-the-badge&logo=ibm)](https://www.ibm.com/it-infrastructure/linuxone)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Container-Docker%20Multi--Arch-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)]()

**EcoTrack AI (CleanConnect)** is a next-generation civic intelligence and waste reporting system built to run seamlessly on **IBM Z (s390x) / LinuxONE Community Cloud**. It empowers citizens to report civic hazards and garbage dumps using AI image analysis, real-time geolocation, and voice assistance, while providing municipal administrators with actionable spatial analytics.

---

## ⚡ Method 1: 1-Click Automated Deployment on IBM Z (Recommended)

When you SSH into your **IBM Z / LinuxONE Community Cloud VM** (Ubuntu / RHEL on `s390x`):

```bash
# 1. Clone the repository
git clone https://github.com/virus-x09/ecotrack-ai.git
cd ecotrack-ai

# 2. Run the 1-click automated deployment script
chmod +x deploy-ibm-z.sh
./deploy-ibm-z.sh
```

That's it! The script will:
- Automatically detect the `s390x` architecture
- Install all OS libraries (`sqlite3`, `python3-venv`, `gcc`)
- Build the Python virtual environment and dependencies
- Register and start the **systemd service** (`ecotrack.service`) to keep the server running 24/7
- Display your **Public IP** and clickable URLs!

---

## 🐳 Method 2: Docker / Container Deployment on IBM Z

EcoTrack AI includes a multi-architecture Dockerfile verified for IBM Z (`linux/s390x`):

```bash
# Build the Docker image natively on LinuxONE
docker build -t ecotrack-ai:ibm-z .

# Run the container in background
docker run -d \
  --name ecotrack-ai \
  --restart always \
  -p 8000:8000 \
  ecotrack-ai:ibm-z
```

Or using **Docker Compose**:
```bash
docker compose up -d
```

---

## 🔑 Demo & Testing Credentials

| Role | Email | Password | Access / Features |
| :--- | :--- | :--- | :--- |
| **Administrator** | `dilipksharma1244@gmail.com` | `Dilip@2006` | Full Admin Dashboard, status approvals, collector assignments |
| **Collector** | `digitalminddilip0906@gmail.com` | *(OTP Login)* | Collector portal, task acceptance, evidence upload |
| **Citizen / Guest** | `citizen@cleanconnect.local` | `Citizen@123` | Public reporting, voice assistant, leaderboard |

---

## 🌐 URLs & Endpoints

Assuming your IBM Z Community Cloud Public IP is `148.100.x.x` (or domain):

- **Citizen Web Portal:** `http://<YOUR_LINUXONE_IP>:8000`
- **Admin Dashboard:** `http://<YOUR_LINUXONE_IP>:8000/admin/`
- **API Documentation (Swagger):** `http://<YOUR_LINUXONE_IP>:8000/docs`
- **Health Check Endpoint:** `http://<YOUR_LINUXONE_IP>:8000/health`

---

## 🔍 Verification Commands on IBM Z VM

Check health status:
```bash
curl -i http://localhost:8000/health
```
*Expected response:* `HTTP/1.1 200 OK` `{"status":"ok"}`

Check background systemd service status:
```bash
sudo systemctl status ecotrack.service
```

View live logs:
```bash
journalctl -u ecotrack.service -f
```

---

## 🏗️ IBM Z / LinuxONE Architectural Compatibility Highlights

1. **Native s390x Compilation**: Pure Python backend with dependencies compatible with IBM Z LinuxONE s390x instruction set.
2. **SQLite Zero-Overhead Embedded Engine**: Embedded SQL database stored locally with pre-populated reports, ensuring fast evaluation without requiring external database provisioning.
3. **Multi-Arch Docker Ready**: Base image `python:3.11-slim` with multi-arch manifest including `linux/s390x`.
4. **Resilient Systemd Unit**: Guarantees high availability and automatic recovery on IBM enterprise cloud infrastructure.
