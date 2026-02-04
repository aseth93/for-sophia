from flask import Flask, request, send_file
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

app = Flask(__name__)

# Email configuration - uses environment variables for security
EMAIL_TO = "abe.seth93@gmail.com"
EMAIL_FROM = os.environ.get("GMAIL_ADDRESS", "abe.seth93@gmail.com")
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

LOG_FILE = "visitors.log"

def send_email(ip, timestamp):
    if not APP_PASSWORD:
        print("No Gmail App Password set - skipping email")
        return

    try:
        msg = MIMEText(f"""
Someone visited your Valentine's page!

IP Address: {ip}
Time: {timestamp}

Could it be Sophia? Go check!
        """)
        msg['Subject'] = "Valentine's Page Visitor Alert!"
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, APP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent for IP: {ip}")
    except Exception as e:
        print(f"Email failed: {e}")

def log_visitor(ip):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log to file
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {ip}\n")

    print(f"Visitor: {ip} at {timestamp}")

    # Send email notification
    send_email(ip, timestamp)

@app.route('/')
def home():
    # Get visitor IP (handles proxies)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()
    log_visitor(ip)

    return send_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
