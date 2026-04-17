import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from nicegui import app

def send_email_alert(subject: str, message: str):
    """
    Send an email alert using SMTP settings from the application config.
    """
    cfg = app.storage.user.get('config', {}).get('notifications', {})
    if not cfg.get('enabled', False):
        return

    smtp_server = cfg.get('smtp_server')
    smtp_port = cfg.get('smtp_port', 587)
    smtp_user = cfg.get('smtp_user')
    # For safety, in a production app this should be encrypted or stored in env vars
    smtp_pass = cfg.get('smtp_pass')
    target_email = cfg.get('target_email')

    if not all([smtp_server, smtp_user, smtp_pass, target_email]):
        print("Alert skipped: SMTP configuration incomplete.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = target_email
        msg['Subject'] = f"QualityPulse Alert: {subject}"
        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"Alert sent to {target_email}: {subject}")
    except Exception as e:
        print(f"Failed to send email alert: {e}")
