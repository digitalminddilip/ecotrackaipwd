import json
import os
import smtplib
from email.message import EmailMessage
from urllib.error import URLError
from urllib.request import Request, urlopen

from .database import find_user_by_id


def _send_email(recipient: str, report_id: str, address: str) -> str:
    smtp_host = os.getenv("CLEANCONNECT_SMTP_HOST")
    smtp_user = os.getenv("CLEANCONNECT_SMTP_USER")
    smtp_password = os.getenv("CLEANCONNECT_SMTP_PASSWORD")
    smtp_port = int(os.getenv("CLEANCONNECT_SMTP_PORT", "587"))
    if not all([smtp_host, smtp_user, smtp_password]):
        return "email-not-configured"

    message = EmailMessage()
    message["Subject"] = f"CleanConnect: Your Report {report_id} has been Resolved"
    message["From"] = smtp_user
    message["To"] = recipient
    message.set_content(
        f"Hello,\n\nWe are pleased to inform you that your report (Reference No: {report_id}) has been successfully resolved and cleaned.\n\nThank you for helping keep the community clean!\n\nBest,\nThe CleanConnect Team"
    )
    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)
    return "email-sent"


def _send_agent_webhook(payload: dict[str, object]) -> str:
    webhook_url = os.getenv("CLEANCONNECT_AGENT_WEBHOOK")
    if not webhook_url:
        return "agent-not-configured"
    request = Request(
        webhook_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=10):
            return "agent-notified"
    except (URLError, TimeoutError):
        return "agent-unavailable"


def notify_reporter(report_id: str, reporter_id: str, address: str | None) -> dict[str, str]:
    user = find_user_by_id(reporter_id)
    if not user:
        return {"email": "reporter-not-found", "agent": "skipped"}
    location = address or "the reported location"
    result = {"email": "email-not-configured", "agent": "agent-not-configured"}
    if user.get("email"):
        try:
            result["email"] = _send_email(user["email"], report_id, location)
        except (OSError, smtplib.SMTPException):
            result["email"] = "email-failed"
    result["agent"] = _send_agent_webhook({
        "event": "location_cleaned",
        "report_id": report_id,
        "reporter_id": reporter_id,
        "reporter_email": user.get("email"),
        "address": address,
    })
    return result


def send_otp_email(recipient: str, otp: str) -> str:
    smtp_host = os.getenv("CLEANCONNECT_SMTP_HOST", "smtp.gmail.com")
    smtp_user = os.getenv("CLEANCONNECT_SMTP_USER", "ecotrackaipwd@gmail.com")
    smtp_password = os.getenv("CLEANCONNECT_SMTP_PASSWORD", "dhdy tbju hhav ncgu")
    smtp_port = int(os.getenv("CLEANCONNECT_SMTP_PORT", "587"))

    message = EmailMessage()
    message["Subject"] = f"CleanConnect Verification Code: {otp}"
    message["From"] = f"CleanConnect Security <{smtp_user}>"
    message["To"] = recipient
    message.set_content(
        f"Hello,\n\n"
        f"Your CleanConnect verification code is: {otp}\n\n"
        f"This code will expire in 10 minutes. Please enter this code in the portal to continue.\n\n"
        f"If you did not request this code, please ignore this email.\n\n"
        f"Best regards,\n"
        f"CleanConnect AI Team"
    )
    # Support HTTPS email delivery (Port 443 - works on Render Free Tier)
    resend_api_key = os.getenv("RESEND_API_KEY")
    if resend_api_key:
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=json.dumps({
                    "from": "CleanConnect <onboarding@resend.dev>",
                    "to": [recipient],
                    "subject": f"CleanConnect Verification Code: {otp}",
                    "text": f"Your CleanConnect verification code is: {otp}\n\nThis code will expire in 10 minutes.",
                }).encode(),
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5):
                return "email-sent"
        except Exception as e:
            print(f"[RESEND ERROR] {e}")

    try:
        # Port 587 with fast 3-second timeout so requests don't hang when cloud blocks SMTP
        with smtplib.SMTP(smtp_host, smtp_port, timeout=3) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
        return "email-sent"
    except (OSError, smtplib.SMTPException) as e:
        print(f"\n[SMTP ERROR] Outbound SMTP port blocked on host ({e}). Falling back to in-app OTP.\n")
        return "email-failed"


def notify_report_created(report_id: str, reporter_id: str) -> dict[str, str]:
    user = find_user_by_id(reporter_id)
    if not user:
        return {"email": "reporter-not-found"}
        
    reporter_email = user.get("email")
    if not reporter_email:
        return {"email": "email-not-configured"}
        
    smtp_host = os.getenv("CLEANCONNECT_SMTP_HOST")
    smtp_user = os.getenv("CLEANCONNECT_SMTP_USER")
    smtp_password = os.getenv("CLEANCONNECT_SMTP_PASSWORD")
    smtp_port = int(os.getenv("CLEANCONNECT_SMTP_PORT", "587"))

    if not all([smtp_host, smtp_user, smtp_password]):
        return {"email": "email-not-configured"}

    message = EmailMessage()
    message["Subject"] = f"CleanConnect: Your Report {report_id} has been Received"
    message["From"] = smtp_user
    message["To"] = reporter_email
    message.set_content(
        f"Hello,\n\nWe have successfully received your report. Your Tracking Reference Number is: {report_id}.\n\nYou can use this number to track the status of your complaint in our system.\n\nThank you for helping keep the community clean!\n\nBest,\nThe CleanConnect Team"
    )
    
    admin_message = EmailMessage()
    admin_message["Subject"] = f"CleanConnect: New Report {report_id} Submitted"
    admin_message["From"] = smtp_user
    admin_message["To"] = "dilipksharma1244@gmail.com"
    admin_message.set_content(
        f"Hello Admin,\n\nA new report has been submitted by {reporter_email} with Tracking Reference Number: {report_id}.\n\nPlease check the dashboard for more details.\n\nBest,\nThe CleanConnect System"
    )
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
            server.send_message(admin_message)
        return {"email": "email-sent"}
    except (OSError, smtplib.SMTPException) as e:
        return {"email": "email-failed"}

def notify_report_rejected(report_id: str, reporter_id: str, collector_id: str, admin_email: str) -> None:
    smtp_host = os.getenv('CLEANCONNECT_SMTP_HOST')
    smtp_user = os.getenv('CLEANCONNECT_SMTP_USER')
    smtp_password = os.getenv('CLEANCONNECT_SMTP_PASSWORD')
    smtp_port = int(os.getenv('CLEANCONNECT_SMTP_PORT', '587'))
    if not all([smtp_host, smtp_user, smtp_password]):
        print(f'\n[DEV MODE] Report {report_id} REJECTED email would be sent to Admin, Collector, and Citizen.\n')
        return

    reporter = find_user_by_id(reporter_id)
    collector = find_user_by_id(collector_id) if collector_id else None
    
    recipients = []
    if reporter and reporter.get('email'):
        recipients.append(reporter['email'])
    if collector and collector.get('email'):
        recipients.append(collector['email'])
    if admin_email:
        recipients.append(admin_email)
        
    if not recipients:
        return

    message = EmailMessage()
    message['Subject'] = f'CleanConnect: Report {report_id} Evidence Rejected'
    message['From'] = smtp_user
    message['To'] = ', '.join(recipients)
    message.set_content(
        f'Hello,\n\nThe cleanup evidence for report (Reference No: {report_id}) was reviewed and REJECTED by the administration.\n\nCollector: Please re-visit the location and upload a new valid photo of the cleaned area.\nCitizen: The cleanup is still pending and is being re-addressed.\n\nBest,\nThe CleanConnect Team'
    )
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as e:
        print(f'\n[DEV MODE] Failed to send rejection email: {e}\n')


