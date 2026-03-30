import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from ..config import get_settings


async def send_email(
    to: str,
    subject: str,
    body_html: str,
    attachment_path: str | None = None,
) -> bool:
    """Send an email via SMTP. Returns True on success."""
    settings = get_settings()
    smtp_host = getattr(settings, "smtp_host", "")
    smtp_port = int(getattr(settings, "smtp_port", 587))
    smtp_user = getattr(settings, "smtp_user", "")
    smtp_password = getattr(settings, "smtp_password", "")

    if not all([smtp_host, smtp_user, smtp_password]):
        # SMTP not configured — log and return
        print(f"[EMAIL SKIPPED] To: {to}, Subject: {subject} (SMTP not configured)")
        return False

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body_html, "html"))

    if attachment_path:
        path = Path(attachment_path)
        if path.exists():
            with open(path, "rb") as f:
                part = MIMEApplication(f.read(), Name=path.name)
                part["Content-Disposition"] = f'attachment; filename="{path.name}"'
                msg.attach(part)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def render_post_service_email(customer_name: str, address: str,
                              products: str, instructions: str,
                              next_visit: str = "") -> str:
    """Render a post-service notification email."""
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
        <div style="background:#2d6a4f;color:#fff;padding:20px;text-align:center;">
            <h2 style="margin:0;">TX TURF PROS</h2>
            <p style="margin:5px 0 0;opacity:.8;">Professional Lawn Care</p>
        </div>
        <div style="padding:20px;background:#f9f9f9;">
            <p>Hi {customer_name},</p>
            <p>TX TURF PROS treated your lawn today at <strong>{address}</strong>.</p>
            <h3 style="color:#2d6a4f;">What We Applied</h3>
            <p>{products}</p>
            <h3 style="color:#2d6a4f;">Care Instructions</h3>
            <p>{instructions}</p>
            {"<h3 style='color:#2d6a4f;'>Next Visit</h3><p>" + next_visit + "</p>" if next_visit else ""}
            <p>Thank you for choosing TX TURF PROS!<br>— Cory</p>
        </div>
        <div style="padding:10px 20px;font-size:12px;color:#999;text-align:center;">
            TX TURF PROS LLC &bull; Lakeway, TX &bull; TDA Licensed Applicator
        </div>
    </div>
    """
